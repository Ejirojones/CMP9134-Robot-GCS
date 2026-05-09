# Privacy Policy — Ground Control Station (GCS)

## 1. What Personal Data is Collected
The Ground Control Station collects the following Personally Identifiable 
Information (PII) during normal operation:
- **Usernames** — used to identify users within the system
- **Password hashes** — stored securely using SHA-256 hashing (never plain text)
- **Timestamps** — date and time of every command issued
- **Command history** — a record of every action taken by each user (move, reset)
- **IP addresses** — may be captured incidentally by the web server logs

## 2. Why This Data is Collected
This data is collected strictly to satisfy the safety audit requirements of the 
Ground Control Station. The mission logging system creates an audit trail so that 
any command sent to the robot can be traced back to the authenticated user who 
issued it. This is a functional requirement for accountability in autonomous systems.
Data is collected under the lawful basis of **legitimate interest** — ensuring 
safety and security of the autonomous robot system.

## 3. How Data is Secured
- Passwords are **never stored in plain text** — only SHA-256 hashes are persisted
- Access to mission logs is restricted via **Role-Based Access Control (RBAC)**
- Only authenticated users with a valid token can access the audit log endpoint
- The database is stored locally and is not exposed to external networks
- In line with GDPR's **Data Minimisation** principle, only data necessary for 
  safety auditing is collected
- In line with GDPR's **Storage Limitation** principle, logs should be reviewed 
  and purged periodically (recommended: every 90 days)

## 4. Data Retention
Mission logs are retained for audit purposes. It is recommended that an 
administrator reviews and exports logs regularly, retaining only what is necessary.

## 5. User Rights
Under UK GDPR, users have the right to:
- Access their personal data
- Request deletion of their data
- Object to processing of their data

To exercise these rights, contact the system administrator.