# Sequence Diagram — Move Robot Command Flow

This diagram traces the chronological execution of a move command
from the Commander through the full system stack.

```mermaid
sequenceDiagram
    actor C as Commander
    participant UI as Web Dashboard
    participant API as FastAPI Backend
    participant Auth as Auth Service
    participant DB as SQLite Database
    participant Robot as Virtual Robot (Docker)

    C->>UI: Enter X=5, Y=5 and click Move Robot
    UI->>API: POST /api/move/secure?x=5&y=5&token=...

    activate API
    API->>Auth: verify_token(token)
    Auth-->>API: {username: "commander1", role: "commander"}

    API->>API: Check role == "commander"

    API->>Robot: POST /api/move {x: 5, y: 5}
    activate Robot
    Robot-->>API: 200 OK {status: "MOVING", position: {x:5, y:5}}
    deactivate Robot

    API->>DB: logCommand("commander1", "MOVE", "x=5,y=5", "success")
    DB-->>API: OK

    API-->>UI: 200 OK {status: "MOVING"}
    deactivate API

    UI->>UI: Update grid position
    UI->>UI: Show "Move command sent!" message
    UI->>UI: Refresh mission audit log
```

## Alternative Flow — Viewer Attempts Move

```mermaid
sequenceDiagram
    actor V as Viewer
    participant UI as Web Dashboard
    participant API as FastAPI Backend

    V->>UI: Attempts to access move controls
    UI->>UI: role == "viewer" → hide move controls
    Note over UI: Controls hidden in frontend
    Note over API: Even if bypassed, API enforces RBAC
    V->>API: POST /api/move/secure?token=viewer_token
    API-->>V: 403 Forbidden "Commanders only"
```