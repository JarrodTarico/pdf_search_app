import React from 'react';
import type { SearchResult } from '../types';

interface SearchResultsProps {
  results: SearchResult[];
  query: string;
}

export function SearchResults({ results, query }: SearchResultsProps) {
  if (results.length === 0) {
    return (
      <div className="search-results empty">
        <p>No results found for "{query}"</p>
      </div>
    );
  }

  const formatConfidence = (score: number): string => {
    return `${(score * 100).toFixed(1)}%`;
  };

  const getConfidenceClass = (score: number): string => {
    if (score >= 0.7) return 'high';
    if (score >= 0.4) return 'medium';
    return 'low';
  };

  const formatSentiment = (score: number): string => {
    if (score >= 0.05) return 'Positive';
    if (score <= -0.05) return 'Negative';
    return 'Neutral';
  };

  const getSentimentClass = (score: number): string => {
    if (score >= 0.05) return 'positive';
    if (score <= -0.05) return 'negative';
    return 'neutral';
  };

  const highlightSnippet = (snippet: string, query: string): React.ReactNode => {
    const terms = query.toLowerCase().split(/\s+/).filter((t) => t.length > 1);
    if (terms.length === 0) return snippet;

    // Create a regex pattern for all query terms
    const pattern = new RegExp(`(${terms.map((t) => t.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')).join('|')})`, 'gi');
    const parts = snippet.split(pattern);

    return parts.map((part, index) => {
      const isMatch = terms.some((term) => part.toLowerCase() === term.toLowerCase());
      return isMatch ? (
        <mark key={index}>{part}</mark>
      ) : (
        <span key={index}>{part}</span>
      );
    });
  };

  return (
    <div className="search-results">
      <h3>
        Found {results.length} result{results.length !== 1 ? 's' : ''} for "{query}"
      </h3>
      <div className="results-list">
        {results.map((result) => (
          <div key={result.pdf_id} className="result-card">
            <div className="result-header">
              <div className="result-filename">
                <svg
                  className="pdf-icon"
                  xmlns="http://www.w3.org/2000/svg"
                  width="20"
                  height="20"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                >
                  <path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z" />
                  <polyline points="14 2 14 8 20 8" />
                </svg>
                <span>{result.filename}</span>
              </div>
              <div className="badges">
                <div className={`confidence-badge ${getConfidenceClass(result.confidence_score)}`}>
                  {formatConfidence(result.confidence_score)} match
                </div>
                <div className={`sentiment-badge ${getSentimentClass(result.sentiment_score)}`}>
                  {formatSentiment(result.sentiment_score)}
                </div>
              </div>
            </div>
            <div className="result-snippet">
              {highlightSnippet(result.snippet, query)}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
