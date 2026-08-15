import React, { useState, useEffect } from 'react';
import { useAuth } from '../../hooks/useAuth';
import { LogIn, Mail, Lock, Loader2, AlertCircle } from 'lucide-react';

interface LoginFormProps {
  onSuccess: () => void;
  onToggleRegister: () => void;
}

export const LoginForm: React.FC<LoginFormProps> = ({ onSuccess, onToggleRegister }) => {
  const { login, isLoading, error, clearError } = useAuth();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [validationError, setValidationError] = useState<string | null>(null);

  // Clear errors when unmounting
  useEffect(() => {
    return () => {
      clearError();
    };
  }, [clearError]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setValidationError(null);

    if (!email.trim() || !password.trim()) {
      setValidationError('Vui lòng nhập đầy đủ email và mật khẩu.');
      return;
    }

    const success = await login(email, password);
    if (success) {
      onSuccess();
    }
  };

  return (
    <div className="glass-card" style={{ padding: '40px', width: '100%', maxWidth: '440px', margin: '0 auto' }}>
      <div style={{ textAlign: 'center', marginBottom: '32px' }}>
        <h2 style={{ fontSize: '2rem', marginBottom: '8px' }} className="text-gradient-primary">
          Chào mừng quay lại
        </h2>
        <p style={{ color: 'var(--text-secondary)', fontSize: '0.95rem' }}>
          Đăng nhập vào Legal Intelligence Platform
        </p>
      </div>

      {(error || validationError) && (
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '12px',
            backgroundColor: 'var(--color-expired-bg)',
            border: '1px solid rgba(239, 68, 68, 0.2)',
            borderRadius: 'var(--radius-sm)',
            padding: '12px 16px',
            marginBottom: '24px',
            color: 'var(--color-expired)',
            fontSize: '0.9rem',
          }}
        >
          <AlertCircle size={18} style={{ flexShrink: 0 }} />
          <span>{validationError || error}</span>
        </div>
      )}

      <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
          <label style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-secondary)' }}>
            Địa chỉ Email
          </label>
          <div style={{ position: 'relative' }}>
            <span style={{ position: 'absolute', left: '14px', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }}>
              <Mail size={18} />
            </span>
            <input
              type="email"
              className="input-field"
              placeholder="ten@congty.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              style={{ paddingLeft: '44px' }}
              disabled={isLoading}
            />
          </div>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
          <label style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-secondary)' }}>
            Mật khẩu
          </label>
          <div style={{ position: 'relative' }}>
            <span style={{ position: 'absolute', left: '14px', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }}>
              <Lock size={18} />
            </span>
            <input
              type="password"
              className="input-field"
              placeholder="••••••••"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              style={{ paddingLeft: '44px' }}
              disabled={isLoading}
            />
          </div>
        </div>

        <button
          type="submit"
          className="btn btn-primary"
          style={{ width: '100%', height: '46px', marginTop: '8px' }}
          disabled={isLoading}
        >
          {isLoading ? (
            <>
              <Loader2 size={18} className="skeleton" style={{ animation: 'spin 1s linear infinite' }} />
              <span>Đang kết nối...</span>
            </>
          ) : (
            <>
              <LogIn size={18} />
              <span>Đăng nhập</span>
            </>
          )}
        </button>
      </form>

      <div style={{ textAlign: 'center', marginTop: '24px', fontSize: '0.9rem', color: 'var(--text-secondary)' }}>
        Chưa có tài khoản?{' '}
        <button
          onClick={onToggleRegister}
          style={{
            background: 'none',
            border: 'none',
            color: 'var(--primary)',
            cursor: 'pointer',
            fontWeight: 500,
            textDecoration: 'underline',
          }}
          disabled={isLoading}
        >
          Đăng ký ngay
        </button>
      </div>
    </div>
  );
};
