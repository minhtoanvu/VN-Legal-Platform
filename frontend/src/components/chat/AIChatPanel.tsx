import React, { useState, useRef, useEffect, useCallback } from 'react';
import type { ChatMessage } from '../../types';
import { MessageSquare, Send, Bot, User, X, Minimize2, Maximize2 } from 'lucide-react';
import { api } from '../../services/api';

interface AIChatPanelProps {
  contextDocId?: string;
}

let messageCounter = 0;
const newId = () => `msg-${++messageCounter}-${Date.now()}`;

export const AIChatPanel: React.FC<AIChatPanelProps> = ({ contextDocId }) => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState('');
  const [isStreaming, setIsStreaming] = useState(false);
  const [isCollapsed, setIsCollapsed] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);
  const abortRef = useRef<AbortController | null>(null);
  const sessionId = useRef(`session-${Date.now()}`);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const sendMessage = useCallback(async () => {
    const query = input.trim();
    if (!query || isStreaming) return;

    setInput('');

    const userMsg: ChatMessage = {
      id: newId(), role: 'user', content: query, timestamp: new Date(),
    };

    const assistantId = newId();
    const assistantMsg: ChatMessage = {
      id: assistantId, role: 'assistant', content: '', timestamp: new Date(), isStreaming: true,
    };

    setMessages(prev => [...prev, userMsg, assistantMsg]);
    setIsStreaming(true);

    abortRef.current = new AbortController();

    try {
      const response = await fetch(`${api.defaults.baseURL}/ai/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${localStorage.getItem('access_token')}`,
        },
        body: JSON.stringify({
          query,
          session_id: sessionId.current,
          context_doc_ids: contextDocId ? [contextDocId] : [],
          history: messages.map(m => ({ role: m.role, content: m.content })).slice(-6),
        }),
        signal: abortRef.current.signal,
      });

      if (!response.ok) throw new Error(`HTTP ${response.status}`);

      const reader = response.body?.getReader();
      const decoder = new TextDecoder();
      let accumulated = '';

      while (reader) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value, { stream: true });
        const lines = chunk.split('\n');

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = line.slice(6).trim();
            if (data === '[DONE]') continue;
            try {
              const parsed = JSON.parse(data);

              if (parsed.text) {
                const citationsMarker = '__CITATIONS__:';
                if (parsed.text.includes(citationsMarker)) {
                  const parts = parsed.text.split(citationsMarker);
                  accumulated += parts[0];
                  try {
                    const citations = JSON.parse(parts[1]);
                    const sources = citations.map((c: any) => ({
                      id: c.doc_id,
                      doc_number: c.doc_number,
                      title: c.title,
                    }));
                    setMessages(prev =>
                      prev.map(m =>
                        m.id === assistantId ? { ...m, content: accumulated, sources } : m
                      )
                    );
                  } catch {
                  }
                } else {
                  accumulated += parsed.text;
                  setMessages(prev =>
                    prev.map(m =>
                      m.id === assistantId ? { ...m, content: accumulated } : m
                    )
                  );
                }
              }

              if (parsed.content) {
                accumulated += parsed.content;
                setMessages(prev =>
                  prev.map(m =>
                    m.id === assistantId ? { ...m, content: accumulated } : m
                  )
                );
              }

              if (parsed.error) {
                accumulated += `\n⚠️ Lỗi: ${parsed.error}`;
                setMessages(prev =>
                  prev.map(m =>
                    m.id === assistantId ? { ...m, content: accumulated } : m
                  )
                );
              }

              if (parsed.sources) {
                setMessages(prev =>
                  prev.map(m =>
                    m.id === assistantId ? { ...m, sources: parsed.sources } : m
                  )
                );
              }
            } catch {
            }
          }
        }
      }
    } catch (err: any) {
      if (err.name !== 'AbortError') {
        setMessages(prev =>
          prev.map(m =>
            m.id === assistantId
              ? { ...m, content: '⚠️ Không thể kết nối đến AI. Vui lòng kiểm tra cấu hình Gemini API Key.', isStreaming: false }
              : m
          )
        );
      }
    } finally {
      setMessages(prev =>
        prev.map(m => (m.id === assistantId ? { ...m, isStreaming: false } : m))
      );
      setIsStreaming(false);
    }
  }, [input, isStreaming, contextDocId]);

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const stopStreaming = () => {
    abortRef.current?.abort();
  };

  return (
    <div
      className="glass-card"
      style={{
        display: 'flex', flexDirection: 'column',
        height: isCollapsed ? 'auto' : '520px',
        border: '1px solid var(--border-medium)',
        overflow: 'hidden',
      }}
    >
      <div style={{
        display: 'flex', alignItems: 'center', justifyContent: 'space-between',
        padding: '14px 18px',
        borderBottom: isCollapsed ? 'none' : '1px solid var(--border-light)',
        background: 'linear-gradient(90deg, rgba(99,102,241,0.08), rgba(20,184,166,0.05))',
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <div style={{
            width: '8px', height: '8px', borderRadius: '50%',
            background: isStreaming ? 'var(--color-active)' : 'var(--primary)',
            boxShadow: isStreaming ? '0 0 6px var(--color-active)' : 'none',
            animation: isStreaming ? 'pulse-glow 1.5s infinite' : 'none',
          }} />
          <MessageSquare size={16} color="var(--primary)" />
          <span style={{ fontSize: '0.9rem', fontWeight: 600, color: 'var(--text-primary)' }}>AI Legal Assistant</span>
          <span style={{
            fontSize: '0.65rem', textTransform: 'uppercase', letterSpacing: '0.07em',
            color: 'var(--secondary)', background: 'var(--secondary-glow)',
            padding: '2px 7px', borderRadius: '999px', fontWeight: 700,
          }}>RAG</span>
        </div>
        <button
          onClick={() => setIsCollapsed(!isCollapsed)}
          style={{ background: 'none', border: 'none', cursor: 'pointer', color: 'var(--text-muted)', padding: '4px' }}
        >
          {isCollapsed ? <Maximize2 size={16} /> : <Minimize2 size={16} />}
        </button>
      </div>

      {!isCollapsed && (
        <>
          <div style={{ flex: 1, overflowY: 'auto', padding: '16px', display: 'flex', flexDirection: 'column', gap: '16px' }}>
            {messages.length === 0 && (
              <div style={{ textAlign: 'center', padding: '32px 16px', color: 'var(--text-muted)' }}>
                <Bot size={36} style={{ margin: '0 auto 12px', opacity: 0.4 }} />
                <p style={{ fontSize: '0.88rem' }}>Đặt câu hỏi về pháp luật, AI sẽ trả lời dựa trên văn bản thực tế.</p>
              </div>
            )}
            {messages.map(msg => (
              <div key={msg.id} style={{ display: 'flex', gap: '10px', alignItems: 'flex-start', flexDirection: msg.role === 'user' ? 'row-reverse' : 'row' }}>
                <div style={{
                  flexShrink: 0, width: '32px', height: '32px', borderRadius: '50%',
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                  background: msg.role === 'user' ? 'var(--primary)' : 'var(--secondary-glow)',
                  border: `1px solid ${msg.role === 'user' ? 'var(--primary-hover)' : 'var(--secondary)'}`,
                }}>
                  {msg.role === 'user' ? <User size={15} color="#fff" /> : <Bot size={15} color="var(--secondary)" />}
                </div>

                <div style={{
                  maxWidth: '82%',
                  background: msg.role === 'user' ? 'var(--primary)' : 'rgba(15,22,38,0.8)',
                  border: `1px solid ${msg.role === 'user' ? 'transparent' : 'var(--border-light)'}`,
                  borderRadius: msg.role === 'user' ? '16px 4px 16px 16px' : '4px 16px 16px 16px',
                  padding: '10px 14px',
                }}>
                  <p style={{
                    fontSize: '0.88rem', lineHeight: 1.65,
                    color: msg.role === 'user' ? '#fff' : 'var(--text-primary)',
                    whiteSpace: 'pre-wrap', wordBreak: 'break-word',
                  }}>
                    {msg.content}
                    {msg.isStreaming && (
                      <span style={{ display: 'inline-block', width: '2px', height: '14px', background: 'var(--secondary)', marginLeft: '3px', animation: 'pulse-glow 0.8s infinite', verticalAlign: 'text-bottom' }} />
                    )}
                  </p>
                  {msg.sources && msg.sources.length > 0 && (
                    <div style={{ marginTop: '10px', paddingTop: '10px', borderTop: '1px solid var(--border-light)' }}>
                      <p style={{ fontSize: '0.72rem', color: 'var(--text-muted)', marginBottom: '6px', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                        Nguồn tham khảo:
                      </p>
                      {msg.sources.slice(0, 3).map(src => (
                        <div key={src.id} style={{ fontSize: '0.78rem', color: 'var(--accent-cyan)', marginBottom: '2px' }}>
                          • {src.doc_number} — {src.title.slice(0, 60)}...
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            ))}
            <div ref={bottomRef} />
          </div>

          <div style={{ padding: '12px 14px', borderTop: '1px solid var(--border-light)', display: 'flex', gap: '8px', alignItems: 'flex-end' }}>
            <textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Đặt câu hỏi về pháp luật... (Enter để gửi)"
              disabled={isStreaming}
              rows={1}
              style={{
                flex: 1, resize: 'none', padding: '10px 14px',
                background: 'rgba(15,22,38,0.6)', border: '1px solid var(--border-light)',
                borderRadius: '10px', color: 'var(--text-primary)',
                fontFamily: 'var(--font-body)', fontSize: '0.88rem', lineHeight: 1.5,
                outline: 'none', transition: 'border 0.15s',
                maxHeight: '100px', overflowY: 'auto',
              }}
              onFocus={(e) => (e.target.style.borderColor = 'var(--primary)')}
              onBlur={(e) => (e.target.style.borderColor = 'var(--border-light)')}
            />
            {isStreaming ? (
              <button
                onClick={stopStreaming}
                className="btn btn-outline"
                style={{ padding: '10px 14px', borderRadius: '10px', height: '42px' }}
              >
                <X size={16} />
              </button>
            ) : (
              <button
                onClick={sendMessage}
                className="btn btn-primary"
                disabled={!input.trim()}
                style={{ padding: '10px 14px', borderRadius: '10px', height: '42px' }}
              >
                <Send size={16} />
              </button>
            )}
          </div>
        </>
      )}
    </div>
  );
};
