"""
SCS Remote Config Service

Provides dynamic app configuration without redeployment.
"""

from typing import TYPE_CHECKING, Any, Dict, List, Optional, Union

if TYPE_CHECKING:
    from ..client import SCS


class RemoteConfigService:
    """
    Remote config service for dynamic configuration.

    Usage:
        # Fetch current config
        config = scs.remote_config.fetch()

        # Get specific value
        theme = scs.remote_config.get('app_theme', default='light')

        # Admin: Create parameter
        scs.remote_config.create_param(
            key='app_theme',
            value='dark',
            description='Default app theme'
        )

        # Admin: Update parameter
        scs.remote_config.update_param('app_theme', 'light')

        # Admin: Publish changes
        scs.remote_config.publish()
    """

    def __init__(self, scs: "SCS"):
        self._scs = scs
        self._cache: Dict[str, Any] = {}
        self._last_fetch: Optional[float] = None

    def fetch(self) -> Dict[str, Any]:
        """
        Fetch the current remote configuration.

        Returns:
            Configuration parameters as a dictionary
        """
        import time

        result = self._scs.request("/api/remoteConfig")

        # Cache the result
        if "parameters" in result:
            self._cache = {
                param["key"]: param.get("value")
                for param in result["parameters"]
            }
        elif isinstance(result, dict):
            self._cache = result

        self._last_fetch = time.time()

        return self._cache

    def get(
        self,
        key: str,
        default: Any = None,
    ) -> Any:
        """
        Get a configuration value.

        Args:
            key: Configuration key
            default: Default value if key not found

        Returns:
            Configuration value or default
        """
        if not self._cache:
            self.fetch()

        return self._cache.get(key, default)

    def get_string(self, key: str, default: str = "") -> str:
        """
        Get a string configuration value.

        Args:
            key: Configuration key
            default: Default value

        Returns:
            String value
        """
        value = self.get(key, default)
        return str(value) if value is not None else default

    def get_int(self, key: str, default: int = 0) -> int:
        """
        Get an integer configuration value.

        Args:
            key: Configuration key
            default: Default value

        Returns:
            Integer value
        """
        value = self.get(key, default)
        try:
            return int(value)
        except (TypeError, ValueError):
            return default

    def get_float(self, key: str, default: float = 0.0) -> float:
        """
        Get a float configuration value.

        Args:
            key: Configuration key
            default: Default value

        Returns:
            Float value
        """
        value = self.get(key, default)
        try:
            return float(value)
        except (TypeError, ValueError):
            return default

    def get_bool(self, key: str, default: bool = False) -> bool:
        """
        Get a boolean configuration value.

        Args:
            key: Configuration key
            default: Default value

        Returns:
            Boolean value
        """
        value = self.get(key, default)

        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            return value.lower() in ("true", "1", "yes", "on")
        if isinstance(value, (int, float)):
            return bool(value)

        return default

    def get_json(self, key: str, default: Any = None) -> Any:
        """
        Get a JSON configuration value.

        Args:
            key: Configuration key
            default: Default value

        Returns:
            Parsed JSON value
        """
        import json

        value = self.get(key, default)

        if isinstance(value, str):
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return default

        return value if value is not None else default

    def get_all(self) -> Dict[str, Any]:
        """
        Get all configuration values.

        Returns:
            All configuration parameters
        """
        if not self._cache:
            self.fetch()
        return self._cache.copy()

    # Admin methods

    def list_params(
        self,
        page: int = 1,
        limit: int = 50,
    ) -> Dict[str, Any]:
        """
        List all configuration parameters (admin).

        Args:
            page: Page number
            limit: Items per page

        Returns:
            Paginated list of parameters
        """
        return self._scs.request(
            "/api/remoteConfig/params",
            params={"page": page, "limit": limit},
        )

    def create_param(
        self,
        key: str,
        value: Any,
        description: Optional[str] = None,
        value_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Create a new configuration parameter (admin).

        Args:
            key: Parameter key
            value: Parameter value
            description: Optional description
            value_type: Optional type hint ('string', 'number', 'boolean', 'json')

        Returns:
            Created parameter
        """
        body = {
            "key": key,
            "value": value,
        }

        if description:
            body["description"] = description
        if value_type:
            body["valueType"] = value_type

        return self._scs.request(
            "/api/remoteConfig/params",
            method="POST",
            body=body,
        )

    def update_param(
        self,
        key: str,
        value: Any,
        description: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Update a configuration parameter (admin).

        Args:
            key: Parameter key
            value: New value
            description: Optional new description

        Returns:
            Updated parameter
        """
        body = {"value": value}

        if description:
            body["description"] = description

        return self._scs.request(
            f"/api/remoteConfig/params/{key}",
            method="PUT",
            body=body,
        )

    def delete_param(self, key: str) -> Dict[str, Any]:
        """
        Delete a configuration parameter (admin).

        Args:
            key: Parameter key

        Returns:
            Confirmation message
        """
        return self._scs.request(
            f"/api/remoteConfig/params/{key}",
            method="DELETE",
        )

    def publish(self) -> Dict[str, Any]:
        """
        Publish configuration changes (admin).

        Makes draft changes live for all clients.

        Returns:
            Publish confirmation with version info
        """
        return self._scs.request(
            "/api/remoteConfig/publish",
            method="POST",
        )

    def list_versions(
        self,
        page: int = 1,
        limit: int = 20,
    ) -> Dict[str, Any]:
        """
        List configuration versions (admin).

        Args:
            page: Page number
            limit: Items per page

        Returns:
            Paginated list of versions
        """
        return self._scs.request(
            "/api/remoteConfig/versions",
            params={"page": page, "limit": limit},
        )

    def rollback(self, version_id: str) -> Dict[str, Any]:
        """
        Rollback to a previous version (admin).

        Args:
            version_id: Version ID to rollback to

        Returns:
            Rollback confirmation
        """
        return self._scs.request(
            f"/api/remoteConfig/rollback/{version_id}",
            method="POST",
        )

    def get_stats(self) -> Dict[str, Any]:
        """
        Get remote config statistics (admin).

        Returns:
            Statistics object
        """
        return self._scs.request("/api/remoteConfig/stats")
