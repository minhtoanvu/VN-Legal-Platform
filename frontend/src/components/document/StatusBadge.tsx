import React from 'react';
import type { DocumentStatus } from '../../types';

interface StatusBadgeProps {
  status: DocumentStatus;
  size?: 'sm' | 'md';
}

const STATUS_CONFIG: Record<DocumentStatus, { label: string; className: string }> = {
  active: { label: 'Còn hiệu lực', className: 'badge badge-active' },
  expired: { label: 'Hết hiệu lực', className: 'badge badge-expired' },
  amended: { label: 'Đã sửa đổi', className: 'badge badge-amended' },
};

export const StatusBadge: React.FC<StatusBadgeProps> = ({ status, size = 'md' }) => {
  const config = STATUS_CONFIG[status] || { label: status, className: 'badge' };
  return (
    <span
      className={config.className}
      style={size === 'sm' ? { fontSize: '0.65rem', padding: '2px 7px' } : undefined}
    >
      {config.label}
    </span>
  );
};
