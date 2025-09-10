### EventSphere API

Backend service for EventSphere a a full-stack college event management system that allows students to discover, register for, and participate in college events while providing organizers and admins with tools to manage events efficiently.

Setup
- Create and activate a Python 3.12 venv
- pip install -r requirements.txt
- Set env vars: SECRET_KEY, JWT_SECRET_KEY, DATABASE_URL (optional), DEFAULT_ADMIN_USERNAME, DEFAULT_ADMIN_PASSWORD
- Run: python run.py

Environment
- Development uses SQLite by default
- Testing uses in-memory SQLite

Endpoints
- GET /api/health
- GET /api/version


