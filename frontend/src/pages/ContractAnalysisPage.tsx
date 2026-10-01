import React, { useState, useRef } from 'react';
import { api } from '../services/api';
import type { ContractReport } from '../types';
import { ClauseCard } from '../components/contract/ClauseCard';
import { ShieldCheck, UploadCloud, FileText, AlertTriangle, AlertCircle, CheckCircle, ArrowRight, Loader2, RefreshCw, Circle, Check } from 'lucide-react';

const LOADING_STEPS = [
  { id: 1, text: "Đã tải lên hợp đồng an toàn" },
  { id: 2, text: "Đang trích xuất văn bản và bóc tách" },
  { id: 3, text: "AI đang phân tích Chain-of-Thought" },
  { id: 4, text: "Đang đánh giá rủi ro pháp lý" }
];

export const ContractAnalysisPage: React.FC = () => {
  const [isDragging, setIsDragging] = useState(false);
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [loadingStep, setLoadingStep] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const [report, setReport] = useState<ContractReport | null>(null);

  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);

    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      validateAndSetFile(e.dataTransfer.files[0]);
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      validateAndSetFile(e.target.files[0]);
    }
  };

  const validateAndSetFile = (selectedFile: File) => {
    setError(null);
    const validTypes = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'text/plain'];

    if (!validTypes.includes(selectedFile.type) && !selectedFile.name.endsWith('.docx') && !selectedFile.name.endsWith('.pdf') && !selectedFile.name.endsWith('.txt')) {
      setError('Định dạng file không hỗ trợ. Vui lòng chọn PDF, DOCX hoặc TXT.');
      return;
    }

    if (selectedFile.size > 5 * 1024 * 1024) {
      setError('File quá lớn. Vui lòng chọn file dưới 5MB.');
      return;
    }

    setFile(selectedFile);
    setReport(null);
  };

  const handleAnalyze = async () => {
    if (!file) return;

    setLoading(true);
    setLoadingStep(1);
    setError(null);

    // Fake progress to improve UX
    const timers = [
      setTimeout(() => setLoadingStep(2), 1500),
      setTimeout(() => setLoadingStep(3), 4500),
      setTimeout(() => setLoadingStep(4), 9500),
    ];

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await api.post<ContractReport>('/contract/analyze', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });
      setReport(response.data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Có lỗi xảy ra khi phân tích hợp đồng. Vui lòng thử lại.');
    } finally {
      timers.forEach(clearTimeout);
      setLoading(false);
      setLoadingStep(0);
    }
  };

  // Tính toán thống kê
  const highRiskCount = report?.analyses.filter(a => a.risk_level === 'high').length || 0;
  const mediumRiskCount = report?.analyses.filter(a => a.risk_level === 'medium').length || 0;
  const lowRiskCount = report?.analyses.filter(a => a.risk_level === 'low').length || 0;

  return (
    <div className="w-full min-h-[calc(100vh-80px)] flex justify-center">
      <div className="w-full max-w-5xl px-6 py-12 fade-in relative">
        {/* Ambient background glow */}
        <div className="absolute top-0 left-1/2 -translate-x-1/2 w-full max-w-3xl h-64 bg-indigo-600/10 rounded-full blur-[100px] pointer-events-none -z-10" />

        {/* Header */}
        <div className="mb-14 text-center">
          <div className="inline-flex items-center justify-center p-3 bg-indigo-500/10 rounded-2xl border border-indigo-500/20 mb-6 shadow-[0_0_30px_rgba(99,102,241,0.15)]">
            <ShieldCheck className="w-8 h-8 text-indigo-400" />
          </div>
          <h1 className="text-3xl md:text-4xl font-bold tracking-tight text-white mb-4">
            Phân Tích Hợp Đồng{" "}
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-indigo-400 to-cyan-400">
              Thông Minh
            </span>
          </h1>
          <p className="text-gray-400 text-base max-w-xl mx-auto leading-relaxed">
            Tự động bóc tách và phân tích rủi ro pháp lý theo từng điều khoản bằng công nghệ AI Chain-of-Thought
          </p>
        </div>

        {!report && (
          <div className="w-full max-w-3xl mx-auto flex flex-col items-center">
            {/* Vùng upload */}
            <div
              className={`glass-card relative w-full rounded-2xl p-6 md:p-8 transition-all duration-500 ${
                loading ? "opacity-50 pointer-events-none scale-[0.98]" : ""
              }`}
            >
              <div
                className={`w-full min-h-[300px] border-2 border-dashed rounded-2xl p-8 md:p-12 transition-all duration-500 flex flex-col items-center justify-center text-center ${
                  isDragging
                    ? "border-indigo-500 bg-indigo-500/10 scale-[1.01]"
                    : "border-white/10 hover:border-indigo-500/40 bg-white/[0.01]"
                }`}
                onDragOver={handleDragOver}
                onDragLeave={handleDragLeave}
                onDrop={handleDrop}
              >
                <input
                  type="file"
                  ref={fileInputRef}
                  className="hidden"
                  onChange={handleFileChange}
                  accept=".pdf,.docx,.txt"
                />

                <div
                  className={`w-20 h-20 rounded-full flex items-center justify-center mb-6 transition-all duration-500 ${
                    isDragging
                      ? "bg-indigo-500 text-white shadow-[0_0_30px_rgba(99,102,241,0.5)] scale-110"
                      : "bg-white/5 text-indigo-400"
                  }`}
                >
                  <UploadCloud className="w-10 h-10" />
                </div>

                {file ? (
                  <div className="mb-8 flex flex-col items-center w-full">
                    <div className="flex items-center justify-center gap-4 bg-white/5 px-6 py-4 rounded-2xl border border-white/10 w-full max-w-md">
                      <FileText className="w-7 h-7 text-indigo-400 shrink-0" />
                      <span className="text-white font-semibold text-lg truncate">{file.name}</span>
                    </div>
                    <p className="text-gray-400 text-sm mt-3">
                      Dung lượng: {(file.size / 1024 / 1024).toFixed(2)} MB
                    </p>
                  </div>
                ) : (
                  <div className="mb-8">
                    <h3 className="text-2xl text-white font-bold mb-2 tracking-tight">
                      Kéo thả hợp đồng vào đây
                    </h3>
                    <p className="text-gray-400 mb-6 text-base">
                      hoặc duyệt file từ máy tính của bạn
                    </p>
                    <div className="flex flex-wrap items-center justify-center gap-6 text-sm font-medium text-gray-500">
                      <span className="flex items-center gap-2">
                        <CheckCircle className="w-4 h-4 text-emerald-500/70" /> PDF, DOCX, TXT
                      </span>
                      <span className="flex items-center gap-2">
                        <CheckCircle className="w-4 h-4 text-emerald-500/70" /> Tối đa 5MB
                      </span>
                    </div>
                  </div>
                )}

                <button
                  className={`px-10 py-3.5 rounded-xl text-base font-semibold transition-all duration-300 ${
                    file
                      ? "bg-transparent border border-white/20 text-gray-300 hover:bg-white/10"
                      : "bg-indigo-500 text-white hover:bg-indigo-600 shadow-[0_4px_20px_rgba(99,102,241,0.3)] hover:-translate-y-0.5"
                  }`}
                  onClick={() => fileInputRef.current?.click()}
                >
                  {file ? "Đổi file khác" : "Duyệt File"}
                </button>
              </div>
            </div>

            {/* Báo lỗi */}
            {error && (
              <div className="mt-6 w-full p-4 bg-red-500/10 border border-red-500/30 rounded-xl flex items-center justify-center gap-3 animate-in fade-in duration-300">
                <AlertTriangle className="w-5 h-5 text-red-500 shrink-0" />
                <p className="text-red-400 text-base font-medium">{error}</p>
              </div>
            )}

            {/* Action / Loading */}
            <div className="w-full mt-8">
              {loading ? (
                <div className="glass-card p-8 rounded-2xl border-indigo-500/30 bg-[#0f1626]/80 flex flex-col gap-5 animate-in slide-in-from-bottom-4 fade-in duration-500 shadow-[0_10px_40px_rgba(99,102,241,0.15)]">
                  <h4 className="text-white font-bold text-lg mb-2 flex items-center gap-3">
                    <Loader2 className="w-5 h-5 text-indigo-400 animate-spin" />
                    Hệ thống đang xử lý...
                  </h4>

                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                    {LOADING_STEPS.map((step) => {
                      const isCompleted = loadingStep > step.id;
                      const isActive = loadingStep === step.id;

                      return (
                        <div
                          key={step.id}
                          className={`flex items-center gap-3 p-3 rounded-xl border transition-all duration-500 ${
                            isCompleted ? 'bg-emerald-500/5 border-emerald-500/20' :
                            isActive ? 'bg-indigo-500/10 border-indigo-500/30 shadow-[0_0_15px_rgba(99,102,241,0.15)]' :
                            'bg-white/5 border-white/5 opacity-50'
                          }`}
                        >
                          <div className="shrink-0">
                            {isCompleted ? (
                              <div className="w-6 h-6 rounded-full bg-emerald-500/20 flex items-center justify-center">
                                <Check className="w-3.5 h-3.5 text-emerald-400" />
                              </div>
                            ) : isActive ? (
                              <div className="w-6 h-6 rounded-full bg-indigo-500/20 flex items-center justify-center">
                                <Loader2 className="w-3.5 h-3.5 text-indigo-400 animate-spin" />
                              </div>
                            ) : (
                              <div className="w-6 h-6 rounded-full border border-gray-600 flex items-center justify-center">
                                <Circle className="w-3.5 h-3.5 text-gray-600 opacity-0" />
                              </div>
                            )}
                          </div>
                          <span className={`text-sm font-medium ${
                            isCompleted ? 'text-emerald-400' :
                            isActive ? 'text-indigo-300' :
                            'text-gray-500'
                          }`}>
                            {step.text}
                          </span>
                        </div>
                      );
                    })}
                  </div>
                </div>
              ) : (
                file && (
                  <button
                    className="w-full py-5 text-xl font-bold rounded-2xl flex items-center justify-center gap-3 transition-all duration-300 bg-gradient-to-r from-indigo-500 to-cyan-500 text-white shadow-[0_8px_30px_rgba(99,102,241,0.3)] hover:shadow-[0_12px_40px_rgba(99,102,241,0.5)] hover:-translate-y-1 border border-indigo-400/20 animate-in fade-in slide-in-from-bottom-4"
                    onClick={handleAnalyze}
                  >
                    Bắt Đầu Quét Rủi Ro <ArrowRight className="w-6 h-6" />
                  </button>
                )
              )}
            </div>
          </div>
        )}

        {/* Kết quả phân tích */}
        {report && (
          <div className="fade-in">
            {/* Header Dashboard Card */}
            <div className="glass-card p-8 mb-8 relative overflow-hidden flex flex-col lg:flex-row gap-8 justify-between items-start lg:items-center">
              {/* Background pattern */}
              <div className="absolute right-0 top-0 w-1/2 h-full bg-gradient-to-l from-indigo-500/5 to-transparent pointer-events-none" />

              <div className="relative z-10">
                <div className="inline-flex items-center gap-2 px-3 py-1 bg-white/5 border border-white/10 rounded-full mb-4">
                  <FileText className="w-4 h-4 text-gray-400" />
                  <span className="text-xs font-medium text-gray-300">Báo cáo phân tích</span>
                </div>
                <h2 className="text-2xl font-bold text-white mb-2">{report.filename}</h2>
                <p className="text-gray-400 text-sm flex items-center gap-2">
                  Đã quét tổng cộng <strong className="text-white">{report.total_clauses}</strong> điều khoản
                </p>
              </div>

              <div className="flex flex-wrap gap-4 relative z-10">
                <div className="flex items-center gap-4 bg-[#080c14]/80 p-4 rounded-xl border border-red-500/20 shadow-[inset_0_1px_0_rgba(255,255,255,0.05),0_0_15px_rgba(239,68,68,0.1)]">
                  <div className="w-12 h-12 rounded-full bg-red-500/10 flex items-center justify-center">
                    <AlertTriangle className="w-6 h-6 text-red-500" />
                  </div>
                  <div>
                    <span className="block text-3xl font-bold text-white">{highRiskCount}</span>
                    <span className="text-xs text-red-400 uppercase tracking-wider font-semibold">Rủi ro cao</span>
                  </div>
                </div>

                <div className="flex items-center gap-4 bg-[#080c14]/80 p-4 rounded-xl border border-yellow-500/20 shadow-[inset_0_1px_0_rgba(255,255,255,0.05)]">
                  <div className="w-12 h-12 rounded-full bg-yellow-500/10 flex items-center justify-center">
                    <AlertCircle className="w-6 h-6 text-yellow-500" />
                  </div>
                  <div>
                    <span className="block text-3xl font-bold text-white">{mediumRiskCount}</span>
                    <span className="text-xs text-yellow-400 uppercase tracking-wider font-semibold">Rủi ro TB</span>
                  </div>
                </div>

                <div className="flex items-center gap-4 bg-[#080c14]/80 p-4 rounded-xl border border-emerald-500/20 shadow-[inset_0_1px_0_rgba(255,255,255,0.05)]">
                  <div className="w-12 h-12 rounded-full bg-emerald-500/10 flex items-center justify-center">
                    <CheckCircle className="w-6 h-6 text-emerald-500" />
                  </div>
                  <div>
                    <span className="block text-3xl font-bold text-white">{lowRiskCount}</span>
                    <span className="text-xs text-emerald-400 uppercase tracking-wider font-semibold">An toàn</span>
                  </div>
                </div>
              </div>
            </div>

            <div className="flex items-center justify-between mb-6">
              <h3 className="text-xl font-bold text-white flex items-center gap-2">
                Chi tiết điều khoản
              </h3>
              <button
                className="flex items-center gap-2 px-4 py-2 bg-white/5 hover:bg-white/10 border border-white/10 rounded-lg text-sm font-medium transition-colors"
                onClick={() => setReport(null)}
              >
                <RefreshCw className="w-4 h-4 text-gray-400" /> Quét file khác
              </button>
            </div>

            <div className="space-y-4">
              {report.analyses.map((analysis, index) => (
                <ClauseCard key={index} analysis={analysis} />
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
