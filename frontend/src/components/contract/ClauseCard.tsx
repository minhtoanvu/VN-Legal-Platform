import React, { useState } from 'react';
import type { ClauseAnalysis } from '../../types';
import { CoTPanel } from './CoTPanel';

interface ClauseCardProps {
  analysis: ClauseAnalysis;
}

export const ClauseCard: React.FC<ClauseCardProps> = ({ analysis }) => {
  const [expanded, setExpanded] = useState(false);

  // Determine colors based on risk level
  const getRiskStyle = () => {
    switch (analysis.risk_level) {
      case 'high':
        return { border: 'border-red-500', bg: 'bg-red-500/10', text: 'text-red-500', label: 'Rủi ro cao' };
      case 'medium':
        return { border: 'border-yellow-500', bg: 'bg-yellow-500/10', text: 'text-yellow-500', label: 'Rủi ro trung bình' };
      case 'low':
      default:
        return { border: 'border-emerald-500', bg: 'bg-emerald-500/10', text: 'text-emerald-500', label: 'An toàn' };
    }
  };

  const style = getRiskStyle();

  return (
    <div className={`glass-card mb-4 border-l-4 ${style.border} transition-all duration-300`}>
      <div 
        className="p-4 cursor-pointer flex justify-between items-start gap-4 hover:bg-white/5"
        onClick={() => setExpanded(!expanded)}
      >
        <div className="flex-1">
          <div className="flex items-center gap-3 mb-2">
            <h3 className="font-semibold text-white">{analysis.clause_title}</h3>
            <span className={`px-2 py-0.5 rounded text-xs font-semibold ${style.bg} ${style.text}`}>
              {style.label} ({analysis.risk_score}/10)
            </span>
          </div>
          <p className="text-sm text-gray-400 line-clamp-2">{analysis.clause_text}</p>
        </div>
        
        <button className="p-2 text-gray-400 hover:text-white transition-colors">
          <svg 
            xmlns="http://www.w3.org/2000/svg" 
            width="20" height="20" 
            viewBox="0 0 24 24" fill="none" stroke="currentColor" 
            strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"
            className={`transform transition-transform duration-300 ${expanded ? 'rotate-180' : ''}`}
          >
            <polyline points="6 9 12 15 18 9"></polyline>
          </svg>
        </button>
      </div>

      {expanded && (
        <div className="p-4 pt-0 border-t border-gray-800/50 mt-2 fade-in">
          <div className="bg-[#080c14] p-3 rounded text-sm text-gray-300 mb-4 border border-gray-800">
            <strong>Nguyên văn:</strong>
            <p className="mt-1">{analysis.clause_text}</p>
          </div>
          
          <CoTPanel analysis={analysis} />
        </div>
      )}
    </div>
  );
};
