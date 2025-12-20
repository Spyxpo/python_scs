"""
SCS Cloud Messaging Service

Provides push notification functionality with topic-based and direct messaging.
"""

from typing import TYPE_CHECKING, Any, Dict, List, Optional

if TYPE_CHECKING:
    from ..client import SCS


class MessagingService:
    """
    Messaging service for push notifications.

    Usage:
        # Register device token
        scs.messaging.register_token(
            token='device-fcm-token',
            platform='android'
        )

        # Subscribe to topic
        scs.messaging.subscribe_to_topic('news', 'device-token')

        # Send to topic
        scs.messaging.send_to_topic(
            topic='news',
            title='Breaking News',
            body='Something happened!',
            data={'articleId': '123'}
        )

        # Send to specific device
        scs.messaging.send_to_token(
            token='device-token',
            title='Personal Alert',
            body='You have a new message'
        )
    """

    def __init__(self, scs: "SCS"):
        self._scs = scs

    # Token management

    def register_token(
        self,
        token: str,
        platform: str,
        device_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Register a device token for push notifications.

        Args:
            token: Device token (FCM, APNS, etc.)
            platform: Platform type ('android', 'ios', 'web')
            device_id: Optional unique device identifier
            metadata: Optional metadata about the device

        Returns:
            Registration confirmation
        """
        body = {
            "token": token,
            "platform": platform,
        }

        if device_id:
            body["deviceId"] = device_id
        if metadata:
            body["metadata"] = metadata

        return self._scs.request(
            "/api/messaging/tokens/register",
            method="POST",
            body=body,
        )

    def unregister_token(self, token: str) -> Dict[str, Any]:
        """
        Unregister a device token.

        Args:
            token: Device token to unregister

        Returns:
            Confirmation message
        """
        return self._scs.request(
            "/api/messaging/tokens/unregister",
            method="POST",
            body={"token": token},
        )

    def list_tokens(
        self,
        page: int = 1,
        limit: int = 20,
    ) -> Dict[str, Any]:
        """
        List registered device tokens.

        Args:
            page: Page number
            limit: Items per page

        Returns:
            Paginated list of tokens
        """
        return self._scs.request(
            "/api/messaging/tokens",
            params={"page": page, "limit": limit},
        )

    # Topic management

    def create_topic(
        self,
        name: str,
        description: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Create a new topic.

        Args:
            name: Topic name
            description: Optional description

        Returns:
            Created topic info
        """
        body = {"name": name}
        if description:
            body["description"] = description

        return self._scs.request(
            "/api/messaging/topics",
            method="POST",
            body=body,
        )

    def list_topics(
        self,
        page: int = 1,
        limit: int = 20,
    ) -> Dict[str, Any]:
        """
        List all topics.

        Args:
            page: Page number
            limit: Items per page

        Returns:
            Paginated list of topics
        """
        return self._scs.request(
            "/api/messaging/topics",
            params={"page": page, "limit": limit},
        )

    def get_topic(self, name: str) -> Dict[str, Any]:
        """
        Get topic details.

        Args:
            name: Topic name

        Returns:
            Topic details
        """
        return self._scs.request(f"/api/messaging/topics/{name}")

    def delete_topic(self, name: str) -> Dict[str, Any]:
        """
        Delete a topic.

        Args:
            name: Topic name

        Returns:
            Confirmation message
        """
        return self._scs.request(
            f"/api/messaging/topics/{name}",
            method="DELETE",
        )

    def subscribe_to_topic(
        self,
        topic: str,
        token: str,
    ) -> Dict[str, Any]:
        """
        Subscribe a device token to a topic.

        Args:
            topic: Topic name
            token: Device token

        Returns:
            Confirmation message
        """
        return self._scs.request(
            "/api/messaging/topics/subscribe",
            method="POST",
            body={
                "topic": topic,
                "token": token,
            },
        )

    def unsubscribe_from_topic(
        self,
        topic: str,
        token: str,
    ) -> Dict[str, Any]:
        """
        Unsubscribe a device token from a topic.

        Args:
            topic: Topic name
            token: Device token

        Returns:
            Confirmation message
        """
        return self._scs.request(
            "/api/messaging/topics/unsubscribe",
            method="POST",
            body={
                "topic": topic,
                "token": token,
            },
        )

    def get_subscriptions(self, token: str) -> Dict[str, Any]:
        """
        Get all topic subscriptions for a device token.

        Args:
            token: Device token

        Returns:
            List of subscribed topics
        """
        return self._scs.request(
            "/api/messaging/subscriptions",
            params={"token": token},
        )

    # Sending messages

    def send_to_topic(
        self,
        topic: str,
        title: str,
        body: str,
        data: Optional[Dict[str, Any]] = None,
        image: Optional[str] = None,
        badge: Optional[int] = None,
        sound: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Send a message to all devices subscribed to a topic.

        Args:
            topic: Topic name
            title: Notification title
            body: Notification body
            data: Optional custom data payload
            image: Optional image URL
            badge: Optional badge count (iOS)
            sound: Optional sound name

        Returns:
            Send result with message ID
        """
        message = {
            "topic": topic,
            "notification": {
                "title": title,
                "body": body,
            },
        }

        if data:
            message["data"] = data
        if image:
            message["notification"]["image"] = image
        if badge is not None:
            message["notification"]["badge"] = badge
        if sound:
            message["notification"]["sound"] = sound

        return self._scs.request(
            "/api/messaging/send",
            method="POST",
            body=message,
        )

    def send_to_token(
        self,
        token: str,
        title: str,
        body: str,
        data: Optional[Dict[str, Any]] = None,
        image: Optional[str] = None,
        badge: Optional[int] = None,
        sound: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Send a message to a specific device token.

        Args:
            token: Device token
            title: Notification title
            body: Notification body
            data: Optional custom data payload
            image: Optional image URL
            badge: Optional badge count (iOS)
            sound: Optional sound name

        Returns:
            Send result with message ID
        """
        message = {
            "token": token,
            "notification": {
                "title": title,
                "body": body,
            },
        }

        if data:
            message["data"] = data
        if image:
            message["notification"]["image"] = image
        if badge is not None:
            message["notification"]["badge"] = badge
        if sound:
            message["notification"]["sound"] = sound

        return self._scs.request(
            "/api/messaging/send/token",
            method="POST",
            body=message,
        )

    def send_to_tokens(
        self,
        tokens: List[str],
        title: str,
        body: str,
        data: Optional[Dict[str, Any]] = None,
        image: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Send a message to multiple device tokens.

        Args:
            tokens: List of device tokens
            title: Notification title
            body: Notification body
            data: Optional custom data payload
            image: Optional image URL

        Returns:
            Send results with success/failure counts
        """
        message = {
            "tokens": tokens,
            "notification": {
                "title": title,
                "body": body,
            },
        }

        if data:
            message["data"] = data
        if image:
            message["notification"]["image"] = image

        return self._scs.request(
            "/api/messaging/send",
            method="POST",
            body=message,
        )

    # Message history

    def list_messages(
        self,
        page: int = 1,
        limit: int = 20,
    ) -> Dict[str, Any]:
        """
        List sent messages.

        Args:
            page: Page number
            limit: Items per page

        Returns:
            Paginated list of messages
        """
        return self._scs.request(
            "/api/messaging/messages",
            params={"page": page, "limit": limit},
        )

    def get_message(self, message_id: str) -> Dict[str, Any]:
        """
        Get message details.

        Args:
            message_id: Message ID

        Returns:
            Message details
        """
        return self._scs.request(f"/api/messaging/messages/{message_id}")

    def delete_message(self, message_id: str) -> Dict[str, Any]:
        """
        Delete a message from history.

        Args:
            message_id: Message ID

        Returns:
            Confirmation message
        """
        return self._scs.request(
            f"/api/messaging/messages/{message_id}",
            method="DELETE",
        )

    # Statistics

    def get_stats(self) -> Dict[str, Any]:
        """
        Get messaging statistics.

        Returns:
            Statistics object with message counts, etc.
        """
        return self._scs.request("/api/messaging/stats")
