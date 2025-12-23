"""
SCS Call Service - Voice/Video Calls, Group Calls, and Live Streaming

This service provides server-side management of calls. For client-side WebRTC
functionality, use the JavaScript, Flutter, Android, or iOS SDKs.
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from ..client import SCS


class CallType(Enum):
    """Call types."""
    VOICE = "voice"
    VIDEO = "video"
    LIVESTREAM = "livestream"


class CallMode(Enum):
    """Call modes."""
    P2P = "p2p"
    GROUP = "group"
    BROADCAST = "broadcast"


class ParticipantRole(Enum):
    """Participant roles."""
    HOST = "host"
    CO_HOST = "co-host"
    PARTICIPANT = "participant"
    VIEWER = "viewer"


@dataclass
class Call:
    """Call data model."""
    call_id: str
    room_id: str
    project_id: str
    type: CallType
    mode: CallMode
    status: str
    host_id: Optional[str]
    host_display_name: Optional[str]
    max_participants: int
    settings: Dict[str, Any]
    started_at: Optional[str]
    ended_at: Optional[str]
    duration: int
    created_at: str

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Call":
        """Create a Call from a dictionary."""
        return cls(
            call_id=data.get("callId", ""),
            room_id=data.get("roomId", ""),
            project_id=data.get("projectId", ""),
            type=CallType(data.get("type", "video")),
            mode=CallMode(data.get("mode", "group")),
            status=data.get("status", ""),
            host_id=data.get("hostId"),
            host_display_name=data.get("hostDisplayName"),
            max_participants=data.get("maxParticipants", 50),
            settings=data.get("settings", {}),
            started_at=data.get("startedAt"),
            ended_at=data.get("endedAt"),
            duration=data.get("duration", 0),
            created_at=data.get("createdAt", ""),
        )


@dataclass
class Participant:
    """Participant data model."""
    participant_id: str
    user_id: Optional[str]
    display_name: str
    role: ParticipantRole
    status: str
    media_state: Dict[str, bool]
    joined_at: str
    left_at: Optional[str]
    duration: int

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Participant":
        """Create a Participant from a dictionary."""
        role_str = data.get("role", "participant")
        try:
            role = ParticipantRole(role_str)
        except ValueError:
            role = ParticipantRole.PARTICIPANT

        return cls(
            participant_id=data.get("participantId", ""),
            user_id=data.get("userId"),
            display_name=data.get("displayName", ""),
            role=role,
            status=data.get("status", ""),
            media_state=data.get("mediaState", {}),
            joined_at=data.get("joinedAt", ""),
            left_at=data.get("leftAt"),
            duration=data.get("duration", 0),
        )


@dataclass
class CallToken:
    """Call token data."""
    token: str
    token_id: str
    role: ParticipantRole
    permissions: List[str]
    expires_at: str

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CallToken":
        """Create a CallToken from a dictionary."""
        role_str = data.get("role", "participant")
        try:
            role = ParticipantRole(role_str)
        except ValueError:
            role = ParticipantRole.PARTICIPANT

        return cls(
            token=data.get("token", ""),
            token_id=data.get("tokenId", ""),
            role=role,
            permissions=data.get("permissions", []),
            expires_at=data.get("expiresAt", ""),
        )


@dataclass
class CallStats:
    """Call service statistics."""
    total_calls: int
    active_calls: int
    total_minutes: int
    recordings: int

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CallStats":
        """Create CallStats from a dictionary."""
        return cls(
            total_calls=data.get("totalCalls", 0),
            active_calls=data.get("activeCalls", 0),
            total_minutes=data.get("totalMinutes", 0),
            recordings=data.get("recordings", 0),
        )


@dataclass
class CallRecording:
    """Recording data."""
    recording_id: str
    call_id: str
    type: str
    format: str
    status: str
    duration: Optional[int]
    size: Optional[int]
    url: Optional[str]
    started_at: str
    stopped_at: Optional[str]

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CallRecording":
        """Create a CallRecording from a dictionary."""
        return cls(
            recording_id=data.get("recordingId", ""),
            call_id=data.get("callId", ""),
            type=data.get("type", ""),
            format=data.get("format", ""),
            status=data.get("status", ""),
            duration=data.get("duration"),
            size=data.get("size"),
            url=data.get("url"),
            started_at=data.get("startedAt", ""),
            stopped_at=data.get("stoppedAt"),
        )


@dataclass
class TranscriptionSegment:
    """Transcription segment."""
    participant_id: str
    display_name: str
    text: str
    timestamp: str
    confidence: Optional[float]

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TranscriptionSegment":
        """Create a TranscriptionSegment from a dictionary."""
        return cls(
            participant_id=data.get("participantId", ""),
            display_name=data.get("displayName", ""),
            text=data.get("text", ""),
            timestamp=data.get("timestamp", ""),
            confidence=data.get("confidence"),
        )


@dataclass
class TranscriptionAnalysis:
    """AI analysis of transcription."""
    summary: Optional[str]
    topics: Optional[List[str]]
    sentiment: Optional[str]
    action_items: Optional[List[str]]

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TranscriptionAnalysis":
        """Create a TranscriptionAnalysis from a dictionary."""
        return cls(
            summary=data.get("summary"),
            topics=data.get("topics"),
            sentiment=data.get("sentiment"),
            action_items=data.get("actionItems"),
        )


@dataclass
class CallTranscription:
    """Transcription data."""
    transcription_id: str
    call_id: str
    status: str
    segments: List[TranscriptionSegment]
    full_text: Optional[str]
    analysis: Optional[TranscriptionAnalysis]

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CallTranscription":
        """Create a CallTranscription from a dictionary."""
        segments = [TranscriptionSegment.from_dict(s) for s in data.get("segments", [])]
        analysis = None
        if data.get("analysis"):
            analysis = TranscriptionAnalysis.from_dict(data["analysis"])

        return cls(
            transcription_id=data.get("transcriptionId", ""),
            call_id=data.get("callId", ""),
            status=data.get("status", ""),
            segments=segments,
            full_text=data.get("fullText"),
            analysis=analysis,
        )


@dataclass
class TurnServer:
    """TURN server configuration."""
    urls: List[str]
    username: Optional[str]
    credential: Optional[str]

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TurnServer":
        """Create a TurnServer from a dictionary."""
        return cls(
            urls=data.get("urls", []),
            username=data.get("username"),
            credential=data.get("credential"),
        )


class CallService:
    """
    Call service for managing voice/video calls, group calls, and live streaming.

    This service provides server-side call management capabilities. For real-time
    WebRTC functionality (joining calls, media streaming), use the client SDKs
    (JavaScript, Flutter, Android, iOS).

    Example:
        # Create a call
        call = scs.calls.create_call(
            call_type=CallType.VIDEO,
            mode=CallMode.GROUP,
            display_name="Host Name"
        )

        # Generate token for a participant
        token = scs.calls.generate_token(
            call_id=call.call_id,
            display_name="Participant Name",
            role=ParticipantRole.PARTICIPANT
        )

        # List active calls
        calls = scs.calls.list_calls(status="active")

        # End a call
        scs.calls.end_call(call_id=call.call_id)
    """

    def __init__(self, client: "SCS"):
        """
        Initialize the call service.

        Args:
            client: SCS client instance
        """
        self._client = client

    def get_stats(self) -> CallStats:
        """
        Get call service statistics.

        Returns:
            CallStats object with usage statistics
        """
        response = self._client.request("/api/calls/stats")
        return CallStats.from_dict(response.get("stats", {}))

    def create_call(
        self,
        call_type: CallType = CallType.VIDEO,
        mode: CallMode = CallMode.GROUP,
        display_name: str = "Host",
        max_participants: int = 50,
        settings: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Call:
        """
        Create a new call.

        Args:
            call_type: Type of call (voice, video, livestream)
            mode: Call mode (p2p, group, broadcast)
            display_name: Display name for the host
            max_participants: Maximum number of participants
            settings: Optional call settings
            metadata: Optional call metadata

        Returns:
            Created Call object
        """
        response = self._client.request(
            "/api/calls/create",
            method="POST",
            body={
                "type": call_type.value,
                "mode": mode.value,
                "displayName": display_name,
                "maxParticipants": max_participants,
                "settings": settings or {},
                "metadata": metadata or {},
            },
        )
        return Call.from_dict(response.get("call", {}))

    def list_calls(
        self,
        status: Optional[str] = None,
        call_type: Optional[str] = None,
        limit: int = 50,
    ) -> List[Call]:
        """
        List calls.

        Args:
            status: Filter by status (active, ended)
            call_type: Filter by type (voice, video, livestream)
            limit: Maximum number of calls to return

        Returns:
            List of Call objects
        """
        params: Dict[str, Any] = {"limit": limit}
        if status:
            params["status"] = status
        if call_type:
            params["type"] = call_type

        response = self._client.request("/api/calls", params=params)
        return [Call.from_dict(c) for c in response.get("calls", [])]

    def get_call(self, call_id: str) -> Call:
        """
        Get call details.

        Args:
            call_id: ID of the call

        Returns:
            Call object
        """
        response = self._client.request(f"/api/calls/{call_id}")
        return Call.from_dict(response.get("call", {}))

    def update_call(self, call_id: str, updates: Dict[str, Any]) -> Call:
        """
        Update call settings.

        Args:
            call_id: ID of the call
            updates: Settings to update

        Returns:
            Updated Call object
        """
        response = self._client.request(
            f"/api/calls/{call_id}",
            method="PUT",
            body=updates,
        )
        return Call.from_dict(response.get("call", {}))

    def end_call(self, call_id: str) -> Call:
        """
        End a call.

        Args:
            call_id: ID of the call

        Returns:
            Ended Call object
        """
        response = self._client.request(
            f"/api/calls/{call_id}",
            method="DELETE",
        )
        return Call.from_dict(response.get("call", {}))

    def generate_token(
        self,
        call_id: str,
        display_name: str,
        user_id: Optional[str] = None,
        role: ParticipantRole = ParticipantRole.PARTICIPANT,
        permissions: Optional[List[str]] = None,
        expires_in: Optional[int] = None,
    ) -> CallToken:
        """
        Generate a join token for a call.

        Args:
            call_id: ID of the call
            display_name: Display name for the participant
            user_id: Optional user ID
            role: Participant role
            permissions: Optional list of permissions
            expires_in: Token expiry in seconds

        Returns:
            CallToken object
        """
        body: Dict[str, Any] = {
            "displayName": display_name,
            "role": role.value,
        }
        if user_id:
            body["userId"] = user_id
        if permissions:
            body["permissions"] = permissions
        if expires_in:
            body["expiresIn"] = expires_in

        response = self._client.request(
            f"/api/calls/{call_id}/tokens",
            method="POST",
            body=body,
        )
        return CallToken.from_dict(response)

    def validate_token(self, call_id: str, token: str) -> Dict[str, Any]:
        """
        Validate a call token.

        Args:
            call_id: ID of the call
            token: Token to validate

        Returns:
            Validation result
        """
        return self._client.request(
            f"/api/calls/{call_id}/tokens/validate",
            method="POST",
            body={"token": token},
        )

    def get_participants(self, call_id: str) -> List[Participant]:
        """
        Get participants in a call.

        Args:
            call_id: ID of the call

        Returns:
            List of Participant objects
        """
        response = self._client.request(f"/api/calls/{call_id}/participants")
        return [Participant.from_dict(p) for p in response.get("participants", [])]

    def kick_participant(self, call_id: str, participant_id: str) -> None:
        """
        Kick a participant from a call.

        Args:
            call_id: ID of the call
            participant_id: ID of the participant to kick
        """
        self._client.request(
            f"/api/calls/{call_id}/participants/{participant_id}/kick",
            method="POST",
            body={},
        )

    def mute_participant(
        self,
        call_id: str,
        participant_id: str,
        media_type: str = "audio",
    ) -> None:
        """
        Mute a participant.

        Args:
            call_id: ID of the call
            participant_id: ID of the participant to mute
            media_type: Type of media to mute (audio/video)
        """
        self._client.request(
            f"/api/calls/{call_id}/participants/{participant_id}/mute",
            method="POST",
            body={"mediaType": media_type},
        )

    def start_recording(
        self,
        call_id: str,
        recording_type: str = "composite",
        recording_format: str = "mp4",
    ) -> Dict[str, Any]:
        """
        Start recording a call.

        Args:
            call_id: ID of the call
            recording_type: Type of recording (composite, individual)
            recording_format: Recording format (mp4, webm)

        Returns:
            Recording start response
        """
        return self._client.request(
            f"/api/calls/{call_id}/recordings/start",
            method="POST",
            body={"type": recording_type, "format": recording_format},
        )

    def stop_recording(self, call_id: str) -> Dict[str, Any]:
        """
        Stop recording a call.

        Args:
            call_id: ID of the call

        Returns:
            Recording stop response
        """
        return self._client.request(
            f"/api/calls/{call_id}/recordings/stop",
            method="POST",
            body={},
        )

    def list_recordings(self, call_id: str) -> List[CallRecording]:
        """
        List recordings for a call.

        Args:
            call_id: ID of the call

        Returns:
            List of CallRecording objects
        """
        response = self._client.request(f"/api/calls/{call_id}/recordings")
        return [CallRecording.from_dict(r) for r in response.get("recordings", [])]

    def start_transcription(self, call_id: str) -> Dict[str, Any]:
        """
        Start real-time transcription for a call.

        Args:
            call_id: ID of the call

        Returns:
            Transcription start response
        """
        return self._client.request(
            f"/api/calls/{call_id}/transcription/start",
            method="POST",
            body={},
        )

    def stop_transcription(self, call_id: str) -> Dict[str, Any]:
        """
        Stop transcription for a call.

        Args:
            call_id: ID of the call

        Returns:
            Transcription stop response
        """
        return self._client.request(
            f"/api/calls/{call_id}/transcription/stop",
            method="POST",
            body={},
        )

    def get_transcription(self, call_id: str) -> Optional[CallTranscription]:
        """
        Get transcription for a call.

        Args:
            call_id: ID of the call

        Returns:
            CallTranscription object or None
        """
        response = self._client.request(f"/api/calls/{call_id}/transcription")
        transcription = response.get("transcription")
        if transcription:
            return CallTranscription.from_dict(transcription)
        return None

    def analyze_recording(
        self,
        recording_id: str,
        options: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Analyze a recording with AI.

        Args:
            recording_id: ID of the recording
            options: Analysis options

        Returns:
            Analysis result
        """
        return self._client.request(
            f"/api/calls/recordings/{recording_id}/analyze",
            method="POST",
            body=options or {},
        )

    def get_turn_servers(self) -> List[TurnServer]:
        """
        Get TURN servers for WebRTC.

        Returns:
            List of TurnServer objects
        """
        response = self._client.request("/api/calls/turn-servers")
        return [TurnServer.from_dict(s) for s in response.get("servers", [])]

    def start_stream(
        self,
        call_id: str,
        rtmp_url: Optional[str] = None,
        stream_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Start live streaming for a call.

        Args:
            call_id: ID of the call
            rtmp_url: Optional RTMP URL for streaming
            stream_key: Optional stream key

        Returns:
            Stream start response
        """
        body: Dict[str, Any] = {}
        if rtmp_url:
            body["rtmpUrl"] = rtmp_url
        if stream_key:
            body["streamKey"] = stream_key

        return self._client.request(
            f"/api/calls/{call_id}/stream/start",
            method="POST",
            body=body,
        )

    def stop_stream(self, call_id: str) -> Dict[str, Any]:
        """
        Stop live streaming for a call.

        Args:
            call_id: ID of the call

        Returns:
            Stream stop response
        """
        return self._client.request(
            f"/api/calls/{call_id}/stream/stop",
            method="POST",
            body={},
        )
