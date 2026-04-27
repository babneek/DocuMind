import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({ baseURL: API_BASE });

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

// ── Types ────────────────────────────────────────────────────────────────────

export interface LoginData { email: string; password: string; }
export interface SignupData { email: string; password: string; }
export interface AuthResponse { access_token: string; token_type: string; }

export interface Document {
  id: number;
  user_id: number;
  file_name: string;
  file_type: string;
  status: string;
  upload_date: string;
  pageindex_doc_id?: string;
}

export interface Note {
  id: number;
  title: string;
  content: string;
  created_at: string;
  updated_at: string;
}

export interface QueryRequest { query: string; doc_id?: number; }

export interface LegalSource {
  type: 'document' | 'general_knowledge';
  mode?: 'semantic' | 'structural';
  doc_id?: number;
  chunk_index?: number;
  relevance_score?: number;
  note?: string;
}

export interface LegalQueryResponse {
  answer: string;
  sources: LegalSource[];
  context_used: boolean;
  context_blocks?: number;
}

export interface LegalSummaryResponse {
  summary: string;
  doc_name: string;
}

export interface ClauseResponse {
  result: string;
  clause_type: string;
  doc_name: string;
}

export interface RiskResponse {
  analysis: string;
  doc_name: string;
}

export interface CompareResponse {
  comparison: string;
  doc1: string;
  doc2: string;
}

// ── Case Law Types ───────────────────────────────────────────────────────────

export interface CaseLawStats {
  total_cases: number;
  courts: string[];
  legal_areas: string[];
  categories: Record<string, number>;
  importance_distribution: {
    Landmark: number;
    Important: number;
    Regular: number;
  };
  last_updated: string;
}

export interface CaseLawCase {
  case_id: string;
  case_name: string;
  citation: string;
  court: string;
  date: string;
  category: string;
  subcategory: string;
  importance: string;
  legal_areas: string[];
  issues: string[];
  holdings: string[];
  relevance_score: number;
  excerpt: string;
}

export interface CaseLawSearchRequest {
  query: string;
  legal_area?: string;
  court?: string;
  category?: string;
  importance?: string;
  top_k?: number;
}

export interface CaseLawSearchResponse {
  message: string;
  cases: CaseLawCase[];
  query: string;
  filters?: {
    legal_area?: string;
    court?: string;
    category?: string;
  };
}

export interface CaseImportRequest {
  mode: 'foundation' | 'domain';
  domain?: string;
}

export interface CaseImportResponse {
  message: string;
  note: string;
  mode: string;
  domain?: string;
  cases_count: number;
}

export interface DomainInfo {
  name: string;
  case_count: number;
  sample_cases: string[];
}

export interface AvailableDomainsResponse {
  domains: DomainInfo[];
  total_domains: number;
}

// ── Auth ─────────────────────────────────────────────────────────────────────

export const login = async (data: LoginData): Promise<AuthResponse> => {
  const formData = new URLSearchParams();
  formData.append('username', data.email);
  formData.append('password', data.password);
  const res = await api.post('/api/auth/login', formData, {
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
  });
  return res.data;
};

export const signup = async (data: SignupData): Promise<AuthResponse> => {
  const res = await api.post('/api/auth/signup', data);
  return res.data;
};

// ── Documents ────────────────────────────────────────────────────────────────

export const getDocuments = async (): Promise<Document[]> => {
  const res = await api.get('/api/documents/');
  return res.data;
};

export const deleteDocument = async (docId: number): Promise<void> => {
  await api.delete(`/api/documents/${docId}`);
};

export const uploadDocument = async (file: File): Promise<{ id: number; filename: string; status: string }> => {
  const formData = new FormData();
  formData.append('file', file);
  const res = await api.post('/api/upload/', formData);
  return res.data;
};

// ── Legal Query Endpoints ────────────────────────────────────────────────────

export const askLegalQuestion = async (data: QueryRequest): Promise<LegalQueryResponse> => {
  const res = await api.post('/api/query/ask', data);
  return res.data;
};

export const summarizeDocument = async (docId: number): Promise<LegalSummaryResponse> => {
  const res = await api.post('/api/query/summarize', { doc_id: docId });
  return res.data;
};

export const extractClause = async (docId: number, clauseType: string): Promise<ClauseResponse> => {
  const res = await api.post('/api/query/extract-clause', { doc_id: docId, clause_type: clauseType });
  return res.data;
};

export const analyzeRisks = async (docId: number): Promise<RiskResponse> => {
  const res = await api.post('/api/query/analyze-risks', { doc_id: docId });
  return res.data;
};

export const compareDocuments = async (docId1: number, docId2: number): Promise<CompareResponse> => {
  const res = await api.post('/api/query/compare', { doc_id_1: docId1, doc_id_2: docId2 });
  return res.data;
};

// ── Notes ────────────────────────────────────────────────────────────────────

export const getNotes = async (): Promise<Note[]> => {
  const res = await api.get('/api/notes/');
  return res.data;
};

export const createNote = async (data: Pick<Note, 'title' | 'content'>): Promise<Note> => {
  const res = await api.post('/api/notes/', data);
  return res.data;
};

export const updateNote = async (noteId: number, data: Pick<Note, 'title' | 'content'>): Promise<Note> => {
  const res = await api.put(`/api/notes/${noteId}`, data);
  return res.data;
};

export const deleteNote = async (noteId: number): Promise<void> => {
  await api.delete(`/api/notes/${noteId}`);
};

export const restructureNote = async (noteId: number, options?: {
  structureType?: string; customSections?: string; style?: string;
}): Promise<Note> => {
  const res = await api.post(`/api/notes/${noteId}/restructure`, options || {});
  return res.data;
};

export const extractStructure = async (noteId: number): Promise<any> => {
  const res = await api.get(`/api/notes/${noteId}/structure`);
  return res.data;
};

export const rebuildNote = async (noteId: number, sections: any[]): Promise<Note> => {
  const res = await api.post(`/api/notes/${noteId}/rebuild`, { sections });
  return res.data;
};

// legacy alias
export const askQuestion = askLegalQuestion;

// ── Case Law Admin Endpoints ─────────────────────────────────────────────────

export const getCaseLawStats = async (): Promise<CaseLawStats> => {
  const res = await api.get('/api/query/case-law-stats');
  return res.data;
};

export const searchCaseLaw = async (data: CaseLawSearchRequest): Promise<CaseLawSearchResponse> => {
  const res = await api.post('/api/query/search-case-law', data);
  return res.data;
};

export const getCaseDetails = async (caseId: string): Promise<{ case: any; case_id: string }> => {
  const res = await api.get(`/api/query/case-law/${caseId}`);
  return res.data;
};

export const triggerCaseImport = async (data: CaseImportRequest): Promise<CaseImportResponse> => {
  const res = await api.post('/api/query/admin/import-cases', null, {
    params: { mode: data.mode, domain: data.domain }
  });
  return res.data;
};

export const getAvailableDomains = async (): Promise<AvailableDomainsResponse> => {
  const res = await api.get('/api/query/admin/available-domains');
  return res.data;
};

export default api;
