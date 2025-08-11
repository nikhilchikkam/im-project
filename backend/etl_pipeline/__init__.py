"""
ETL Pipeline for OneWorldSync to DigitalOcean Spaces
"""

from .etl_orchestrator import OneWorldSyncETL
from .config import ETLConfig
from .spaces_manager import SpacesManager
from .ows_client import OneWorldSyncClient
from .sync_manager import SyncManager

__version__ = "1.0.0"
__all__ = [
    "OneWorldSyncETL",
    "ETLConfig", 
    "SpacesManager",
    "OneWorldSyncClient",
    "SyncManager"
] 