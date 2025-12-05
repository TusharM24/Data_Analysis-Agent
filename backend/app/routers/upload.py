"""File upload and version management router."""
import os
import aiofiles
import pandas as pd
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from ..config import settings
from ..models import (
    UploadResponse, 
    VersionListResponse, 
    SwitchVersionRequest, 
    SwitchVersionResponse,
    DatasetVersion
)
from ..services.summary import DatasetAnalyzer
from ..services.session import session_manager

router = APIRouter(prefix="/api", tags=["upload"])


@router.post("/upload", response_model=UploadResponse)
async def upload_file(file: UploadFile = File(...)):
    """
    Upload a CSV or Excel file and create a new analysis session.
    
    Returns session ID, dataset summary, and initial version info.
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
        
        # Create session (this also creates v1)
        session = session_manager.create_session(
            dataset_path=file_path,
            dataset_filename=filename,
            summary=summary_dict
        )
        
        # Rename file to use session ID
        new_path = os.path.join(settings.upload_dir, f"{session.session_id}_v1.{extension}")
        os.rename(file_path, new_path)
        
        # Update the version's file path
        if session.versions:
            session.versions[0].file_path = new_path
        
        # Get the initial version for response
        initial_version = session.get_current_version()
        version_response = DatasetVersion(
            version_id=initial_version.version_id,
            version_number=initial_version.version_number,
            file_path=initial_version.file_path,
            summary=summary,
            change_description=initial_version.change_description,
            created_at=initial_version.created_at
        ) if initial_version else None
        
        return UploadResponse(
            session_id=session.session_id,
            summary=summary,
            message=f"Successfully uploaded {filename}. You can now ask questions about your data!",
            version=version_response
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


# ==================== Version Management Endpoints ====================

@router.get("/versions/{session_id}", response_model=VersionListResponse)
async def list_versions(session_id: str):
    """List all dataset versions for a session."""
    session = session_manager.get_session(session_id)
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Convert internal versions to API model
    versions = []
    for v in session.versions:
        # Re-create summary model from dict
        summary_model = DatasetAnalyzer.dict_to_summary(v.summary)
        versions.append(DatasetVersion(
            version_id=v.version_id,
            version_number=v.version_number,
            file_path=v.file_path,
            summary=summary_model,
            change_description=v.change_description,
            created_at=v.created_at
        ))
    
    return VersionListResponse(
        versions=versions,
        current_version_id=session.current_version_id
    )


@router.post("/switch-version", response_model=SwitchVersionResponse)
async def switch_version(request: SwitchVersionRequest):
    """Switch to a different dataset version."""
    session = session_manager.get_session(request.session_id)
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Attempt to switch
    success = session.switch_version(request.version_id)
    
    if not success:
        raise HTTPException(
            status_code=404, 
            detail=f"Version {request.version_id} not found"
        )
    
    # Get the new current version
    current = session.get_current_version()
    summary_model = DatasetAnalyzer.dict_to_summary(current.summary)
    
    return SwitchVersionResponse(
        success=True,
        current_version=DatasetVersion(
            version_id=current.version_id,
            version_number=current.version_number,
            file_path=current.file_path,
            summary=summary_model,
            change_description=current.change_description,
            created_at=current.created_at
        ),
        message=f"Switched to version {current.version_number}: {current.change_description}"
    )


# ==================== Session Management Endpoints ====================

@router.get("/sessions")
async def list_sessions():
    """List all active sessions."""
    return {"sessions": session_manager.list_sessions()}


@router.get("/session/{session_id}")
async def get_session(session_id: str):
    """Get information about a specific session including versions."""
    session = session_manager.get_session(session_id)
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    current_version = session.get_current_version()
    
    return {
        "session_id": session.session_id,
        "dataset_filename": session.dataset_filename,
        "created_at": session.created_at.isoformat(),
        "message_count": len(session.messages),
        "summary": session.summary,
        "version_count": len(session.versions),
        "current_version_id": session.current_version_id,
        "current_version_number": current_version.version_number if current_version else 1
    }


@router.delete("/session/{session_id}")
async def delete_session(session_id: str):
    """Delete a session and all its associated data (including version files)."""
    session = session_manager.get_session(session_id)
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Delete all version files
    for version in session.versions:
        if os.path.exists(version.file_path):
            try:
                os.remove(version.file_path)
            except:
                pass
    
    # Delete session
    session_manager.delete_session(session_id)
    
    return {"message": "Session and all versions deleted successfully"}


@router.get("/download/{version_id}")
async def download_version(version_id: str):
    """Download a specific dataset version as CSV."""
    # Find the version across all sessions
    for session in session_manager._sessions.values():
        for version in session.versions:
            if version.version_id == version_id:
                if not os.path.exists(version.file_path):
                    raise HTTPException(status_code=404, detail="Version file not found")
                
                # Generate download filename
                base_name = session.dataset_filename.rsplit('.', 1)[0]
                download_name = f"{base_name}_v{version.version_number}.csv"
                
                return FileResponse(
                    path=version.file_path,
                    filename=download_name,
                    media_type="text/csv"
                )
    
    raise HTTPException(status_code=404, detail="Version not found")
