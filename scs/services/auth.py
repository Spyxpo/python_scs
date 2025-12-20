"""
SCS Authentication Service
"""

from typing import TYPE_CHECKING, Any, Dict, List, Optional

if TYPE_CHECKING:
    from ..client import SCS


class AuthService:
    """
    Authentication service for user management.

    Usage:
        # Register a new user
        user = scs.auth.register(
            email='user@example.com',
            password='password123',
            display_name='John Doe'
        )

        # Login
        user = scs.auth.login(email='user@example.com', password='password123')

        # Get current user
        me = scs.auth.get_current_user()

        # Update profile
        scs.auth.update_profile(display_name='Jane Doe')

        # Logout
        scs.auth.logout()
    """

    def __init__(self, scs: "SCS"):
        self._scs = scs

    def register(
        self,
        email: str,
        password: str,
        display_name: Optional[str] = None,
        custom_data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Register a new user.

        Args:
            email: User email
            password: User password
            display_name: Optional display name
            custom_data: Optional custom data to store with user

        Returns:
            User object with token
        """
        body = {
            "email": email,
            "password": password,
        }

        if display_name:
            body["displayName"] = display_name
        if custom_data:
            body["customData"] = custom_data

        result = self._scs.request(
            "/api/auth/project/register",
            method="POST",
            body=body,
            include_auth=False,
        )

        # Auto-set user token
        if "token" in result:
            self._scs.set_user_token(result["token"])

        return result

    def login(
        self,
        email: str,
        password: str,
    ) -> Dict[str, Any]:
        """
        Login a user.

        Args:
            email: User email
            password: User password

        Returns:
            User object with token
        """
        result = self._scs.request(
            "/api/auth/project/login",
            method="POST",
            body={
                "email": email,
                "password": password,
            },
            include_auth=False,
        )

        # Auto-set user token
        if "token" in result:
            self._scs.set_user_token(result["token"])

        return result

    def logout(self) -> None:
        """
        Logout the current user (clears the stored token).
        """
        self._scs.set_user_token(None)

    def get_current_user(self) -> Dict[str, Any]:
        """
        Get the currently authenticated user.

        Returns:
            User object
        """
        return self._scs.request("/api/auth/project/me")

    def update_profile(
        self,
        display_name: Optional[str] = None,
        custom_data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Update the current user's profile.

        Args:
            display_name: New display name
            custom_data: Custom data to update

        Returns:
            Updated user object
        """
        body = {}

        if display_name is not None:
            body["displayName"] = display_name
        if custom_data is not None:
            body["customData"] = custom_data

        return self._scs.request(
            "/api/auth/project/profile",
            method="PUT",
            body=body,
        )

    def change_password(
        self,
        current_password: str,
        new_password: str,
    ) -> Dict[str, Any]:
        """
        Change the current user's password.

        Args:
            current_password: Current password
            new_password: New password

        Returns:
            Success message
        """
        return self._scs.request(
            "/api/auth/project/password",
            method="PUT",
            body={
                "currentPassword": current_password,
                "newPassword": new_password,
            },
        )

    def delete_account(self) -> Dict[str, Any]:
        """
        Delete the current user's account.

        Returns:
            Success message
        """
        result = self._scs.request(
            "/api/auth/project/account",
            method="DELETE",
        )

        # Clear token after deletion
        self._scs.set_user_token(None)

        return result

    # Admin methods

    def list_users(
        self,
        page: int = 1,
        limit: int = 20,
        search: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        List all users (admin only).

        Args:
            page: Page number
            limit: Items per page
            search: Optional search query

        Returns:
            Paginated list of users
        """
        params = {
            "page": page,
            "limit": limit,
        }

        if search:
            params["search"] = search

        return self._scs.request(
            "/api/auth/project/users",
            params=params,
        )

    def get_user(self, uid: str) -> Dict[str, Any]:
        """
        Get a specific user by ID (admin only).

        Args:
            uid: User ID

        Returns:
            User object
        """
        return self._scs.request(f"/api/auth/project/users/{uid}")

    def update_user_status(
        self,
        uid: str,
        disabled: bool,
    ) -> Dict[str, Any]:
        """
        Enable or disable a user (admin only).

        Args:
            uid: User ID
            disabled: Whether to disable the user

        Returns:
            Updated user object
        """
        return self._scs.request(
            f"/api/auth/project/users/{uid}/status",
            method="PUT",
            body={"disabled": disabled},
        )

    def delete_user(self, uid: str) -> Dict[str, Any]:
        """
        Delete a user (admin only).

        Args:
            uid: User ID

        Returns:
            Success message
        """
        return self._scs.request(
            f"/api/auth/project/users/{uid}",
            method="DELETE",
        )
