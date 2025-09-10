import os, logging

class Config:
    # Logging configuration
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    BASE_LOG_LEVEL = os.getenv("BASE_LOG_LEVEL", "WARNING")
    
    ENV = os.getenv("ENV") or "development"
    SECRET_KEY = os.getenv("SECRET_KEY") or os.environ.get("SECRET_KEY")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    DEBUG = (ENV == "development")  # Enable debug mode only in development
    EMERGENCY_MODE = os.getenv("EMERGENCY_MODE") or os.environ.get("EMERGENCY_MODE") or False
    
    CLIENT_ORIGINS = os.getenv("CLIENT_ORIGINS") or os.environ.get("CLIENT_ORIGINS") or "http://localhost:3000,http://localhost:2007,http://localhost:5173,http://localhost:5000"
    CLIENT_ORIGINS = [origin.strip() for origin in CLIENT_ORIGINS.split(",")]
    
    SEED_DB = False
    DEFAULT_ADMIN_USERNAME = os.getenv("DEFAULT_ADMIN_USERNAME")
    DEFAULT_ADMIN_PASSWORD = os.getenv("DEFAULT_ADMIN_PASSWORD")
    
    # JWT configurations
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY") or os.environ.get('JWT_SECRET_KEY')
    
    # mail configurations
    MAIL_SERVER = os.getenv("MAIL_SERVER") or 'smtp.gmail.com'
    MAIL_PORT = os.getenv("MAIL_PORT") or 587
    MAIL_USE_SSL = False
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.getenv("MAIL_USERNAME")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
    MAIL_DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER')
    MAIL_ALIAS = (f"{MAIL_DEFAULT_SENDER}", f"{MAIL_USERNAME}")
    
    # Domains
    APP_DOMAIN_NAME = os.getenv("APP_DOMAIN_NAME") or "http://localhost:3000"
    API_DOMAIN_NAME = os.getenv("API_DOMAIN_NAME") or "http://localhost:5000"
    
    # Cloudinary configurations
    CLOUDINARY_CLOUD_NAME = os.getenv("CLOUDINARY_CLOUD_NAME")
    CLOUDINARY_API_KEY = os.getenv("CLOUDINARY_API_KEY")
    CLOUDINARY_API_SECRET = os.getenv("CLOUDINARY_API_SECRET")

class DevelopmentConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL") or os.getenv("DATABASE_URL") or "sqlite:///db.sqlite3"

class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")

class TestingConfig(Config):
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"


# Map config based on environment
config_by_name = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig
}

def configure_logging(app):
    if not app.logger.handlers:
        formatter = logging.Formatter("[%(asctime)s] ==> %(levelname)s in %(module)s: %(message)s")
        
        # Stream handler
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        app.logger.addHandler(stream_handler)
        
        app.logger.setLevel(logging.DEBUG)  # Set the desired logging level