"""Chat router for conversation with the EDA agent."""
import os
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from ..models import ChatRequest, ChatResponse, DatasetVersion
from ..services.session import session_manager
from ..services.summary import DatasetAnalyzer
from ..agent.workflow import run_agent
from ..config import settings

router = APIRouter(prefix="/api", tags=["chat"])


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Send a message to the EDA agent and get a response.
    
    The agent will:
    1. Understand your query
    2. Generate appropriate Python code
    3. Execute the code safely
    4. Return results and any generated visualizations
    5. If data transformation is requested, create a new dataset version
    """
    # Get session
    session = session_manager.get_session(request.session_id)
    
    if not session:
        raise HTTPException(
            status_code=404,
            detail="Session not found. Please upload a dataset first."
        )
    
    # Add user message to history
    session.add_user_message(request.message)
    
    # Prepare messages for agent (convert to dict format)
    messages = [
        {
            'role': 'user' if hasattr(msg, 'type') and msg.type == 'human' else 'assistant',
            'content': msg.content
        }
        for msg in session.messages
    ]
    
    try:
        # Run the agent
        result = await run_agent(
            messages=messages,
            dataset_info=session.summary,
            dataset_path=session.dataset_path,
            session_id=session.session_id
        )
        
        # Add assistant response to history
        session.add_assistant_message(result.get('response', ''))
        
        # Track code if generated
        if result.get('code'):
            session.add_code(result['code'])
        
        # Track plots
        for plot in result.get('plots', []):
            session.add_plot(plot)
        
        # Convert plot paths to URLs
        plot_urls = [
            f"/api/plots/{os.path.basename(p)}"
            for p in result.get('plots', [])
        ]
        
        # Handle new version creation
        new_version_response = None
        new_version_info = result.get('new_version')
        
        if new_version_info and new_version_info.get('file_path'):
            file_path = new_version_info['file_path']
            description = new_version_info.get('description', 'Transformed dataset')
            
            # Generate summary for new version
            try:
                new_summary = DatasetAnalyzer.analyze_from_path(
                    file_path, 
                    session.dataset_filename
                )
                new_summary_dict = new_summary.model_dump()
                
                # Add version to session
                new_version = session.add_version(
                    file_path=file_path,
                    summary=new_summary_dict,
                    change_description=description
                )
                
                # Create response model
                new_version_response = DatasetVersion(
                    version_id=new_version.version_id,
                    version_number=new_version.version_number,
                    file_path=new_version.file_path,
                    summary=new_summary,
                    change_description=new_version.change_description,
                    created_at=new_version.created_at
                )
                
                print(f"Created new dataset version: v{new_version.version_number} - {description}")
                
            except Exception as e:
                print(f"Error creating new version: {e}")
                # Don't fail the whole request if version creation fails
        
        return ChatResponse(
            response=result.get('response', 'I encountered an issue processing your request.'),
            code=result.get('code'),
            plots=plot_urls,
            execution_result=result.get('execution_result'),
            error=result.get('error'),
            new_version=new_version_response
        )
        
    except Exception as e:
        # Log the error
        import traceback
        traceback.print_exc()
        
        error_message = f"An error occurred while processing your request: {str(e)}"
        session.add_assistant_message(error_message)
        
        return ChatResponse(
            response=error_message,
            error=str(e)
        )


@router.get("/plots/{filename}")
async def get_plot(filename: str):
    """Serve a generated plot image."""
    # Security: ensure filename doesn't contain path traversal
    if '..' in filename or '/' in filename or '\\' in filename:
        raise HTTPException(status_code=400, detail="Invalid filename")
    
    plot_path = os.path.join(settings.plots_dir, filename)
    
    if not os.path.exists(plot_path):
        raise HTTPException(status_code=404, detail="Plot not found")
    
    return FileResponse(
        plot_path,
        media_type="image/png",
        headers={"Cache-Control": "max-age=3600"}
    )


@router.get("/history/{session_id}")
async def get_chat_history(session_id: str):
    """Get the chat history for a session."""
    session = session_manager.get_session(session_id)
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    history = []
    for msg in session.messages:
        history.append({
            'role': 'user' if hasattr(msg, 'type') and msg.type == 'human' else 'assistant',
            'content': msg.content
        })
    
    return {
        "session_id": session_id,
        "messages": history,
        "code_history": session.code_history,
        "plots": [f"/api/plots/{os.path.basename(p)}" for p in session.plots],
        "version_count": len(session.versions),
        "current_version_id": session.current_version_id
    }


@router.post("/clear/{session_id}")
async def clear_history(session_id: str):
    """Clear the chat history for a session (keeps the dataset and versions)."""
    session = session_manager.get_session(session_id)
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session.messages = []
    session.code_history = []
    
    return {"message": "Chat history cleared"}
