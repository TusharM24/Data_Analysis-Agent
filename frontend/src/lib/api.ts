import axios from 'axios';
import type { 
  UploadResponse, 
  ChatResponse, 
  SessionInfo, 
  VersionListResponse, 
  SwitchVersionResponse 
} from '../types';

// Use environment variable for API URL, fallback to local development
const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';
const API_PREFIX = '/api';

const api = axios.create({
  baseURL: `${API_BASE}${API_PREFIX}`,
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
  version_count: number;
  current_version_id: string;
}> {
  const response = await api.get(`/history/${sessionId}`);
  return response.data;
}

export async function clearHistory(sessionId: string): Promise<void> {
  await api.post(`/clear/${sessionId}`);
}

// ==================== Version Management ====================

// Get all versions for a session
export async function getVersions(sessionId: string): Promise<VersionListResponse> {
  const response = await api.get<VersionListResponse>(`/versions/${sessionId}`);
  return response.data;
}

// Switch to a different version
export async function switchVersion(
  sessionId: string, 
  versionId: string
): Promise<SwitchVersionResponse> {
  const response = await api.post<SwitchVersionResponse>('/switch-version', {
    session_id: sessionId,
    version_id: versionId,
  });
  return response.data;
}

// ==================== Utilities ====================

// Get plot URL
export function getPlotUrl(plotPath: string): string {
  // If it's already a full URL, return as is
  if (plotPath.startsWith('http://') || plotPath.startsWith('https://')) {
    return plotPath;
  }
  // If it starts with /api/, prepend the base URL
  if (plotPath.startsWith('/api/')) {
    return `${API_BASE}${plotPath}`;
  }
  // Otherwise, construct the full URL
  return `${API_BASE}${API_PREFIX}${plotPath}`;
}
