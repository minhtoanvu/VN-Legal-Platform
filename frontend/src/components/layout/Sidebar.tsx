import React, { useState } from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth';
import {
  Search, BarChart2, Scale, LogOut, ChevronLeft, ChevronRight,
  User, Shield, FolderOpen,
} from 'lucide-react';

const NAV_ITEMS = [
  { to: '/search',    icon: <Search size={20} />,     label: 'Tìm kiếm' },
  { to: '/workspace', icon: <FolderOpen size={20} />, label: 'Workspace' },
  { to: '/analytics', icon: <BarChart2 size={20} />,  label: 'Thống kê' },
];

export const Sidebar: React.FC = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [collapsed, setCollapsed] = useState(false);

  const handleLogout = () => {
    logout();
    navigate('/auth', { replace: true });
  };

  return (
    <aside
      style={{
        width: collapsed ? '68px' : '220px',
        minHeight: '100vh',
        background: 'var(--bg-surface)',
        borderRight: '1px solid var(--border-light)',
        display: 'flex', flexDirection: 'column',
        transition: 'width 0.3s cubic-bezier(0.16,1,0.3,1)',
        flexShrink: 0,
        position: 'relative', zIndex: 10,
        overflow: 'hidden',
      }}
    >
      {/* Logo */}
      <div style={{ padding: collapsed ? '20px 0' : '24px 20px', borderBottom: '1px solid var(--border-light)', display: 'flex', alignItems: 'center', gap: '12px' }}>
        <div style={{
          flexShrink: 0, width: '36px', height: '36px', borderRadius: '10px',
          background: 'linear-gradient(135deg, var(--primary), var(--accent-purple))',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          boxShadow: '0 0 12px rgba(99,102,241,0.4)',
          marginLeft: collapsed ? 'auto' : '0', marginRight: collapsed ? 'auto' : '0',
        }}>
          <Scale size={20} color="#fff" />
        </div>
        {!collapsed && (
          <div>
            <p style={{ fontSize: '0.9rem', fontWeight: 800, fontFamily: 'var(--font-heading)', lineHeight: 1.2 }} className="text-gradient-primary">
              LexAI
            </p>
            <p style={{ fontSize: '0.68rem', color: 'var(--text-muted)', lineHeight: 1 }}>Legal Intelligence</p>
          </div>
        )}
      </div>

      {/* Nav */}
      <nav style={{ flex: 1, padding: '16px 8px' }}>
        {NAV_ITEMS.map(({ to, icon, label }) => (
          <NavLink
            key={to}
            to={to}
            style={({ isActive }) => ({
              display: 'flex', alignItems: 'center',
              gap: '12px',
              padding: collapsed ? '12px 0' : '11px 14px',
              justifyContent: collapsed ? 'center' : 'flex-start',
              borderRadius: 'var(--radius-sm)',
              marginBottom: '4px',
              color: isActive ? 'var(--primary)' : 'var(--text-secondary)',
              background: isActive ? 'var(--primary-glow)' : 'transparent',
              border: `1px solid ${isActive ? 'rgba(99,102,241,0.2)' : 'transparent'}`,
              fontWeight: isActive ? 600 : 400,
              fontSize: '0.9rem',
              textDecoration: 'none',
              transition: 'all 0.15s ease',
              whiteSpace: 'nowrap',
              overflow: 'hidden',
            })}
            title={collapsed ? label : undefined}
          >
            {icon}
            {!collapsed && <span>{label}</span>}
          </NavLink>
        ))}
      </nav>

      {/* Collapse toggle */}
      <button
        onClick={() => setCollapsed(!collapsed)}
        style={{
          position: 'absolute', top: '50%', right: '-12px',
          width: '24px', height: '24px',
          background: 'var(--bg-surface)', border: '1px solid var(--border-medium)',
          borderRadius: '50%', cursor: 'pointer',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          color: 'var(--text-muted)', zIndex: 20,
          transform: 'translateY(-50%)',
          transition: 'all 0.15s ease',
        }}
      >
        {collapsed ? <ChevronRight size={14} /> : <ChevronLeft size={14} />}
      </button>

      {/* User info + Logout */}
      <div style={{ padding: collapsed ? '12px 4px' : '12px 10px', borderTop: '1px solid var(--border-light)' }}>
        {!collapsed && user && (
          <div style={{
            padding: '10px 12px', borderRadius: 'var(--radius-sm)',
            background: 'rgba(255,255,255,0.02)', marginBottom: '8px',
            display: 'flex', alignItems: 'center', gap: '10px',
          }}>
            <div style={{
              width: '32px', height: '32px', borderRadius: '50%', flexShrink: 0,
              background: 'linear-gradient(135deg, var(--primary), var(--accent-purple))',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
            }}>
              {user.role === 'admin' ? <Shield size={15} color="#fff" /> : <User size={15} color="#fff" />}
            </div>
            <div style={{ minWidth: 0 }}>
              <p style={{ fontSize: '0.82rem', fontWeight: 600, color: 'var(--text-primary)', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                {user.full_name}
              </p>
              <p style={{ fontSize: '0.7rem', color: 'var(--text-muted)', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                {user.email}
              </p>
            </div>
          </div>
        )}
        <button
          onClick={handleLogout}
          style={{
            width: '100%', display: 'flex', alignItems: 'center',
            gap: collapsed ? '0' : '10px', justifyContent: collapsed ? 'center' : 'flex-start',
            padding: '10px 12px',
            background: 'none', border: '1px solid transparent',
            borderRadius: 'var(--radius-sm)', cursor: 'pointer',
            color: 'var(--text-muted)', fontSize: '0.88rem',
            transition: 'all 0.15s ease',
          }}
          onMouseEnter={e => {
            (e.currentTarget as HTMLElement).style.color = 'var(--color-expired)';
            (e.currentTarget as HTMLElement).style.background = 'var(--color-expired-bg)';
            (e.currentTarget as HTMLElement).style.borderColor = 'rgba(239,68,68,0.2)';
          }}
          onMouseLeave={e => {
            (e.currentTarget as HTMLElement).style.color = 'var(--text-muted)';
            (e.currentTarget as HTMLElement).style.background = 'none';
            (e.currentTarget as HTMLElement).style.borderColor = 'transparent';
          }}
          title={collapsed ? 'Đăng xuất' : undefined}
        >
          <LogOut size={18} />
          {!collapsed && <span>Đăng xuất</span>}
        </button>
      </div>
    </aside>
  );
};
