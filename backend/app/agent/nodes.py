"""LangGraph node implementations for the EDA agent."""
import re
from typing import Dict, Any
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, BaseMessage
from ..config import settings
from ..services.sandbox import code_sandbox
from .prompts import (
    SYSTEM_PROMPT,
    CODE_GENERATION_PROMPT,
    QUERY_UNDERSTANDING_PROMPT,
    RESULT_FORMATTING_PROMPT,
    ERROR_RECOVERY_PROMPT
)


class AgentNodes:
    """Collection of node functions for the LangGraph workflow."""
    
    def __init__(self):
        self.llm = ChatGroq(
            api_key=settings.groq_api_key,
            model_name=settings.groq_model,
            temperature=0.3
        )
    
    def understand_query(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Node 1: Understand the user's query and classify intent.
        """
        messages = state.get('messages', [])
        if not messages:
            state['error'] = "No messages in conversation"
            return state
        
        user_message = messages[-1].get('content', '') if isinstance(messages[-1], dict) else messages[-1].content
        dataset_info = state.get('dataset_info', {})
        
        columns = [col.get('name', col) if isinstance(col, dict) else str(col) 
                   for col in dataset_info.get('columns', [])]
        
        prompt = QUERY_UNDERSTANDING_PROMPT.format(
            user_request=user_message,
            columns=columns
        )
        
        response = self.llm.invoke([HumanMessage(content=prompt)])
        state['query_type'] = response.content.strip().upper()
        
        return state
    
    def generate_code(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Node 2: Generate Python code based on the user's request.
        """
        messages = state.get('messages', [])
        user_message = messages[-1].get('content', '') if isinstance(messages[-1], dict) else messages[-1].content
        dataset_info = state.get('dataset_info', {})
        
        # Build conversation context
        conversation_context = self._build_conversation_context(messages[:-1])
        
        # Format dataset info for prompt
        dataset_info_str = self._format_dataset_info(dataset_info)
        
        prompt = CODE_GENERATION_PROMPT.format(
            dataset_info=dataset_info_str,
            user_request=user_message,
            conversation_context=conversation_context
        )
        
        # Generate code
        response = self.llm.invoke([
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=prompt)
        ])
        
        # Extract code from response
        code = self._extract_code(response.content)
        state['generated_code'] = code
        
        return state
    
    def validate_code(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Node 3: Validate the generated code for security and correctness.
        """
        code = state.get('generated_code', '')
        
        if not code:
            state['error'] = "No code was generated"
            return state
        
        # Use sandbox validation
        is_valid, error = code_sandbox.validate_code(code)
        
        if not is_valid:
            state['error'] = error
            state['validation_failed'] = True
        else:
            state['validation_failed'] = False
        
        return state
    
    def execute_code(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Node 4: Execute the validated code in the sandbox.
        """
        code = state.get('generated_code', '')
        dataset_path = state.get('dataset_path', '')
        session_id = state.get('session_id', 'unknown')
        
        if not dataset_path:
            state['error'] = "No dataset path provided"
            return state
        
        # Execute in sandbox
        result = code_sandbox.execute(code, dataset_path, session_id)
        
        state['execution_result'] = result
        state['plots'] = result.get('plots', [])
        
        if not result.get('success'):
            state['error'] = result.get('error')
        
        return state
    
    def format_response(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Node 5: Format the execution result into a user-friendly response.
        """
        messages = state.get('messages', [])
        user_message = messages[-1].get('content', '') if isinstance(messages[-1], dict) else messages[-1].content
        code = state.get('generated_code', '')
        execution_result = state.get('execution_result', {})
        plots = state.get('plots', [])
        error = state.get('error')
        
        prompt = RESULT_FORMATTING_PROMPT.format(
            user_request=user_message,
            code=code,
            output=execution_result.get('output', 'No output'),
            plots=f"{len(plots)} plot(s) generated" if plots else "No plots",
            error=error or "None"
        )
        
        response = self.llm.invoke([
            SystemMessage(content="You are a helpful data analyst. Format results clearly and provide insights."),
            HumanMessage(content=prompt)
        ])
        
        state['response'] = response.content
        
        return state
    
    def handle_error(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Error recovery node: Try to fix and regenerate code.
        """
        error = state.get('error', '')
        code = state.get('generated_code', '')
        messages = state.get('messages', [])
        user_message = messages[-1].get('content', '') if isinstance(messages[-1], dict) else messages[-1].content
        dataset_info = state.get('dataset_info', {})
        
        # Only attempt recovery once
        if state.get('recovery_attempted'):
            state['response'] = f"I encountered an error and couldn't recover: {error}\n\nPlease try rephrasing your request or check if the columns you mentioned exist in the dataset."
            return state
        
        state['recovery_attempted'] = True
        
        prompt = ERROR_RECOVERY_PROMPT.format(
            error=error,
            code=code,
            dataset_info=self._format_dataset_info(dataset_info),
            user_request=user_message
        )
        
        response = self.llm.invoke([
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=prompt)
        ])
        
        # Extract corrected code
        corrected_code = self._extract_code(response.content)
        state['generated_code'] = corrected_code
        state['error'] = None
        
        return state
    
    def _build_conversation_context(self, messages: list, max_messages: int = 6) -> str:
        """Build conversation context from message history."""
        if not messages:
            return "No previous conversation."
        
        context_messages = messages[-max_messages:]
        context_parts = []
        
        for msg in context_messages:
            if isinstance(msg, dict):
                role = msg.get('role', 'unknown')
                content = msg.get('content', '')
            else:
                role = 'user' if isinstance(msg, HumanMessage) else 'assistant'
                content = msg.content
            
            # Truncate long messages
            if len(content) > 300:
                content = content[:300] + "..."
            
            context_parts.append(f"{role.upper()}: {content}")
        
        return "\n".join(context_parts)
    
    def _format_dataset_info(self, info: Dict[str, Any]) -> str:
        """Format dataset info for prompts."""
        if not info:
            return "No dataset information available."
        
        parts = [
            f"Shape: {info.get('shape', 'Unknown')}",
            f"Columns ({len(info.get('columns', []))}):"
        ]
        
        for col in info.get('columns', [])[:20]:  # Limit to 20 columns
            if isinstance(col, dict):
                name = col.get('name', 'Unknown')
                dtype = col.get('dtype', 'Unknown')
                nulls = col.get('null_count', 0)
                parts.append(f"  - {name} ({dtype}, {nulls} nulls)")
            else:
                parts.append(f"  - {col}")
        
        if len(info.get('columns', [])) > 20:
            parts.append(f"  ... and {len(info['columns']) - 20} more columns")
        
        parts.extend([
            f"\nNumerical columns: {', '.join(info.get('numerical_columns', [])[:10])}",
            f"Categorical columns: {', '.join(info.get('categorical_columns', [])[:10])}"
        ])
        
        missing = info.get('missing_values', {})
        if missing:
            parts.append(f"\nMissing values: {sum(missing.values())} total")
        
        return "\n".join(parts)
    
    def _extract_code(self, response: str) -> str:
        """Extract Python code from LLM response."""
        # Try to find code block
        code_pattern = r'```(?:python)?\n(.*?)```'
        matches = re.findall(code_pattern, response, re.DOTALL)
        
        if matches:
            return matches[0].strip()
        
        # If no code block, assume the entire response is code
        # (after removing any obvious non-code parts)
        lines = response.strip().split('\n')
        code_lines = []
        
        for line in lines:
            # Skip lines that look like explanations
            if line.strip().startswith('#') or not line.strip():
                code_lines.append(line)
            elif any(kw in line for kw in ['import ', 'def ', 'class ', 'if ', 'for ', 'while ', 'df', 'plt.', 'sns.', 'print', '=']):
                code_lines.append(line)
            elif code_lines:  # Continue if we're in a code block
                code_lines.append(line)
        
        return '\n'.join(code_lines).strip()

