"""
SCS (Spyxpo Cloud Services) Python SDK Client
"""

import json
from pathlib import Path
from typing import Any, Dict, Optional, Union
from urllib.parse import urljoin

import requests

from .exceptions import (
    SCSError,
    AuthenticationError,
    NotFoundError,
    ValidationError,
)


class SCS:
    """
    Main SCS client class.

    Usage:
        # Initialize from config file
        scs = SCS.initialize_app('./scs-info.json')

        # Or initialize with config dict
        scs = SCS({
            'api_key': 'your-api-key',
            'project_id': 'your-project-id',
            'base_url': 'http://localhost:3001'
        })

        # Access services
        user = scs.auth.login(email='user@example.com', password='password')
        docs = scs.database.collection('users').get()
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize SCS client with configuration.

        Args:
            config: Configuration dictionary with api_key, project_id, and optional base_url
        """
        self._api_key = config.get("api_key")
        self._project_id = config.get("project_id")
        self._base_url = config.get("base_url", "http://localhost:3001")

        if not self._api_key:
            raise ValueError("api_key is required")
        if not self._project_id:
            raise ValueError("project_id is required")

        # Remove trailing slash from base URL
        self._base_url = self._base_url.rstrip("/")

        # User token for authenticated requests
        self._user_token: Optional[str] = None

        # Lazy-loaded services
        self._auth: Optional["AuthService"] = None
        self._database: Optional["DatabaseService"] = None
        self._storage: Optional["StorageService"] = None
        self._realtime: Optional["RealtimeService"] = None
        self._messaging: Optional["MessagingService"] = None
        self._remote_config: Optional["RemoteConfigService"] = None
        self._functions: Optional["FunctionsService"] = None
        self._ai: Optional["AIService"] = None
        self._ml: Optional["MLService"] = None
        self._calls: Optional["CallService"] = None

        # HTTP session for connection pooling
        self._session = requests.Session()

    @classmethod
    def initialize_app(cls, config_path: Union[str, Path]) -> "SCS":
        """
        Initialize SCS client from a configuration file.

        Args:
            config_path: Path to scs-info.json configuration file

        Returns:
            Initialized SCS client
        """
        config_path = Path(config_path)

        if not config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")

        with open(config_path, "r") as f:
            config_data = json.load(f)

        # Support multiple config formats
        if "sdk_config" in config_data:
            sdk_config = config_data["sdk_config"]
            return cls({
                "api_key": sdk_config.get("api_key"),
                "project_id": sdk_config.get("project_id"),
                "base_url": sdk_config.get("base_url", "http://localhost:3001"),
            })
        elif "client" in config_data and "project_info" in config_data:
            return cls({
                "api_key": config_data["client"].get("api_key"),
                "project_id": config_data["project_info"].get("project_id"),
                "base_url": config_data["project_info"].get("api_url", "http://localhost:3001"),
            })
        else:
            # Assume direct config format
            return cls(config_data)

    @property
    def api_key(self) -> str:
        """Get the API key."""
        return self._api_key

    @property
    def project_id(self) -> str:
        """Get the project ID."""
        return self._project_id

    @property
    def base_url(self) -> str:
        """Get the base URL."""
        return self._base_url

    @property
    def user_token(self) -> Optional[str]:
        """Get the current user token."""
        return self._user_token

    def set_user_token(self, token: Optional[str]) -> None:
        """
        Set the user authentication token.

        Args:
            token: JWT token or None to clear
        """
        self._user_token = token

    def _get_headers(self, include_auth: bool = True) -> Dict[str, str]:
        """
        Get request headers.

        Args:
            include_auth: Whether to include Authorization header if token exists

        Returns:
            Headers dictionary
        """
        headers = {
            "Content-Type": "application/json",
            "X-API-Key": self._api_key,
        }

        if include_auth and self._user_token:
            headers["Authorization"] = f"Bearer {self._user_token}"

        return headers

    def _handle_response(self, response: requests.Response) -> Any:
        """
        Handle HTTP response and raise appropriate exceptions.

        Args:
            response: HTTP response object

        Returns:
            Parsed JSON response

        Raises:
            SCSError: For various HTTP errors
        """
        try:
            data = response.json()
        except json.JSONDecodeError:
            data = {"message": response.text}

        if response.status_code >= 400:
            error_message = data.get("error") or data.get("message") or "Unknown error"

            if response.status_code == 401:
                raise AuthenticationError(
                    error_message,
                    status=response.status_code,
                    response=data,
                )
            elif response.status_code == 404:
                raise NotFoundError(
                    error_message,
                    status=response.status_code,
                    response=data,
                )
            elif response.status_code == 400:
                raise ValidationError(
                    error_message,
                    status=response.status_code,
                    response=data,
                )
            else:
                raise SCSError(
                    error_message,
                    status=response.status_code,
                    response=data,
                )

        return data

    def request(
        self,
        endpoint: str,
        method: str = "GET",
        body: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        include_auth: bool = True,
    ) -> Any:
        """
        Make an HTTP request to the SCS API.

        Args:
            endpoint: API endpoint (e.g., '/api/auth/project/login')
            method: HTTP method
            body: Request body (JSON)
            params: Query parameters
            headers: Additional headers
            include_auth: Whether to include Authorization header

        Returns:
            Parsed JSON response
        """
        url = urljoin(self._base_url + "/", endpoint.lstrip("/"))

        request_headers = self._get_headers(include_auth)
        if headers:
            request_headers.update(headers)

        response = self._session.request(
            method=method,
            url=url,
            json=body,
            params=params,
            headers=request_headers,
        )

        return self._handle_response(response)

    def upload_request(
        self,
        endpoint: str,
        files: Dict[str, Any],
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Any:
        """
        Make a multipart/form-data upload request.

        Args:
            endpoint: API endpoint
            files: Files to upload (dict of field_name: file_tuple)
            data: Additional form data
            headers: Additional headers

        Returns:
            Parsed JSON response
        """
        url = urljoin(self._base_url + "/", endpoint.lstrip("/"))

        request_headers = {
            "X-API-Key": self._api_key,
        }

        if self._user_token:
            request_headers["Authorization"] = f"Bearer {self._user_token}"

        if headers:
            request_headers.update(headers)

        response = self._session.post(
            url=url,
            files=files,
            data=data,
            headers=request_headers,
        )

        return self._handle_response(response)

    def download_request(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
    ) -> bytes:
        """
        Make a download request and return raw bytes.

        Args:
            endpoint: API endpoint
            params: Query parameters

        Returns:
            Raw bytes content
        """
        url = urljoin(self._base_url + "/", endpoint.lstrip("/"))

        headers = {
            "X-API-Key": self._api_key,
        }

        if self._user_token:
            headers["Authorization"] = f"Bearer {self._user_token}"

        response = self._session.get(
            url=url,
            params=params,
            headers=headers,
        )

        if response.status_code >= 400:
            self._handle_response(response)

        return response.content

    # Service properties (lazy loading)

    @property
    def auth(self) -> "AuthService":
        """Get the authentication service."""
        if self._auth is None:
            from .services.auth import AuthService
            self._auth = AuthService(self)
        return self._auth

    @property
    def database(self) -> "DatabaseService":
        """Get the database service."""
        if self._database is None:
            from .services.database import DatabaseService
            self._database = DatabaseService(self)
        return self._database

    @property
    def storage(self) -> "StorageService":
        """Get the storage service."""
        if self._storage is None:
            from .services.storage import StorageService
            self._storage = StorageService(self)
        return self._storage

    @property
    def realtime(self) -> "RealtimeService":
        """Get the realtime service."""
        if self._realtime is None:
            from .services.realtime import RealtimeService
            self._realtime = RealtimeService(self)
        return self._realtime

    @property
    def messaging(self) -> "MessagingService":
        """Get the messaging service."""
        if self._messaging is None:
            from .services.messaging import MessagingService
            self._messaging = MessagingService(self)
        return self._messaging

    @property
    def remote_config(self) -> "RemoteConfigService":
        """Get the remote config service."""
        if self._remote_config is None:
            from .services.remote_config import RemoteConfigService
            self._remote_config = RemoteConfigService(self)
        return self._remote_config

    @property
    def functions(self) -> "FunctionsService":
        """Get the functions service."""
        if self._functions is None:
            from .services.functions import FunctionsService
            self._functions = FunctionsService(self)
        return self._functions

    @property
    def ai(self) -> "AIService":
        """Get the AI service."""
        if self._ai is None:
            from .services.ai import AIService
            self._ai = AIService(self)
        return self._ai

    @property
    def ml(self) -> "MLService":
        """Get the ML service."""
        if self._ml is None:
            from .services.ml import MLService
            self._ml = MLService(self)
        return self._ml

    @property
    def calls(self) -> "CallService":
        """Get the calls service for voice/video calls, group calls, and live streaming."""
        if self._calls is None:
            from .services.calls import CallService
            self._calls = CallService(self)
        return self._calls

    def close(self) -> None:
        """Close the HTTP session and cleanup resources."""
        if self._realtime:
            self._realtime.disconnect()
        self._session.close()

    def __enter__(self) -> "SCS":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.close()
