"""LangGraph workflow definition for the EDA agent."""
from typing import Dict, Any, TypedDict, List, Annotated
from langgraph.graph import StateGraph, END
from langchain_core.messages import BaseMessage
import operator
from .nodes import AgentNodes


class AgentState(TypedDict):
    """State schema for the agent workflow."""
    messages: List[Dict[str, str]]
    dataset_info: Dict[str, Any]
    dataset_path: str
    session_id: str
    query_type: str
    generated_code: str
    validation_failed: bool
    execution_result: Dict[str, Any]
    plots: List[str]
    error: str
    response: str
    recovery_attempted: bool


def create_agent_workflow():
    """
    Create and compile the LangGraph workflow for the EDA agent.
    
    The workflow consists of 5 main nodes:
    1. understand_query - Classify the user's intent
    2. generate_code - Generate Python code for the analysis
    3. validate_code - Check code safety and correctness
    4. execute_code - Run code in sandbox
    5. format_response - Format results for the user
    
    Plus an error recovery node for handling failures.
    """
    # Initialize nodes
    nodes = AgentNodes()
    
    # Create the graph
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("understand_query", nodes.understand_query)
    workflow.add_node("generate_code", nodes.generate_code)
    workflow.add_node("validate_code", nodes.validate_code)
    workflow.add_node("execute_code", nodes.execute_code)
    workflow.add_node("format_response", nodes.format_response)
    workflow.add_node("handle_error", nodes.handle_error)
    
    # Define the workflow edges
    workflow.set_entry_point("understand_query")
    
    # understand_query -> generate_code
    workflow.add_edge("understand_query", "generate_code")
    
    # generate_code -> validate_code
    workflow.add_edge("generate_code", "validate_code")
    
    # validate_code -> execute_code OR handle_error
    def route_after_validation(state: AgentState) -> str:
        if state.get('validation_failed') or state.get('error'):
            return "handle_error"
        return "execute_code"
    
    workflow.add_conditional_edges(
        "validate_code",
        route_after_validation,
        {
            "execute_code": "execute_code",
            "handle_error": "handle_error"
        }
    )
    
    # execute_code -> format_response OR handle_error
    def route_after_execution(state: AgentState) -> str:
        execution_result = state.get('execution_result', {})
        if not execution_result.get('success') and not state.get('recovery_attempted'):
            return "handle_error"
        return "format_response"
    
    workflow.add_conditional_edges(
        "execute_code",
        route_after_execution,
        {
            "format_response": "format_response",
            "handle_error": "handle_error"
        }
    )
    
    # handle_error -> validate_code (retry) OR format_response (give up)
    def route_after_error(state: AgentState) -> str:
        if state.get('recovery_attempted') and state.get('generated_code'):
            return "validate_code"
        return "format_response"
    
    workflow.add_conditional_edges(
        "handle_error",
        route_after_error,
        {
            "validate_code": "validate_code",
            "format_response": "format_response"
        }
    )
    
    # format_response -> END
    workflow.add_edge("format_response", END)
    
    # Compile the workflow
    return workflow.compile()


# Create a singleton instance
_agent_workflow = None


def get_agent_workflow():
    """Get or create the agent workflow instance."""
    global _agent_workflow
    if _agent_workflow is None:
        _agent_workflow = create_agent_workflow()
    return _agent_workflow


async def run_agent(
    messages: List[Dict[str, str]],
    dataset_info: Dict[str, Any],
    dataset_path: str,
    session_id: str
) -> Dict[str, Any]:
    """
    Run the agent workflow with the given inputs.
    
    Args:
        messages: Conversation history
        dataset_info: Dataset summary information
        dataset_path: Path to the CSV file
        session_id: Session identifier
        
    Returns:
        Dictionary with response, code, plots, and any errors
    """
    workflow = get_agent_workflow()
    
    initial_state = {
        'messages': messages,
        'dataset_info': dataset_info,
        'dataset_path': dataset_path,
        'session_id': session_id,
        'query_type': '',
        'generated_code': '',
        'validation_failed': False,
        'execution_result': {},
        'plots': [],
        'error': '',
        'response': '',
        'recovery_attempted': False
    }
    
    # Run the workflow
    final_state = workflow.invoke(initial_state)
    
    return {
        'response': final_state.get('response', ''),
        'code': final_state.get('generated_code', ''),
        'plots': final_state.get('plots', []),
        'execution_result': final_state.get('execution_result', {}),
        'error': final_state.get('error')
    }

