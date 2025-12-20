"""
SCS Realtime Service

Provides real-time data synchronization via WebSocket (Socket.IO).
"""

import json
import threading
from typing import TYPE_CHECKING, Any, Callable, Dict, List, Optional

try:
    import socketio
    HAS_SOCKETIO = True
except ImportError:
    HAS_SOCKETIO = False
    socketio = None

if TYPE_CHECKING:
    from ..client import SCS


class RealtimeReference:
    """
    Reference to a real-time data path.

    Usage:
        chat_ref = scs.realtime.ref('chat/room1')

        # Listen for changes
        def on_update(data, event):
            print(f'Update: {data}')

        unsubscribe = chat_ref.on(on_update)

        # Later, unsubscribe
        unsubscribe()
    """

    def __init__(self, realtime: "RealtimeService", path: str):
        """
        Initialize realtime reference.

        Args:
            realtime: RealtimeService instance
            path: Data path to subscribe to
        """
        self._realtime = realtime
        self._path = path
        self._listeners: List[Callable] = []

    @property
    def path(self) -> str:
        """Get the data path."""
        return self._path

    def on(
        self,
        callback: Callable[[Any, str], None],
    ) -> Callable[[], None]:
        """
        Subscribe to data changes.

        Args:
            callback: Function called with (data, event_type) on updates

        Returns:
            Unsubscribe function
        """
        self._listeners.append(callback)
        self._realtime._subscribe(self._path, callback)

        def unsubscribe():
            if callback in self._listeners:
                self._listeners.remove(callback)
                self._realtime._unsubscribe(self._path, callback)

        return unsubscribe

    def once(
        self,
        callback: Callable[[Any, str], None],
    ) -> None:
        """
        Subscribe to a single data update.

        Args:
            callback: Function called with (data, event_type) once
        """
        def wrapper(data, event):
            callback(data, event)
            unsubscribe()

        unsubscribe = self.on(wrapper)

    def off(self) -> None:
        """
        Remove all listeners for this reference.
        """
        for callback in self._listeners.copy():
            self._realtime._unsubscribe(self._path, callback)
        self._listeners.clear()


class RealtimeService:
    """
    Realtime service for live data synchronization.

    Usage:
        # Connect to realtime service
        scs.realtime.connect()

        # Get reference
        chat_ref = scs.realtime.ref('chat/room1')

        # Subscribe to updates
        def on_message(data, event):
            print(f'New message: {data}')

        unsubscribe = chat_ref.on(on_message)

        # Disconnect when done
        scs.realtime.disconnect()
    """

    def __init__(self, scs: "SCS"):
        if not HAS_SOCKETIO:
            raise ImportError(
                "python-socketio is required for realtime functionality. "
                "Install it with: pip install python-socketio[client]"
            )

        self._scs = scs
        self._sio: Optional[socketio.Client] = None
        self._connected = False
        self._subscriptions: Dict[str, List[Callable]] = {}
        self._lock = threading.Lock()

    @property
    def connected(self) -> bool:
        """Check if connected to realtime service."""
        return self._connected

    def connect(self) -> None:
        """
        Connect to the realtime service.

        Raises:
            ConnectionError: If connection fails
        """
        if self._connected:
            return

        self._sio = socketio.Client()

        # Set up event handlers
        @self._sio.event
        def connect():
            self._connected = True
            # Authenticate after connection
            self._sio.emit("authenticate", {
                "apiKey": self._scs.api_key,
                "projectId": self._scs.project_id,
                "userToken": self._scs.user_token,
            })

        @self._sio.event
        def disconnect():
            self._connected = False

        @self._sio.event
        def data_update(data):
            self._handle_data_update(data)

        @self._sio.event
        def error(data):
            print(f"Realtime error: {data}")

        # Connect to server
        realtime_url = self._scs.base_url.replace("/api", "")
        try:
            self._sio.connect(
                realtime_url,
                namespaces=["/realtime"],
                transports=["websocket"],
            )
        except Exception as e:
            from ..exceptions import ConnectionError
            raise ConnectionError(f"Failed to connect to realtime service: {e}")

    def disconnect(self) -> None:
        """
        Disconnect from the realtime service.
        """
        if self._sio and self._connected:
            self._sio.disconnect()
            self._connected = False
            self._subscriptions.clear()

    def ref(self, path: str) -> RealtimeReference:
        """
        Get a reference to a data path.

        Args:
            path: Data path (e.g., 'chat/room1')

        Returns:
            RealtimeReference
        """
        return RealtimeReference(self, path)

    def _subscribe(self, path: str, callback: Callable) -> None:
        """
        Internal method to subscribe to a path.

        Args:
            path: Data path
            callback: Callback function
        """
        with self._lock:
            if path not in self._subscriptions:
                self._subscriptions[path] = []
                # Send subscribe message to server
                if self._sio and self._connected:
                    self._sio.emit("subscribe", {"path": path})

            self._subscriptions[path].append(callback)

    def _unsubscribe(self, path: str, callback: Callable) -> None:
        """
        Internal method to unsubscribe from a path.

        Args:
            path: Data path
            callback: Callback function
        """
        with self._lock:
            if path in self._subscriptions:
                if callback in self._subscriptions[path]:
                    self._subscriptions[path].remove(callback)

                # If no more listeners, unsubscribe from server
                if not self._subscriptions[path]:
                    del self._subscriptions[path]
                    if self._sio and self._connected:
                        self._sio.emit("unsubscribe", {"path": path})

    def _handle_data_update(self, data: Dict[str, Any]) -> None:
        """
        Handle data update from server.

        Args:
            data: Update data with path and payload
        """
        path = data.get("path", "")
        payload = data.get("data")
        event_type = data.get("event", "update")

        with self._lock:
            # Check for exact path match
            if path in self._subscriptions:
                for callback in self._subscriptions[path]:
                    try:
                        callback(payload, event_type)
                    except Exception as e:
                        print(f"Error in realtime callback: {e}")

            # Check for parent path matches
            for sub_path, callbacks in self._subscriptions.items():
                if path.startswith(sub_path + "/") or sub_path.startswith(path + "/"):
                    for callback in callbacks:
                        try:
                            callback(payload, event_type)
                        except Exception as e:
                            print(f"Error in realtime callback: {e}")
