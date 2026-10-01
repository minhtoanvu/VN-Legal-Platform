import React from 'react';
import type { ClauseAnalysis } from '../../types';
import { Brain, Scale, ShieldAlert, Lightbulb, BookOpen } from 'lucide-react';

interface CoTPanelProps {
  analysis: ClauseAnalysis;
}

export const CoTPanel: React.FC<CoTPanelProps> = ({ analysis }) => {
  return (
    <div className="relative rounded-lg p-5 mt-4 bg-gradient-to-br from-[#151f33]/80 to-[#080c14]/90 border border-indigo-500/10 shadow-[inset_0_1px_0_rgba(255,255,255,0.05)] overflow-hidden">
      {/* Decorative background glow */}
      <div className="absolute top-0 right-0 w-64 h-64 bg-indigo-500/5 rounded-full blur-3xl -translate-y-1/2 translate-x-1/3 pointer-events-none"></div>

      <div className="flex items-center justify-between mb-5 relative z-10">
        <h4 className="text-xs font-bold text-indigo-400 uppercase tracking-widest flex items-center gap-2">
          <Brain className="w-4 h-4" />
          AI Chain-of-Thought
        </h4>
        {analysis.is_reflected && (
          <span className="flex items-center gap-1.5 px-2 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wider bg-emerald-500/10 border border-emerald-500/20 text-emerald-400">
            <svg className="w-3 h-3" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><polyline points="20 6 9 17 4 12"></polyline></svg>
            Self-Reflected
          </span>
        )}
      </div>

      <div className="grid md:grid-cols-2 gap-6 relative z-10">
        <div className="space-y-6">
          {/* Step 1 */}
          <div className="group">
            <div className="flex items-center gap-2 mb-2">
              <div className="w-6 h-6 rounded bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center text-indigo-400">
                <BookOpen className="w-3.5 h-3.5" />
              </div>
              <strong className="text-gray-200 font-medium text-sm">Bản chất điều khoản</strong>
            </div>
            <p className="text-[0.9rem] text-gray-400 whitespace-pre-wrap leading-relaxed pl-8 border-l border-white/5 group-hover:border-indigo-500/20 transition-colors">{analysis.step1_identification}</p>
          </div>
          
          {/* Step 3 */}
          <div className="group">
            <div className="flex items-center gap-2 mb-2">
              <div className="w-6 h-6 rounded bg-rose-500/10 border border-rose-500/20 flex items-center justify-center text-rose-400">
                <ShieldAlert className="w-3.5 h-3.5" />
              </div>
              <strong className="text-gray-200 font-medium text-sm">Đánh giá rủi ro</strong>
            </div>
            <p className="text-[0.9rem] text-gray-400 whitespace-pre-wrap leading-relaxed pl-8 border-l border-white/5 group-hover:border-rose-500/20 transition-colors">{analysis.step3_risk_evaluation}</p>
          </div>
        </div>
        
        <div className="space-y-6">
          {/* Step 2 */}
          <div className="group">
            <div className="flex items-center gap-2 mb-2">
              <div className="w-6 h-6 rounded bg-amber-500/10 border border-amber-500/20 flex items-center justify-center text-amber-400">
                <Scale className="w-3.5 h-3.5" />
              </div>
              <strong className="text-gray-200 font-medium text-sm">Đối chiếu pháp luật</strong>
            </div>
            <p className="text-[0.9rem] text-gray-400 whitespace-pre-wrap leading-relaxed pl-8 border-l border-white/5 group-hover:border-amber-500/20 transition-colors">{analysis.step2_legal_comparison}</p>
          </div>
          
          {/* Step 4 */}
          <div className="group">
            <div className="flex items-center gap-2 mb-2">
              <div className="w-6 h-6 rounded bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center text-emerald-400">
                <Lightbulb className="w-3.5 h-3.5" />
              </div>
              <strong className="text-gray-200 font-medium text-sm">Đề xuất</strong>
            </div>
            <p className="text-[0.9rem] text-gray-400 whitespace-pre-wrap leading-relaxed pl-8 border-l border-white/5 group-hover:border-emerald-500/20 transition-colors">{analysis.step4_suggestion}</p>
          </div>
        </div>
      </div>

      {analysis.citations.length > 0 && (
        <div className="mt-6 pt-5 border-t border-white/5 relative z-10">
          <strong className="text-gray-400 text-xs font-semibold uppercase tracking-wider block mb-3 flex items-center gap-2">
            <Scale className="w-3.5 h-3.5" /> Căn cứ pháp lý
          </strong>
          <div className="grid gap-3">
            {analysis.citations.map((c, i) => (
              <div key={i} className="bg-[#080c14]/60 p-3.5 rounded-lg border border-white/5 hover:border-indigo-500/30 transition-colors group">
                <div className="flex items-center gap-2 mb-1.5">
                  <span className="text-indigo-400 font-medium text-sm bg-indigo-500/10 px-2 py-0.5 rounded text-xs">{c.doc_number}</span>
                  <span className="text-gray-300 text-sm font-medium line-clamp-1">{c.title}</span>
                </div>
                <p className="text-gray-500 text-[0.85rem] italic pl-2 border-l-2 border-indigo-500/20 leading-relaxed group-hover:border-indigo-500/40 transition-colors">
                  "{c.snippet}"
                </p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
