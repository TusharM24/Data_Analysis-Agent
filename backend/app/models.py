"""Pydantic models for API requests and responses."""
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum


class MessageRole(str, Enum):
    """Message role enumeration."""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class ColumnInfo(BaseModel):
    """Information about a dataset column."""
    name: str
    dtype: str
    non_null_count: int
    null_count: int
    unique_count: int
    sample_values: List[Any]


class DatasetSummary(BaseModel):
    """Summary statistics for an uploaded dataset."""
    filename: str
    shape: tuple
    columns: List[ColumnInfo]
    numerical_columns: List[str]
    categorical_columns: List[str]
    datetime_columns: List[str]
    missing_values: Dict[str, int]
    memory_usage: str
    head_preview: List[Dict[str, Any]]


class DatasetVersion(BaseModel):
    """Represents a version of the dataset."""
    version_id: str
    version_number: int
    file_path: str
    summary: DatasetSummary
    change_description: str  # "Original upload" or "Removed nulls, added column X"
    created_at: datetime = Field(default_factory=datetime.utcnow)


class UploadResponse(BaseModel):
    """Response from file upload endpoint."""
    session_id: str
    summary: DatasetSummary
    message: str
    version: Optional[DatasetVersion] = None


class ChatMessage(BaseModel):
    """A single chat message."""
    role: MessageRole
    content: str
    code: Optional[str] = None
    plots: Optional[List[str]] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ChatRequest(BaseModel):
    """Request to the chat endpoint."""
    session_id: str
    message: str


class ChatResponse(BaseModel):
    """Response from the chat endpoint."""
    response: str
    code: Optional[str] = None
    plots: List[str] = []
    execution_result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    new_version: Optional[DatasetVersion] = None  # If a new version was created


class VersionListResponse(BaseModel):
    """Response for listing dataset versions."""
    versions: List[DatasetVersion]
    current_version_id: str


class SwitchVersionRequest(BaseModel):
    """Request to switch dataset version."""
    session_id: str
    version_id: str


class SwitchVersionResponse(BaseModel):
    """Response after switching version."""
    success: bool
    current_version: DatasetVersion
    message: str


class SessionInfo(BaseModel):
    """Information about a session."""
    session_id: str
    dataset_filename: str
    created_at: datetime
    message_count: int
    version_count: int = 1
    current_version_id: Optional[str] = None


class AgentState(BaseModel):
    """State passed through the LangGraph workflow."""
    messages: List[Dict[str, str]]
    dataset_info: Dict[str, Any]
    dataset_path: str
    session_id: str
    generated_code: Optional[str] = None
    execution_result: Optional[Dict[str, Any]] = None
    plots: List[str] = []
    error: Optional[str] = None
    new_version: Optional[Dict[str, Any]] = None  # If transformation created new version
    
    class Config:
        arbitrary_types_allowed = True
