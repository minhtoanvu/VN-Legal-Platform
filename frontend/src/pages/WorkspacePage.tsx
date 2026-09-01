import React, { useState, useEffect, useCallback } from 'react';
import type { Collection, DocInCollection } from '../types';
import { api } from '../services/api';
import {
  FolderOpen, Plus, Trash2, FileText, ExternalLink,
  BookMarked, Loader2, FolderX, X, Check,
  StickyNote,
} from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { StatusBadge } from '../components/document/StatusBadge';

/* ── tiny modal ──────────────────────────────────────────────────────── */
interface CreateModalProps {
  onClose: () => void;
  onCreate: (name: string, desc: string) => Promise<void>;
}
const CreateModal: React.FC<CreateModalProps> = ({ onClose, onCreate }) => {
  const [name, setName] = useState('');
  const [desc, setDesc] = useState('');
  const [saving, setSaving] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim()) return;
    setSaving(true);
    try { await onCreate(name.trim(), desc.trim()); onClose(); }
    finally { setSaving(false); }
  };

  return (
    <div style={{
      position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.6)',
      display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 100,
      backdropFilter: 'blur(4px)',
    }}>
      <div className="glass-card" style={{ width: 420, padding: '28px 32px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 20 }}>
          <h3 style={{ fontSize: '1rem', fontWeight: 700, color: 'var(--text-primary)' }}>
            Tạo Collection mới
          </h3>
          <button onClick={onClose} style={{ background: 'none', border: 'none', cursor: 'pointer', color: 'var(--text-muted)' }}>
            <X size={18} />
          </button>
        </div>
        <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
          <div>
            <label style={{ fontSize: '0.78rem', color: 'var(--text-muted)', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.05em', display: 'block', marginBottom: 6 }}>
              Tên collection *
            </label>
            <input
              id="collection-name-input"
              className="input-field"
              value={name}
              onChange={e => setName(e.target.value)}
              placeholder="VD: Luật Lao động 2024"
              autoFocus
              style={{ width: '100%', padding: '10px 14px', fontSize: '0.9rem' }}
            />
          </div>
          <div>
            <label style={{ fontSize: '0.78rem', color: 'var(--text-muted)', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.05em', display: 'block', marginBottom: 6 }}>
              Mô tả (tuỳ chọn)
            </label>
            <textarea
              className="input-field"
              value={desc}
              onChange={e => setDesc(e.target.value)}
              placeholder="Ghi chú thêm về collection này..."
              rows={3}
              style={{ width: '100%', padding: '10px 14px', fontSize: '0.88rem', resize: 'none' }}
            />
          </div>
          <div style={{ display: 'flex', gap: 10, justifyContent: 'flex-end', marginTop: 6 }}>
            <button type="button" onClick={onClose} className="btn btn-outline" style={{ padding: '9px 18px' }}>Huỷ</button>
            <button
              id="collection-create-btn"
              type="submit"
              className="btn btn-primary"
              disabled={!name.trim() || saving}
              style={{ padding: '9px 18px', display: 'flex', alignItems: 'center', gap: 8 }}
            >
              {saving ? <Loader2 size={15} style={{ animation: 'spin 1s linear infinite' }} /> : <Check size={15} />}
              Tạo
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

/* ── main page ───────────────────────────────────────────────────────── */
export const WorkspacePage: React.FC = () => {
  const navigate = useNavigate();
  const [collections, setCollections] = useState<Collection[]>([]);
  const [selectedCol, setSelectedCol] = useState<Collection | null>(null);
  const [docs, setDocs] = useState<DocInCollection[]>([]);
  const [loadingCols, setLoadingCols] = useState(true);
  const [loadingDocs, setLoadingDocs] = useState(false);
  const [showCreate, setShowCreate] = useState(false);
  const [deletingColId, setDeletingColId] = useState<string | null>(null);
  const [removingDocId, setRemovingDocId] = useState<string | null>(null);

  /* fetch collections */
  const fetchCollections = useCallback(async () => {
    setLoadingCols(true);
    try {
      const res = await api.get<Collection[]>('/workspace/collections');
      setCollections(res.data);
    } catch { /* ignore */ }
    finally { setLoadingCols(false); }
  }, []);

  useEffect(() => { fetchCollections(); }, [fetchCollections]);

  /* fetch docs when collection selected */
  useEffect(() => {
    if (!selectedCol) { setDocs([]); return; }
    setLoadingDocs(true);
    api.get<DocInCollection[]>(`/workspace/collections/${selectedCol.id}/docs`)
      .then(r => setDocs(r.data))
      .catch(() => setDocs([]))
      .finally(() => setLoadingDocs(false));
  }, [selectedCol]);

  /* create collection */
  const handleCreate = async (name: string, desc: string) => {
    await api.post('/workspace/collections', { name, description: desc || null });
    await fetchCollections();
  };

  /* delete collection */
  const handleDeleteCol = async (colId: string) => {
    if (!window.confirm('Xóa collection này? Các văn bản trong collection sẽ không bị xóa.')) return;
    setDeletingColId(colId);
    try {
      await api.delete(`/workspace/collections/${colId}`);
      if (selectedCol?.id === colId) setSelectedCol(null);
      await fetchCollections();
    } finally { setDeletingColId(null); }
  };

  /* remove doc from collection */
  const handleRemoveDoc = async (docId: string) => {
    if (!selectedCol) return;
    setRemovingDocId(docId);
    try {
      await api.delete(`/workspace/collections/${selectedCol.id}/docs/${docId}`);
      setDocs(prev => prev.filter(d => d.id !== docId));
      // Update count
      setCollections(prev => prev.map(c =>
        c.id === selectedCol.id ? { ...c, doc_count: Math.max(0, c.doc_count - 1) } : c
      ));
    } finally { setRemovingDocId(null); }
  };

  return (
    <div style={{ display: 'flex', height: '100vh', overflow: 'hidden' }}>
      {showCreate && <CreateModal onClose={() => setShowCreate(false)} onCreate={handleCreate} />}

      {/* ── LEFT: Collections panel ──────────────────────────────── */}
      <div style={{
        width: 300, flexShrink: 0,
        borderRight: '1px solid var(--border-light)',
        background: 'var(--bg-surface)',
        display: 'flex', flexDirection: 'column',
        overflow: 'hidden',
      }}>
        {/* Header */}
        <div style={{ padding: '24px 20px 16px', borderBottom: '1px solid var(--border-light)' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 4 }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
              <div style={{
                width: 34, height: 34, borderRadius: 10,
                background: 'linear-gradient(135deg, var(--primary), var(--accent-purple))',
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                boxShadow: '0 0 12px rgba(99,102,241,0.35)',
              }}>
                <BookMarked size={17} color="#fff" />
              </div>
              <div>
                <h2 style={{ fontSize: '0.95rem', fontWeight: 700, color: 'var(--text-primary)' }}>Collections</h2>
                <p style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>{collections.length} nhóm</p>
              </div>
            </div>
            <button
              id="create-collection-btn"
              onClick={() => setShowCreate(true)}
              className="btn btn-primary"
              style={{ padding: '7px 10px', borderRadius: 8, display: 'flex', alignItems: 'center', gap: 5, fontSize: '0.82rem' }}
              title="Tạo collection mới"
            >
              <Plus size={15} /> Mới
            </button>
          </div>
        </div>

        {/* List */}
        <div style={{ flex: 1, overflowY: 'auto', padding: '10px 10px' }}>
          {loadingCols ? (
            <div style={{ display: 'flex', justifyContent: 'center', padding: 40 }}>
              <Loader2 size={24} color="var(--primary)" style={{ animation: 'spin 1s linear infinite' }} />
            </div>
          ) : collections.length === 0 ? (
            <div style={{ textAlign: 'center', padding: '40px 16px', color: 'var(--text-muted)' }}>
              <FolderX size={40} style={{ margin: '0 auto 12px', opacity: 0.3 }} />
              <p style={{ fontSize: '0.85rem' }}>Chưa có collection nào.</p>
              <p style={{ fontSize: '0.78rem', marginTop: 6 }}>Nhấn <strong>+ Mới</strong> để tạo.</p>
            </div>
          ) : (
            collections.map(col => {
              const isSelected = selectedCol?.id === col.id;
              return (
                <div
                  key={col.id}
                  id={`collection-${col.id}`}
                  onClick={() => setSelectedCol(col)}
                  style={{
                    padding: '11px 14px', borderRadius: 10, marginBottom: 4,
                    cursor: 'pointer', display: 'flex', alignItems: 'center', gap: 10,
                    background: isSelected ? 'var(--primary-glow)' : 'transparent',
                    border: `1px solid ${isSelected ? 'rgba(99,102,241,0.25)' : 'transparent'}`,
                    transition: 'all 0.15s ease',
                  }}
                  onMouseEnter={e => { if (!isSelected) (e.currentTarget as HTMLDivElement).style.background = 'rgba(255,255,255,0.03)'; }}
                  onMouseLeave={e => { if (!isSelected) (e.currentTarget as HTMLDivElement).style.background = 'transparent'; }}
                >
                  <FolderOpen size={17} color={isSelected ? 'var(--primary)' : 'var(--text-muted)'} style={{ flexShrink: 0 }} />
                  <div style={{ flex: 1, minWidth: 0 }}>
                    <p style={{
                      fontSize: '0.88rem', fontWeight: isSelected ? 600 : 400,
                      color: isSelected ? 'var(--primary)' : 'var(--text-primary)',
                      overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap',
                    }}>
                      {col.name}
                    </p>
                    {col.description && (
                      <p style={{ fontSize: '0.72rem', color: 'var(--text-muted)', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                        {col.description}
                      </p>
                    )}
                  </div>
                  {/* Doc count badge */}
                  <span style={{
                    fontSize: '0.7rem', fontWeight: 700, padding: '2px 7px',
                    borderRadius: 99, flexShrink: 0,
                    background: isSelected ? 'rgba(99,102,241,0.2)' : 'rgba(255,255,255,0.06)',
                    color: isSelected ? 'var(--primary)' : 'var(--text-muted)',
                  }}>
                    {col.doc_count}
                  </span>
                  {/* Delete btn */}
                  <button
                    onClick={e => { e.stopPropagation(); handleDeleteCol(col.id); }}
                    disabled={deletingColId === col.id}
                    style={{
                      background: 'none', border: 'none', cursor: 'pointer', padding: 4,
                      color: 'var(--text-muted)', borderRadius: 6, flexShrink: 0,
                      opacity: 0.5, transition: 'opacity 0.15s, color 0.15s',
                    }}
                    onMouseEnter={e => { (e.currentTarget as HTMLButtonElement).style.opacity = '1'; (e.currentTarget as HTMLButtonElement).style.color = 'var(--color-expired)'; }}
                    onMouseLeave={e => { (e.currentTarget as HTMLButtonElement).style.opacity = '0.5'; (e.currentTarget as HTMLButtonElement).style.color = 'var(--text-muted)'; }}
                    title="Xóa collection"
                  >
                    {deletingColId === col.id
                      ? <Loader2 size={14} style={{ animation: 'spin 1s linear infinite' }} />
                      : <Trash2 size={14} />}
                  </button>
                </div>
              );
            })
          )}
        </div>
      </div>

      {/* ── RIGHT: Documents in selected collection ──────────────── */}
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
        {!selectedCol ? (
          /* Empty state — no collection selected */
          <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: '100%', color: 'var(--text-muted)' }}>
            <div style={{
              width: 80, height: 80, borderRadius: 24,
              background: 'linear-gradient(135deg, rgba(99,102,241,0.1), rgba(168,85,247,0.1))',
              border: '1px solid rgba(99,102,241,0.15)',
              display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: 20,
            }}>
              <FolderOpen size={36} color="var(--primary)" style={{ opacity: 0.5 }} />
            </div>
            <h3 style={{ fontSize: '1.05rem', fontWeight: 600, color: 'var(--text-secondary)', marginBottom: 8 }}>
              Chọn một collection
            </h3>
            <p style={{ fontSize: '0.85rem', textAlign: 'center', maxWidth: 320, lineHeight: 1.6 }}>
              Chọn collection ở bên trái để xem danh sách văn bản đã lưu, hoặc tạo collection mới.
            </p>
          </div>
        ) : (
          <>
            {/* Header */}
            <div style={{
              padding: '20px 28px 16px',
              borderBottom: '1px solid var(--border-light)',
              background: 'linear-gradient(180deg, rgba(99,102,241,0.04) 0%, transparent 100%)',
            }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                <div style={{
                  width: 10, height: 10, borderRadius: '50%',
                  background: 'var(--primary)', boxShadow: '0 0 8px rgba(99,102,241,0.6)',
                }} />
                <h1 style={{ fontSize: '1.25rem', fontWeight: 800, letterSpacing: '-0.02em' }} className="text-gradient-primary">
                  {selectedCol.name}
                </h1>
                <span style={{
                  fontSize: '0.72rem', fontWeight: 700, padding: '3px 10px',
                  borderRadius: 99, background: 'var(--primary-glow)',
                  color: 'var(--primary)', border: '1px solid rgba(99,102,241,0.2)',
                }}>
                  {docs.length} văn bản
                </span>
              </div>
              {selectedCol.description && (
                <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginTop: 6, marginLeft: 22 }}>
                  {selectedCol.description}
                </p>
              )}
            </div>

            {/* Docs list */}
            <div style={{ flex: 1, overflowY: 'auto', padding: '20px 28px' }}>
              {loadingDocs ? (
                <div style={{ display: 'flex', justifyContent: 'center', paddingTop: 60 }}>
                  <Loader2 size={28} color="var(--primary)" style={{ animation: 'spin 1s linear infinite' }} />
                </div>
              ) : docs.length === 0 ? (
                <div style={{ textAlign: 'center', padding: '60px 20px', color: 'var(--text-muted)' }}>
                  <FileText size={48} style={{ margin: '0 auto 16px', opacity: 0.2 }} />
                  <p style={{ fontSize: '0.92rem', fontWeight: 500, color: 'var(--text-secondary)', marginBottom: 8 }}>
                    Collection trống
                  </p>
                  <p style={{ fontSize: '0.82rem', lineHeight: 1.7 }}>
                    Thêm văn bản vào collection này từ trang<br />
                    <strong>Tìm kiếm</strong> hoặc trang <strong>Chi tiết văn bản</strong>.
                  </p>
                </div>
              ) : (
                <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
                  {docs.map(doc => (
                    <div
                      key={doc.id}
                      id={`workspace-doc-${doc.id}`}
                      className="glass-card"
                      style={{
                        padding: '16px 20px',
                        display: 'flex', alignItems: 'center', gap: 16,
                        transition: 'border-color 0.15s, box-shadow 0.15s',
                        cursor: 'default',
                      }}
                      onMouseEnter={e => { (e.currentTarget as HTMLDivElement).style.borderColor = 'rgba(99,102,241,0.2)'; }}
                      onMouseLeave={e => { (e.currentTarget as HTMLDivElement).style.borderColor = 'var(--border-light)'; }}
                    >
                      {/* Doc icon */}
                      <div style={{
                        width: 40, height: 40, borderRadius: 10, flexShrink: 0,
                        background: 'rgba(99,102,241,0.1)',
                        border: '1px solid rgba(99,102,241,0.15)',
                        display: 'flex', alignItems: 'center', justifyContent: 'center',
                      }}>
                        <FileText size={18} color="var(--primary)" />
                      </div>

                      {/* Info */}
                      <div style={{ flex: 1, minWidth: 0 }}>
                        <p style={{ fontSize: '0.92rem', fontWeight: 600, color: 'var(--text-primary)', marginBottom: 4, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                          {doc.title}
                        </p>
                        <div style={{ display: 'flex', alignItems: 'center', gap: 10, flexWrap: 'wrap' }}>
                          <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontFamily: 'var(--font-mono)' }}>
                            {doc.doc_number}
                          </span>
                          {doc.doc_type && (
                            <span style={{ fontSize: '0.72rem', color: 'var(--text-muted)', padding: '2px 7px', background: 'rgba(255,255,255,0.04)', borderRadius: 4, border: '1px solid var(--border-light)' }}>
                              {doc.doc_type}
                            </span>
                          )}
                          {doc.status && <StatusBadge status={doc.status as any} />}
                        </div>
                      </div>

                      {/* Actions */}
                      <div style={{ display: 'flex', alignItems: 'center', gap: 8, flexShrink: 0 }}>
                        <button
                          onClick={() => navigate(`/documents/${doc.id}`)}
                          className="btn btn-outline"
                          style={{ padding: '7px 12px', fontSize: '0.8rem', display: 'flex', alignItems: 'center', gap: 6 }}
                          title="Xem chi tiết"
                        >
                          <ExternalLink size={14} /> Xem
                        </button>
                        <button
                          onClick={() => handleRemoveDoc(doc.id)}
                          disabled={removingDocId === doc.id}
                          style={{
                            background: 'none', border: '1px solid transparent', cursor: 'pointer',
                            padding: '7px 10px', borderRadius: 8, color: 'var(--text-muted)',
                            transition: 'all 0.15s', display: 'flex', alignItems: 'center',
                          }}
                          onMouseEnter={e => {
                            (e.currentTarget as HTMLButtonElement).style.color = 'var(--color-expired)';
                            (e.currentTarget as HTMLButtonElement).style.background = 'var(--color-expired-bg)';
                            (e.currentTarget as HTMLButtonElement).style.borderColor = 'rgba(239,68,68,0.2)';
                          }}
                          onMouseLeave={e => {
                            (e.currentTarget as HTMLButtonElement).style.color = 'var(--text-muted)';
                            (e.currentTarget as HTMLButtonElement).style.background = 'none';
                            (e.currentTarget as HTMLButtonElement).style.borderColor = 'transparent';
                          }}
                          title="Xóa khỏi collection"
                        >
                          {removingDocId === doc.id
                            ? <Loader2 size={15} style={{ animation: 'spin 1s linear infinite' }} />
                            : <Trash2 size={15} />}
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </>
        )}
      </div>

      {/* Floating tip */}
      <div style={{
        position: 'fixed', bottom: 20, right: 24,
        display: 'flex', alignItems: 'center', gap: 8,
        padding: '8px 14px', borderRadius: 99,
        background: 'rgba(15,22,38,0.9)', border: '1px solid var(--border-medium)',
        fontSize: '0.76rem', color: 'var(--text-muted)',
        backdropFilter: 'blur(8px)',
      }}>
        <StickyNote size={13} color="var(--secondary)" />
        Ghi chú: xem trong trang <strong style={{ color: 'var(--text-secondary)', marginLeft: 3 }}>Chi tiết văn bản</strong>
      </div>
    </div>
  );
};
