import React, { useState, useEffect } from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import { LoginForm } from '../components/auth/LoginForm';
import { RegisterForm } from '../components/auth/RegisterForm';
import { Scale } from 'lucide-react';

export const AuthPage: React.FC = () => {
  const { isAuthenticated, checkAuth } = useAuth();
  const [showRegister, setShowRegister] = useState(false);

  useEffect(() => {
    checkAuth();
  }, [checkAuth]);

  if (isAuthenticated) return <Navigate to="/search" replace />;

  return (
    <div
      style={{
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '24px',
        position: 'relative',
        overflow: 'hidden',
      }}
    >
      {/* Animated background blobs */}
      <div style={{
        position: 'absolute', inset: 0, zIndex: 0,
        background: 'var(--bg-base)',
      }}>
        <div style={{
          position: 'absolute', width: '600px', height: '600px',
          background: 'radial-gradient(circle, rgba(99,102,241,0.12) 0%, transparent 70%)',
          top: '-200px', left: '-100px',
          animation: 'float 8s ease-in-out infinite',
        }} />
        <div style={{
          position: 'absolute', width: '500px', height: '500px',
          background: 'radial-gradient(circle, rgba(20,184,166,0.08) 0%, transparent 70%)',
          bottom: '-150px', right: '-100px',
          animation: 'float 10s ease-in-out infinite reverse',
        }} />
        <div style={{
          position: 'absolute', width: '300px', height: '300px',
          background: 'radial-gradient(circle, rgba(168,85,247,0.07) 0%, transparent 70%)',
          top: '40%', left: '60%',
          animation: 'float 7s ease-in-out infinite 2s',
        }} />
      </div>

      {/* Main content */}
      <div style={{ position: 'relative', zIndex: 1, width: '100%', maxWidth: '900px', display: 'flex', gap: '48px', alignItems: 'center' }}>
        {/* Left — Branding */}
        <div style={{ flex: 1, display: 'none' }} className="auth-branding">
          <div style={{ display: 'flex', alignItems: 'center', gap: '14px', marginBottom: '32px' }}>
            <div style={{
              width: '52px', height: '52px', borderRadius: '16px',
              background: 'linear-gradient(135deg, var(--primary), var(--accent-purple))',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              boxShadow: '0 0 24px rgba(99,102,241,0.5)',
            }}>
              <Scale size={28} color="#fff" />
            </div>
            <div>
              <h1 style={{ fontSize: '1.8rem', fontWeight: 800, letterSpacing: '-0.03em' }} className="text-gradient-primary">
                LexAI
              </h1>
              <p style={{ fontSize: '0.78rem', color: 'var(--text-muted)', letterSpacing: '0.12em', textTransform: 'uppercase' }}>
                Legal Intelligence Platform
              </p>
            </div>
          </div>

          <h2 style={{ fontSize: '2.2rem', fontWeight: 700, lineHeight: 1.3, marginBottom: '20px' }}>
            Tra cứu pháp luật<br />
            <span className="text-gradient-rainbow">thông minh hơn</span>
          </h2>

          <p style={{ color: 'var(--text-secondary)', lineHeight: 1.8, marginBottom: '32px', fontSize: '0.95rem' }}>
            Nền tảng AI kết hợp Retrieval-Augmented Generation (RAG) và Chain-of-Thought
            để trả lời câu hỏi pháp lý dựa trên hơn 1,000 văn bản pháp luật Việt Nam.
          </p>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
            {[
              { icon: '🔍', label: 'Tìm kiếm Hybrid', desc: 'BM25 + Semantic Vector Search' },
              { icon: '🤖', label: 'AI Chat RAG', desc: 'Hỏi đáp có nguồn trích dẫn rõ ràng' },
              { icon: '🕸️', label: 'Knowledge Graph', desc: 'Mạng quan hệ văn bản pháp luật' },
            ].map(({ icon, label, desc }) => (
              <div key={label} style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
                <span style={{ fontSize: '1.4rem' }}>{icon}</span>
                <div>
                  <p style={{ fontWeight: 600, fontSize: '0.9rem' }}>{label}</p>
                  <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>{desc}</p>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Right — Form */}
        <div style={{ flex: '0 0 auto', width: '100%', maxWidth: '440px', perspective: '1200px' }}>
          <div
            style={{
              display: 'grid',
              transform: showRegister ? 'rotateY(180deg)' : 'rotateY(0deg)',
              transition: 'transform 0.6s cubic-bezier(0.4, 0, 0.2, 1)',
              transformStyle: 'preserve-3d',
            }}
          >
            {/* Front: Login */}
            <div style={{
              gridArea: '1 / 1 / 2 / 2',
              backfaceVisibility: 'hidden',
              WebkitBackfaceVisibility: 'hidden',
              opacity: showRegister ? 0 : 1,
              pointerEvents: showRegister ? 'none' : 'auto',
              transition: 'opacity 0.6s',
            }}>
              <LoginForm
                onSuccess={() => {}}
                onToggleRegister={() => setShowRegister(true)}
              />
            </div>

            {/* Back: Register */}
            <div style={{
              gridArea: '1 / 1 / 2 / 2',
              backfaceVisibility: 'hidden',
              WebkitBackfaceVisibility: 'hidden',
              transform: 'rotateY(180deg)',
              opacity: !showRegister ? 0 : 1,
              pointerEvents: !showRegister ? 'none' : 'auto',
              transition: 'opacity 0.6s',
            }}>
              <RegisterForm
                onSuccess={() => setShowRegister(false)}
                onToggleLogin={() => setShowRegister(false)}
              />
            </div>
          </div>
        </div>
      </div>

      <style>{`
        @keyframes float {
          0%, 100% { transform: translateY(0px) scale(1); }
          50% { transform: translateY(-30px) scale(1.05); }
        }
        @keyframes spin {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }
        @media (min-width: 768px) {
          .auth-branding { display: flex !important; flex-direction: column; }
        }
      `}</style>
    </div>
  );
};
