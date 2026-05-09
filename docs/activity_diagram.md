# Activity Diagram — Move Robot Authorization Flow

This diagram models the business logic executed when a user
attempts to send a move command to the robot.

```mermaid
stateDiagram-v2
    [*] --> ReceiveRequest
    ReceiveRequest --> VerifyToken

    state verify_token <<choice>>
    VerifyToken --> verify_token
    verify_token --> RejectUnauthorized : Token invalid or expired
    verify_token --> CheckRole : Token valid

    state check_role <<choice>>
    CheckRole --> check_role
    check_role --> RejectForbidden : Role is Viewer
    check_role --> SendToRobot : Role is Commander

    state robot_response <<choice>>
    SendToRobot --> robot_response
    robot_response --> LogSuccess : Robot responds 200 OK
    robot_response --> LogError : Robot unreachable or error

    LogSuccess --> ReturnSuccess
    LogError --> ReturnError
    RejectUnauthorized --> Return401
    RejectForbidden --> Return403

    ReturnSuccess --> [*]
    ReturnError --> [*]
    Return401 --> [*]
    Return403 --> [*]
```

## Flow Description

1. Request received at `POST /api/move/secure`
2. Token is verified using HMAC signature check
3. If invalid → 401 Unauthorized returned immediately
4. If valid → user role is checked
5. If Viewer → 403 Forbidden returned
6. If Commander → move command sent to Virtual Robot API
7. If robot responds → success logged to mission log
8. If robot unreachable → error logged to mission log
9. Response returned to client