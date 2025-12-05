"""File upload router."""
import os
import aiofiles
import pandas as pd
from fastapi import APIRouter, UploadFile, File, HTTPException
from ..config import settings
from ..models import UploadResponse
from ..services.summary import DatasetAnalyzer
from ..services.session import session_manager

router = APIRouter(prefix="/api", tags=["upload"])


@router.post("/upload", response_model=UploadResponse)
async def upload_file(file: UploadFile = File(...)):
    """
    Upload a CSV or Excel file and create a new analysis session.
    
    Returns session ID and dataset summary.
    """
    # Validate file type
    filename = file.filename or "unknown"
    extension = filename.lower().split('.')[-1]
    
    if extension not in ['csv', 'xls', 'xlsx']:
        raise HTTPException(
            status_code=400,
            detail="Only CSV and Excel files are supported"
        )
    
    # Ensure upload directory exists
    os.makedirs(settings.upload_dir, exist_ok=True)
    
    # Read file content
    content = await file.read()
    
    # Check file size
    if len(content) > settings.max_file_size:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum size is {settings.max_file_size // (1024*1024)}MB"
        )
    
    # Create a temporary session ID for the file path
    import uuid
    temp_id = str(uuid.uuid4())
    file_path = os.path.join(settings.upload_dir, f"{temp_id}.{extension}")
    
    # Save file
    async with aiofiles.open(file_path, 'wb') as f:
        await f.write(content)
    
    try:
        # Load and analyze dataset
        if extension == 'csv':
            df = pd.read_csv(file_path)
        else:
            df = pd.read_excel(file_path)
        
        # Generate summary
        summary = DatasetAnalyzer.analyze(df, filename)
        
        # Convert to dict for session storage
        summary_dict = summary.model_dump()
        
        # Create session
        session = session_manager.create_session(
            dataset_path=file_path,
            dataset_filename=filename,
            summary=summary_dict
        )
        
        # Rename file to use session ID
        new_path = os.path.join(settings.upload_dir, f"{session.session_id}.{extension}")
        os.rename(file_path, new_path)
        
        # Update session with new path
        session.dataset_path = new_path
        
        return UploadResponse(
            session_id=session.session_id,
            summary=summary,
            message=f"Successfully uploaded {filename}. You can now ask questions about your data!"
        )
        
    except pd.errors.EmptyDataError:
        os.remove(file_path)
        raise HTTPException(status_code=400, detail="The uploaded file is empty")
    except pd.errors.ParserError as e:
        os.remove(file_path)
        raise HTTPException(status_code=400, detail=f"Failed to parse file: {str(e)}")
    except Exception as e:
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")


@router.get("/sessions")
async def list_sessions():
    """List all active sessions."""
    return {"sessions": session_manager.list_sessions()}


@router.get("/session/{session_id}")
async def get_session(session_id: str):
    """Get information about a specific session."""
    session = session_manager.get_session(session_id)
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return {
        "session_id": session.session_id,
        "dataset_filename": session.dataset_filename,
        "created_at": session.created_at.isoformat(),
        "message_count": len(session.messages),
        "summary": session.summary
    }


@router.delete("/session/{session_id}")
async def delete_session(session_id: str):
    """Delete a session and its associated data."""
    session = session_manager.get_session(session_id)
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Delete uploaded file
    if os.path.exists(session.dataset_path):
        os.remove(session.dataset_path)
    
    # Delete session
    session_manager.delete_session(session_id)
    
    return {"message": "Session deleted successfully"}

