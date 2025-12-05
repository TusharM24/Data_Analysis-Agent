"""Session management service with dataset versioning."""
import uuid
import os
from datetime import datetime
from typing import Dict, Optional, List, Any
from dataclasses import dataclass, field
import pandas as pd
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage


@dataclass
class DatasetVersion:
    """Represents a version of the dataset."""
    version_id: str
    version_number: int
    file_path: str
    summary: Dict[str, Any]
    change_description: str
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API responses."""
        return {
            'version_id': self.version_id,
            'version_number': self.version_number,
            'file_path': self.file_path,
            'summary': self.summary,
            'change_description': self.change_description,
            'created_at': self.created_at.isoformat()
        }


@dataclass
class Session:
    """Represents a user session with dataset versioning and conversation history."""
    session_id: str
    dataset_filename: str
    created_at: datetime = field(default_factory=datetime.utcnow)
    messages: List[BaseMessage] = field(default_factory=list)
    code_history: List[str] = field(default_factory=list)
    plots: List[str] = field(default_factory=list)
    
    # Versioning
    versions: List[DatasetVersion] = field(default_factory=list)
    current_version_id: str = ""
    
    _dataframe: Optional[pd.DataFrame] = field(default=None, repr=False)
    
    # ==================== Version Management ====================
    
    def add_version(
        self, 
        file_path: str, 
        summary: Dict[str, Any], 
        change_description: str
    ) -> DatasetVersion:
        """Add a new dataset version."""
        version_number = len(self.versions) + 1
        version_id = str(uuid.uuid4())[:8]
        
        version = DatasetVersion(
            version_id=version_id,
            version_number=version_number,
            file_path=file_path,
            summary=summary,
            change_description=change_description
        )
        
        self.versions.append(version)
        self.current_version_id = version_id
        self._dataframe = None  # Reset cached dataframe
        
        return version
    
    def get_version(self, version_id: str) -> Optional[DatasetVersion]:
        """Get a specific version by ID."""
        for v in self.versions:
            if v.version_id == version_id:
                return v
        return None
    
    def get_current_version(self) -> Optional[DatasetVersion]:
        """Get the current active version."""
        return self.get_version(self.current_version_id)
    
    def switch_version(self, version_id: str) -> bool:
        """Switch to a different version."""
        version = self.get_version(version_id)
        if version:
            self.current_version_id = version_id
            self._dataframe = None  # Reset cached dataframe
            return True
        return False
    
    @property
    def dataset_path(self) -> str:
        """Get current version's file path."""
        current = self.get_current_version()
        return current.file_path if current else ""
    
    @property
    def summary(self) -> Dict[str, Any]:
        """Get current version's summary."""
        current = self.get_current_version()
        return current.summary if current else {}
    
    # ==================== Message Management ====================
    
    def add_user_message(self, content: str):
        """Add a user message to the conversation."""
        self.messages.append(HumanMessage(content=content))
    
    def add_assistant_message(self, content: str):
        """Add an assistant message to the conversation."""
        self.messages.append(AIMessage(content=content))
    
    def add_code(self, code: str):
        """Add executed code to history."""
        self.code_history.append(code)
        # Keep only last 10 code snippets
        self.code_history = self.code_history[-10:]
    
    def add_plot(self, plot_path: str):
        """Add a generated plot path."""
        self.plots.append(plot_path)
    
    def get_recent_messages(self, count: int = 10) -> List[BaseMessage]:
        """Get the most recent messages."""
        return self.messages[-count:]
    
    def get_recent_code(self, count: int = 5) -> List[str]:
        """Get the most recent code snippets."""
        return self.code_history[-count:]
    
    @property
    def dataframe(self) -> pd.DataFrame:
        """Lazy load the dataframe from current version."""
        if self._dataframe is None and self.dataset_path:
            self._dataframe = pd.read_csv(self.dataset_path)
        return self._dataframe
    
    def get_context_summary(self) -> str:
        """Generate a context summary for the LLM."""
        summary = self.summary
        current_version = self.get_current_version()
        version_info = f"v{current_version.version_number}" if current_version else "v1"
        
        context = f"""Dataset: {self.dataset_filename} ({version_info})
Shape: {summary.get('shape', 'Unknown')}
Columns: {', '.join([c['name'] for c in summary.get('columns', [])])}
Numerical columns: {', '.join(summary.get('numerical_columns', []))}
Categorical columns: {', '.join(summary.get('categorical_columns', []))}
Missing values: {sum(summary.get('missing_values', {}).values())} total across {len(summary.get('missing_values', {}))} columns
"""
        
        # Add version history context
        if len(self.versions) > 1:
            context += f"\nDataset has {len(self.versions)} versions. Currently using {version_info}.\n"
        
        # Add recent code context
        if self.code_history:
            context += "\nRecent code executed:\n"
            for i, code in enumerate(self.get_recent_code(3), 1):
                context += f"\n--- Code {i} ---\n{code[:500]}...\n" if len(code) > 500 else f"\n--- Code {i} ---\n{code}\n"
        
        return context


class SessionManager:
    """Manages user sessions in memory."""
    
    def __init__(self):
        self._sessions: Dict[str, Session] = {}
    
    def create_session(
        self, 
        dataset_path: str, 
        dataset_filename: str,
        summary: Dict[str, Any]
    ) -> Session:
        """Create a new session with initial dataset version."""
        session_id = str(uuid.uuid4())
        
        session = Session(
            session_id=session_id,
            dataset_filename=dataset_filename
        )
        
        # Add initial version (v1 - Original)
        session.add_version(
            file_path=dataset_path,
            summary=summary,
            change_description="Original upload"
        )
        
        self._sessions[session_id] = session
        return session
    
    def get_session(self, session_id: str) -> Optional[Session]:
        """Get a session by ID."""
        return self._sessions.get(session_id)
    
    def delete_session(self, session_id: str) -> bool:
        """Delete a session and its version files."""
        session = self._sessions.get(session_id)
        if session:
            # Clean up version files (except original which is in uploads)
            for version in session.versions[1:]:  # Skip v1 (original)
                if os.path.exists(version.file_path):
                    try:
                        os.remove(version.file_path)
                    except:
                        pass
            del self._sessions[session_id]
            return True
        return False
    
    def list_sessions(self) -> List[Dict[str, Any]]:
        """List all active sessions."""
        return [
            {
                'session_id': s.session_id,
                'dataset_filename': s.dataset_filename,
                'created_at': s.created_at.isoformat(),
                'message_count': len(s.messages),
                'version_count': len(s.versions),
                'current_version_id': s.current_version_id
            }
            for s in self._sessions.values()
        ]
    
    def cleanup_old_sessions(self, max_age_hours: int = 24):
        """Remove sessions older than max_age_hours."""
        now = datetime.utcnow()
        to_delete = []
        
        for session_id, session in self._sessions.items():
            age = (now - session.created_at).total_seconds() / 3600
            if age > max_age_hours:
                to_delete.append(session_id)
        
        for session_id in to_delete:
            self.delete_session(session_id)
        
        return len(to_delete)


# Global session manager instance
session_manager = SessionManager()
