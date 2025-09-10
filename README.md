### Folio API

Backend service for a multi-tenant portfolio CMS. Flask + SQLAlchemy, JWT, and payment integrations.

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


