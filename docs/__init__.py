"""
Flask OpenAPI Documentation Package

A reusable package for generating comprehensive OpenAPI documentation 
with Flask-Pydantic-Spec, featuring custom metadata, security schemes,
and flexible configuration.

Author: Emmanuel Olowu
License: MIT
"""

from .core import FlaskOpenAPISpec, SecurityScheme, QueryParameter
from .config import DocsConfig, ContactInfo, SecuritySchemeConfig

__version__ = "1.0.0"
__author__ = "Emmanuel Olowu"

# Create a default instance for endpoint decorator export
_default_spec = FlaskOpenAPISpec(DocsConfig.create_default())
endpoint = _default_spec.endpoint

# Public API
__all__ = [
    "FlaskOpenAPISpec",
    "SecurityScheme",
    "QueryParameter",
    "endpoint",
    "DocsConfig",
    "ContactInfo",
    "SecuritySchemeConfig",
]
