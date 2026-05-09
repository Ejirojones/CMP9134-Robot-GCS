# Component Diagram — System Architecture

This high-level diagram shows how all system components connect
and communicate across the Docker network.

```mermaid
graph TB
    subgraph Browser["User Browser"]
        USER[👤 User]
    end

    subgraph GCS["Ground Control Station (Docker Compose Network)"]
        subgraph Frontend["Frontend Container (Nginx :80)"]
            HTML["HTML/CSS/JS Dashboard"]
        end

        subgraph Backend["Backend Container (Uvicorn :8000)"]
            API["FastAPI Application"]
            AUTH["Auth Service\n(HMAC Tokens)"]
            RBAC["RBAC Middleware"]
            LOGGER["Mission Logger"]
        end

        subgraph Database["Data Layer"]
            DB[(SQLite DB\nUsers + Logs)]
        end
    end

    subgraph RobotContainer["Virtual Robot Container (:5000)"]
        ROBOT["Robot Simulator\nREST API"]
    end

    subgraph CI["GitHub Actions (CI/CD)"]
        PIPELINE["Build → Test → Push"]
    end

    USER -->|HTTP :80| HTML
    HTML -->|REST API calls| API
    API --> AUTH
    API --> RBAC
    API --> LOGGER
    LOGGER -->|Read/Write| DB
    AUTH -->|Read| DB
    API -->|POST /api/move\nGET /api/status| ROBOT
    PIPELINE -->|Deploys| GCS
```

## Component Responsibilities

| Component | Technology | Responsibility |
|---|---|---|
| Frontend | HTML/CSS/JS + Nginx | User interface, login, grid display |
| Backend | FastAPI + Uvicorn | API routes, RBAC, business logic |
| Auth Service | Python (HMAC) | Token creation and verification |
| Mission Logger | Python + SQLite | Audit trail of all commands |
| Database | SQLite | Persistent storage of users and logs |
| Robot Simulator | Docker container | Virtual robot REST API |
| CI/CD Pipeline | GitHub Actions | Automated testing and delivery |