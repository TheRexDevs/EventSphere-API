from flask import Flask

from config import Config, config_by_name
from .context_processors import app_context_Processor
from .extensions import initialize_extensions
from .logging import configure_logging
from .seed import seed_database
from .utils.hooks import register_hooks
from .blueprints import register_blueprints
from .docs import init_docs

def create_app(config_name=Config.ENV, seed_db=Config.SEED_DB):
    '''
    Creates and configures the Flask application instance.

    Args:
        config_name: The configuration class to use (Defaults to Config).

    Returns:
        The Flask application instance.
    '''
    
    app = Flask(__name__)
    
    app.config.from_object(config_by_name[config_name])
    app.context_processor(app_context_Processor)
    
    # Initialize Flask extensions
    initialize_extensions(app=app)
    
    # Register before and after request hooks
    register_hooks(app=app)
    
    # Configure logging
    configure_logging(app)

    # Register blueprints
    register_blueprints(app)
    
    # Initialize OpenAPI docs (Swagger UI and Redoc)
    init_docs(app)
    
    # initialize database defaults values
    if seed_db:
        seed_database(app)
    
    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
