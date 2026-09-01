import React, { useEffect, useState, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import type { DocumentDetail, GraphData, Collection, Note } from '../types';
import { StatusBadge } from '../components/document/StatusBadge';
import { AIChatPanel } from '../components/chat/AIChatPanel';
import { KnowledgeGraph } from '../components/graph/KnowledgeGraph';
import { api } from '../services/api';
import {
  ArrowLeft, Calendar, Building2, FileText, GitBranch,
  Layers, Loader2, AlertTriangle, ExternalLink,
  BookmarkPlus, StickyNote, BookMarked, Trash2, Plus, Check,
} from 'lucide-react';

const RELATION_LABELS: Record<string, string> = {
  guides: 'Hướng dẫn', amends: 'Sửa đổi', replaces: 'Thay thế', revokes: 'Bãi bỏ', cites: 'Trích dẫn',
};
const RELATION_COLORS: Record<string, string> = {
  guides: '#3b82f6', amends: '#f97316', replaces: '#8b5cf6', revokes: '#ef4444', cites: '#6b7280',
};

interface BookmarkDropdownProps {
  docId: string;
  onClose: () => void;
}
const BookmarkDropdown: React.FC<BookmarkDropdownProps> = ({ docId, onClose }) => {
  const [collections, setCollections] = useState<Collection[]>([]);
  const [loading, setLoading] = useState(true);
  const [savingId, setSavingId] = useState<string | null>(null);
  const [savedIds, setSavedIds] = useState<Set<string>>(new Set());

  useEffect(() => {
    api.get<Collection[]>('/workspace/collections')
      .then(r => setCollections(r.data))
      .finally(() => setLoading(false));
  }, []);

  const handleAdd = async (colId: string) => {
    setSavingId(colId);
    try {
      await api.post(`/workspace/collections/${colId}/docs`, { doc_id: docId });
      setSavedIds(prev => new Set(prev).add(colId));
    } finally { setSavingId(null); }
  };

  return (
    <div style={{
      position: 'absolute', top: '110%', right: 0, zIndex: 50,
      background: 'var(--bg-surface)', border: '1px solid var(--border-medium)',
      borderRadius: 12, minWidth: 240, boxShadow: 'var(--shadow-lg)',
      overflow: 'hidden',
    }}>
      <div style={{ padding: '12px 16px', borderBottom: '1px solid var(--border-light)' }}>
        <p style={{ fontSize: '0.82rem', fontWeight: 700, color: 'var(--text-primary)' }}>Lưu vào Collection</p>
      </div>
      <div style={{ maxHeight: 240, overflowY: 'auto', padding: '6px' }}>
        {loading ? (
          <div style={{ display: 'flex', justifyContent: 'center', padding: 20 }}>
            <Loader2 size={18} color="var(--primary)" style={{ animation: 'spin 1s linear infinite' }} />
          </div>
        ) : collections.length === 0 ? (
          <div style={{ padding: '16px', textAlign: 'center', fontSize: '0.82rem', color: 'var(--text-muted)' }}>
            Chưa có collection nào.<br />
            <span style={{ color: 'var(--primary)', fontSize: '0.78rem' }}>Tạo trong trang Workspace</span>
          </div>
        ) : (
          collections.map(col => {
            const saved = savedIds.has(col.id);
            return (
              <button
                key={col.id}
                onClick={() => !saved && handleAdd(col.id)}
                disabled={savingId === col.id || saved}
                style={{
                  width: '100%', display: 'flex', alignItems: 'center', gap: 10,
                  padding: '9px 12px', borderRadius: 8,
                  background: saved ? 'rgba(16,185,129,0.07)' : 'transparent',
                  border: `1px solid ${saved ? 'rgba(16,185,129,0.2)' : 'transparent'}`,
                  cursor: saved ? 'default' : 'pointer',
                  color: saved ? 'var(--color-active)' : 'var(--text-secondary)',
                  fontSize: '0.85rem', textAlign: 'left', marginBottom: 2,
                  transition: 'all 0.12s',
                }}
                onMouseEnter={e => { if (!saved) (e.currentTarget as HTMLButtonElement).style.background = 'rgba(255,255,255,0.04)'; }}
                onMouseLeave={e => { if (!saved) (e.currentTarget as HTMLButtonElement).style.background = 'transparent'; }}
              >
                <BookMarked size={14} color={saved ? 'var(--color-active)' : 'var(--text-muted)'} />
                <span style={{ flex: 1, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{col.name}</span>
                {savingId === col.id
                  ? <Loader2 size={13} style={{ animation: 'spin 1s linear infinite' }} />
                  : saved ? <Check size={13} /> : null}
              </button>
            );
          })
        )}
      </div>
      <div style={{ padding: '8px 6px', borderTop: '1px solid var(--border-light)' }}>
        <button
          onClick={onClose}
          style={{ width: '100%', padding: '8px', borderRadius: 8, background: 'none', border: 'none', cursor: 'pointer', color: 'var(--text-muted)', fontSize: '0.8rem' }}
        >
          Đóng
        </button>
      </div>
    </div>
  );
};

interface NotesTabProps { docId: string; }
const NotesTab: React.FC<NotesTabProps> = ({ docId }) => {
  const [notes, setNotes] = useState<Note[]>([]);
  const [loading, setLoading] = useState(true);
  const [newContent, setNewContent] = useState('');
  const [saving, setSaving] = useState(false);
  const [deletingId, setDeletingId] = useState<string | null>(null);

  const fetchNotes = useCallback(() => {
    setLoading(true);
    api.get<Note[]>(`/workspace/notes/${docId}`)
      .then(r => setNotes(r.data))
      .finally(() => setLoading(false));
  }, [docId]);

  useEffect(() => { fetchNotes(); }, [fetchNotes]);

  const handleAdd = async () => {
    if (!newContent.trim()) return;
    setSaving(true);
    try {
      await api.post<Note>('/workspace/notes', { doc_id: docId, content: newContent.trim() });
      setNewContent('');
      fetchNotes();
    } finally { setSaving(false); }
  };

  const handleDelete = async (noteId: string) => {
    setDeletingId(noteId);
    try {
      await api.delete(`/workspace/notes/${noteId}`);
      setNotes(prev => prev.filter(n => n.id !== noteId));
    } finally { setDeletingId(null); }
  };

  return (
    <div style={{ maxWidth: 700 }}>
      <h2 style={{ fontSize: '1rem', fontWeight: 700, marginBottom: 20, display: 'flex', alignItems: 'center', gap: 8 }}>
        <StickyNote size={17} color="var(--secondary)" /> Ghi chú cá nhân
      </h2>

      <div className="glass-card" style={{ padding: '18px 20px', marginBottom: 20 }}>
        <textarea
          id="note-textarea"
          className="input-field"
          value={newContent}
          onChange={e => setNewContent(e.target.value)}
          placeholder="Ghi chú của bạn về văn bản này..."
          rows={3}
          style={{ width: '100%', resize: 'none', padding: '10px 14px', marginBottom: 10, fontSize: '0.88rem' }}
        />
        <div style={{ display: 'flex', justifyContent: 'flex-end' }}>
          <button
            id="note-save-btn"
            onClick={handleAdd}
            disabled={!newContent.trim() || saving}
            className="btn btn-primary"
            style={{ padding: '8px 18px', fontSize: '0.85rem', display: 'flex', alignItems: 'center', gap: 7 }}
          >
            {saving ? <Loader2 size={14} style={{ animation: 'spin 1s linear infinite' }} /> : <Plus size={14} />}
            Thêm ghi chú
          </button>
        </div>
      </div>

      {loading ? (
        <div style={{ display: 'flex', justifyContent: 'center', padding: 40 }}>
          <Loader2 size={24} color="var(--primary)" style={{ animation: 'spin 1s linear infinite' }} />
        </div>
      ) : notes.length === 0 ? (
        <div style={{ textAlign: 'center', padding: '40px 16px', color: 'var(--text-muted)' }}>
          <StickyNote size={40} style={{ margin: '0 auto 12px', opacity: 0.2 }} />
          <p style={{ fontSize: '0.85rem' }}>Chưa có ghi chú nào. Thêm ghi chú đầu tiên ở trên.</p>
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
          {notes.map(note => (
            <div
              key={note.id}
              className="glass-card"
              style={{ padding: '14px 18px', display: 'flex', gap: 14, alignItems: 'flex-start' }}
            >
              <div style={{
                width: 32, height: 32, borderRadius: 8, flexShrink: 0,
                background: 'rgba(20,184,166,0.1)', border: '1px solid rgba(20,184,166,0.2)',
                display: 'flex', alignItems: 'center', justifyContent: 'center',
              }}>
                <StickyNote size={15} color="var(--secondary)" />
              </div>
              <p style={{ flex: 1, fontSize: '0.88rem', color: 'var(--text-secondary)', lineHeight: 1.65, whiteSpace: 'pre-wrap', wordBreak: 'break-word' }}>
                {note.content}
              </p>
              <button
                onClick={() => handleDelete(note.id)}
                disabled={deletingId === note.id}
                style={{
                  background: 'none', border: 'none', cursor: 'pointer',
                  color: 'var(--text-muted)', padding: 4, borderRadius: 6, flexShrink: 0,
                  transition: 'color 0.12s',
                }}
                onMouseEnter={e => (e.currentTarget as HTMLButtonElement).style.color = 'var(--color-expired)'}
                onMouseLeave={e => (e.currentTarget as HTMLButtonElement).style.color = 'var(--text-muted)'}
                title="Xóa ghi chú"
              >
                {deletingId === note.id
                  ? <Loader2 size={14} style={{ animation: 'spin 1s linear infinite' }} />
                  : <Trash2 size={14} />}
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export const DocumentPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [doc, setDoc] = useState<DocumentDetail | null>(null);
  const [graph, setGraph] = useState<GraphData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<'overview' | 'graph' | 'chat' | 'notes'>('overview');
  const [error, setError] = useState<string | null>(null);
  const [showBookmark, setShowBookmark] = useState(false);

  useEffect(() => {
    if (!id) return;
    setIsLoading(true);
    setError(null);

    Promise.all([
      api.get<DocumentDetail>(`/documents/${id}`),
      api.get<GraphData>(`/graph/${id}?depth=2`).catch(() => null),
    ])
      .then(([docRes, graphRes]) => {
        setDoc(docRes.data);
        if (graphRes) setGraph(graphRes.data);
      })
      .catch(() => setError('Không thể tải văn bản. Vui lòng thử lại.'))
      .finally(() => setIsLoading(false));
  }, [id]);

  const formatDate = (d: string | null) => d ? new Date(d).toLocaleDateString('vi-VN', { day: '2-digit', month: '2-digit', year: 'numeric' }) : '—';

  if (isLoading) {
    return (
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100vh', flexDirection: 'column', gap: '16px' }}>
        <Loader2 size={32} color="var(--primary)" style={{ animation: 'spin 1s linear infinite' }} />
        <p style={{ color: 'var(--text-muted)' }}>Đang tải văn bản...</p>
      </div>
    );
  }

  if (error || !doc) {
    return (
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100vh', flexDirection: 'column', gap: '16px' }}>
        <AlertTriangle size={36} color="var(--color-expired)" />
        <p style={{ color: 'var(--text-secondary)' }}>{error || 'Không tìm thấy văn bản.'}</p>
        <button className="btn btn-outline" onClick={() => navigate(-1)}><ArrowLeft size={16} /> Quay lại</button>
      </div>
    );
  }

  const TABS = [
    { key: 'overview', label: 'Tổng quan', icon: <FileText size={15} /> },
    { key: 'graph', label: 'Sơ đồ quan hệ', icon: <GitBranch size={15} /> },
    { key: 'notes', label: 'Ghi chú', icon: <StickyNote size={15} /> },
    { key: 'chat', label: 'Hỏi AI', icon: <Layers size={15} /> },
  ] as const;

  return (
    <div style={{ height: '100vh', display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
      <div style={{
        padding: '20px 32px', borderBottom: '1px solid var(--border-light)',
        background: 'var(--bg-surface)',
        flexShrink: 0,
      }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '14px' }}>
          <button
            onClick={() => navigate(-1)}
            className="btn btn-ghost"
            style={{ padding: '6px 10px', fontSize: '0.85rem' }}
          >
            <ArrowLeft size={16} /> Quay lại kết quả tìm kiếm
          </button>

          <div style={{ position: 'relative' }}>
            <button
              id="bookmark-btn"
              onClick={() => setShowBookmark(v => !v)}
              className={`btn ${showBookmark ? 'btn-primary' : 'btn-outline'}`}
              style={{ padding: '8px 16px', fontSize: '0.85rem', display: 'flex', alignItems: 'center', gap: 8 }}
            >
              <BookmarkPlus size={16} />
              Lưu vào Collection
            </button>
            {showBookmark && id && (
              <BookmarkDropdown docId={id} onClose={() => setShowBookmark(false)} />
            )}
          </div>
        </div>

        <div style={{ display: 'flex', alignItems: 'flex-start', gap: '16px' }}>
          <div style={{
            flexShrink: 0, width: '48px', height: '48px', borderRadius: '12px',
            background: 'var(--primary-glow)', border: '1px solid rgba(99,102,241,0.25)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
          }}>
            <FileText size={22} color="var(--primary)" />
          </div>
          <div style={{ flex: 1, minWidth: 0 }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px', flexWrap: 'wrap', marginBottom: '8px' }}>
              <span style={{ fontSize: '0.75rem', fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.07em' }}>{doc.doc_type}</span>
              <span style={{ fontSize: '0.82rem', color: 'var(--text-muted)' }}>{doc.doc_number}</span>
              <StatusBadge status={doc.status} />
            </div>
            <h1 style={{ fontSize: '1.2rem', fontWeight: 700, lineHeight: 1.4, marginBottom: '10px' }}>{doc.title}</h1>
            <div style={{ display: 'flex', gap: '24px', flexWrap: 'wrap' }}>
              {[
                { icon: <Building2 size={14} />, label: doc.issuing_body },
                { icon: <Calendar size={14} />, label: `Ban hành: ${formatDate(doc.issue_date)}` },
                { icon: <Calendar size={14} />, label: `Hiệu lực: ${formatDate(doc.effective_date)}` },
              ].map(({ icon, label }) => (
                <span key={label} style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.82rem', color: 'var(--text-muted)' }}>
                  {icon} {label}
                </span>
              ))}
            </div>
          </div>
        </div>

        <div style={{ display: 'flex', gap: '4px', marginTop: '20px' }}>
          {TABS.map(({ key, label, icon }) => (
            <button
              key={key}
              id={`tab-${key}`}
              onClick={() => setActiveTab(key)}
              style={{
                display: 'flex', alignItems: 'center', gap: '8px',
                padding: '8px 18px', fontSize: '0.85rem',
                borderRadius: 'var(--radius-sm)',
                border: 'none', cursor: 'pointer',
                fontWeight: activeTab === key ? 600 : 400,
                background: activeTab === key ? 'var(--primary-glow)' : 'transparent',
                color: activeTab === key ? 'var(--primary)' : 'var(--text-secondary)',
                transition: 'all 0.15s ease',
              }}
            >
              {icon} {label}
            </button>
          ))}
        </div>
      </div>

      <div style={{ flex: 1, overflowY: 'auto', padding: '28px 32px' }}>
        {activeTab === 'overview' && (
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 320px', gap: '24px', maxWidth: '1200px' }}>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
              {doc.content_summary && (
                <div className="glass-card" style={{ padding: '24px' }}>
                  <h2 style={{ fontSize: '1rem', fontWeight: 700, marginBottom: '14px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <FileText size={16} color="var(--primary)" /> Tóm tắt nội dung
                  </h2>
                  <p style={{ fontSize: '0.9rem', color: 'var(--text-secondary)', lineHeight: 1.75 }}>
                    {doc.content_summary}
                  </p>
                </div>
              )}

              {doc.relations && doc.relations.length > 0 && (
                <div className="glass-card" style={{ padding: '24px' }}>
                  <h2 style={{ fontSize: '1rem', fontWeight: 700, marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <GitBranch size={16} color="var(--primary)" /> Quan hệ văn bản ({doc.relations.length})
                  </h2>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                    {doc.relations.map(rel => (
                      <div
                        key={rel.id}
                        onClick={() => navigate(`/documents/${rel.related_doc_id}`)}
                        style={{
                          display: 'flex', alignItems: 'center', gap: '12px',
                          padding: '12px 16px', borderRadius: 'var(--radius-sm)',
                          border: '1px solid var(--border-light)', cursor: 'pointer',
                          transition: 'all 0.15s ease',
                          background: 'rgba(255,255,255,0.01)',
                        }}
                        onMouseEnter={e => (e.currentTarget as HTMLElement).style.borderColor = 'var(--border-medium)'}
                        onMouseLeave={e => (e.currentTarget as HTMLElement).style.borderColor = 'var(--border-light)'}
                      >
                        <span style={{
                          fontSize: '0.72rem', fontWeight: 700, padding: '3px 10px', borderRadius: '999px', flexShrink: 0,
                          background: `${RELATION_COLORS[rel.relation_type.toLowerCase()] || '#6b7280'}18`,
                          color: RELATION_COLORS[rel.relation_type.toLowerCase()] || '#6b7280',
                          border: `1px solid ${RELATION_COLORS[rel.relation_type.toLowerCase()] || '#6b7280'}33`,
                        }}>
                          {RELATION_LABELS[rel.relation_type.toLowerCase()] || rel.relation_type}
                        </span>
                        <div style={{ flex: 1, minWidth: 0 }}>
                          <p style={{ fontSize: '0.82rem', fontWeight: 500, color: 'var(--text-secondary)' }}>{rel.related_doc_number}</p>
                          <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{rel.related_doc_title}</p>
                        </div>
                        <ExternalLink size={14} color="var(--text-muted)" />
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {doc.content_full && (
                <div className="glass-card" style={{ padding: '24px' }}>
                  <h2 style={{ fontSize: '1rem', fontWeight: 700, marginBottom: '14px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <FileText size={16} color="var(--primary)" /> Nội dung văn bản
                  </h2>
                  <div 
                    className="document-html-content"
                    style={{
                      fontSize: '0.9rem', color: 'var(--text-secondary)', lineHeight: 1.75,
                      maxHeight: '600px', overflowY: 'auto',
                      paddingRight: '12px',
                      whiteSpace: 'pre-wrap'
                    }}
                    dangerouslySetInnerHTML={{ __html: doc.content_full }}
                  />
                </div>
              )}
            </div>

            <div className="glass-card" style={{ padding: '24px', alignSelf: 'start' }}>
              <h2 style={{ fontSize: '0.9rem', fontWeight: 700, marginBottom: '18px', textTransform: 'uppercase', letterSpacing: '0.05em', color: 'var(--text-muted)' }}>
                Thông tin văn bản
              </h2>
              {(
                [
                  ['Số hiệu', doc.doc_number],
                  ['Loại văn bản', doc.doc_type],
                  ['Cơ quan ban hành', doc.issuing_body],
                  ['Ngày ban hành', formatDate(doc.issue_date)],
                  ['Ngày có hiệu lực', formatDate(doc.effective_date)],
                  ['Ngày hết hiệu lực', formatDate(doc.expiry_date)],
                  doc.chunks_count !== undefined ? ['Số đoạn văn bản', `${doc.chunks_count} đoạn`] : null,
                ] as ([string, string | number | null] | null)[]
              ).filter((item): item is [string, string | number | null] => item !== null).map(([k, v]) => (
                <div key={k} style={{ display: 'flex', justifyContent: 'space-between', padding: '10px 0', borderBottom: '1px solid var(--border-light)', gap: '12px' }}>
                  <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)', flexShrink: 0 }}>{k}</span>
                  <span style={{ fontSize: '0.82rem', color: 'var(--text-primary)', textAlign: 'right', wordBreak: 'break-word' }}>{v || '—'}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {activeTab === 'graph' && (
          <div style={{ maxWidth: '900px' }}>
            <h2 style={{ fontSize: '1rem', fontWeight: 700, marginBottom: '16px' }}>Sơ đồ quan hệ văn bản</h2>
            {graph ? (
              <KnowledgeGraph 
                data={graph} 
                onNodeClick={(nodeId) => navigate(`/documents/${nodeId}`)}
              />
            ) : (
              <div className="glass-card" style={{ padding: '48px', textAlign: 'center', color: 'var(--text-muted)' }}>
                <GitBranch size={36} style={{ margin: '0 auto 12px', opacity: 0.3 }} />
                <p>Văn bản này chưa có dữ liệu quan hệ.</p>
              </div>
            )}
          </div>
        )}

        {activeTab === 'notes' && id && <NotesTab docId={id} />}

        {activeTab === 'chat' && (
          <div style={{ maxWidth: '700px' }}>
            <h2 style={{ fontSize: '1rem', fontWeight: 700, marginBottom: '16px' }}>Hỏi AI về văn bản này</h2>
            <AIChatPanel contextDocId={id} />
          </div>
        )}
      </div>

      {showBookmark && (
        <div
          style={{ position: 'fixed', inset: 0, zIndex: 40 }}
          onClick={() => setShowBookmark(false)}
        />
      )}
    </div>
  );
};
