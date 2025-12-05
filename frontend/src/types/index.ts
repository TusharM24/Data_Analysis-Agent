// API Types

export interface ColumnInfo {
  name: string;
  dtype: string;
  non_null_count: number;
  null_count: number;
  unique_count: number;
  sample_values: unknown[];
}

export interface DatasetSummary {
  filename: string;
  shape: [number, number];
  columns: ColumnInfo[];
  numerical_columns: string[];
  categorical_columns: string[];
  datetime_columns: string[];
  missing_values: Record<string, number>;
  memory_usage: string;
  head_preview: Record<string, unknown>[];
}

// Dataset Versioning Types

export interface DatasetVersion {
  version_id: string;
  version_number: number;
  file_path: string;
  summary: DatasetSummary;
  change_description: string;
  created_at: string;
  // Frontend-only field for user-customizable display name
  displayName?: string;
}

export interface VersionListResponse {
  versions: DatasetVersion[];
  current_version_id: string;
}

export interface SwitchVersionResponse {
  success: boolean;
  current_version: DatasetVersion;
  message: string;
}

export interface UploadResponse {
  session_id: string;
  summary: DatasetSummary;
  message: string;
  version?: DatasetVersion;
}

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  code?: string;
  plots?: string[];
  timestamp: Date;
  isLoading?: boolean;
}

export interface ChatResponse {
  response: string;
  code?: string;
  plots: string[];
  execution_result?: Record<string, unknown>;
  error?: string;
  new_version?: DatasetVersion;
}

export interface SessionInfo {
  session_id: string;
  dataset_filename: string;
  created_at: string;
  message_count: number;
  summary?: DatasetSummary;
  version_count?: number;
  current_version_id?: string;
}

// UI State Types

export interface AppState {
  sessionId: string | null;
  summary: DatasetSummary | null;
  messages: ChatMessage[];
  isLoading: boolean;
  error: string | null;
}

// Version display name storage (frontend only)
export interface VersionDisplayNames {
  [versionId: string]: string;
}
