"""
SCS SDK Exceptions
"""

from typing import Any, Optional


class SCSError(Exception):
    """Base exception for all SCS SDK errors."""

    def __init__(
        self,
        message: str,
        status: Optional[int] = None,
        response: Optional[Any] = None,
    ):
        super().__init__(message)
        self.message = message
        self.status = status
        self.response = response

    def __str__(self) -> str:
        if self.status:
            return f"[{self.status}] {self.message}"
        return self.message


class AuthenticationError(SCSError):
    """Raised when authentication fails."""

    pass


class NotFoundError(SCSError):
    """Raised when a resource is not found."""

    pass


class ValidationError(SCSError):
    """Raised when validation fails."""

    pass


class ConnectionError(SCSError):
    """Raised when connection to the server fails."""

    pass
