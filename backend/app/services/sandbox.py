"""Secure code execution sandbox."""
import subprocess
import tempfile
import os
import json
import re
import uuid
import glob
from typing import Dict, Any, Optional, Tuple, Set
from ..config import settings


class CodeSandbox:
    """
    Executes Python code in a sandboxed environment.
    Uses subprocess isolation with strict timeouts and output capture.
    """
    
    # Forbidden patterns that should never appear in generated code
    FORBIDDEN_PATTERNS = [
        r'\bos\.system\b',
        r'\bos\.popen\b',
        r'\bos\.exec\b',
        r'\bos\.spawn\b',
        r'\bsubprocess\b',
        r'\b__import__\b',
        r'\beval\s*\(',
        r'\bexec\s*\(',
        r'\bcompile\s*\(',
        r'\bshutil\b',
        r'\bsocket\b',
        r'\brequests\b',
        r'\burllib\b',
        r'\bftplib\b',
        r'\bsmtplib\b',
        r'\bpickle\b',
        r'\bshelve\b',
        r'\b__builtins__\b',
        r'\bglobals\s*\(\)',
        r'\blocals\s*\(\)',
    ]
    
    # Allowed imports
    ALLOWED_IMPORTS = {
        'pandas', 'pd',
        'numpy', 'np',
        'matplotlib', 'matplotlib.pyplot', 'plt',
        'seaborn', 'sns',
        'plotly', 'plotly.express', 'px', 'plotly.graph_objects', 'go',
        'scipy', 'scipy.stats',
        'sklearn', 'scikit-learn',
        'statsmodels',
        'json',
        'math',
        'statistics',
        'datetime',
        'collections',
        're',
    }
    
    def __init__(self, plots_dir: str = None):
        self.plots_dir = plots_dir or settings.plots_dir
        os.makedirs(self.plots_dir, exist_ok=True)
    
    def validate_code(self, code: str) -> Tuple[bool, Optional[str]]:
        """
        Validate code for security issues.
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check for forbidden patterns
        for pattern in self.FORBIDDEN_PATTERNS:
            if re.search(pattern, code, re.IGNORECASE):
                return False, f"Code contains forbidden pattern: {pattern}"
        
        # Check for suspicious string patterns
        if '\\x' in code or '\\u' in code:
            return False, "Code contains suspicious escape sequences"
        
        # Basic syntax check
        try:
            compile(code, '<string>', 'exec')
        except SyntaxError as e:
            return False, f"Syntax error: {str(e)}"
        
        return True, None
    
    def _get_existing_plots(self) -> Set[str]:
        """Get set of existing plot files in plots directory."""
        existing = set()
        for ext in ['*.png', '*.jpg', '*.jpeg', '*.svg', '*.pdf']:
            existing.update(glob.glob(os.path.join(self.plots_dir, ext)))
        return existing
    
    def execute(
        self, 
        code: str, 
        dataset_path: str,
        session_id: str
    ) -> Dict[str, Any]:
        """
        Execute code in a sandboxed subprocess.
        
        Args:
            code: Python code to execute
            dataset_path: Path to the CSV file
            session_id: Session ID for plot naming
            
        Returns:
            Dictionary with execution results
        """
        # Validate first
        is_valid, error = self.validate_code(code)
        if not is_valid:
            return {
                'success': False,
                'error': error,
                'output': None,
                'plots': []
            }
        
        # Convert paths to absolute to avoid working directory issues
        abs_dataset_path = os.path.abspath(dataset_path)
        abs_plots_dir = os.path.abspath(self.plots_dir)
        
        # Generate unique plot filename prefix
        plot_id = str(uuid.uuid4())[:8]
        plot_prefix = f"{session_id}_{plot_id}"
        plot_path = os.path.join(abs_plots_dir, f"{plot_prefix}.png")
        
        # Get existing plots before execution
        existing_plots = self._get_existing_plots()
        
        # Create execution script with absolute paths
        script = self._create_execution_script(code, abs_dataset_path, plot_path, plot_prefix, abs_plots_dir)
        
        # Write script to temp file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(script)
            script_path = f.name
        
        try:
            # Execute with timeout
            result = subprocess.run(
                ['python', script_path],
                capture_output=True,
                timeout=settings.execution_timeout,
                text=True,
                env={
                    **os.environ,
                    'MPLBACKEND': 'Agg'  # Non-interactive matplotlib backend
                }
            )
            
            # Parse output
            output = result.stdout
            error_output = result.stderr
            
            # Find ALL new plots created during execution
            current_plots = self._get_existing_plots()
            new_plots = list(current_plots - existing_plots)
            
            # Also check for plots saved in the plots directory with our prefix
            for f in os.listdir(self.plots_dir):
                if f.startswith(plot_prefix) and f.endswith('.png'):
                    full_path = os.path.join(self.plots_dir, f)
                    if full_path not in new_plots:
                        new_plots.append(full_path)
            
            # Sort plots by modification time (newest first) and limit to 10
            new_plots.sort(key=lambda x: os.path.getmtime(x), reverse=True)
            new_plots = new_plots[:10]  # Limit to 10 plots max
            
            # Try to extract JSON result from output
            result_data = None
            if output:
                try:
                    # Look for JSON in the output
                    json_match = re.search(r'```json\n(.*?)\n```', output, re.DOTALL)
                    if json_match:
                        result_data = json.loads(json_match.group(1))
                    elif output.strip().startswith('{') or output.strip().startswith('['):
                        result_data = json.loads(output.strip())
                except json.JSONDecodeError:
                    pass
            
            if result.returncode != 0:
                return {
                    'success': False,
                    'error': error_output or "Code execution failed",
                    'output': output,
                    'plots': new_plots
                }
            
            return {
                'success': True,
                'error': None,
                'output': output,
                'result': result_data,
                'plots': new_plots
            }
            
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'error': f"Code execution timed out after {settings.execution_timeout} seconds",
                'output': None,
                'plots': []
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'output': None,
                'plots': []
            }
        finally:
            # Cleanup temp file
            if os.path.exists(script_path):
                os.remove(script_path)
    
    def _create_execution_script(
        self, 
        code: str, 
        dataset_path: str, 
        plot_path: str,
        plot_prefix: str,
        plots_dir: str
    ) -> str:
        """Create the execution script with necessary imports and setup."""
        return f'''
import warnings
warnings.filterwarnings('ignore')

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import json
import os
from datetime import datetime

# Set plot styling
plt.style.use('seaborn-v0_8-whitegrid')
sns.set_palette("husl")
plt.rcParams['figure.figsize'] = [10, 6]
plt.rcParams['figure.dpi'] = 100

# Load the dataset
df = pd.read_csv("{dataset_path}")

# Plot configuration
PLOTS_DIR = "{plots_dir}"
PLOT_PREFIX = "{plot_prefix}"
_plot_counter = [0]  # Use list to allow modification in nested function

def save_plot(name=None):
    """
    Save the current matplotlib figure.
    
    Args:
        name: Optional custom name for the plot. If not provided, uses auto-generated name.
    """
    if name:
        filename = f"{{PLOT_PREFIX}}_{{name}}.png"
    else:
        _plot_counter[0] += 1
        filename = f"{{PLOT_PREFIX}}_plot{{_plot_counter[0]}}.png"
    
    filepath = os.path.join(PLOTS_DIR, filename)
    plt.tight_layout()
    plt.savefig(filepath, bbox_inches='tight', dpi=150)
    plt.close()
    print(f"Plot saved: {{filename}}")
    return filepath

# Helper to convert results to JSON-safe format
def to_json_safe(obj):
    if isinstance(obj, (pd.DataFrame, pd.Series)):
        return obj.to_dict()
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, (np.integer, np.floating)):
        return obj.item()
    elif isinstance(obj, dict):
        return {{k: to_json_safe(v) for k, v in obj.items()}}
    elif isinstance(obj, (list, tuple)):
        return [to_json_safe(v) for v in obj]
    return obj

# User code execution
try:
{self._indent_code(code)}
    
    # Auto-save any open matplotlib figures
    if plt.get_fignums():
        save_plot()
        
except Exception as e:
    print(f"Error: {{str(e)}}")
    import traceback
    traceback.print_exc()
'''
    
    def _indent_code(self, code: str, spaces: int = 4) -> str:
        """Indent code block."""
        indent = ' ' * spaces
        return '\n'.join(indent + line for line in code.split('\n'))


# Global sandbox instance
code_sandbox = CodeSandbox()
