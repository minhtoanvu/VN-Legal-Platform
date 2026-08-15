import React, { useEffect, useRef } from 'react';
import { Network } from 'vis-network';
import { DataSet } from 'vis-data';
import type { GraphData } from '../../types';

interface KnowledgeGraphProps {
  data: GraphData;
}

const RELATION_COLORS: Record<string, string> = {
  guides:   '#3b82f6',
  amends:   '#f97316',
  replaces: '#8b5cf6',
  revokes:  '#ef4444',
  cites:    '#6b7280',
};

const RELATION_LABELS: Record<string, string> = {
  guides:   'Hướng dẫn',
  amends:   'Sửa đổi',
  replaces: 'Thay thế',
  revokes:  'Bãi bỏ',
  cites:    'Trích dẫn',
};

export const KnowledgeGraph: React.FC<KnowledgeGraphProps> = ({ data }) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const networkRef = useRef<Network | null>(null);

  useEffect(() => {
    if (!containerRef.current || !data) return;

    const nodes = new DataSet(
      data.nodes.map(node => ({
        id: node.id,
        label: node.label.length > 30 ? node.label.slice(0, 30) + '…' : node.label,
        title: node.label,
        shape: 'dot',
        size: node.is_center ? 24 : 16,
        color: {
          background: node.is_center ? '#6366f1' : '#1e293b',
          border: node.is_center ? '#a5b4fc' : '#334155',
          highlight: { background: '#6366f1', border: '#a5b4fc' },
          hover: { background: '#4f46e5', border: '#818cf8' },
        },
        font: {
          color: '#f8fafc',
          size: node.is_center ? 13 : 11,
          face: 'Inter, sans-serif',
        },
        borderWidth: node.is_center ? 2 : 1,
        shadow: node.is_center,
      }))
    );

    const edges = new DataSet(
      data.edges.map(edge => ({
        id: edge.id,
        from: edge.from,
        to: edge.to,
        label: RELATION_LABELS[edge.relation_type] || edge.relation_type,
        color: {
          color: RELATION_COLORS[edge.relation_type] || '#6b7280',
          highlight: '#fff',
          opacity: 0.8,
        },
        font: { color: RELATION_COLORS[edge.relation_type] || '#6b7280', size: 10, align: 'middle' },
        arrows: 'to',
        smooth: { enabled: true, type: 'curvedCW', roundness: 0.2 },
        width: 1.5,
      }))
    );

    const options = {
      physics: {
        enabled: true,
        solver: 'forceAtlas2Based',
        forceAtlas2Based: { gravitationalConstant: -50, springLength: 120 },
        stabilization: { iterations: 150 },
      },
      interaction: {
        hover: true,
        tooltipDelay: 100,
        zoomView: true,
        dragView: true,
      },
      layout: { randomSeed: 42 },
      nodes: { chosen: true },
      edges: { chosen: true },
    };

    networkRef.current = new Network(containerRef.current, { nodes, edges: edges as any }, options);

    return () => {
      networkRef.current?.destroy();
      networkRef.current = null;
    };
  }, [data]);

  return (
    <div style={{ position: 'relative', width: '100%', height: '420px', borderRadius: 'var(--radius-md)', overflow: 'hidden', background: 'rgba(8,12,20,0.8)' }}>
      <div ref={containerRef} style={{ width: '100%', height: '100%' }} />

      {/* Legend */}
      <div style={{
        position: 'absolute', bottom: '12px', left: '12px',
        background: 'rgba(15,22,38,0.85)', backdropFilter: 'blur(8px)',
        border: '1px solid var(--border-light)',
        borderRadius: 'var(--radius-sm)', padding: '10px 14px',
      }}>
        <p style={{ fontSize: '0.7rem', fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '8px' }}>
          Quan hệ
        </p>
        {Object.entries(RELATION_LABELS).map(([key, label]) => (
          <div key={key} style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
            <div style={{ width: '20px', height: '2px', background: RELATION_COLORS[key], borderRadius: '1px' }} />
            <span style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>{label}</span>
          </div>
        ))}
      </div>
    </div>
  );
};
