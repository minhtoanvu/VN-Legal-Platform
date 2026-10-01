import React, { useState } from 'react';
import type { ClauseAnalysis } from '../../types';
import { CoTPanel } from './CoTPanel';
import { AlertTriangle, AlertCircle, CheckCircle, ChevronDown } from 'lucide-react';

interface ClauseCardProps {
  analysis: ClauseAnalysis;
}

export const ClauseCard: React.FC<ClauseCardProps> = ({ analysis }) => {
  const [expanded, setExpanded] = useState(false);

  // Determine styles and icons based on risk level
  const getRiskStyle = () => {
    switch (analysis.risk_level) {
      case 'high':
        return { 
          border: 'border-red-500/50', 
          bg: 'bg-red-500/10', 
          text: 'text-red-400', 
          label: 'Rủi ro cao',
          glow: 'shadow-[0_0_15px_rgba(239,68,68,0.15)]',
          icon: <AlertTriangle className="w-4 h-4 text-red-400" />
        };
      case 'medium':
        return { 
          border: 'border-yellow-500/50', 
          bg: 'bg-yellow-500/10', 
          text: 'text-yellow-400', 
          label: 'Rủi ro trung bình',
          glow: 'shadow-[0_0_15px_rgba(234,179,8,0.1)]',
          icon: <AlertCircle className="w-4 h-4 text-yellow-400" />
        };
      case 'low':
      default:
        return { 
          border: 'border-emerald-500/40', 
          bg: 'bg-emerald-500/10', 
          text: 'text-emerald-400', 
          label: 'An toàn',
          glow: 'shadow-none',
          icon: <CheckCircle className="w-4 h-4 text-emerald-400" />
        };
    }
  };

  const style = getRiskStyle();

  return (
    <div 
      className={`relative rounded-xl border border-white/5 bg-[#0f1626]/80 backdrop-blur-md overflow-hidden transition-all duration-300 ${expanded ? 'border-white/15 shadow-lg' : 'hover:border-white/15'} mb-5 ${style.glow}`}
    >
      {/* Accent left border */}
      <div className={`absolute left-0 top-0 bottom-0 w-1 ${style.bg} border-l ${style.border}`}></div>
      
      <div 
        className="p-5 pl-7 cursor-pointer flex justify-between items-start gap-4 hover:bg-white/[0.02] transition-colors"
        onClick={() => setExpanded(!expanded)}
      >
        <div className="flex-1">
          <div className="flex flex-wrap items-center gap-3 mb-2.5">
            <h3 className="text-lg font-semibold text-white/95 tracking-tight">{analysis.clause_title}</h3>
            
            <div className="flex items-center gap-2">
              <span className={`flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold ${style.bg} border ${style.border} ${style.text} shadow-[inset_0_1px_0_rgba(255,255,255,0.1)]`}>
                {style.icon}
                {style.label}
              </span>
              <span className="text-xs font-medium text-gray-500 bg-[#080c14] px-2.5 py-1 rounded-full border border-gray-800">
                Điểm rủi ro: <span className="text-gray-300">{analysis.risk_score}/10</span>
              </span>
            </div>
          </div>
          <p className="text-[0.95rem] text-gray-400 leading-relaxed line-clamp-2 pr-4">{analysis.clause_text}</p>
        </div>
        
        <button className="p-2 text-gray-500 hover:text-white hover:bg-white/5 rounded-full transition-all mt-1">
          <ChevronDown 
            className={`w-5 h-5 transform transition-transform duration-300 ${expanded ? 'rotate-180 text-primary' : ''}`}
          />
        </button>
      </div>

      <div 
        className={`grid transition-all duration-400 ease-in-out ${expanded ? 'grid-rows-[1fr] opacity-100' : 'grid-rows-[0fr] opacity-0'}`}
      >
        <div className="overflow-hidden">
          <div className="p-5 pl-7 pt-0 border-t border-white/5 mt-2">
            <div className="bg-[#080c14]/80 p-4 rounded-lg text-[0.9rem] text-gray-300 mb-5 border border-white/5 shadow-inner">
              <strong className="text-gray-400 text-xs uppercase tracking-wider block mb-2">Nguyên văn điều khoản</strong>
              <p className="whitespace-pre-wrap leading-relaxed opacity-90">{analysis.clause_text}</p>
            </div>
            
            <CoTPanel analysis={analysis} />
          </div>
        </div>
      </div>
    </div>
  );
};
