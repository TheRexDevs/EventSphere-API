import pytest
from app import create_app
from app.extensions import db

@pytest.fixture
def app():
    """Create and configure a new app instance for each test."""
    app = create_app(config_name="testing", seed_db=False)

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()