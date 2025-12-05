"""Chat router for conversation with the EDA agent."""
import os
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from ..models import ChatRequest, ChatResponse
from ..services.session import session_manager
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
        
        return ChatResponse(
            response=result.get('response', 'I encountered an issue processing your request.'),
            code=result.get('code'),
            plots=plot_urls,
            execution_result=result.get('execution_result'),
            error=result.get('error')
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
        "plots": [f"/api/plots/{os.path.basename(p)}" for p in session.plots]
    }


@router.post("/clear/{session_id}")
async def clear_history(session_id: str):
    """Clear the chat history for a session (keeps the dataset)."""
    session = session_manager.get_session(session_id)
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session.messages = []
    session.code_history = []
    
    return {"message": "Chat history cleared"}

