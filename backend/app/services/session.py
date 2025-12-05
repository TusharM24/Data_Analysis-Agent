"""Session management service."""
import uuid
from datetime import datetime
from typing import Dict, Optional, List, Any
from dataclasses import dataclass, field
import pandas as pd
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage


@dataclass
class Session:
    """Represents a user session with dataset and conversation history."""
    session_id: str
    dataset_path: str
    dataset_filename: str
    summary: Dict[str, Any]
    created_at: datetime = field(default_factory=datetime.utcnow)
    messages: List[BaseMessage] = field(default_factory=list)
    code_history: List[str] = field(default_factory=list)
    plots: List[str] = field(default_factory=list)
    _dataframe: Optional[pd.DataFrame] = field(default=None, repr=False)
    
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
        """Lazy load the dataframe."""
        if self._dataframe is None:
            self._dataframe = pd.read_csv(self.dataset_path)
        return self._dataframe
    
    def get_context_summary(self) -> str:
        """Generate a context summary for the LLM."""
        summary = self.summary
        context = f"""Dataset: {self.dataset_filename}
Shape: {summary.get('shape', 'Unknown')}
Columns: {', '.join([c['name'] for c in summary.get('columns', [])])}
Numerical columns: {', '.join(summary.get('numerical_columns', []))}
Categorical columns: {', '.join(summary.get('categorical_columns', []))}
Missing values: {sum(summary.get('missing_values', {}).values())} total across {len(summary.get('missing_values', {}))} columns
"""
        
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
        """Create a new session."""
        session_id = str(uuid.uuid4())
        session = Session(
            session_id=session_id,
            dataset_path=dataset_path,
            dataset_filename=dataset_filename,
            summary=summary
        )
        self._sessions[session_id] = session
        return session
    
    def get_session(self, session_id: str) -> Optional[Session]:
        """Get a session by ID."""
        return self._sessions.get(session_id)
    
    def delete_session(self, session_id: str) -> bool:
        """Delete a session."""
        if session_id in self._sessions:
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
                'message_count': len(s.messages)
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

