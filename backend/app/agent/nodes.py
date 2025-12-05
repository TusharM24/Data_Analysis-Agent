"""LangGraph node implementations for the EDA agent with retry support."""
import re
from typing import Dict, Any, List
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

# Maximum retries (should match workflow.py)
MAX_RETRIES = 3


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
            state['error'] = None  # Clear any previous error
        
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
        else:
            state['error'] = None  # Clear error on success
        
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
        retry_count = state.get('retry_count', 0)
        
        # Add retry info to output if retries were needed
        retry_info = ""
        if retry_count > 0:
            retry_info = f"\n(Note: Successfully completed after {retry_count} retry attempt(s))"
        
        prompt = RESULT_FORMATTING_PROMPT.format(
            user_request=user_message,
            code=code,
            output=execution_result.get('output', 'No output') + retry_info,
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
        Supports up to MAX_RETRIES attempts with context from previous failures.
        """
        error = state.get('error', '')
        code = state.get('generated_code', '')
        messages = state.get('messages', [])
        user_message = messages[-1].get('content', '') if isinstance(messages[-1], dict) else messages[-1].content
        dataset_info = state.get('dataset_info', {})
        
        # Get current retry count and history
        retry_count = state.get('retry_count', 0)
        previous_errors = state.get('previous_errors', [])
        previous_codes = state.get('previous_codes', [])
        
        # Check if we've exceeded retry limit
        if retry_count >= MAX_RETRIES:
            state['response'] = self._format_final_error(error, previous_errors, user_message)
            return state
        
        # Save current error and code to history
        if error and error not in previous_errors:
            previous_errors.append(error)
        if code and code not in previous_codes:
            previous_codes.append(code)
        
        state['previous_errors'] = previous_errors
        state['previous_codes'] = previous_codes
        
        # Increment retry counter
        retry_count += 1
        state['retry_count'] = retry_count
        
        print(f"🔄 Retry attempt {retry_count}/{MAX_RETRIES} - Error: {error[:100]}...")
        
        # Build enhanced error recovery prompt with history
        prompt = self._build_retry_prompt(
            error=error,
            code=code,
            dataset_info=dataset_info,
            user_message=user_message,
            previous_errors=previous_errors,
            previous_codes=previous_codes,
            retry_count=retry_count
        )
        
        response = self.llm.invoke([
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=prompt)
        ])
        
        # Extract corrected code
        corrected_code = self._extract_code(response.content)
        state['generated_code'] = corrected_code
        state['error'] = None  # Clear error to allow retry
        state['validation_failed'] = False
        
        return state
    
    def _build_retry_prompt(
        self,
        error: str,
        code: str,
        dataset_info: Dict[str, Any],
        user_message: str,
        previous_errors: List[str],
        previous_codes: List[str],
        retry_count: int
    ) -> str:
        """Build an enhanced prompt for error recovery with context from previous attempts."""
        
        # Base error recovery prompt
        base_prompt = ERROR_RECOVERY_PROMPT.format(
            error=error,
            code=code,
            dataset_info=self._format_dataset_info(dataset_info),
            user_request=user_message
        )
        
        # Add context about previous attempts if this isn't the first retry
        if retry_count > 1 and len(previous_errors) > 1:
            history_context = "\n\nPREVIOUS FAILED ATTEMPTS:\n"
            for i, (prev_err, prev_code) in enumerate(zip(previous_errors[:-1], previous_codes[:-1]), 1):
                history_context += f"\n--- Attempt {i} ---\n"
                history_context += f"Error: {prev_err[:200]}\n"
                history_context += f"Code snippet: {prev_code[:300]}...\n"
            
            base_prompt += history_context
            base_prompt += f"\n\nThis is attempt {retry_count}/{MAX_RETRIES}. "
            base_prompt += "Try a DIFFERENT approach than the previous attempts. "
            base_prompt += "Consider using alternative methods or libraries."
        
        # Add specific hints based on common error patterns
        hints = self._get_error_hints(error)
        if hints:
            base_prompt += f"\n\nHINTS FOR THIS ERROR:\n{hints}"
        
        return base_prompt
    
    def _get_error_hints(self, error: str) -> str:
        """Get specific hints based on the error message."""
        hints = []
        error_lower = error.lower()
        
        if 'sparse_output' in error_lower or 'sparse' in error_lower:
            hints.append("- For OneHotEncoder, use sparse_output=False instead of sparse=False (sklearn >= 1.2)")
            hints.append("- Alternative: Use pd.get_dummies(df, columns=['col']) for simpler one-hot encoding")
        
        if 'keyerror' in error_lower or 'not in index' in error_lower:
            hints.append("- Check column name spelling and case sensitivity")
            hints.append("- Use df.columns.tolist() to see available columns")
        
        if 'length' in error_lower or 'shape' in error_lower or 'mismatch' in error_lower:
            hints.append("- Ensure x and y have the same length for plotting")
            hints.append("- For countplot, use: sns.countplot(x='column', data=df) or sns.countplot(x=df['column'])")
            hints.append("- Don't mix value_counts() index with full dataframe in same plot")
        
        if 'nan' in error_lower or 'null' in error_lower or 'missing' in error_lower:
            hints.append("- Use .dropna() or .fillna() before operations that can't handle NaN")
            hints.append("- Check for missing values: df['col'].isna().sum()")
        
        if 'dtype' in error_lower or 'type' in error_lower:
            hints.append("- Convert column types explicitly: df['col'].astype(str) or pd.to_numeric()")
            hints.append("- For LabelEncoder, convert to string first: le.fit_transform(df['col'].astype(str))")
        
        if 'memory' in error_lower:
            hints.append("- Reduce data size: use .head(1000) for testing")
            hints.append("- Process in chunks if dataset is large")
        
        if 'seaborn' in error_lower or 'countplot' in error_lower or 'barplot' in error_lower:
            hints.append("- For top N values: sns.countplot(x='col', data=df, order=df['col'].value_counts().head(N).index)")
            hints.append("- Don't pass both x=series and data=df when they don't align")
        
        return "\n".join(hints) if hints else ""
    
    def _format_final_error(self, error: str, previous_errors: List[str], user_message: str) -> str:
        """Format the final error message after all retries failed."""
        response = f"""I apologize, but I wasn't able to complete your request after {MAX_RETRIES} attempts.

**Your request:** {user_message}

**Final error:** {error}

**What I tried:**
"""
        for i, err in enumerate(previous_errors, 1):
            response += f"\n{i}. Attempt failed with: {err[:150]}..."
        
        response += """

**Suggestions:**
- Try rephrasing your request to be more specific
- Check if the column names you mentioned exist in the dataset
- Try breaking down complex requests into simpler steps
- For visualization issues, try specifying the exact chart type you want

Would you like to try a different approach?"""
        
        return response
    
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
