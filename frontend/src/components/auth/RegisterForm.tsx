import React, { useState, useEffect } from 'react';
import { useAuth } from '../../hooks/useAuth';
import { UserPlus, Mail, Lock, User, Loader2, AlertCircle, CheckCircle2 } from 'lucide-react';

interface RegisterFormProps {
  onSuccess: () => void;
  onToggleLogin: () => void;
}

export const RegisterForm: React.FC<RegisterFormProps> = ({ onSuccess, onToggleLogin }) => {
  const { register, isLoading, error, clearError } = useAuth();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [fullName, setFullName] = useState('');
  const [validationError, setValidationError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  useEffect(() => {
    return () => clearError();
  }, [clearError]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setValidationError(null);

    if (!email.trim() || !password.trim() || !fullName.trim()) {
      setValidationError('Vui lòng điền đầy đủ thông tin.');
      return;
    }
    if (password !== confirmPassword) {
      setValidationError('Mật khẩu xác nhận không khớp.');
      return;
    }
    if (password.length < 8) {
      setValidationError('Mật khẩu phải có ít nhất 8 ký tự.');
      return;
    }

    const ok = await register(email, password, fullName);
    if (ok) {
      setSuccess(true);
      setTimeout(() => onSuccess(), 1500);
    }
  };

  if (success) {
    return (
      <div className="glass-card" style={{ padding: '40px', width: '100%', maxWidth: '440px', margin: '0 auto', textAlign: 'center' }}>
        <CheckCircle2 size={56} color="var(--color-active)" style={{ margin: '0 auto 20px' }} />
        <h2 style={{ fontSize: '1.6rem', marginBottom: '8px' }} className="text-gradient-secondary">
          Đăng ký thành công!
        </h2>
        <p style={{ color: 'var(--text-secondary)' }}>Đang chuyển hướng đến trang đăng nhập...</p>
      </div>
    );
  }

  return (
    <div className="glass-card" style={{ padding: '40px', width: '100%', maxWidth: '440px', margin: '0 auto' }}>
      <div style={{ textAlign: 'center', marginBottom: '32px' }}>
        <h2 style={{ fontSize: '2rem', marginBottom: '8px' }} className="text-gradient-secondary">
          Tạo tài khoản
        </h2>
        <p style={{ color: 'var(--text-secondary)', fontSize: '0.95rem' }}>
          Tham gia Legal Intelligence Platform
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

      <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '18px' }}>
        {[
          { label: 'Họ và tên', icon: <User size={18} />, type: 'text', value: fullName, setter: setFullName, placeholder: 'Nguyễn Văn A' },
          { label: 'Địa chỉ Email', icon: <Mail size={18} />, type: 'email', value: email, setter: setEmail, placeholder: 'ten@congty.com' },
          { label: 'Mật khẩu', icon: <Lock size={18} />, type: 'password', value: password, setter: setPassword, placeholder: '••••••••' },
          { label: 'Xác nhận mật khẩu', icon: <Lock size={18} />, type: 'password', value: confirmPassword, setter: setConfirmPassword, placeholder: '••••••••' },
        ].map(({ label, icon, type, value, setter, placeholder }) => (
          <div key={label} style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
            <label style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-secondary)' }}>{label}</label>
            <div style={{ position: 'relative' }}>
              <span style={{ position: 'absolute', left: '14px', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }}>
                {icon}
              </span>
              <input
                type={type}
                className="input-field"
                placeholder={placeholder}
                value={value}
                onChange={(e) => setter(e.target.value)}
                style={{ paddingLeft: '44px' }}
                disabled={isLoading}
              />
            </div>
          </div>
        ))}

        <button
          type="submit"
          className="btn btn-secondary"
          style={{ width: '100%', height: '46px', marginTop: '8px' }}
          disabled={isLoading}
        >
          {isLoading ? (
            <>
              <Loader2 size={18} style={{ animation: 'spin 1s linear infinite' }} />
              <span>Đang xử lý...</span>
            </>
          ) : (
            <>
              <UserPlus size={18} />
              <span>Đăng ký</span>
            </>
          )}
        </button>
      </form>

      <div style={{ textAlign: 'center', marginTop: '24px', fontSize: '0.9rem', color: 'var(--text-secondary)' }}>
        Đã có tài khoản?{' '}
        <button
          onClick={onToggleLogin}
          style={{ background: 'none', border: 'none', color: 'var(--primary)', cursor: 'pointer', fontWeight: 500, textDecoration: 'underline' }}
          disabled={isLoading}
        >
          Đăng nhập
        </button>
      </div>
    </div>
  );
};
