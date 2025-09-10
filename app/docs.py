"""
OpenAPI documentation setup for Folio Builder API.

This module integrates the reusable Flask OpenAPI Documentation package
with the Folio Builder API, providing comprehensive API documentation
with custom configuration and metadata.
"""

from __future__ import annotations

from flask import Flask

# Import the reusable docs package
from docs import FlaskOpenAPISpec, SecurityScheme, QueryParameter, DocsConfig, endpoint


# Create configuration for Folio Builder API dynamically
config = DocsConfig.from_dict({
    'title': 'EventSphere API',
    'version': '1.0.0',
    'description': 'You can checkout more details [here](https://github.com/TheRexDevs/EventSphere-API)',
    'contact': {
        'email': 'zeddyemy@gmail.com',
        'name': 'Emmanuel Olowu',
        'url': 'https://eshomonu.com/'
    },
    'security_schemes': {
        'PublicBearerAuth': {
            'description': 'Login as a customer to use API Endpoints'
        },
        'AdminBearerAuth': {
            'description': 'Login as an Admin user to use Admin API Endpoints'
        }
    },
    'preserve_flask_routes': False,
    'clear_auto_discovered': True,
    'add_default_responses': True
})

# Create the OpenAPI spec instance with our configuration
spec_instance = FlaskOpenAPISpec(config)

# Expose the spec object for @spec.validate decorators
spec = spec_instance.spec


def init_docs(app: Flask) -> None:
    """
    Initialize OpenAPI documentation for the Folio Builder API.
    
    Args:
        app: The Flask application instance to configure
    """
    spec_instance.init_app(app)
