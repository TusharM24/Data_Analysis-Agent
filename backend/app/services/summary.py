"""Dataset summary and analysis service."""
import pandas as pd
import numpy as np
from typing import Dict, Any, List
from ..models import DatasetSummary, ColumnInfo


class DatasetAnalyzer:
    """Analyzes datasets and generates comprehensive summaries."""
    
    @staticmethod
    def analyze(df: pd.DataFrame, filename: str) -> DatasetSummary:
        """
        Generate a comprehensive summary of the dataset.
        
        Args:
            df: The pandas DataFrame to analyze
            filename: Original filename of the dataset
            
        Returns:
            DatasetSummary with all relevant statistics
        """
        # Identify column types
        numerical_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
        datetime_cols = df.select_dtypes(include=['datetime64']).columns.tolist()
        
        # Try to detect datetime columns that might be stored as strings
        for col in categorical_cols[:]:
            if df[col].dropna().head(100).apply(
                lambda x: DatasetAnalyzer._is_datetime_string(str(x))
            ).mean() > 0.8:
                try:
                    pd.to_datetime(df[col].dropna().head(100))
                    datetime_cols.append(col)
                    categorical_cols.remove(col)
                except:
                    pass
        
        # Generate column information
        columns_info = []
        for col in df.columns:
            sample_values = df[col].dropna().head(5).tolist()
            # Convert numpy types to Python native types
            sample_values = [
                v.item() if hasattr(v, 'item') else v 
                for v in sample_values
            ]
            
            columns_info.append(ColumnInfo(
                name=col,
                dtype=str(df[col].dtype),
                non_null_count=int(df[col].notna().sum()),
                null_count=int(df[col].isna().sum()),
                unique_count=int(df[col].nunique()),
                sample_values=sample_values
            ))
        
        # Calculate missing values
        missing_values = {
            col: int(df[col].isna().sum()) 
            for col in df.columns 
            if df[col].isna().sum() > 0
        }
        
        # Memory usage
        memory_bytes = df.memory_usage(deep=True).sum()
        if memory_bytes < 1024:
            memory_str = f"{memory_bytes} bytes"
        elif memory_bytes < 1024 * 1024:
            memory_str = f"{memory_bytes / 1024:.2f} KB"
        else:
            memory_str = f"{memory_bytes / (1024 * 1024):.2f} MB"
        
        # Head preview (convert to serializable format)
        head_preview = df.head(10).replace({np.nan: None}).to_dict(orient='records')
        for record in head_preview:
            for key, value in record.items():
                if hasattr(value, 'item'):
                    record[key] = value.item()
                elif pd.isna(value):
                    record[key] = None
        
        return DatasetSummary(
            filename=filename,
            shape=(df.shape[0], df.shape[1]),
            columns=columns_info,
            numerical_columns=numerical_cols,
            categorical_columns=categorical_cols,
            datetime_columns=datetime_cols,
            missing_values=missing_values,
            memory_usage=memory_str,
            head_preview=head_preview
        )
    
    @staticmethod
    def _is_datetime_string(s: str) -> bool:
        """Check if a string looks like a datetime."""
        datetime_patterns = [
            r'\d{4}-\d{2}-\d{2}',
            r'\d{2}/\d{2}/\d{4}',
            r'\d{2}-\d{2}-\d{4}',
        ]
        import re
        return any(re.search(p, s) for p in datetime_patterns)
    
    @staticmethod
    def get_statistics(df: pd.DataFrame) -> Dict[str, Any]:
        """Get detailed statistics for numerical columns."""
        stats = {}
        numerical_cols = df.select_dtypes(include=[np.number]).columns
        
        for col in numerical_cols:
            col_stats = {
                'mean': float(df[col].mean()) if not pd.isna(df[col].mean()) else None,
                'std': float(df[col].std()) if not pd.isna(df[col].std()) else None,
                'min': float(df[col].min()) if not pd.isna(df[col].min()) else None,
                'max': float(df[col].max()) if not pd.isna(df[col].max()) else None,
                'median': float(df[col].median()) if not pd.isna(df[col].median()) else None,
                'q25': float(df[col].quantile(0.25)) if not pd.isna(df[col].quantile(0.25)) else None,
                'q75': float(df[col].quantile(0.75)) if not pd.isna(df[col].quantile(0.75)) else None,
            }
            stats[col] = col_stats
        
        return stats
    
    @staticmethod
    def get_correlations(df: pd.DataFrame) -> Dict[str, Dict[str, float]]:
        """Calculate correlation matrix for numerical columns."""
        numerical_df = df.select_dtypes(include=[np.number])
        if numerical_df.empty or len(numerical_df.columns) < 2:
            return {}
        
        corr_matrix = numerical_df.corr()
        return corr_matrix.to_dict()

