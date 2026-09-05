# Security & Privacy Architecture

## 1. Authentication & Password Security
- **Bcrypt Hashing**: Passwords are never stored in plaintext. They are salted and hashed using `bcrypt` with work factors suitable for cryptographic safety.
- **JWT Tokens**: Authenticated requests use standard Bearer tokens signed with `HS256` and secret keys loaded strictly from environment variables.
- **Role-Based Access Control (RBAC)**: Distinct permissions separate `student` (candidate) users from `admin` users. Administrative endpoints require explicit `role: admin` verification.

## 2. Resume & Privacy Protection
- **User Isolation**: Candidate resumes and profiles are scoped by `user_id`. No cross-user profile leakage or IDOR vulnerabilities exist.
- **Local Document Parsing**: Document parsing uses PyMuPDF and python-docx locally on the application server. Raw resumes are not transmitted to third-party services.
- **Delete Account & Profile**: Candidates retain full control to edit or overwrite their profile data at any time.

## 3. Prompt Injection Defense
Job descriptions and resume contents are untrusted external text. The system enforces strict architectural defenses:
- All external inputs are treated strictly as **DATA**, never as control instructions.
- LLM prompts explicitly frame resume and job descriptions within data delimiters and instruct the model to disregard instructions embedded inside external text.
- Fallback to 100% deterministic rule-based algorithms is active by default.

## 4. Input Validation & DoS Prevention
- **File Validation**: Enforces maximum upload size (10 MB) and restricts extensions strictly to `.pdf`, `.docx`, and `.txt`.
- **Pydantic v2**: All API endpoints use strict schema validation to prevent malformed or malicious payloads.
