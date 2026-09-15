import React, { useEffect, useState } from 'react';
import { Shield, Users, FileText, Database } from 'lucide-react';
import { api } from '../services/api';

interface UserItem {
  id: string;
  email: string;
  full_name: string;
  role: 'user' | 'enterprise' | 'admin';
  is_active: boolean;
  created_at: string;
  last_login?: string;
}

export const AdminPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'users' | 'documents'>('users');
  const [users, setUsers] = useState<UserItem[]>([]);
  const [stats, setStats] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    setLoading(true);
    try {
      const [usersRes, statsRes] = await Promise.all([
        api.get('/admin/users'),
        api.get('/admin/stats')
      ]);
      setUsers(usersRes.data);
      setStats(statsRes.data);
    } catch (err) {
      console.error('Failed to fetch admin data', err);
    } finally {
      setLoading(false);
    }
  };

  const toggleUserStatus = async (userId: string, currentStatus: boolean) => {
    try {
      await api.patch(`/admin/users/${userId}/status`, { is_active: !currentStatus });
      setUsers(users.map(u => u.id === userId ? { ...u, is_active: !currentStatus } : u));
    } catch {
      alert('Lỗi khi đổi trạng thái user.');
    }
  };

  const changeUserRole = async (userId: string, newRole: string) => {
    try {
      await api.patch(`/admin/users/${userId}/role`, { role: newRole });
      setUsers(users.map(u => u.id === userId ? { ...u, role: newRole as any } : u));
    } catch {
      alert('Lỗi khi đổi quyền user.');
    }
  };

  if (loading) {
    return <div style={{ padding: 40, color: '#fff' }}>Đang tải dữ liệu Admin...</div>;
  }

  return (
    <div style={{ padding: '32px', maxWidth: '1200px', margin: '0 auto', color: 'var(--text-primary)' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '32px' }}>
        <div style={{
          width: '48px', height: '48px', borderRadius: '12px',
          background: 'linear-gradient(135deg, rgba(99,102,241,0.2), rgba(168,85,247,0.2))',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          color: 'var(--primary)'
        }}>
          <Shield size={24} />
        </div>
        <div>
          <h1 style={{ fontSize: '2rem', fontWeight: 800, margin: 0 }}>Quản trị hệ thống</h1>
          <p style={{ color: 'var(--text-muted)', margin: 0 }}>Quản lý người dùng, văn bản và theo dõi số liệu</p>
        </div>
      </div>

      {stats && (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '20px', marginBottom: '32px' }}>
          <div style={{ background: 'var(--bg-surface)', padding: '24px', borderRadius: '16px', border: '1px solid var(--border-light)' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '12px', color: 'var(--text-secondary)' }}>
              <Users size={20} />
              <span style={{ fontWeight: 600 }}>Tổng Users</span>
            </div>
            <div style={{ fontSize: '2rem', fontWeight: 800 }}>{stats.users.total}</div>
            <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginTop: '8px' }}>
              <span style={{ color: 'var(--color-success)' }}>{stats.users.active}</span> đang hoạt động
            </div>
          </div>
          
          <div style={{ background: 'var(--bg-surface)', padding: '24px', borderRadius: '16px', border: '1px solid var(--border-light)' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '12px', color: 'var(--text-secondary)' }}>
              <FileText size={20} />
              <span style={{ fontWeight: 600 }}>Tổng Văn bản</span>
            </div>
            <div style={{ fontSize: '2rem', fontWeight: 800 }}>{stats.documents.total}</div>
            <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginTop: '8px' }}>
              <span style={{ color: 'var(--color-success)' }}>{stats.documents.active}</span> có hiệu lực
            </div>
          </div>
          
          <div style={{ background: 'var(--bg-surface)', padding: '24px', borderRadius: '16px', border: '1px solid var(--border-light)' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '12px', color: 'var(--text-secondary)' }}>
              <Database size={20} />
              <span style={{ fontWeight: 600 }}>ETL Sync</span>
            </div>
            <div style={{ fontSize: '2rem', fontWeight: 800 }}>Ready</div>
            <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginTop: '8px' }}>
              PostgreSQL + pgvector
            </div>
          </div>
        </div>
      )}

      {/* Tabs */}
      <div style={{ display: 'flex', gap: '16px', marginBottom: '24px', borderBottom: '1px solid var(--border-medium)' }}>
        <button
          onClick={() => setActiveTab('users')}
          style={{
            padding: '12px 24px', background: 'none', border: 'none',
            borderBottom: activeTab === 'users' ? '2px solid var(--primary)' : '2px solid transparent',
            color: activeTab === 'users' ? 'var(--primary)' : 'var(--text-muted)',
            fontWeight: activeTab === 'users' ? 600 : 400,
            cursor: 'pointer', fontSize: '1rem', transition: 'all 0.2s'
          }}
        >
          Người dùng
        </button>
        <button
          onClick={() => setActiveTab('documents')}
          style={{
            padding: '12px 24px', background: 'none', border: 'none',
            borderBottom: activeTab === 'documents' ? '2px solid var(--primary)' : '2px solid transparent',
            color: activeTab === 'documents' ? 'var(--primary)' : 'var(--text-muted)',
            fontWeight: activeTab === 'documents' ? 600 : 400,
            cursor: 'pointer', fontSize: '1rem', transition: 'all 0.2s'
          }}
        >
          Văn bản
        </button>
      </div>

      {/* Tab Content */}
      {activeTab === 'users' && (
        <div style={{ background: 'var(--bg-surface)', borderRadius: '16px', border: '1px solid var(--border-light)', overflow: 'hidden' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left' }}>
            <thead>
              <tr style={{ background: 'rgba(255,255,255,0.02)', borderBottom: '1px solid var(--border-medium)' }}>
                <th style={{ padding: '16px', fontWeight: 600, color: 'var(--text-secondary)' }}>Người dùng</th>
                <th style={{ padding: '16px', fontWeight: 600, color: 'var(--text-secondary)' }}>Vai trò</th>
                <th style={{ padding: '16px', fontWeight: 600, color: 'var(--text-secondary)' }}>Trạng thái</th>
                <th style={{ padding: '16px', fontWeight: 600, color: 'var(--text-secondary)', textAlign: 'right' }}>Hành động</th>
              </tr>
            </thead>
            <tbody>
              {users.map(u => (
                <tr key={u.id} style={{ borderBottom: '1px solid var(--border-light)' }}>
                  <td style={{ padding: '16px' }}>
                    <div style={{ fontWeight: 500 }}>{u.full_name}</div>
                    <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>{u.email}</div>
                  </td>
                  <td style={{ padding: '16px' }}>
                    <select
                      value={u.role}
                      onChange={(e) => changeUserRole(u.id, e.target.value)}
                      style={{
                        padding: '6px 12px', borderRadius: '8px',
                        background: 'var(--bg-background)', border: '1px solid var(--border-medium)',
                        color: 'var(--text-primary)', outline: 'none'
                      }}
                    >
                      <option value="user">User</option>
                      <option value="enterprise">Enterprise</option>
                      <option value="admin">Admin</option>
                    </select>
                  </td>
                  <td style={{ padding: '16px' }}>
                    <span style={{
                      padding: '4px 10px', borderRadius: '100px', fontSize: '0.8rem', fontWeight: 500,
                      background: u.is_active ? 'rgba(34,197,94,0.1)' : 'rgba(239,68,68,0.1)',
                      color: u.is_active ? 'var(--color-success)' : 'var(--color-expired)'
                    }}>
                      {u.is_active ? 'Active' : 'Locked'}
                    </span>
                  </td>
                  <td style={{ padding: '16px', textAlign: 'right' }}>
                    <button
                      onClick={() => toggleUserStatus(u.id, u.is_active)}
                      style={{
                        padding: '8px 16px', borderRadius: '8px', cursor: 'pointer',
                        background: u.is_active ? 'rgba(239,68,68,0.1)' : 'rgba(34,197,94,0.1)',
                        border: 'none', color: u.is_active ? 'var(--color-expired)' : 'var(--color-success)',
                        fontWeight: 600, fontSize: '0.85rem'
                      }}
                    >
                      {u.is_active ? 'Khóa' : 'Kích hoạt'}
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {activeTab === 'documents' && (
        <div style={{ background: 'var(--bg-surface)', padding: '40px', borderRadius: '16px', border: '1px solid var(--border-light)', textAlign: 'center' }}>
          <FileText size={48} color="var(--text-muted)" style={{ margin: '0 auto 16px' }} />
          <h3 style={{ margin: '0 0 8px 0', fontSize: '1.2rem' }}>Quản lý văn bản</h3>
          <p style={{ color: 'var(--text-muted)', margin: '0 0 24px 0', maxWidth: '500px', marginLeft: 'auto', marginRight: 'auto' }}>
            Hệ thống ETL hiện tự động đồng bộ văn bản. Bạn có thể trigger tiến trình đồng bộ thủ công.
          </p>
          <button
            onClick={async () => {
              try {
                await api.post('/admin/documents/sync');
                alert('Đã gửi yêu cầu đồng bộ. Vui lòng kiểm tra tiến trình trên server.');
              } catch {
                alert('Không thể gọi API đồng bộ ETL.');
              }
            }}
            style={{
              padding: '12px 24px', background: 'var(--primary)', color: '#fff',
              border: 'none', borderRadius: '8px', fontWeight: 600, cursor: 'pointer'
            }}
          >
            Chạy đồng bộ ETL ngay
          </button>
        </div>
      )}
    </div>
  );
};
