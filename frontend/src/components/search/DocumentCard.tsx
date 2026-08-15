import React from 'react';
import { useNavigate } from 'react-router-dom';
import type { SearchResult } from '../../types';
import { StatusBadge } from '../document/StatusBadge';
import { FileText, Calendar, Building2, ChevronRight } from 'lucide-react';

interface DocumentCardProps {
  doc: SearchResult;
  query?: string;
}

export const DocumentCard: React.FC<DocumentCardProps> = ({ doc, query }) => {
  const navigate = useNavigate();

  const highlightText = (text: string, query?: string): React.ReactNode => {
    if (!query || !text) return text;
    const parts = text.split(new RegExp(`(${query.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')})`, 'gi'));
    return parts.map((part, i) =>
      part.toLowerCase() === query.toLowerCase() ? (
        <mark key={i} style={{ background: 'rgba(99,102,241,0.25)', color: 'var(--primary)', borderRadius: '2px', padding: '0 2px' }}>
          {part}
        </mark>
      ) : part
    );
  };

  const formatDate = (dateStr: string | null): string => {
    if (!dateStr) return '—';
    return new Date(dateStr).toLocaleDateString('vi-VN', { day: '2-digit', month: '2-digit', year: 'numeric' });
  };

  return (
    <div
      className="glass-card glass-card-interactive"
      style={{ padding: '20px 24px', cursor: 'pointer', marginBottom: '12px' }}
      onClick={() => navigate(`/documents/${doc.id}`)}
      role="button"
      tabIndex={0}
      onKeyDown={(e) => e.key === 'Enter' && navigate(`/documents/${doc.id}`)}
    >
      <div style={{ display: 'flex', alignItems: 'flex-start', gap: '16px' }}>
        {/* Icon */}
        <div style={{
          flexShrink: 0,
          width: '44px', height: '44px',
          background: 'var(--primary-glow)',
          border: '1px solid rgba(99,102,241,0.2)',
          borderRadius: '10px',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
        }}>
          <FileText size={20} color="var(--primary)" />
        </div>

        {/* Content */}
        <div style={{ flex: 1, minWidth: 0 }}>
          {/* Header row */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', flexWrap: 'wrap', marginBottom: '6px' }}>
            <span style={{
              fontSize: '0.72rem', fontWeight: 700, color: 'var(--text-muted)',
              textTransform: 'uppercase', letterSpacing: '0.07em',
            }}>
              {doc.doc_type}
            </span>
            <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>{doc.doc_number}</span>
            <StatusBadge status={doc.status} size="sm" />
            {doc.rrf_score !== undefined && (
              <span style={{
                marginLeft: 'auto', fontSize: '0.72rem', color: 'var(--text-muted)',
                background: 'rgba(255,255,255,0.04)', padding: '2px 8px', borderRadius: '999px',
              }}>
                Score: {(doc.rrf_score * 100).toFixed(1)}%
              </span>
            )}
          </div>

          {/* Title */}
          <h3 style={{
            fontSize: '0.97rem', fontWeight: 600, lineHeight: 1.5,
            marginBottom: '10px', color: 'var(--text-primary)',
            display: '-webkit-box', WebkitLineClamp: 2, WebkitBoxOrient: 'vertical', overflow: 'hidden',
          }}>
            {highlightText(doc.title, query)}
          </h3>

          {/* Excerpt */}
          {(doc.content_snippet || doc.excerpt) && (
            <p style={{
              fontSize: '0.85rem', color: 'var(--text-secondary)', lineHeight: 1.6,
              marginBottom: '12px',
              display: '-webkit-box', WebkitLineClamp: 3, WebkitBoxOrient: 'vertical', overflow: 'hidden',
            }}>
              {highlightText(doc.content_snippet || doc.excerpt || "", query)}
            </p>
          )}

          {/* Meta */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '20px', flexWrap: 'wrap' }}>
            <span style={{ display: 'flex', alignItems: 'center', gap: '5px', fontSize: '0.8rem', color: 'var(--text-muted)' }}>
              <Building2 size={13} />
              {doc.issuing_body || '—'}
            </span>
            <span style={{ display: 'flex', alignItems: 'center', gap: '5px', fontSize: '0.8rem', color: 'var(--text-muted)' }}>
              <Calendar size={13} />
              {formatDate(doc.issue_date)}
            </span>
          </div>
        </div>

        {/* Arrow */}
        <ChevronRight size={18} color="var(--text-muted)" style={{ flexShrink: 0, marginTop: '2px' }} />
      </div>
    </div>
  );
};
