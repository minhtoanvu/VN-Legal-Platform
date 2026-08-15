import React, { useState, useRef, useEffect } from 'react';
import { Search, Cpu, BarChart2, Zap, X } from 'lucide-react';
import type { SearchMode } from '../../types';

interface SearchBarProps {
  value: string;
  onChange: (val: string) => void;
  onSearch: (query: string, mode: SearchMode) => void;
  mode: SearchMode;
  onModeChange: (mode: SearchMode) => void;
  isLoading?: boolean;
}

const MODES: { key: SearchMode; label: string; icon: React.ReactNode; desc: string }[] = [
  { key: 'hybrid',   label: 'Hybrid',   icon: <Zap size={14} />,      desc: 'Kết hợp BM25 + Semantic (tốt nhất)' },
  { key: 'semantic', label: 'Semantic', icon: <Cpu size={14} />,      desc: 'Tìm theo ngữ nghĩa (AI vector search)' },
  { key: 'keyword',  label: 'Từ khóa',  icon: <BarChart2 size={14} />, desc: 'Tìm theo từ khóa chính xác (BM25)' },
];

export const SearchBar: React.FC<SearchBarProps> = ({ value, onChange, onSearch, mode, onModeChange, isLoading }) => {
  const inputRef = useRef<HTMLInputElement>(null);
  const [focused, setFocused] = useState(false);

  // Keyboard shortcut: Ctrl+K / Cmd+K
  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        inputRef.current?.focus();
      }
    };
    window.addEventListener('keydown', handler);
    return () => window.removeEventListener('keydown', handler);
  }, []);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (value.trim()) onSearch(value.trim(), mode);
  };

  return (
    <div style={{ width: '100%' }}>
      {/* Mode selector */}
      <div style={{ display: 'flex', gap: '8px', marginBottom: '12px' }}>
        {MODES.map(({ key, label, icon, desc }) => (
          <button
            key={key}
            type="button"
            title={desc}
            onClick={() => onModeChange(key)}
            style={{
              display: 'flex', alignItems: 'center', gap: '6px',
              padding: '6px 14px',
              fontSize: '0.82rem', fontWeight: mode === key ? 700 : 500,
              borderRadius: '999px',
              border: `1px solid ${mode === key ? 'var(--primary)' : 'var(--border-light)'}`,
              background: mode === key ? 'var(--primary-glow)' : 'transparent',
              color: mode === key ? 'var(--primary)' : 'var(--text-muted)',
              cursor: 'pointer',
              transition: 'all 0.15s ease',
            }}
          >
            {icon}
            {label}
          </button>
        ))}
      </div>

      {/* Search input */}
      <form onSubmit={handleSubmit} style={{ position: 'relative' }}>
        <div
          style={{
            display: 'flex', alignItems: 'center',
            background: focused ? 'rgba(15,22,38,0.9)' : 'rgba(15,22,38,0.6)',
            border: `1.5px solid ${focused ? 'var(--primary)' : 'var(--border-medium)'}`,
            borderRadius: '12px',
            boxShadow: focused ? '0 0 0 3px var(--primary-glow)' : 'none',
            transition: 'all 0.2s ease',
            overflow: 'hidden',
          }}
        >
          <span style={{ paddingLeft: '18px', color: 'var(--text-muted)', flexShrink: 0 }}>
            <Search size={20} />
          </span>
          <input
            ref={inputRef}
            type="text"
            value={value}
            onChange={(e) => onChange(e.target.value)}
            onFocus={() => setFocused(true)}
            onBlur={() => setFocused(false)}
            placeholder="Tìm kiếm văn bản pháp luật... (Ctrl+K)"
            style={{
              flex: 1, padding: '16px 12px',
              background: 'transparent', border: 'none', outline: 'none',
              color: 'var(--text-primary)', fontSize: '1rem',
              fontFamily: 'var(--font-body)',
            }}
          />
          {value && (
            <button
              type="button"
              onClick={() => onChange('')}
              style={{ padding: '0 12px', background: 'none', border: 'none', color: 'var(--text-muted)', cursor: 'pointer' }}
            >
              <X size={16} />
            </button>
          )}
          <button
            type="submit"
            className="btn btn-primary"
            disabled={isLoading || !value.trim()}
            style={{ margin: '8px', borderRadius: '8px', padding: '10px 22px', flexShrink: 0 }}
          >
            {isLoading ? (
              <span style={{ animation: 'spin 1s linear infinite', display: 'inline-block' }}>⟳</span>
            ) : 'Tìm kiếm'}
          </button>
        </div>
      </form>

      {/* Hint */}
      <p style={{ marginTop: '8px', fontSize: '0.78rem', color: 'var(--text-muted)' }}>
        {MODES.find(m => m.key === mode)?.desc}
      </p>
    </div>
  );
};
