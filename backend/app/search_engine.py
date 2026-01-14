import re
from typing import List, Tuple
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer

from .database import get_all_pdfs

# Download VADER lexicon if not already present
try:
    nltk.data.find('sentiment/vader_lexicon.zip')
except LookupError:
    nltk.download('vader_lexicon', quiet=True)


class SearchEngine:
    """TF-IDF based search engine for PDF documents."""
    
    def __init__(self):
        self.vectorizer = TfidfVectorizer(
            lowercase=True,
            stop_words='english',
            ngram_range=(1, 2),  # Use unigrams and bigrams
            max_features=10000
        )
        self.tfidf_matrix = None
        self.documents = []
        self.sentiment_analyzer = SentimentIntensityAnalyzer()
    
    def _calculate_sentiment(self, text: str) -> float:
        """
        Calculate sentiment score for a text snippet using VADER.
        
        Args:
            text: The text to analyze
            
        Returns:
            Compound sentiment score from -1 (negative) to 1 (positive)
        """
        scores = self.sentiment_analyzer.polarity_scores(text)
        return round(scores['compound'], 4)
    
    def _build_index(self) -> None:
        """Build or rebuild the TF-IDF index from all documents in the database."""
        self.documents = get_all_pdfs()
        
        if not self.documents:
            self.tfidf_matrix = None
            return
        
        texts = [doc['text_content'] for doc in self.documents]
        self.tfidf_matrix = self.vectorizer.fit_transform(texts)
    
    def search(self, query: str, top_k: int = 10) -> List[dict]:
        """
        Search for documents matching the query.
        
        Args:
            query: The search query string
            top_k: Maximum number of results to return
            
        Returns:
            List of search results with pdf_id, filename, confidence_score, and snippet
        """
        # Always rebuild index to ensure we have latest documents
        self._build_index()
        
        if not self.documents or self.tfidf_matrix is None:
            return []
        
        # Transform query using the same vectorizer
        query_vector = self.vectorizer.transform([query])
        
        # Calculate cosine similarity between query and all documents
        similarities = cosine_similarity(query_vector, self.tfidf_matrix).flatten()
        
        # Get indices of top results (sorted by similarity, descending)
        top_indices = np.argsort(similarities)[::-1][:top_k]
        
        results = []
        for idx in top_indices:
            score = float(similarities[idx])
            
            # Only include results with non-zero similarity
            if score > 0:
                doc = self.documents[idx]
                snippet = self._extract_snippet(doc['text_content'], query)
                sentiment_score = self._calculate_sentiment(snippet)
                
                results.append({
                    'pdf_id': doc['id'],
                    'filename': doc['filename'],
                    'confidence_score': round(score, 4),
                    'sentiment_score': sentiment_score,
                    'snippet': snippet
                })
        
        return results
    
    def _extract_snippet(self, text: str, query: str, context_chars: int = 100) -> str:
        """
        Extract a snippet of text around the first occurrence of query terms.
        
        Args:
            text: The full document text
            query: The search query
            context_chars: Number of characters to include before and after match
            
        Returns:
            A snippet of text showing the match context
        """
        # Normalize text and query
        text_lower = text.lower()
        query_terms = query.lower().split()
        
        # Find the first occurrence of any query term
        best_pos = len(text)
        matched_term = ""
        
        for term in query_terms:
            if len(term) < 2:  # Skip very short terms
                continue
            pos = text_lower.find(term)
            if pos != -1 and pos < best_pos:
                best_pos = pos
                matched_term = term
        
        if best_pos == len(text):
            # No exact match found, return beginning of document
            snippet = text[:context_chars * 2].strip()
            if len(text) > context_chars * 2:
                snippet += "..."
            return snippet
        
        # Calculate snippet boundaries
        start = max(0, best_pos - context_chars)
        end = min(len(text), best_pos + len(matched_term) + context_chars)
        
        # Extract snippet
        snippet = text[start:end].strip()
        
        # Add ellipsis if we're not at the beginning/end
        if start > 0:
            snippet = "..." + snippet
        if end < len(text):
            snippet = snippet + "..."
        
        # Clean up whitespace
        snippet = re.sub(r'\s+', ' ', snippet)
        
        return snippet


# Global search engine instance
search_engine = SearchEngine()


def search_documents(query: str, top_k: int = 10) -> List[dict]:
    """
    Search for documents matching the query.
    
    Args:
        query: The search query string
        top_k: Maximum number of results to return
        
    Returns:
        List of search results
    """
    return search_engine.search(query, top_k)
