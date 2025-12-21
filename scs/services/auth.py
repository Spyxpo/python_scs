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

    # OAuth and Social Sign-In Methods

    def sign_in_with_google(
        self,
        id_token: str,
        access_token: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Sign in with Google.

        Args:
            id_token: Google ID token from Google Sign-In
            access_token: Optional Google access token

        Returns:
            User object with token
        """
        body = {"idToken": id_token}
        if access_token:
            body["accessToken"] = access_token

        result = self._scs.request(
            "/api/auth/project/oauth/google",
            method="POST",
            body=body,
            include_auth=False,
        )

        if "token" in result:
            self._scs.set_user_token(result["token"])

        return result

    def sign_in_with_facebook(
        self,
        access_token: str,
    ) -> Dict[str, Any]:
        """
        Sign in with Facebook.

        Args:
            access_token: Facebook access token from Facebook Login

        Returns:
            User object with token
        """
        result = self._scs.request(
            "/api/auth/project/oauth/facebook",
            method="POST",
            body={"accessToken": access_token},
            include_auth=False,
        )

        if "token" in result:
            self._scs.set_user_token(result["token"])

        return result

    def sign_in_with_apple(
        self,
        identity_token: str,
        authorization_code: Optional[str] = None,
        full_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Sign in with Apple.

        Args:
            identity_token: Apple identity token
            authorization_code: Optional Apple authorization code
            full_name: Optional user's full name (first sign-in only)

        Returns:
            User object with token
        """
        body = {"identityToken": identity_token}
        if authorization_code:
            body["authorizationCode"] = authorization_code
        if full_name:
            body["fullName"] = full_name

        result = self._scs.request(
            "/api/auth/project/oauth/apple",
            method="POST",
            body=body,
            include_auth=False,
        )

        if "token" in result:
            self._scs.set_user_token(result["token"])

        return result

    def sign_in_with_github(
        self,
        code: str,
        redirect_uri: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Sign in with GitHub.

        Args:
            code: GitHub OAuth authorization code
            redirect_uri: Optional redirect URI used in OAuth flow

        Returns:
            User object with token
        """
        body = {"code": code}
        if redirect_uri:
            body["redirectUri"] = redirect_uri

        result = self._scs.request(
            "/api/auth/project/oauth/github",
            method="POST",
            body=body,
            include_auth=False,
        )

        if "token" in result:
            self._scs.set_user_token(result["token"])

        return result

    def sign_in_with_twitter(
        self,
        oauth_token: str,
        oauth_token_secret: str,
    ) -> Dict[str, Any]:
        """
        Sign in with Twitter/X.

        Args:
            oauth_token: Twitter OAuth token
            oauth_token_secret: Twitter OAuth token secret

        Returns:
            User object with token
        """
        result = self._scs.request(
            "/api/auth/project/oauth/twitter",
            method="POST",
            body={
                "oauthToken": oauth_token,
                "oauthTokenSecret": oauth_token_secret,
            },
            include_auth=False,
        )

        if "token" in result:
            self._scs.set_user_token(result["token"])

        return result

    def sign_in_with_microsoft(
        self,
        access_token: str,
        id_token: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Sign in with Microsoft.

        Args:
            access_token: Microsoft access token
            id_token: Optional Microsoft ID token

        Returns:
            User object with token
        """
        body = {"accessToken": access_token}
        if id_token:
            body["idToken"] = id_token

        result = self._scs.request(
            "/api/auth/project/oauth/microsoft",
            method="POST",
            body=body,
            include_auth=False,
        )

        if "token" in result:
            self._scs.set_user_token(result["token"])

        return result

    def sign_in_anonymously(
        self,
        custom_data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Sign in anonymously.
        Creates a temporary anonymous account that can be linked to a permanent account later.

        Args:
            custom_data: Optional custom data to store with the anonymous user

        Returns:
            User object with token
        """
        body = {}
        if custom_data:
            body["customData"] = custom_data

        result = self._scs.request(
            "/api/auth/project/anonymous",
            method="POST",
            body=body,
            include_auth=False,
        )

        if "token" in result:
            self._scs.set_user_token(result["token"])

        return result

    def send_phone_verification_code(
        self,
        phone_number: str,
        recaptcha_token: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Sign in with phone number - Step 1: Send verification code.

        Args:
            phone_number: Phone number in E.164 format (e.g., +1234567890)
            recaptcha_token: Optional reCAPTCHA token for verification

        Returns:
            Verification session info
        """
        body = {"phoneNumber": phone_number}
        if recaptcha_token:
            body["recaptchaToken"] = recaptcha_token

        return self._scs.request(
            "/api/auth/project/phone/send-code",
            method="POST",
            body=body,
            include_auth=False,
        )

    def sign_in_with_phone_number(
        self,
        verification_id: str,
        code: str,
    ) -> Dict[str, Any]:
        """
        Sign in with phone number - Step 2: Verify code and sign in.

        Args:
            verification_id: Verification ID from send_phone_verification_code
            code: SMS verification code

        Returns:
            User object with token
        """
        result = self._scs.request(
            "/api/auth/project/phone/verify",
            method="POST",
            body={
                "verificationId": verification_id,
                "code": code,
            },
            include_auth=False,
        )

        if "token" in result:
            self._scs.set_user_token(result["token"])

        return result

    def sign_in_with_custom_token(
        self,
        token: str,
    ) -> Dict[str, Any]:
        """
        Sign in with a custom token.

        Args:
            token: Custom JWT token generated by your backend

        Returns:
            User object with token
        """
        result = self._scs.request(
            "/api/auth/project/custom-token",
            method="POST",
            body={"token": token},
            include_auth=False,
        )

        if "token" in result:
            self._scs.set_user_token(result["token"])

        return result

    def link_provider(
        self,
        provider: str,
        credentials: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Link an OAuth provider to the current account.

        Args:
            provider: Provider name (google, facebook, apple, github, twitter, microsoft)
            credentials: Provider-specific credentials

        Returns:
            Updated user object
        """
        return self._scs.request(
            f"/api/auth/project/link/{provider}",
            method="POST",
            body=credentials,
        )

    def unlink_provider(
        self,
        provider: str,
    ) -> Dict[str, Any]:
        """
        Unlink an OAuth provider from the current account.

        Args:
            provider: Provider name to unlink

        Returns:
            Updated user object
        """
        return self._scs.request(
            f"/api/auth/project/unlink/{provider}",
            method="POST",
        )

    def fetch_sign_in_methods_for_email(
        self,
        email: str,
    ) -> Dict[str, Any]:
        """
        Get available sign-in methods for an email.

        Args:
            email: Email address to check

        Returns:
            List of sign-in methods for this email
        """
        return self._scs.request(
            "/api/auth/project/providers",
            method="POST",
            body={"email": email},
            include_auth=False,
        )

    def send_password_reset_email(
        self,
        email: str,
    ) -> Dict[str, Any]:
        """
        Send password reset email.

        Args:
            email: Email address to send reset link to

        Returns:
            Success response
        """
        return self._scs.request(
            "/api/auth/project/password-reset",
            method="POST",
            body={"email": email},
            include_auth=False,
        )

    def confirm_password_reset(
        self,
        code: str,
        new_password: str,
    ) -> Dict[str, Any]:
        """
        Confirm password reset with code.

        Args:
            code: Password reset code from email
            new_password: New password

        Returns:
            Success response
        """
        return self._scs.request(
            "/api/auth/project/password-reset/confirm",
            method="POST",
            body={
                "code": code,
                "newPassword": new_password,
            },
            include_auth=False,
        )

    def send_email_verification(self) -> Dict[str, Any]:
        """
        Send email verification.

        Returns:
            Success response
        """
        return self._scs.request(
            "/api/auth/project/verify-email",
            method="POST",
        )

    def verify_email(
        self,
        code: str,
    ) -> Dict[str, Any]:
        """
        Verify email with code.

        Args:
            code: Email verification code

        Returns:
            Success response
        """
        return self._scs.request(
            "/api/auth/project/verify-email/confirm",
            method="POST",
            body={"code": code},
        )

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
