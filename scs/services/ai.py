"""
AI Service - AI chat and text completion
"""

from typing import Any, Dict, List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from ..client import SCS


class AIService:
    """
    AI service for chat, text completion, and image generation.

    Usage:
        # Chat
        response = scs.ai.chat(message="Hello, world!")

        # Complete text
        response = scs.ai.complete(prompt="Once upon a time")

        # Generate image
        response = scs.ai.generate_image(prompt="A sunset over mountains")
    """

    def __init__(self, client: "SCS"):
        self._client = client

    def chat(
        self,
        message: str,
        model: Optional[str] = None,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        conversation_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Send a chat message.

        Args:
            message: User message
            model: AI model to use
            system_prompt: System prompt for context
            temperature: Temperature (0-1)
            conversation_id: Conversation ID for context

        Returns:
            Chat response with reply
        """
        body = {"message": message}
        if model:
            body["model"] = model
        if system_prompt:
            body["systemPrompt"] = system_prompt
        if temperature is not None:
            body["temperature"] = temperature
        if conversation_id:
            body["conversationId"] = conversation_id

        return self._client.request("/api/ai/chat", method="POST", body=body)

    def complete(
        self,
        prompt: str,
        model: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
    ) -> Dict[str, Any]:
        """
        Complete text.

        Args:
            prompt: Text prompt
            model: AI model to use
            max_tokens: Maximum tokens to generate
            temperature: Temperature (0-1)

        Returns:
            Completion response
        """
        body = {"prompt": prompt}
        if model:
            body["model"] = model
        if max_tokens:
            body["maxTokens"] = max_tokens
        if temperature is not None:
            body["temperature"] = temperature

        return self._client.request("/api/ai/complete", method="POST", body=body)

    def generate_image(
        self,
        prompt: str,
        model: Optional[str] = None,
        size: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Generate an image.

        Args:
            prompt: Image description
            model: AI model to use
            size: Image size (256x256, 512x512, 1024x1024)

        Returns:
            Image generation response with URL
        """
        body = {"prompt": prompt}
        if model:
            body["model"] = model
        if size:
            body["size"] = size

        return self._client.request("/api/ai/generate-image", method="POST", body=body)

    def list_models(self) -> List[Dict[str, Any]]:
        """
        List available AI models.

        Returns:
            List of available models
        """
        response = self._client.request("/api/ai/models")
        return response.get("models", [])

    def pull_model(self, model_name: str) -> Dict[str, Any]:
        """
        Pull a model (download to local).

        Args:
            model_name: Name of the model to pull

        Returns:
            Pull status response
        """
        return self._client.request(
            "/api/ai/models/pull",
            method="POST",
            body={"name": model_name}
        )

    # Conversation management

    def list_conversations(
        self,
        limit: Optional[int] = None,
        skip: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """
        List conversations.

        Args:
            limit: Maximum number of conversations
            skip: Number to skip

        Returns:
            List of conversations
        """
        params = {}
        if limit:
            params["limit"] = limit
        if skip:
            params["skip"] = skip

        response = self._client.request("/api/ai/conversations", params=params)
        return response.get("conversations", [])

    def create_conversation(
        self,
        title: Optional[str] = None,
        model: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Create a new conversation.

        Args:
            title: Conversation title
            model: AI model to use

        Returns:
            Created conversation
        """
        body = {}
        if title:
            body["title"] = title
        if model:
            body["model"] = model

        response = self._client.request(
            "/api/ai/conversations",
            method="POST",
            body=body
        )
        return response.get("conversation", response)

    def get_conversation(self, conversation_id: str) -> Dict[str, Any]:
        """
        Get a conversation by ID.

        Args:
            conversation_id: Conversation ID

        Returns:
            Conversation with messages
        """
        response = self._client.request(f"/api/ai/conversations/{conversation_id}")
        return response.get("conversation", response)

    def delete_conversation(self, conversation_id: str) -> bool:
        """
        Delete a conversation.

        Args:
            conversation_id: Conversation ID

        Returns:
            True if successful
        """
        self._client.request(
            f"/api/ai/conversations/{conversation_id}",
            method="DELETE"
        )
        return True

    def get_stats(self) -> Dict[str, Any]:
        """
        Get AI statistics.

        Returns:
            AI usage statistics
        """
        response = self._client.request("/api/ai/stats")
        return response.get("stats", response)
