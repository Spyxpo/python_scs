"""
Basic usage example for SCS Python SDK
"""

from scs import SCS, SCSError, AuthenticationError

# Initialize from config file
# scs = SCS.initialize_app('./scs-info.json')

# Or initialize with config dict
scs = SCS({
    'api_key': 'pk_your_api_key',
    'project_id': 'your-project-id',
    'base_url': 'http://localhost:3001'
})


def auth_example():
    """Authentication examples"""
    print("\n=== Authentication ===")

    try:
        # Register a new user
        user = scs.auth.register(
            email='test@example.com',
            password='password123',
            display_name='Test User'
        )
        print(f"Registered: {user}")

    except SCSError as e:
        print(f"Registration failed (user may exist): {e.message}")

    try:
        # Login
        user = scs.auth.login(
            email='test@example.com',
            password='password123'
        )
        print(f"Logged in as: {user.get('user', {}).get('email')}")

        # Get current user
        me = scs.auth.get_current_user()
        print(f"Current user: {me}")

    except AuthenticationError as e:
        print(f"Login failed: {e.message}")


def database_example():
    """Database examples"""
    print("\n=== Database ===")

    # Get collection reference
    users = scs.database.collection('users')

    # Add a document
    new_doc = users.add({
        'name': 'John Doe',
        'email': 'john@example.com',
        'age': 30,
        'tags': ['developer', 'python']
    })
    print(f"Created document: {new_doc}")

    # Get all documents
    all_users = users.get()
    print(f"All users: {len(all_users)} documents")

    # Query with filters
    adults = users.where('age', '>=', 18).order_by('name').limit(5).get()
    print(f"Adults: {len(adults)} documents")

    # Get specific document
    if all_users:
        doc_id = all_users[0].get('_id')
        doc = users.doc(doc_id).get()
        print(f"Document: {doc}")


def storage_example():
    """Storage examples"""
    print("\n=== Storage ===")

    # Upload from bytes
    content = b"Hello, World!"
    result = scs.storage.upload_bytes(
        data=content,
        filename='hello.txt',
        content_type='text/plain',
        folder='examples'
    )
    print(f"Uploaded: {result}")

    # List files
    files = scs.storage.list_files()
    print(f"Files: {files}")


def remote_config_example():
    """Remote Config examples"""
    print("\n=== Remote Config ===")

    # Fetch configuration
    config = scs.remote_config.fetch()
    print(f"Config: {config}")

    # Get typed values
    theme = scs.remote_config.get_string('app_theme', default='light')
    max_items = scs.remote_config.get_int('max_items', default=10)
    print(f"Theme: {theme}, Max Items: {max_items}")


def functions_example():
    """Serverless Functions examples"""
    print("\n=== Functions ===")

    try:
        # Invoke a function
        result = scs.functions.invoke('hello', {'name': 'World'})
        print(f"Function result: {result}")
    except SCSError as e:
        print(f"Function not found or error: {e.message}")


def messaging_example():
    """Cloud Messaging examples"""
    print("\n=== Messaging ===")

    try:
        # List topics
        topics = scs.messaging.list_topics()
        print(f"Topics: {topics}")

        # Get stats
        stats = scs.messaging.get_stats()
        print(f"Stats: {stats}")
    except SCSError as e:
        print(f"Messaging error: {e.message}")


if __name__ == '__main__':
    try:
        auth_example()
        database_example()
        storage_example()
        remote_config_example()
        functions_example()
        messaging_example()
    except Exception as e:
        print(f"Error: {e}")
    finally:
        scs.close()
