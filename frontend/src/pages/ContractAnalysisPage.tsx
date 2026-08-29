import React, { useState, useRef } from 'react';
import { api } from '../services/api';
import type { ContractReport } from '../types';
import { ClauseCard } from '../components/contract/ClauseCard';

export const ContractAnalysisPage: React.FC = () => {
  const [isDragging, setIsDragging] = useState(false);
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
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
      const droppedFile = e.dataTransfer.files[0];
      validateAndSetFile(droppedFile);
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
    setError(null);
    
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
      setLoading(false);
    }
  };

  // Tính toán thống kê
  const highRiskCount = report?.analyses.filter(a => a.risk_level === 'high').length || 0;
  const mediumRiskCount = report?.analyses.filter(a => a.risk_level === 'medium').length || 0;
  const lowRiskCount = report?.analyses.filter(a => a.risk_level === 'low').length || 0;

  return (
    <div className="container mx-auto px-4 py-8 max-w-5xl fade-in">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gradient-primary mb-2">Smart Contract Analysis</h1>
        <p className="text-gray-400">Phân tích rủi ro pháp lý hợp đồng tự động bằng AI (RAG + Chain-of-Thought)</p>
      </div>

      {!report && (
        <div className="glass-card p-8 text-center">
          <div 
            className={`border-2 border-dashed rounded-lg p-12 transition-colors duration-300 ${
              isDragging ? 'border-primary bg-primary-glow' : 'border-gray-700 hover:border-gray-500'
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
            
            <div className="flex flex-col items-center justify-center">
              <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1" strokeLinecap="round" strokeLinejoin="round" className="text-gray-500 mb-4">
                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                <polyline points="14 2 14 8 20 8"></polyline>
                <line x1="12" y1="18" x2="12" y2="12"></line>
                <line x1="9" y1="15" x2="15" y2="15"></line>
              </svg>
              
              {file ? (
                <div className="mb-4">
                  <p className="text-white font-medium text-lg">{file.name}</p>
                  <p className="text-gray-400 text-sm">{(file.size / 1024 / 1024).toFixed(2)} MB</p>
                </div>
              ) : (
                <>
                  <p className="text-gray-300 font-medium mb-2">Kéo thả file hợp đồng vào đây</p>
                  <p className="text-gray-500 text-sm mb-6">Hỗ trợ định dạng: PDF, DOCX, TXT (Tối đa 5MB)</p>
                </>
              )}
              
              <button 
                className="btn btn-outline"
                onClick={() => fileInputRef.current?.click()}
              >
                {file ? 'Chọn file khác' : 'Chọn file từ máy tính'}
              </button>
            </div>
          </div>

          {error && (
            <div className="mt-4 p-3 bg-red-500/10 border border-red-500/30 rounded text-red-500 text-sm">
              {error}
            </div>
          )}

          <div className="mt-8">
            <button 
              className="btn btn-primary w-full py-3 text-lg"
              disabled={!file || loading}
              onClick={handleAnalyze}
            >
              {loading ? (
                <>
                  <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  Hệ thống đang trích xuất và AI đang phân tích (có thể mất 10-30s)...
                </>
              ) : 'Bắt Đầu Phân Tích Rủi Ro'}
            </button>
          </div>
        </div>
      )}

      {/* Kết quả phân tích */}
      {report && (
        <div className="fade-in">
          <div className="glass-card p-6 mb-6 flex flex-wrap gap-6 justify-between items-center">
            <div>
              <h2 className="text-xl font-bold text-white">{report.filename}</h2>
              <p className="text-gray-400 text-sm mt-1">Đã phân tích {report.total_clauses} điều khoản</p>
            </div>
            
            <div className="flex gap-4">
              <div className="bg-red-500/10 border border-red-500/20 px-4 py-2 rounded-lg text-center">
                <span className="block text-2xl font-bold text-red-500">{highRiskCount}</span>
                <span className="text-xs text-gray-400 uppercase">Rủi ro cao</span>
              </div>
              <div className="bg-yellow-500/10 border border-yellow-500/20 px-4 py-2 rounded-lg text-center">
                <span className="block text-2xl font-bold text-yellow-500">{mediumRiskCount}</span>
                <span className="text-xs text-gray-400 uppercase">Rủi ro TB</span>
              </div>
              <div className="bg-emerald-500/10 border border-emerald-500/20 px-4 py-2 rounded-lg text-center">
                <span className="block text-2xl font-bold text-emerald-500">{lowRiskCount}</span>
                <span className="text-xs text-gray-400 uppercase">An toàn</span>
              </div>
            </div>
            
            <button className="btn btn-outline" onClick={() => setReport(null)}>
              Phân tích file khác
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
  );
};
