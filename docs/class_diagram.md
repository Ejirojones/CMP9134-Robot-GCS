# Class Diagram — Ground Control Station Backend

This diagram defines the Object-Oriented architecture of the
backend, showing classes, attributes, methods and relationships.

```mermaid
classDiagram
    class User {
        +String username
        +String password_hash
        +String role
        +register(username, password, role) dict
        +login(username, password) dict
        +getRole() String
    }

    class RobotClient {
        -String _base
        +get_status() dict
        +move(int x, int y) dict
        +reset() dict
    }

    class MissionLog {
        +int id
        +String timestamp
        +String username
        +String action
        +String details
        +String result
        +logCommand(username, action, details, result)
        +getLogs(limit) list
    }

    class RobotConnectionError {
        +String message
    }

    class AuthService {
        +hash_password(password) String
        +verify_password(password, hash) bool
        +create_token(username, role) String
        +verify_token(token) dict
    }

    User "1" --> "1" RobotClient : uses
    User "1" --> "*" MissionLog : generates
    RobotClient --> RobotConnectionError : raises
    RobotClient "1" --> "*" MissionLog : logs to
    AuthService --> User : authenticates
```

## Class Descriptions

| Class | Responsibility |
|---|---|
| User | Represents an authenticated system user with a role |
| RobotClient | Facade pattern — wraps all HTTP calls to robot API |
| MissionLog | Audit trail — every command stored with timestamp and user |
| RobotConnectionError | Custom exception for robot communication failures |
| AuthService | Handles password hashing and HMAC token management |