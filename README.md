# SCS Python SDK

Python SDK for SCS (Spyxpo Cloud Services) - an open-source Backend-as-a-Service platform.

## Installation

```bash
pip install scs-sdk
```

For realtime functionality (WebSocket support):

```bash
pip install scs-sdk[realtime]
```

## Quick Start

```python
from scs import SCS

# Initialize from config file
scs = SCS.initialize_app('./scs-info.json')

# Or initialize with config dict
scs = SCS({
    'api_key': 'your-api-key',
    'project_id': 'your-project-id',
    'base_url': 'https://your-scs-instance.com'
})

# Authentication
user = scs.auth.login(email='user@example.com', password='password123')

# Database
users = scs.database.collection('users').where('age', '>=', 18).limit(10).get()

# Storage
scs.storage.upload('./image.png', folder='images')
```

## Services

### Authentication

```python
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

# Change password
scs.auth.change_password(
    current_password='old123',
    new_password='new456'
)

# Logout
scs.auth.logout()
```

### Database

Document database with query builder:

```python
# Get collection reference
users = scs.database.collection('users')

# Add a document
new_user = users.add({
    'name': 'John Doe',
    'email': 'john@example.com',
    'age': 30
})

# Get all documents
all_users = users.get()

# Query with filters
adults = users.where('age', '>=', 18).where('status', '==', 'active').get()

# Ordering and pagination
recent = users.order_by('createdAt', 'desc').limit(10).skip(20).get()

# Get specific document
doc = users.doc('user123').get()

# Update document
users.doc('user123').update({'age': 31})

# Delete document
users.doc('user123').delete()

# Subcollections
posts = users.doc('user123').collection('posts').get()
```

Query operators: `==`, `!=`, `>`, `>=`, `<`, `<=`, `in`, `contains`

### Storage

```python
# Upload from file path
file_info = scs.storage.upload('./image.png')

# Upload with folder
file_info = scs.storage.upload('./doc.pdf', folder='documents')

# Upload from bytes
file_info = scs.storage.upload_bytes(
    data=image_bytes,
    filename='image.png',
    content_type='image/png'
)

# List files
files = scs.storage.list_files(folder='images')

# Get file reference
file_ref = scs.storage.ref('file-id')

# Download file
content = file_ref.download()

# Download to file
file_ref.download_to_file('./local_file.png')

# Get metadata
metadata = file_ref.get_metadata()

# Delete file
file_ref.delete()

# Folder operations
scs.storage.create_folder('my-folder')
scs.storage.delete_folder('my-folder')
```

### Realtime Database

Real-time data synchronization via WebSocket:

```python
# Connect to realtime service
scs.realtime.connect()

# Get reference
chat_ref = scs.realtime.ref('chat/room1')

# Subscribe to updates
def on_message(data, event):
    print(f'Event: {event}, Data: {data}')

unsubscribe = chat_ref.on(on_message)

# Subscribe to single update
chat_ref.once(lambda data, event: print(data))

# Unsubscribe
unsubscribe()

# Disconnect
scs.realtime.disconnect()
```

### Cloud Messaging

Push notifications with topics and direct messaging:

```python
# Register device token
scs.messaging.register_token(
    token='device-fcm-token',
    platform='android'
)

# Topic operations
scs.messaging.create_topic('news', description='News updates')
scs.messaging.subscribe_to_topic('news', 'device-token')
scs.messaging.unsubscribe_from_topic('news', 'device-token')

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

# Send to multiple devices
scs.messaging.send_to_tokens(
    tokens=['token1', 'token2'],
    title='Broadcast',
    body='Hello everyone!'
)
```

### Remote Config

Dynamic app configuration:

```python
# Fetch configuration
config = scs.remote_config.fetch()

# Get values with type safety
theme = scs.remote_config.get_string('app_theme', default='light')
max_items = scs.remote_config.get_int('max_items', default=10)
enabled = scs.remote_config.get_bool('feature_enabled', default=False)
settings = scs.remote_config.get_json('settings', default={})

# Admin: Manage parameters
scs.remote_config.create_param(
    key='app_theme',
    value='dark',
    description='Default app theme'
)
scs.remote_config.update_param('app_theme', 'light')
scs.remote_config.delete_param('old_param')

# Publish changes
scs.remote_config.publish()

# Version management
versions = scs.remote_config.list_versions()
scs.remote_config.rollback('version-id')
```

### Serverless Functions

Execute custom code on the backend:

```python
# Invoke a function
result = scs.functions.invoke('processOrder', {
    'orderId': '12345',
    'action': 'confirm'
})

# Admin: Create a function
scs.functions.create(
    name='processOrder',
    code='''
    module.exports = async (data, context) => {
        const { orderId, action } = data;
        // Process order...
        return { success: true, orderId };
    };
    ''',
    runtime='nodejs18',
    timeout=30000,
    memory=256
)

# Admin: List functions
functions = scs.functions.list()

# Admin: Update function
scs.functions.update('function-id', code='...')

# Admin: Test function
result = scs.functions.test('function-id', {'test': 'data'})

# Admin: Get logs
logs = scs.functions.get_logs('function-id')
```

## Configuration File

Create an `scs-info.json` file:

```json
{
  "sdk_config": {
    "api_key": "pk_your_api_key",
    "project_id": "your-project-id",
    "base_url": "https://your-scs-instance.com"
  }
}
```

## Error Handling

```python
from scs import SCS, SCSError, AuthenticationError, NotFoundError, ValidationError

try:
    user = scs.auth.login(email='user@example.com', password='wrong')
except AuthenticationError as e:
    print(f'Auth failed: {e.message}')
    print(f'Status: {e.status}')
except NotFoundError as e:
    print(f'Not found: {e.message}')
except ValidationError as e:
    print(f'Validation error: {e.message}')
except SCSError as e:
    print(f'SCS error: {e.message}')
```

## Context Manager

```python
with SCS({'api_key': '...', 'project_id': '...'}) as scs:
    users = scs.database.collection('users').get()
# Connection automatically closed
```

## Requirements

- Python 3.8+
- requests
- python-socketio[client] (optional, for realtime functionality)

## License

MIT License
