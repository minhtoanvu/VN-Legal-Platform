import React from 'react';
import type { ClauseAnalysis } from '../../types';

interface CoTPanelProps {
  analysis: ClauseAnalysis;
}

export const CoTPanel: React.FC<CoTPanelProps> = ({ analysis }) => {
  return (
    <div className="glass-card p-4 mt-3" style={{ background: 'rgba(15, 22, 38, 0.4)' }}>
      <h4 className="text-sm font-semibold text-primary mb-3 uppercase tracking-wider flex items-center gap-2">
        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M12 2v20"/><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/></svg>
        AI Phân Tích Lập Luận (Chain-of-Thought)
        {analysis.is_reflected && (
          <span className="badge badge-active ml-2" style={{ fontSize: '0.65rem' }}>Self-Reflected</span>
        )}
      </h4>

      <div className="space-y-4 text-sm">
        <div>
          <strong className="text-gray-300 block mb-1">1. Bản chất điều khoản:</strong>
          <p className="text-gray-400">{analysis.step1_identification}</p>
        </div>
        
        <div>
          <strong className="text-gray-300 block mb-1">2. Đối chiếu pháp luật:</strong>
          <p className="text-gray-400">{analysis.step2_legal_comparison}</p>
        </div>
        
        <div>
          <strong className="text-gray-300 block mb-1">3. Đánh giá rủi ro:</strong>
          <p className="text-gray-400">{analysis.step3_risk_evaluation}</p>
        </div>
        
        <div>
          <strong className="text-gray-300 block mb-1">4. Đề xuất:</strong>
          <p className="text-gray-400">{analysis.step4_suggestion}</p>
        </div>
      </div>

      {analysis.citations.length > 0 && (
        <div className="mt-4 pt-3 border-t border-gray-800">
          <strong className="text-gray-300 text-xs uppercase block mb-2">Trích dẫn luật:</strong>
          <div className="flex flex-col gap-2">
            {analysis.citations.map((c, i) => (
              <div key={i} className="bg-[#0f1626] p-2 rounded border border-gray-800 text-xs">
                <span className="text-secondary font-semibold">{c.doc_number}</span> - {c.title}
                <p className="text-gray-500 mt-1 italic">"...{c.snippet}..."</p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
