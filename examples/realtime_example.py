"""
Realtime database example for SCS Python SDK

Requires: pip install scs-sdk[realtime]
"""

import time
from scs import SCS

scs = SCS({
    'api_key': 'pk_your_api_key',
    'project_id': 'your-project-id',
    'base_url': 'http://localhost:3001'
})


def on_chat_update(data, event):
    """Handle chat updates"""
    print(f"[{event}] New message: {data}")


def main():
    print("Connecting to realtime service...")

    # Connect to realtime service
    scs.realtime.connect()
    print("Connected!")

    # Subscribe to chat room
    chat_ref = scs.realtime.ref('chat/general')
    unsubscribe = chat_ref.on(on_chat_update)
    print("Subscribed to chat/general")

    try:
        # Keep the connection alive
        print("Listening for updates (Ctrl+C to stop)...")
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        print("\nStopping...")

    finally:
        # Cleanup
        unsubscribe()
        scs.realtime.disconnect()
        scs.close()
        print("Disconnected")


if __name__ == '__main__':
    main()
