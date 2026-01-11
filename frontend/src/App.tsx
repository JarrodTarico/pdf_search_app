import { useState, useCallback } from 'react';
import { FileUpload } from './components/FileUpload';
import { SearchBar } from './components/SearchBar';
import { SearchResults } from './components/SearchResults';
import { searchPDFs } from './api';
import { PDFUploadResult, SearchResult } from './types';
import './App.css';

function App() {
  const [uploadedFiles, setUploadedFiles] = useState<PDFUploadResult[]>([]);
  const [searchResults, setSearchResults] = useState<SearchResult[]>([]);
  const [currentQuery, setCurrentQuery] = useState<string>('');
  const [isSearching, setIsSearching] = useState(false);
  const [searchError, setSearchError] = useState<string | null>(null);
  const [hasSearched, setHasSearched] = useState(false);

  const handleUploadSuccess = useCallback((results: PDFUploadResult[]) => {
    setUploadedFiles((prev) => [...prev, ...results]);
  }, []);

  const handleSearch = useCallback(async (query: string) => {
    setIsSearching(true);
    setSearchError(null);
    setCurrentQuery(query);
    setHasSearched(true);

    try {
      const response = await searchPDFs(query);
      setSearchResults(response.results);
    } catch (error) {
      setSearchError('Failed to search. Please make sure the backend is running.');
      setSearchResults([]);
    } finally {
      setIsSearching(false);
    }
  }, []);

  return (
    <div className="app">
      <header className="app-header">
        <h1>PDF Search</h1>
        <p>Upload PDFs and search across their content</p>
      </header>

      <main className="app-main">
        <section className="upload-section">
          <h2>Upload PDFs</h2>
          <FileUpload onUploadSuccess={handleUploadSuccess} />

          {uploadedFiles.length > 0 && (
            <div className="uploaded-files-list">
              <h4>Uploaded PDFs ({uploadedFiles.length})</h4>
              <ul>
                {uploadedFiles.map((file) => (
                  <li key={file.pdf_id}>
                    <span className="file-icon">📄</span>
                    {file.filename}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </section>

        <section className="search-section">
          <h2>Search Documents</h2>
          <SearchBar onSearch={handleSearch} isSearching={isSearching} />

          {searchError && (
            <div className="error-message">
              {searchError}
            </div>
          )}

          {hasSearched && !searchError && (
            <SearchResults results={searchResults} query={currentQuery} />
          )}
        </section>
      </main>

      <footer className="app-footer">
        <p>PDF Search App - Built with React + FastAPI</p>
      </footer>
    </div>
  );
}

export default App;
