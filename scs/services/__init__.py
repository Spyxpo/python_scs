"""
SCS SDK Services
"""

from .auth import AuthService
from .database import DatabaseService, CollectionReference, DocumentReference
from .storage import StorageService, StorageReference
from .realtime import RealtimeService, RealtimeReference
from .messaging import MessagingService
from .remote_config import RemoteConfigService
from .functions import FunctionsService

__all__ = [
    "AuthService",
    "DatabaseService",
    "CollectionReference",
    "DocumentReference",
    "StorageService",
    "StorageReference",
    "RealtimeService",
    "RealtimeReference",
    "MessagingService",
    "RemoteConfigService",
    "FunctionsService",
]
