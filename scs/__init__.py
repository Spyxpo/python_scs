"""
SCS (Spyxpo Cloud Services) Python SDK

A self-hosted, Firebase-like Backend-as-a-Service SDK for Python.
"""

from .client import SCS
from .exceptions import SCSError, AuthenticationError, NotFoundError, ValidationError

__version__ = "1.0.0"
__all__ = [
    "SCS",
    "SCSError",
    "AuthenticationError",
    "NotFoundError",
    "ValidationError",
]
