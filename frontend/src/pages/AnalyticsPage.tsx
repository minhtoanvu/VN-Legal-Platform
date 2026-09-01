import React, { useEffect, useState } from 'react';
import type { AnalyticsDashboard } from '../types';
import { api } from '../services/api';
import { Loader2, Database, Zap, Clock, Activity, FilePlus } from 'lucide-react';
import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer, BarChart, Bar, XAxis, YAxis, CartesianGrid } from 'recharts';

const STATUS_COLORS = { active: '#10b981', expired: '#ef4444', amended: '#f97316' };
const STATUS_LABELS = { active: 'Còn hiệu lực', expired: 'Hết hiệu lực', amended: 'Đã sửa đổi' };
const MODE_COLORS: Record<string, string> = { hybrid: '#6366f1', semantic: '#14b8a6', bm25: '#f97316' };
const MODE_LABELS: Record<string, string> = { hybrid: 'Hybrid', semantic: 'Semantic', bm25: 'BM25' };

export const AnalyticsPage: React.FC = () => {
  const [data, setData] = useState<AnalyticsDashboard | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    api.get<AnalyticsDashboard>('/analytics/dashboard')
      .then(r => setData(r.data))
      .catch(console.error)
      .finally(() => setIsLoading(false));
  }, []);

  if (isLoading) {
    return (
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100vh', flexDirection: 'column', gap: '16px' }}>
        <Loader2 size={32} color="var(--primary)" style={{ animation: 'spin 1s linear infinite' }} />
        <p style={{ color: 'var(--text-muted)' }}>Đang tải thống kê...</p>
      </div>
    );
  }

  if (!data) {
    return (
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100vh' }}>
        <p style={{ color: 'var(--text-muted)' }}>Không thể tải dữ liệu thống kê.</p>
      </div>
    );
  }

  const statusChartData = (data.documents_by_status || []).map((item: any) => ({
    name: STATUS_LABELS[item.status as keyof typeof STATUS_LABELS] || item.status,
    value: item.count,
    color: STATUS_COLORS[item.status as keyof typeof STATUS_COLORS] || '#6b7280',
  }));

  const docTypeData = (data.documents_by_type || [])
    .sort((a: any, b: any) => b.count - a.count)
    .slice(0, 8)
    .map((item: any) => ({ name: item.doc_type.length > 14 ? item.doc_type.slice(0, 14) + '…' : item.doc_type, value: item.count }));

  const issuingBodyData = (data.top_issuing_bodies || [])
    .sort((a: any, b: any) => b.count - a.count)
    .slice(0, 8)
    .map((item: any) => ({ name: item.issuing_body.length > 20 ? item.issuing_body.slice(0, 20) + '…' : item.issuing_body, value: item.count }));

  const fieldData = (data.documents_by_field || [])
    .sort((a: any, b: any) => b.count - a.count)
    .slice(0, 8)
    .map((item: any) => ({ name: item.field.length > 20 ? item.field.slice(0, 20) + '…' : item.field, value: item.count }));

  const STAT_CARDS = [
    {
      icon: <Database size={22} color="var(--primary)" />,
      label: 'Văn bản pháp luật',
      value: data.kpi?.total_documents.toLocaleString('vi-VN') || 0,
      color: 'var(--primary)',
      glow: 'var(--primary-glow)',
    },
    {
      icon: <Activity size={22} color="var(--accent)" />,
      label: 'Lượt tra cứu',
      value: data.kpi?.total_queries.toLocaleString('vi-VN') || 0,
      color: 'var(--accent)',
      glow: 'var(--accent-glow)',
    },
    {
      icon: <FilePlus size={22} color="var(--accent-purple)" />,
      label: 'VB Mới (30 ngày)',
      value: data.kpi?.new_docs_30d.toLocaleString('vi-VN') || 0,
      color: 'var(--accent-purple)',
      glow: 'rgba(168,85,247,0.15)',
    },
    {
      icon: <Clock size={22} color="var(--accent-cyan)" />,
      label: 'Thời gian TB',
      value: `${Math.round(data.avg_query_duration_ms ?? 0)} ms`,
      color: 'var(--accent-cyan)',
      glow: 'rgba(6,182,212,0.15)',
    },
  ];

  return (
    <div style={{ padding: '32px', maxWidth: '1200px', margin: '0 auto' }}>
      {/* Header */}
      <div style={{ marginBottom: '32px' }}>
        <h1 style={{ fontSize: '1.6rem', fontWeight: 800, letterSpacing: '-0.02em', marginBottom: '4px' }} className="text-gradient-primary">
          Dashboard Thống kê
        </h1>
        <p style={{ color: 'var(--text-muted)', fontSize: '0.88rem' }}>
          Tổng quan hệ thống AI Legal Intelligence Platform
        </p>
      </div>

      {/* Stat cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '16px', marginBottom: '32px' }}>
        {STAT_CARDS.map(({ icon, label, value, color, glow }) => (
          <div
            key={label}
            className="glass-card"
            style={{ padding: '24px', display: 'flex', alignItems: 'center', gap: '18px' }}
          >
            <div style={{
              width: '52px', height: '52px', borderRadius: '14px',
              background: glow, border: `1px solid ${color}33`,
              display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0,
            }}>
              {icon}
            </div>
            <div>
              <p style={{ fontSize: '0.78rem', color: 'var(--text-muted)', marginBottom: '4px', textTransform: 'uppercase', letterSpacing: '0.05em', fontWeight: 600 }}>
                {label}
              </p>
              <p style={{ fontSize: '1.8rem', fontWeight: 800, color, lineHeight: 1, fontFamily: 'var(--font-heading)' }}>
                {value}
              </p>
            </div>
          </div>
        ))}
      </div>

      {/* Charts row 1 */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1.8fr', gap: '20px', marginBottom: '20px' }}>
        {/* Status pie chart */}
        <div className="glass-card" style={{ padding: '24px' }}>
          <h2 style={{ fontSize: '0.95rem', fontWeight: 700, marginBottom: '20px' }}>Phân loại hiệu lực</h2>
          <ResponsiveContainer width="100%" height={220}>
            <PieChart>
              <Pie data={statusChartData} cx="50%" cy="50%" innerRadius={55} outerRadius={90} paddingAngle={3} dataKey="value">
                {statusChartData.map((entry) => (
                  <Cell key={entry.name} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip
                contentStyle={{ background: 'var(--bg-surface)', border: '1px solid var(--border-light)', borderRadius: '8px', fontSize: '0.82rem' }}
                formatter={(value) => [Number(value).toLocaleString('vi-VN'), 'Văn bản']}
              />
            </PieChart>
          </ResponsiveContainer>
          {/* Legend */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', marginTop: '12px' }}>
            {statusChartData.map(d => (
              <div key={d.name} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <div style={{ width: '10px', height: '10px', borderRadius: '50%', background: d.color }} />
                  <span style={{ fontSize: '0.82rem', color: 'var(--text-secondary)' }}>{d.name}</span>
                </div>
                <span style={{ fontSize: '0.82rem', fontWeight: 600, color: 'var(--text-primary)' }}>
                  {d.value.toLocaleString('vi-VN')}
                </span>
              </div>
            ))}
          </div>
        </div>

        {/* Doc types bar chart */}
        <div className="glass-card" style={{ padding: '24px' }}>
          <h2 style={{ fontSize: '0.95rem', fontWeight: 700, marginBottom: '20px' }}>Top loại văn bản</h2>
          <ResponsiveContainer width="100%" height={260}>
            <BarChart data={docTypeData} layout="vertical" margin={{ left: 0, right: 16 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" horizontal={false} />
              <XAxis type="number" tick={{ fill: 'var(--text-muted)', fontSize: 11 }} />
              <YAxis type="category" dataKey="name" tick={{ fill: 'var(--text-secondary)', fontSize: 11 }} width={110} />
              <Tooltip
                contentStyle={{ background: 'var(--bg-surface)', border: '1px solid var(--border-light)', borderRadius: '8px', fontSize: '0.82rem' }}
                formatter={(v) => [Number(v).toLocaleString('vi-VN'), 'Văn bản']}
              />
              <Bar dataKey="value" fill="var(--primary)" radius={[0, 4, 4, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
      
      {/* Charts row 2 */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px', marginBottom: '32px' }}>
        {/* Issuing bodies bar chart */}
        <div className="glass-card" style={{ padding: '24px' }}>
          <h2 style={{ fontSize: '0.95rem', fontWeight: 700, marginBottom: '20px' }}>Top cơ quan ban hành</h2>
          <ResponsiveContainer width="100%" height={260}>
            <BarChart data={issuingBodyData} layout="vertical" margin={{ left: 0, right: 16 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" horizontal={false} />
              <XAxis type="number" tick={{ fill: 'var(--text-muted)', fontSize: 11 }} />
              <YAxis type="category" dataKey="name" tick={{ fill: 'var(--text-secondary)', fontSize: 11 }} width={140} />
              <Tooltip
                contentStyle={{ background: 'var(--bg-surface)', border: '1px solid var(--border-light)', borderRadius: '8px', fontSize: '0.82rem' }}
                formatter={(v) => [Number(v).toLocaleString('vi-VN'), 'Văn bản']}
              />
              <Bar dataKey="value" fill="var(--accent-purple)" radius={[0, 4, 4, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Fields bar chart */}
        <div className="glass-card" style={{ padding: '24px' }}>
          <h2 style={{ fontSize: '0.95rem', fontWeight: 700, marginBottom: '20px' }}>Top lĩnh vực</h2>
          <ResponsiveContainer width="100%" height={260}>
            <BarChart data={fieldData} layout="vertical" margin={{ left: 0, right: 16 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" horizontal={false} />
              <XAxis type="number" tick={{ fill: 'var(--text-muted)', fontSize: 11 }} />
              <YAxis type="category" dataKey="name" tick={{ fill: 'var(--text-secondary)', fontSize: 11 }} width={140} />
              <Tooltip
                contentStyle={{ background: 'var(--bg-surface)', border: '1px solid var(--border-light)', borderRadius: '8px', fontSize: '0.82rem' }}
                formatter={(v) => [Number(v).toLocaleString('vi-VN'), 'Văn bản']}
              />
              <Bar dataKey="value" fill="var(--accent-cyan)" radius={[0, 4, 4, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Recent queries */}
      {data.recent_queries && data.recent_queries.length > 0 && (
        <div className="glass-card" style={{ padding: '24px' }}>
          <h2 style={{ fontSize: '0.95rem', fontWeight: 700, marginBottom: '18px', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Zap size={16} color="var(--primary)" /> Lượt tìm kiếm gần đây
          </h2>
          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse' }}>
              <thead>
                <tr style={{ borderBottom: '1px solid var(--border-light)' }}>
                  {['Câu truy vấn', 'Chế độ', 'Kết quả', 'Thời gian', 'Ngày'].map(h => (
                    <th key={h} style={{ padding: '10px 14px', textAlign: 'left', fontSize: '0.75rem', fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {data.recent_queries.map((q, i) => (
                  <tr
                    key={i}
                    style={{ borderBottom: '1px solid var(--border-light)', transition: 'background 0.1s' }}
                    onMouseEnter={e => (e.currentTarget as HTMLElement).style.background = 'rgba(255,255,255,0.02)'}
                    onMouseLeave={e => (e.currentTarget as HTMLElement).style.background = 'transparent'}
                  >
                    <td style={{ padding: '12px 14px', fontSize: '0.85rem', maxWidth: '320px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                      {q.query}
                    </td>
                    <td style={{ padding: '12px 14px' }}>
                      <span style={{
                        fontSize: '0.72rem', fontWeight: 700, padding: '3px 8px', borderRadius: '999px', textTransform: 'uppercase',
                        background: `${MODE_COLORS[q.mode] || '#6366f1'}18`, color: MODE_COLORS[q.mode] || '#6366f1',
                        border: `1px solid ${MODE_COLORS[q.mode] || '#6366f1'}33`,
                      }}>
                        {MODE_LABELS[q.mode] || q.mode}
                      </span>
                    </td>
                    <td style={{ padding: '12px 14px', fontSize: '0.85rem', color: 'var(--text-secondary)' }}>{q.result_count}</td>
                    <td style={{ padding: '12px 14px', fontSize: '0.85rem', color: 'var(--text-muted)' }}>{q.duration_ms}ms</td>
                    <td style={{ padding: '12px 14px', fontSize: '0.82rem', color: 'var(--text-muted)' }}>
                      {new Date(q.created_at).toLocaleString('vi-VN', { day: '2-digit', month: '2-digit', hour: '2-digit', minute: '2-digit' })}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
};
