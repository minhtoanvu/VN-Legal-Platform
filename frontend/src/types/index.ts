// ===== Auth =====
export interface User {
  id: string;
  email: string;
  full_name: string;
  role: 'admin' | 'user';
  organization_id: string | null;
  created_at: string;
}

export interface AuthTokens {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

// ===== Documents =====
export type DocumentStatus = 'active' | 'expired' | 'amended';
export type DocumentType =
  | 'Thông tư'
  | 'Nghị định'
  | 'Quyết định'
  | 'Luật'
  | 'Nghị quyết'
  | 'Thông tư liên tịch'
  | 'Pháp lệnh'
  | 'Hiến pháp'
  | string;

export interface DocumentListItem {
  id: string;
  title: string;
  doc_number: string;
  doc_type: DocumentType;
  issuing_body: string;
  issue_date: string | null;
  effective_date: string | null;
  status: DocumentStatus;
  excerpt?: string;
  content_snippet?: string;
  score?: number;
}

export interface DocumentRelation {
  id: string;
  relation_type: 'guides' | 'amends' | 'replaces' | 'revokes' | 'cites';
  related_doc_id: string;
  related_doc_title: string;
  related_doc_number: string;
  direction: 'outgoing' | 'incoming';
}

export interface DocumentDetail extends DocumentListItem {
  content_summary: string | null;
  content: string | null;
  expiry_date: string | null;
  relations: DocumentRelation[];
  chunks_count: number;
}

export interface TimelineEvent {
  date: string;
  event_type: string;
  description: string;
  related_doc_id?: string;
  related_doc_title?: string;
}

// ===== Search =====
export type SearchMode = 'keyword' | 'semantic' | 'hybrid';

export interface SearchFilters {
  doc_type?: string;
  status?: DocumentStatus;
  year_from?: number;
  year_to?: number;
}

export interface SearchRequest {
  query: string;
  mode: SearchMode;
  limit?: number;
  offset?: number;
  filters?: SearchFilters;
}

export interface SearchResult extends DocumentListItem {
  chunk_text?: string;
  rrf_score?: number;
}

export interface SearchResponse {
  results: SearchResult[];
  total: number;
  query: string;
  mode: SearchMode;
  duration_ms: number;
}

// ===== AI Chat =====
export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  sources?: DocumentListItem[];
  timestamp: Date;
  isStreaming?: boolean;
}

export interface ChatRequest {
  query: string;
  session_id?: string;
  context_doc_ids?: string[];
}

// ===== Knowledge Graph =====
export interface GraphNode {
  id: string;
  label: string;
  doc_type: DocumentType;
  status: DocumentStatus;
  is_center?: boolean;
}

export interface GraphEdge {
  id: string;
  from: string;
  to: string;
  relation_type: 'guides' | 'amends' | 'replaces' | 'revokes' | 'cites';
  label: string;
}

export interface GraphData {
  nodes: GraphNode[];
  edges: GraphEdge[];
  center_doc_id: string;
}

// ===== Analytics =====
export interface AnalyticsDashboard {
  kpi: {
    total_documents: number;
    total_queries: number;
    new_docs_30d: number;
  };
  documents_by_field: { field: string; count: number }[];
  documents_by_type: { doc_type: string; count: number }[];
  documents_by_status: { status: string; count: number }[];
  documents_by_year: { year: number; count: number }[];
  top_query_types: { query_type: string; count: number }[];
  top_issuing_bodies: { issuing_body: string; count: number }[];
  recent_queries?: {
    query: string;
    mode: SearchMode;
    result_count: number;
    duration_ms: number;
    created_at: string;
  }[];
  avg_query_duration_ms?: number;
}

// ===== Workspace =====
export interface Collection {
  id: string;
  name: string;
  description: string | null;
  is_shared: boolean;
  doc_count: number;
}

export interface CollectionCreate {
  name: string;
  description?: string;
  is_shared?: boolean;
}

export interface DocInCollection {
  id: string;
  title: string;
  doc_number: string;
  doc_type: DocumentType | null;
  issuing_body: string | null;
  status: DocumentStatus | null;
}

export interface Note {
  id: string;
  doc_id: string;
  content: string;
}

// ===== Contract Analysis =====
export interface CitationInfo {
  doc_number: string;
  title: string;
  snippet: string;
}

export interface ClauseAnalysis {
  clause_title: string;
  clause_text: string;
  step1_identification: string;
  step2_legal_comparison: string;
  step3_risk_evaluation: string;
  step4_suggestion: string;
  risk_score: number;
  risk_level: 'low' | 'medium' | 'high';
  citations: CitationInfo[];
  is_reflected: boolean;
}

export interface ContractReport {
  filename: string;
  total_clauses: number;
  analyses: ClauseAnalysis[];
}

