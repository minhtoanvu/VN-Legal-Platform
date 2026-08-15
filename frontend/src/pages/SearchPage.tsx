import React, { useState, useCallback } from 'react';
import { SearchBar } from '../components/search/SearchBar';
import { SearchResults } from '../components/search/SearchResults';
import { AIChatPanel } from '../components/chat/AIChatPanel';
import type { SearchMode, SearchResponse } from '../types';
import { api } from '../services/api';
import { MessageSquare, SlidersHorizontal, X } from 'lucide-react';

export const SearchPage: React.FC = () => {
  const [query, setQuery] = useState('');
  const [mode, setMode] = useState<SearchMode>('hybrid');
  const [response, setResponse] = useState<SearchResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [hasSearched, setHasSearched] = useState(false);
  const [showChat, setShowChat] = useState(true);
  const [showFilters, setShowFilters] = useState(false);
  const [filterStatus, setFilterStatus] = useState('');
  const [filterDocType, setFilterDocType] = useState('');
  const [filterYearFrom, setFilterYearFrom] = useState('');
  const [filterField, setFilterField] = useState('');
  const [filterIssuingBody, setFilterIssuingBody] = useState('');

  const handleSearch = useCallback(async (q: string, m: SearchMode) => {
    setIsLoading(true);
    setHasSearched(true);

    try {
      const body: Record<string, unknown> = { query: q, mode: m, limit: 20 };
      const filters: Record<string, unknown> = {};
      if (filterStatus) filters.status = filterStatus;
      if (filterDocType) filters.doc_type = filterDocType;
      if (filterYearFrom) filters.year_from = parseInt(filterYearFrom);
      if (filterIssuingBody) filters.issuing_body = filterIssuingBody;
      
      // Pass the field filter to body.field instead of body.filters.field
      if (filterField) body.field = filterField;
      if (Object.keys(filters).length > 0) body.filters = filters;

      const res = await api.post<SearchResponse>('/search', body);
      setResponse(res.data);
    } catch (err) {
      console.error('Search failed:', err);
      setResponse({ results: [], total: 0, query: q, mode: m, duration_ms: 0 });
    } finally {
      setIsLoading(false);
    }
  }, [filterStatus, filterDocType, filterYearFrom, filterField, filterIssuingBody]);

  const DOC_TYPES = ['Thông tư', 'Nghị định', 'Quyết định', 'Luật', 'Nghị quyết', 'Thông tư liên tịch', 'Pháp lệnh'];
  const FIELDS = ['Lao động', 'Thuế', 'Tài chính', 'Hành chính'];

  return (
    <div style={{ display: 'flex', height: '100vh', overflow: 'hidden' }}>
      {/* Main search panel */}
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden', padding: '28px 32px' }}>
        {/* Page header */}
        <div style={{ marginBottom: '24px' }}>
          <h1 style={{ fontSize: '1.6rem', fontWeight: 800, letterSpacing: '-0.02em', marginBottom: '4px' }} className="text-gradient-primary">
            Tìm kiếm văn bản pháp luật
          </h1>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.88rem' }}>
            Tìm kiếm trong 1,000+ văn bản pháp luật Việt Nam
          </p>
        </div>

        {/* Search bar */}
        <SearchBar
          value={query}
          onChange={setQuery}
          onSearch={handleSearch}
          mode={mode}
          onModeChange={setMode}
          isLoading={isLoading}
        />

        {/* Filter toggle */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginTop: '14px' }}>
          <button
            onClick={() => setShowFilters(!showFilters)}
            className={`btn ${showFilters ? 'btn-primary' : 'btn-outline'}`}
            style={{ padding: '7px 14px', fontSize: '0.82rem', borderRadius: '8px' }}
          >
            <SlidersHorizontal size={14} />
            Bộ lọc {(filterStatus || filterDocType || filterYearFrom || filterField || filterIssuingBody) ? '●' : ''}
          </button>

          {(filterStatus || filterDocType || filterYearFrom || filterField || filterIssuingBody) && (
            <button
              onClick={() => { setFilterStatus(''); setFilterDocType(''); setFilterYearFrom(''); setFilterField(''); setFilterIssuingBody(''); }}
              style={{ background: 'none', border: 'none', color: 'var(--text-muted)', cursor: 'pointer', fontSize: '0.8rem', display: 'flex', alignItems: 'center', gap: '4px' }}
            >
              <X size={13} /> Xóa bộ lọc
            </button>
          )}
        </div>

        {/* Filters panel */}
        {showFilters && (
          <div style={{
            display: 'flex', gap: '12px', flexWrap: 'wrap',
            marginTop: '12px', padding: '16px',
            background: 'rgba(15,22,38,0.6)', border: '1px solid var(--border-light)',
            borderRadius: 'var(--radius-md)',
          }}>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
              <label style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.05em' }}>Lĩnh vực</label>
              <select
                value={filterField}
                onChange={e => setFilterField(e.target.value)}
                className="input-field"
                style={{ width: '160px', padding: '8px 12px', fontSize: '0.85rem' }}
              >
                <option value="">Tất cả</option>
                {FIELDS.map(f => <option key={f} value={f}>{f}</option>)}
              </select>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
              <label style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.05em' }}>Trạng thái</label>
              <select
                value={filterStatus}
                onChange={e => setFilterStatus(e.target.value)}
                className="input-field"
                style={{ width: '160px', padding: '8px 12px', fontSize: '0.85rem' }}
              >
                <option value="">Tất cả</option>
                <option value="active">Còn hiệu lực</option>
                <option value="expired">Hết hiệu lực</option>
                <option value="amended">Đã sửa đổi</option>
              </select>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
              <label style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.05em' }}>Loại văn bản</label>
              <select
                value={filterDocType}
                onChange={e => setFilterDocType(e.target.value)}
                className="input-field"
                style={{ width: '200px', padding: '8px 12px', fontSize: '0.85rem' }}
              >
                <option value="">Tất cả</option>
                {DOC_TYPES.map(t => <option key={t} value={t}>{t}</option>)}
              </select>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
              <label style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.05em' }}>Cơ quan ban hành</label>
              <input
                type="text"
                value={filterIssuingBody}
                onChange={e => setFilterIssuingBody(e.target.value)}
                className="input-field"
                placeholder="VD: Bộ Tài chính"
                style={{ width: '180px', padding: '8px 12px', fontSize: '0.85rem' }}
              />
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
              <label style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.05em' }}>Năm từ</label>
              <input
                type="number"
                value={filterYearFrom}
                onChange={e => setFilterYearFrom(e.target.value)}
                className="input-field"
                placeholder="2010"
                min="1945"
                max={new Date().getFullYear()}
                style={{ width: '120px', padding: '8px 12px', fontSize: '0.85rem' }}
              />
            </div>
          </div>
        )}

        {/* Results (scrollable) */}
        <div style={{ flex: 1, overflowY: 'auto', marginTop: '4px' }}>
          <SearchResults
            response={response}
            isLoading={isLoading}
            query={query}
            hasSearched={hasSearched}
          />
        </div>
      </div>

      {/* AI Chat sidebar */}
      <div style={{
        width: showChat ? '360px' : '0',
        flexShrink: 0,
        transition: 'width 0.3s cubic-bezier(0.16,1,0.3,1)',
        borderLeft: showChat ? '1px solid var(--border-light)' : 'none',
        background: showChat ? 'var(--bg-surface)' : 'transparent',
        overflow: 'hidden',
        display: 'flex', flexDirection: 'column',
      }}>
        {showChat && (
          <div style={{ padding: '16px', display: 'flex', flexDirection: 'column', height: '100%' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
              <span style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-secondary)' }}>AI Legal Assistant</span>
              <button
                onClick={() => setShowChat(false)}
                style={{ background: 'none', border: 'none', cursor: 'pointer', color: 'var(--text-muted)' }}
              >
                <X size={16} />
              </button>
            </div>
            <div style={{ flex: 1, overflow: 'hidden' }}>
              <AIChatPanel />
            </div>
          </div>
        )}
      </div>

      {/* Toggle chat button (when closed) */}
      {!showChat && (
        <button
          onClick={() => setShowChat(true)}
          className="btn btn-primary"
          style={{
            position: 'fixed', bottom: '24px', right: '24px',
            borderRadius: '50%', width: '52px', height: '52px', padding: 0,
            boxShadow: 'var(--shadow-glow)',
            zIndex: 50,
          }}
          title="Mở AI Chat"
        >
          <MessageSquare size={22} />
        </button>
      )}
    </div>
  );
};
