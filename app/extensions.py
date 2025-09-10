'''
This module initializes the extensions used in the Flask application.

It sets up SQLAlchemy, Flask-Mail, and Celery with the configurations defined in the Config class.

@author: Emmanuel Olowu
@link: https://github.com/zeddyemy
'''

from flask_cors import CORS
from flask import Flask
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_caching import Cache
from flask_admin import Admin
from flask_login import LoginManager, UserMixin, current_user

from config import Config

cors = CORS()
mail = Mail()
db = SQLAlchemy()
migration = Migrate()
jwt_extended = JWTManager()
app_cache = Cache(config={'CACHE_TYPE': 'flask_caching.backends.SimpleCache'})
login_manager: LoginManager = LoginManager()

def initialize_extensions(app: Flask):
    """Initialize Flask extensions (DB, Mail, Auth, Cache, Migrations, CORS)."""
    db.init_app(app)
    mail.init_app(app)

    login_manager.init_app(app)
    setattr(login_manager, 'login_view', 'panel.login')

    @login_manager.user_loader
    def load_user(user_id):
        return load_app_user(user_id, app)

    jwt_extended.init_app(app)
    app_cache.init_app(app)
    migration.init_app(app, db=db)

    cors.init_app(app=app, resources={r"/*": {"origins": Config.CLIENT_ORIGINS}}, supports_credentials=True)

def load_app_user(user_id: str, app: Flask):
    """Return the `AppUser` with roles for the given ID, or `None` if missing."""
    from app.models import AppUser
    from sqlalchemy.orm import joinedload
    from typing import Any, cast

    try:
        session = cast(Any, db.session)
        return session.get(AppUser, int(user_id), options=[joinedload(cast(Any, AppUser).roles)])
    except Exception as e:
        app.logger.error(f"Error loading user {user_id}: {e}")
        return None
