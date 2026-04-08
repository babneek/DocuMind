import axios from 'axios';

const API_BASE = 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE,
});

// Add token to requests if available
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export interface LoginData {
  email: string;
  password: string;
}

export interface SignupData {
  email: string;
  password: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
}

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

export interface QueryRequest {
  query: string;
  doc_id?: number;
}

export interface QueryResponse {
  answer: string;
  sources?: Array<Record<string, unknown>>;
}

// Auth
export const login = async (data: LoginData): Promise<AuthResponse> => {
  const formData = new URLSearchParams();
  formData.append('username', data.email);
  formData.append('password', data.password);
  const response = await api.post('/api/auth/login', formData, {
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
  });
  return response.data;
};

export const signup = async (data: SignupData): Promise<AuthResponse> => {
  const response = await api.post('/api/auth/signup', data);
  return response.data;
};

// Documents
export const getDocuments = async (): Promise<Document[]> => {
  const response = await api.get('/api/documents/');
  return response.data;
};

export const deleteDocument = async (docId: number): Promise<void> => {
  await api.delete(`/api/documents/${docId}`);
};

// Summary
export const summarizeDocument = async (docId: number): Promise<{ summary: string }> => {
  const response = await api.post('/api/query/summarize', { doc_id: docId });
  return response.data;
};

// Upload
export const uploadDocument = async (file: File): Promise<{ id: number; filename: string; status: string }> => {
  const formData = new FormData();
  formData.append('file', file);
  console.log('[API] Uploading file:', file.name, 'Size:', file.size, 'Type:', file.type);
  const response = await api.post('/api/upload/', formData);
  console.log('[API] Upload response:', response.data);
  return response.data;
};

// Notes
export const getNotes = async (): Promise<Note[]> => {
  const response = await api.get('/api/notes/');
  return response.data;
};

export const createNote = async (data: Pick<Note, 'title' | 'content'>): Promise<Note> => {
  const response = await api.post('/api/notes/', data);
  return response.data;
};

export const updateNote = async (noteId: number, data: Pick<Note, 'title' | 'content'>): Promise<Note> => {
  const response = await api.put(`/api/notes/${noteId}`, data);
  return response.data;
};

export const deleteNote = async (noteId: number): Promise<void> => {
  await api.delete(`/api/notes/${noteId}`);
};

export const restructureNote = async (noteId: number, options?: { structureType?: string; customSections?: string; style?: string }): Promise<Note> => {
  const response = await api.post(`/api/notes/${noteId}/restructure`, options || {});
  return response.data;
};

export const extractStructure = async (noteId: number): Promise<any> => {
  const response = await api.get(`/api/notes/${noteId}/structure`);
  return response.data;
};

export const rebuildNote = async (noteId: number, sections: any[]): Promise<Note> => {
  const response = await api.post(`/api/notes/${noteId}/rebuild`, { sections });
  return response.data;
};

// Query
export const askQuestion = async (data: QueryRequest): Promise<QueryResponse> => {
  const response = await api.post('/api/query/ask', data);
  return response.data;
};

export default api;