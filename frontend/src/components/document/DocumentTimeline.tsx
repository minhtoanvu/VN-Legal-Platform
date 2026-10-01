import React from 'react';
import type { TimelineEvent } from '../../types';
import { Clock, FileText, Activity, AlertCircle, ArrowRight } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

interface DocumentTimelineProps {
  timeline: TimelineEvent[];
}

export const DocumentTimeline: React.FC<DocumentTimelineProps> = ({ timeline }) => {
  const navigate = useNavigate();

  if (!timeline || timeline.length === 0) {
    return <div style={{ padding: '20px', color: 'var(--text-muted)' }}>Không có dữ liệu timeline.</div>;
  }

  const EVENT_STYLES: Record<string, { color: string; icon: React.ReactNode }> = {
    issued: { color: 'var(--color-active)', icon: <FileText size={14} /> },
    effective: { color: '#3b82f6', icon: <Clock size={14} /> },
    amended: { color: '#f97316', icon: <Activity size={14} /> },
    expired: { color: 'var(--color-expired)', icon: <AlertCircle size={14} /> },
  };

  const formatDate = (d: string | undefined | null) => d ? new Date(d).toLocaleDateString('vi-VN', { day: '2-digit', month: '2-digit', year: 'numeric' }) : 'Không rõ';

  return (
    <div style={{ position: 'relative', paddingLeft: '24px' }}>
      {/* Vertical line */}
      <div style={{
        position: 'absolute',
        top: '16px',
        bottom: '16px',
        left: '7px',
        width: '2px',
        background: 'var(--border-medium)',
        borderRadius: '2px'
      }} />

      {timeline.map((event, index) => {
        const style = EVENT_STYLES[event.event_type] || { color: '#6b7280', icon: <Clock size={14} /> };
        const isClickable = event.event_type === 'amended' && event.related_doc_id;

        return (
          <div key={index} style={{ position: 'relative', paddingBottom: index === timeline.length - 1 ? '0' : '28px' }}>
            {/* Dot */}
            <div style={{
              position: 'absolute',
              left: '-24px',
              top: '4px',
              width: '16px',
              height: '16px',
              borderRadius: '50%',
              background: 'var(--bg-surface)',
              border: `2px solid ${style.color}`,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              zIndex: 1
            }}>
              <div style={{ width: '6px', height: '6px', borderRadius: '50%', background: style.color }} />
            </div>

            <div 
              onClick={() => isClickable && event.related_doc_id && navigate(`/documents/${event.related_doc_id}`)}
              style={{ 
                display: 'flex', 
                flexDirection: 'column', 
                gap: '4px',
                background: isClickable ? 'rgba(255,255,255,0.02)' : 'transparent',
                padding: '8px 12px',
                borderRadius: '8px',
                border: isClickable ? '1px solid var(--border-light)' : '1px solid transparent',
                cursor: isClickable ? 'pointer' : 'default',
                transition: 'all 0.2s'
              }}
              onMouseEnter={e => { if(isClickable) (e.currentTarget as HTMLElement).style.borderColor = 'var(--border-medium)' }}
              onMouseLeave={e => { if(isClickable) (e.currentTarget as HTMLElement).style.borderColor = 'var(--border-light)' }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <span style={{ 
                  color: style.color, 
                  fontSize: '0.75rem', 
                  fontWeight: 700, 
                  textTransform: 'uppercase',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '4px',
                  background: `${style.color}15`,
                  padding: '2px 8px',
                  borderRadius: '999px'
                }}>
                  {style.icon} {event.event_type}
                </span>
                <span style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
                  {formatDate(event.date)}
                </span>
              </div>
              <p style={{ fontSize: '0.9rem', color: 'var(--text-primary)', marginTop: '4px', lineHeight: 1.4 }}>
                {event.label || event.description || 'Sự kiện'}
              </p>
              {isClickable && (
                <div style={{ display: 'flex', alignItems: 'center', gap: '4px', color: '#f97316', fontSize: '0.8rem', marginTop: '4px', fontWeight: 600 }}>
                  Xem văn bản sửa đổi <ArrowRight size={14} />
                </div>
              )}
            </div>
          </div>
        );
      })}
    </div>
  );
};
