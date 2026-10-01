import React, { useState } from 'react';
import { User, Lock, Save, Shield } from 'lucide-react';
import { useAuth } from '../hooks/useAuth';
import { api } from '../services/api';

export const ProfilePage: React.FC = () => {
  const { user } = useAuth();
  const [fullName, setFullName] = useState(user?.full_name || '');
  const [currentPassword, setCurrentPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [loading, setLoading] = useState(false);

  const handleUpdateProfile = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      await api.patch('/auth/me', { full_name: fullName });
      alert('Cập nhật hồ sơ thành công! Vui lòng tải lại trang để thấy thay đổi.');
    } catch (err: any) {
      alert('Lỗi: ' + (err.response?.data?.detail || err.message));
    } finally {
      setLoading(false);
    }
  };

  const handleChangePassword = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      await api.post('/auth/change-password', {
        current_password: currentPassword,
        new_password: newPassword
      });
      alert('Đổi mật khẩu thành công!');
      setCurrentPassword('');
      setNewPassword('');
    } catch (err: any) {
      alert('Lỗi: ' + (err.response?.data?.detail || err.message));
    } finally {
      setLoading(false);
    }
  };

  if (!user) return null;

  return (
    <div style={{ padding: '32px', maxWidth: '800px', margin: '0 auto', color: 'var(--text-primary)' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '32px' }}>
        <div style={{
          width: '48px', height: '48px', borderRadius: '12px',
          background: 'linear-gradient(135deg, rgba(99,102,241,0.2), rgba(168,85,247,0.2))',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          color: 'var(--primary)'
        }}>
          {user.role === 'admin' ? <Shield size={24} /> : <User size={24} />}
        </div>
        <div>
          <h1 style={{ fontSize: '2rem', fontWeight: 800, margin: 0 }}>Hồ sơ cá nhân</h1>
          <p style={{ color: 'var(--text-muted)', margin: 0 }}>{user.email}</p>
        </div>
      </div>

      <div style={{ display: 'grid', gap: '24px' }}>
        {/* Update Profile Form */}
        <div style={{ background: 'var(--bg-surface)', padding: '24px', borderRadius: '16px', border: '1px solid var(--border-light)' }}>
          <h2 style={{ fontSize: '1.2rem', marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <User size={18} /> Cập nhật thông tin
          </h2>
          <form onSubmit={handleUpdateProfile} style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
            <div>
              <label style={{ display: 'block', fontSize: '0.9rem', color: 'var(--text-secondary)', marginBottom: '8px' }}>Họ và tên</label>
              <input
                type="text"
                value={fullName}
                onChange={e => setFullName(e.target.value)}
                required
                style={{
                  width: '100%', padding: '10px 14px', borderRadius: '8px',
                  background: 'var(--bg-background)', border: '1px solid var(--border-medium)',
                  color: 'var(--text-primary)', outline: 'none'
                }}
              />
            </div>
            <div>
              <label style={{ display: 'block', fontSize: '0.9rem', color: 'var(--text-secondary)', marginBottom: '8px' }}>Vai trò (Role)</label>
              <input
                type="text"
                value={user.role.toUpperCase()}
                disabled
                style={{
                  width: '100%', padding: '10px 14px', borderRadius: '8px',
                  background: 'rgba(255,255,255,0.02)', border: '1px solid var(--border-light)',
                  color: 'var(--text-muted)', cursor: 'not-allowed'
                }}
              />
            </div>
            <button
              type="submit"
              disabled={loading}
              style={{
                alignSelf: 'flex-start', padding: '10px 24px', borderRadius: '8px',
                background: 'var(--primary)', color: '#fff', border: 'none',
                fontWeight: 600, cursor: loading ? 'not-allowed' : 'pointer',
                display: 'flex', alignItems: 'center', gap: '8px'
              }}
            >
              <Save size={16} /> Lưu thay đổi
            </button>
          </form>
        </div>

        {/* Change Password Form */}
        <div style={{ background: 'var(--bg-surface)', padding: '24px', borderRadius: '16px', border: '1px solid var(--border-light)' }}>
          <h2 style={{ fontSize: '1.2rem', marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Lock size={18} /> Đổi mật khẩu
          </h2>
          <form onSubmit={handleChangePassword} style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
            <div>
              <label style={{ display: 'block', fontSize: '0.9rem', color: 'var(--text-secondary)', marginBottom: '8px' }}>Mật khẩu hiện tại</label>
              <input
                type="password"
                value={currentPassword}
                onChange={e => setCurrentPassword(e.target.value)}
                required
                style={{
                  width: '100%', padding: '10px 14px', borderRadius: '8px',
                  background: 'var(--bg-background)', border: '1px solid var(--border-medium)',
                  color: 'var(--text-primary)', outline: 'none'
                }}
              />
            </div>
            <div>
              <label style={{ display: 'block', fontSize: '0.9rem', color: 'var(--text-secondary)', marginBottom: '8px' }}>Mật khẩu mới</label>
              <input
                type="password"
                value={newPassword}
                onChange={e => setNewPassword(e.target.value)}
                required
                minLength={6}
                style={{
                  width: '100%', padding: '10px 14px', borderRadius: '8px',
                  background: 'var(--bg-background)', border: '1px solid var(--border-medium)',
                  color: 'var(--text-primary)', outline: 'none'
                }}
              />
            </div>
            <button
              type="submit"
              disabled={loading}
              style={{
                alignSelf: 'flex-start', padding: '10px 24px', borderRadius: '8px',
                background: 'var(--bg-background)', color: 'var(--text-primary)', border: '1px solid var(--border-medium)',
                fontWeight: 600, cursor: loading ? 'not-allowed' : 'pointer',
                display: 'flex', alignItems: 'center', gap: '8px'
              }}
            >
              <Lock size={16} /> Cập nhật mật khẩu
            </button>
          </form>
        </div>
      </div>
    </div>
  );
};
