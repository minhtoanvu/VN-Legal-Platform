import React from 'react';
import type { SearchResponse } from '../../types';
import { DocumentCard } from './DocumentCard';
import { FileSearch } from 'lucide-react';

interface SearchResultsProps {
  response: SearchResponse | null;
  isLoading: boolean;
  query: string;
  hasSearched: boolean;
}

export const SearchResults: React.FC<SearchResultsProps> = ({ response, isLoading, query, hasSearched }) => {
  if (isLoading) {
    return (
      <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', marginTop: '24px' }}>
        {[1, 2, 3].map(i => (
          <div
            key={i}
            className="skeleton"
            style={{ height: '110px', borderRadius: 'var(--radius-md)', opacity: 1 - i * 0.15 }}
          />
        ))}
      </div>
    );
  }

  if (!hasSearched) {
    return (
      <div style={{ textAlign: 'center', padding: '64px 24px', color: 'var(--text-muted)' }}>
        <FileSearch size={48} style={{ margin: '0 auto 16px', opacity: 0.4 }} />
        <p style={{ fontSize: '1rem', fontWeight: 500 }}>Nhập từ khóa để tìm kiếm văn bản pháp luật</p>
        <p style={{ fontSize: '0.85rem', marginTop: '8px', opacity: 0.7 }}>
          Hỗ trợ hơn 1,000 văn bản pháp luật Việt Nam
        </p>
      </div>
    );
  }

  if (!response || response.results.length === 0) {
    return (
      <div style={{ textAlign: 'center', padding: '64px 24px', color: 'var(--text-muted)' }}>
        <FileSearch size={48} style={{ margin: '0 auto 16px', opacity: 0.4 }} />
        <p style={{ fontSize: '1rem', fontWeight: 500 }}>Không tìm thấy kết quả nào</p>
        <p style={{ fontSize: '0.85rem', marginTop: '8px', opacity: 0.7 }}>
          Thử tìm với từ khóa khác hoặc chuyển sang chế độ Hybrid/Semantic
        </p>
      </div>
    );
  }

  return (
    <div style={{ marginTop: '20px' }}>
      {/* Summary bar */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
        <p style={{ fontSize: '0.88rem', color: 'var(--text-secondary)' }}>
          Tìm thấy <strong style={{ color: 'var(--text-primary)' }}>{response.total}</strong> kết quả
          {response.duration_ms && (
            <span style={{ color: 'var(--text-muted)', marginLeft: '8px' }}>
              ({response.duration_ms}ms)
            </span>
          )}
        </p>
        <span style={{
          fontSize: '0.75rem', textTransform: 'uppercase', letterSpacing: '0.06em',
          color: 'var(--primary)', fontWeight: 600,
          background: 'var(--primary-glow)', padding: '3px 10px', borderRadius: '999px',
        }}>
          {response.mode === 'hybrid' ? 'Hybrid RRF' : response.mode === 'semantic' ? 'Vector Search' : 'BM25 FTS'}
        </span>
      </div>

      {/* Results list */}
      <div>
        {response.results.map(doc => (
          <DocumentCard key={doc.id} doc={doc} query={query} />
        ))}
      </div>
    </div>
  );
};
