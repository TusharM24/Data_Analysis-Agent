import axios from 'axios';
import type { UploadResponse, ChatResponse, SessionInfo } from '../types';

const API_BASE = '/api';

const api = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
});

// File upload
export async function uploadFile(file: File): Promise<UploadResponse> {
  const formData = new FormData();
  formData.append('file', file);

  const response = await api.post<UploadResponse>('/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });

  return response.data;
}

// Chat
export async function sendMessage(sessionId: string, message: string): Promise<ChatResponse> {
  const response = await api.post<ChatResponse>('/chat', {
    session_id: sessionId,
    message,
  });

  return response.data;
}

// Sessions
export async function getSessions(): Promise<{ sessions: SessionInfo[] }> {
  const response = await api.get<{ sessions: SessionInfo[] }>('/sessions');
  return response.data;
}

export async function getSession(sessionId: string): Promise<SessionInfo> {
  const response = await api.get<SessionInfo>(`/session/${sessionId}`);
  return response.data;
}

export async function deleteSession(sessionId: string): Promise<void> {
  await api.delete(`/session/${sessionId}`);
}

// Chat history
export async function getChatHistory(sessionId: string): Promise<{
  session_id: string;
  messages: Array<{ role: string; content: string }>;
  code_history: string[];
  plots: string[];
}> {
  const response = await api.get(`/history/${sessionId}`);
  return response.data;
}

export async function clearHistory(sessionId: string): Promise<void> {
  await api.post(`/clear/${sessionId}`);
}

// Get plot URL
export function getPlotUrl(plotPath: string): string {
  if (plotPath.startsWith('/api/')) {
    return plotPath;
  }
  return `${API_BASE}${plotPath}`;
}

