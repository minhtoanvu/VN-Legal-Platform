import { useQuery } from '@tanstack/react-query';
import { api } from '../services/api';

export interface SearchResult {
  doc_id: string;
  doc_number: string;
  title: string;
  snippet: string;
  score: number;
  field?: string;
  status?: string;
}

interface SearchResponse {
  results: SearchResult[];
  total: number;
  mode: 'keyword' | 'semantic' | 'hybrid';
}

interface SearchParams {
  query: string;
  mode: 'keyword' | 'semantic' | 'hybrid';
  field?: string | null;
}

const fetchSearchResults = async (params: SearchParams): Promise<SearchResponse> => {
  if (!params.query.trim()) {
    return { results: [], total: 0, mode: params.mode };
  }

  const response = await api.post('/search', {
    query: params.query,
    mode: params.mode,
    field: params.field || null,
  });
  return response.data;
};

export const useSearch = (params: SearchParams) => {
  return useQuery<SearchResponse, Error>({
    queryKey: ['search', params.query, params.mode, params.field],
    queryFn: () => fetchSearchResults(params),
    enabled: params.query.trim().length > 0,
    staleTime: 5 * 60 * 1000,
    retry: 1,
  });
};
