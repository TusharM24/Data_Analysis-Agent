"""Secure code execution sandbox with dataset versioning support."""
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
    Supports dataset versioning through save_dataframe() function.
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
        'sklearn.preprocessing',
        'sklearn.impute',
        'sklearn.feature_selection',
        'sklearn.model_selection',
        'sklearn.metrics',
        'statsmodels',
        'json',
        'math',
        'statistics',
        'datetime',
        'collections',
        're',
        'Counter',
    }
    
    # Marker used to detect version saves in output
    VERSION_SAVED_MARKER = "__VERSION_SAVED__"
    
    def __init__(self, plots_dir: str = None, versions_dir: str = None):
        self.plots_dir = plots_dir or settings.plots_dir
        self.versions_dir = versions_dir or os.path.join(settings.upload_dir, "versions")
        os.makedirs(self.plots_dir, exist_ok=True)
        os.makedirs(self.versions_dir, exist_ok=True)
    
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
            Dictionary with execution results, including new_version if created
        """
        # Validate first
        is_valid, error = self.validate_code(code)
        if not is_valid:
            return {
                'success': False,
                'error': error,
                'output': None,
                'plots': [],
                'new_version': None
            }
        
        # Convert paths to absolute to avoid working directory issues
        abs_dataset_path = os.path.abspath(dataset_path)
        abs_plots_dir = os.path.abspath(self.plots_dir)
        abs_versions_dir = os.path.abspath(self.versions_dir)
        
        # Generate unique IDs for plots and potential new version
        execution_id = str(uuid.uuid4())[:8]
        plot_prefix = f"{session_id}_{execution_id}"
        version_path = os.path.join(abs_versions_dir, f"{session_id}_{execution_id}.csv")
        
        # Get existing plots before execution
        existing_plots = self._get_existing_plots()
        
        # Create execution script with absolute paths
        script = self._create_execution_script(
            code, 
            abs_dataset_path, 
            plot_prefix, 
            abs_plots_dir,
            version_path
        )
        
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
            
            # Check if a new version was saved
            new_version = None
            if self.VERSION_SAVED_MARKER in output:
                # Parse version info from output
                version_match = re.search(
                    rf'{self.VERSION_SAVED_MARKER}:(.+?):(.+?)(?:\n|$)', 
                    output
                )
                if version_match and os.path.exists(version_path):
                    new_version = {
                        'file_path': version_path,
                        'description': version_match.group(2).strip()
                    }
            
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
                    'plots': new_plots,
                    'new_version': new_version
                }
            
            return {
                'success': True,
                'error': None,
                'output': output,
                'result': result_data,
                'plots': new_plots,
                'new_version': new_version
            }
            
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'error': f"Code execution timed out after {settings.execution_timeout} seconds",
                'output': None,
                'plots': [],
                'new_version': None
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'output': None,
                'plots': [],
                'new_version': None
            }
        finally:
            # Cleanup temp file
            if os.path.exists(script_path):
                os.remove(script_path)
    
    def _create_execution_script(
        self, 
        code: str, 
        dataset_path: str, 
        plot_prefix: str,
        plots_dir: str,
        version_path: str
    ) -> str:
        """Create the execution script with necessary imports and setup."""
        return f'''
import warnings
warnings.filterwarnings('ignore')

# Core data libraries
import pandas as pd
import numpy as np
import json
import os
from datetime import datetime
import re
from collections import Counter

# Visualization
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns

# Scikit-learn preprocessing
from sklearn.preprocessing import (
    StandardScaler,
    MinMaxScaler,
    RobustScaler,
    MaxAbsScaler,
    Normalizer,
    LabelEncoder,
    OrdinalEncoder,
    OneHotEncoder,
    Binarizer,
    PolynomialFeatures,
    PowerTransformer,
    QuantileTransformer,
    FunctionTransformer
)

# Scikit-learn imputation
from sklearn.impute import SimpleImputer, KNNImputer

# Scikit-learn feature selection
from sklearn.feature_selection import (
    SelectKBest,
    chi2,
    f_classif,
    mutual_info_classif,
    VarianceThreshold
)

# Scikit-learn model selection (for train/test split)
from sklearn.model_selection import train_test_split

# Scikit-learn metrics (for evaluation)
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    classification_report,
    mean_squared_error,
    mean_absolute_error,
    r2_score
)

# Scipy stats for statistical transformations
from scipy import stats
from scipy.stats import zscore, boxcox, yeojohnson

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
VERSION_PATH = "{version_path}"
_plot_counter = [0]  # Use list to allow modification in nested function
_version_saved = [False]  # Track if version was saved

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

def save_dataframe(description="Transformed dataset"):
    """
    Save the current dataframe as a new version.
    
    IMPORTANT: Only call this when the user explicitly asks to transform/clean/modify the data.
    Do NOT call for analysis-only queries.
    
    Args:
        description: Brief description of changes made (e.g., "Removed null values", "Added age_group column")
    
    Example:
        # User asked to clean the data
        df = df.dropna()
        df = df.drop_duplicates()
        save_dataframe("Removed null values and duplicates")
    """
    global df
    if _version_saved[0]:
        print("Warning: Version already saved in this execution. Skipping duplicate save.")
        return
    
    df.to_csv(VERSION_PATH, index=False)
    _version_saved[0] = True
    print(f"__VERSION_SAVED__:{{VERSION_PATH}}:{{description}}")
    print(f"Dataset saved as new version: {{description}}")
    print(f"New shape: {{df.shape[0]}} rows x {{df.shape[1]}} columns")

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
