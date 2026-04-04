"""
AI Service - AI chat, text completion, and AI agents
"""

from typing import Any, Dict, List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from ..client import SCS


class AIService:
    """
    AI service for chat, text completion, image generation, and AI agents.

    Usage:
        # Chat
        response = scs.ai.chat(message="Hello, world!")

        # Complete text
        response = scs.ai.complete(prompt="Once upon a time")

        # Generate image
        response = scs.ai.generate_image(prompt="A sunset over mountains")

        # Create an agent
        agent = scs.ai.create_agent(
            name="Assistant",
            instructions="You are a helpful assistant."
        )

        # Run agent
        response = scs.ai.run_agent(agent_id="...", input="Hello!")
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

    # ==================== AI AGENTS ====================

    def create_agent(
        self,
        name: str,
        instructions: Optional[str] = None,
        description: Optional[str] = None,
        model: Optional[str] = None,
        tools: Optional[List[str]] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Create a new AI agent.

        Args:
            name: Agent name
            instructions: System instructions for the agent
            description: Agent description
            model: AI model to use
            tools: List of tool IDs the agent can use
            temperature: Temperature (0-1)
            max_tokens: Maximum tokens for responses
            metadata: Additional metadata

        Returns:
            Created agent
        """
        body: Dict[str, Any] = {"name": name}
        if instructions:
            body["instructions"] = instructions
        if description:
            body["description"] = description
        if model:
            body["model"] = model
        if tools:
            body["tools"] = tools
        if temperature is not None:
            body["temperature"] = temperature
        if max_tokens:
            body["maxTokens"] = max_tokens
        if metadata:
            body["metadata"] = metadata

        response = self._client.request("/api/ai/agents", method="POST", body=body)
        return response.get("agent", response)

    def list_agents(
        self,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        status: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        List all agents.

        Args:
            limit: Maximum number of agents
            offset: Number to skip
            status: Filter by status (active, inactive)

        Returns:
            List of agents
        """
        params = {}
        if limit:
            params["limit"] = limit
        if offset:
            params["offset"] = offset
        if status:
            params["status"] = status

        response = self._client.request("/api/ai/agents", params=params)
        return response.get("agents", [])

    def get_agent(self, agent_id: str) -> Dict[str, Any]:
        """
        Get an agent by ID.

        Args:
            agent_id: Agent ID

        Returns:
            Agent details
        """
        response = self._client.request(f"/api/ai/agents/{agent_id}")
        return response.get("agent", response)

    def update_agent(
        self,
        agent_id: str,
        name: Optional[str] = None,
        instructions: Optional[str] = None,
        description: Optional[str] = None,
        model: Optional[str] = None,
        tools: Optional[List[str]] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None,
        status: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Update an agent.

        Args:
            agent_id: Agent ID
            name: Agent name
            instructions: System instructions
            description: Agent description
            model: AI model to use
            tools: List of tool IDs
            temperature: Temperature (0-1)
            max_tokens: Maximum tokens
            metadata: Additional metadata
            status: Agent status (active, inactive)

        Returns:
            Updated agent
        """
        body: Dict[str, Any] = {}
        if name:
            body["name"] = name
        if instructions:
            body["instructions"] = instructions
        if description:
            body["description"] = description
        if model:
            body["model"] = model
        if tools is not None:
            body["tools"] = tools
        if temperature is not None:
            body["temperature"] = temperature
        if max_tokens:
            body["maxTokens"] = max_tokens
        if metadata:
            body["metadata"] = metadata
        if status:
            body["status"] = status

        response = self._client.request(
            f"/api/ai/agents/{agent_id}",
            method="PUT",
            body=body
        )
        return response.get("agent", response)

    def delete_agent(self, agent_id: str) -> bool:
        """
        Delete an agent.

        Args:
            agent_id: Agent ID

        Returns:
            True if successful
        """
        self._client.request(f"/api/ai/agents/{agent_id}", method="DELETE")
        return True

    def run_agent(
        self,
        agent_id: str,
        input: str,
        session_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Run an agent with input.

        Args:
            agent_id: Agent ID
            input: User input message
            session_id: Session ID for conversation continuity
            context: Additional context data

        Returns:
            Agent response with output and session ID
        """
        body: Dict[str, Any] = {"input": input}
        if session_id:
            body["sessionId"] = session_id
        if context:
            body["context"] = context

        return self._client.request(
            f"/api/ai/agents/{agent_id}/run",
            method="POST",
            body=body
        )

    def list_agent_sessions(
        self,
        agent_id: str,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """
        List sessions for an agent.

        Args:
            agent_id: Agent ID
            limit: Maximum number of sessions
            offset: Number to skip

        Returns:
            List of sessions
        """
        params = {}
        if limit:
            params["limit"] = limit
        if offset:
            params["offset"] = offset

        response = self._client.request(
            f"/api/ai/agents/{agent_id}/sessions",
            params=params
        )
        return response.get("sessions", [])

    def get_agent_session(
        self,
        agent_id: str,
        session_id: str,
    ) -> Dict[str, Any]:
        """
        Get an agent session with full message history.

        Args:
            agent_id: Agent ID
            session_id: Session ID

        Returns:
            Session with messages
        """
        response = self._client.request(
            f"/api/ai/agents/{agent_id}/sessions/{session_id}"
        )
        return response.get("session", response)

    def delete_agent_session(
        self,
        agent_id: str,
        session_id: str,
    ) -> bool:
        """
        Delete an agent session.

        Args:
            agent_id: Agent ID
            session_id: Session ID

        Returns:
            True if successful
        """
        self._client.request(
            f"/api/ai/agents/{agent_id}/sessions/{session_id}",
            method="DELETE"
        )
        return True

    # Agent Tools

    def define_tool(
        self,
        name: str,
        description: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Define a tool that agents can use.

        Args:
            name: Tool name
            description: Tool description
            parameters: JSON schema for tool parameters

        Returns:
            Created tool
        """
        body: Dict[str, Any] = {"name": name}
        if description:
            body["description"] = description
        if parameters:
            body["parameters"] = parameters

        response = self._client.request("/api/ai/tools", method="POST", body=body)
        return response.get("tool", response)

    def list_tools(self) -> List[Dict[str, Any]]:
        """
        List all defined tools.

        Returns:
            List of tools
        """
        response = self._client.request("/api/ai/tools")
        return response.get("tools", [])

    def delete_tool(self, tool_id: str) -> bool:
        """
        Delete a tool.

        Args:
            tool_id: Tool ID

        Returns:
            True if successful
        """
        self._client.request(f"/api/ai/tools/{tool_id}", method="DELETE")
        return True

    # ==================== TTS & STT ====================

    def text_to_speech(
        self,
        text: str,
        voice: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Convert text to speech.

        Args:
            text: Text to convert to speech
            voice: Voice preset (optional, defaults to 'v2/en_speaker_6')

        Returns:
            TTS response with base64 encoded audio data
        """
        body: Dict[str, Any] = {"text": text}
        if voice:
            body["voice"] = voice

        return self._client.request("/api/ai/tts", method="POST", body=body)

    def speech_to_text(
        self,
        audio: str,
    ) -> Dict[str, Any]:
        """
        Convert speech to text.

        Args:
            audio: Base64 encoded audio data

        Returns:
            STT response with transcribed text
        """
        body = {"audio": audio}
        return self._client.request("/api/ai/stt", method="POST", body=body)

    # ==================== PROVIDER SETTINGS ====================

    def get_provider_settings(self) -> Dict[str, Any]:
        """
        Get the LLM provider configured for this project.

        Supported providers: huggingface, openai, groq, anthropic, google,
            together, mistral, openrouter, custom

        Returns:
            Dict with 'settings' (current config) and 'supportedProviders' list.
            Note: the API key is never returned — only 'hasApiKey' boolean.
        """
        return self._client.request("/api/ai/settings/provider")

    def update_provider_settings(
        self,
        provider: str,
        api_key: str,
        model: Optional[str] = None,
        base_url: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Configure which LLM provider this project uses.

        Args:
            provider:  Provider ID — one of: huggingface, openai, groq,
                       anthropic, google, together, mistral, openrouter, custom
            api_key:   API key or token for the provider
                       (Hugging Face: hf_xxx from huggingface.co/settings/tokens)
            model:     Default model ID to use (optional, provider default used if omitted)
            base_url:  Custom base URL — only needed when provider='custom'

        Returns:
            Dict with 'message' confirming the update.

        Example::

            scs.ai.update_provider_settings(
                provider="huggingface",
                api_key="hf_...",
                model="meta-llama/Llama-3.2-3B-Instruct",
            )
        """
        body: Dict[str, Any] = {"provider": provider, "apiKey": api_key}
        if model:
            body["model"] = model
        if base_url:
            body["baseUrl"] = base_url
        return self._client.request("/api/ai/settings/provider", method="PUT", body=body)
