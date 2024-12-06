import os
import sys
from typing import Optional

class PathUtils:
    """Utility class for handling project paths"""
    
    _project_root: Optional[str] = None
    
    @classmethod
    def get_project_root(cls) -> str:
        """Get the project root directory
        
        Returns:
            str: Absolute path to project root
        """
        if cls._project_root is None:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            # Go up two levels (from utils/ to project root)
            cls._project_root = os.path.dirname(os.path.dirname(current_dir))
        return cls._project_root
    
    @classmethod
    def setup_python_path(cls) -> None:
        """Add project root to Python path"""
        project_root = cls.get_project_root()
        if project_root not in sys.path:
            sys.path.append(project_root)
    
    @classmethod
    def get_config_path(cls) -> str:
        """Get the path to config directory
        
        Returns:
            str: Absolute path to config directory
        """
        return os.path.join(cls.get_project_root(), "config")
    
    @classmethod
    def get_relative_path(cls, path: str) -> str:
        """Convert absolute path to relative path from project root
        
        Args:
            path: Absolute path
            
        Returns:
            str: Relative path from project root
        """
        return os.path.relpath(path, cls.get_project_root()) 