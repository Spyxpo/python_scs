# Changelog

All notable changes to the SCS Python SDK will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2024-12-20

### Added
- Initial release of SCS Python SDK
- Authentication module with register, login, logout, and profile management
- Database module with document CRUD operations and subcollections
- Query builder with filters, ordering, and pagination
- Storage module with file and bytes upload support
- File download, listing, and folder management
- Realtime Database with WebSocket synchronization (optional dependency)
- Subscribe/unsubscribe pattern for real-time updates
- Cloud Messaging for push notifications with topic support
- Send to single device, multiple devices, or topics
- Remote Config for dynamic configuration management
- Config versioning and rollback support
- Serverless Functions invocation and management
- Function testing and log retrieval

### Features
- Pythonic API design with snake_case naming
- Context manager support for automatic cleanup
- Typed error handling with specific exception classes
- JSON config file support (scs-info.json)
- Optional realtime dependency for WebSocket features
- Compatible with Python 3.8+
