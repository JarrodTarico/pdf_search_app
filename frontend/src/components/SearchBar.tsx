import React, { useState, useCallback } from 'react';

interface SearchBarProps {
  onSearch: (query: string) => void;
  isSearching: boolean;
}

export function SearchBar({ onSearch, isSearching }: SearchBarProps) {
  const [query, setQuery] = useState('');

  const handleSubmit = useCallback(
    (e: React.FormEvent) => {
      e.preventDefault();
      if (query.trim()) {
        onSearch(query.trim());
      }
    },
    [query, onSearch]
  );

  const handleKeyDown = useCallback(
    (e: React.KeyboardEvent) => {
      if (e.key === 'Enter' && query.trim()) {
        onSearch(query.trim());
      }
    },
    [query, onSearch]
  );

  return (
    <div className="search-bar">
      <form onSubmit={handleSubmit}>
        <div className="search-input-container">
          <svg
            className="search-icon"
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
            <circle cx="11" cy="11" r="8" />
            <path d="m21 21-4.35-4.35" />
          </svg>
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Search across all uploaded PDFs..."
            className="search-input"
            disabled={isSearching}
          />
          <button
            type="submit"
            className="search-button"
            disabled={isSearching || !query.trim()}
          >
            {isSearching ? 'Searching...' : 'Search'}
          </button>
        </div>
      </form>
    </div>
  );
}
