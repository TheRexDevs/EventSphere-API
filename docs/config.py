"""
Configuration system for Flask OpenAPI Documentation Package.

This module provides a flexible configuration system that allows easy
customization of API documentation metadata, security schemes, and behavior.
"""

from __future__ import annotations

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field


@dataclass
class ContactInfo:
    """Contact information for the API documentation."""
    email: Optional[str] = None
    name: Optional[str] = None
    url: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for OpenAPI spec."""
        return {k: v for k, v in {
            'email': self.email,
            'name': self.name,
            'url': self.url
        }.items() if v is not None}


@dataclass
class SecuritySchemeConfig:
    """Configuration for a security scheme."""
    name: str
    scheme_type: str = "apiKey"
    location: str = "header"  # header, query, cookie
    parameter_name: str = "Authorization"
    description: Optional[str] = None
    
    def to_openapi_dict(self) -> Dict[str, Any]:
        """Convert to OpenAPI security scheme format."""
        scheme = {
            'type': self.scheme_type,
            'in': self.location,
            'name': self.parameter_name,
        }
        if self.description:
            scheme['description'] = self.description
        return scheme


@dataclass
class DocsConfig:
    """Main configuration class for Flask OpenAPI documentation."""
    
    # Basic API Information
    title: str = "Flask API"
    version: str = "1.0.0"
    description: Optional[str] = None
    terms_of_service: Optional[str] = None
    
    # Contact Information
    contact: Optional[ContactInfo] = None
    
    # License Information
    license_name: Optional[str] = None
    license_url: Optional[str] = None
    
    # Server Information
    servers: List[Dict[str, str]] = field(default_factory=list)
    
    # Security Schemes
    security_schemes: Dict[str, SecuritySchemeConfig] = field(default_factory=dict)
    
    # Customization Options
    preserve_flask_routes: bool = True  # Keep <string:param> format
    clear_auto_discovered: bool = True  # Remove auto-discovered duplicates
    add_default_responses: bool = True  # Add default response schemas
    
    # External Documentation
    external_docs_url: Optional[str] = None
    external_docs_description: Optional[str] = None
    
    @classmethod
    def create_default(cls) -> 'DocsConfig':
        """Create a default configuration with common settings."""
        return cls(
            title="Flask API",
            version="1.0.0",
            description="API documentation generated with Flask OpenAPI Docs",
            contact=ContactInfo(
                email="api@example.com",
                name="API Team"
            ),
            security_schemes={
                "BearerAuth": SecuritySchemeConfig(
                    name="BearerAuth",
                    description="JWT Bearer token authentication"
                )
            }
        )
    
    @classmethod
    def from_env(cls, prefix: str = "API_") -> 'DocsConfig':
        """Create configuration from environment variables with optional prefix.
        
        Args:
            prefix: Environment variable prefix (default: 'API_')
            
        Environment Variables:
            {prefix}TITLE: API title
            {prefix}VERSION: API version
            {prefix}DESCRIPTION: API description
            {prefix}CONTACT_EMAIL: Contact email
            {prefix}CONTACT_NAME: Contact name
            {prefix}CONTACT_URL: Contact URL
            {prefix}LICENSE_NAME: License name
            {prefix}LICENSE_URL: License URL
            {prefix}PRESERVE_FLASK_ROUTES: Keep Flask route format (true/false)
        """
        import os
        
        # Helper function to get bool from env
        def get_bool(key: str, default: bool) -> bool:
            value = os.getenv(key, str(default)).lower()
            return value in ('true', '1', 'yes', 'on')
        
        # Create contact info if any contact env vars are present
        contact = None
        contact_email = os.getenv(f"{prefix}CONTACT_EMAIL")
        contact_name = os.getenv(f"{prefix}CONTACT_NAME")
        contact_url = os.getenv(f"{prefix}CONTACT_URL")
        
        if any([contact_email, contact_name, contact_url]):
            contact = ContactInfo(
                email=contact_email,
                name=contact_name,
                url=contact_url
            )
        
        return cls(
            title=os.getenv(f"{prefix}TITLE", "Flask API"),
            version=os.getenv(f"{prefix}VERSION", "1.0.0"),
            description=os.getenv(f"{prefix}DESCRIPTION"),
            contact=contact,
            license_name=os.getenv(f"{prefix}LICENSE_NAME"),
            license_url=os.getenv(f"{prefix}LICENSE_URL"),
            preserve_flask_routes=get_bool(f"{prefix}PRESERVE_FLASK_ROUTES", True),
            clear_auto_discovered=get_bool(f"{prefix}CLEAR_AUTO_DISCOVERED", True),
            add_default_responses=get_bool(f"{prefix}ADD_DEFAULT_RESPONSES", True)
        )
    
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> 'DocsConfig':
        """Create configuration from a dictionary.
        
        Args:
            config_dict: Dictionary containing configuration values
            
        Example:
            config = DocsConfig.from_dict({
                'title': 'My API',
                'version': '2.0.0',
                'contact': {'email': 'dev@example.com', 'name': 'Dev Team'},
                'security_schemes': {
                    'BearerAuth': {'description': 'JWT authentication'}
                }
            })
        """
        # Extract contact info if present
        contact = None
        if 'contact' in config_dict:
            contact_data = config_dict['contact']
            if isinstance(contact_data, dict):
                contact = ContactInfo(**contact_data)
        
        # Extract security schemes if present
        security_schemes = {}
        if 'security_schemes' in config_dict:
            schemes_data = config_dict['security_schemes']
            if isinstance(schemes_data, dict):
                for name, scheme_data in schemes_data.items():
                    if isinstance(scheme_data, dict):
                        security_schemes[name] = SecuritySchemeConfig(name=name, **scheme_data)
        
        # Create the config with known fields
        known_fields = {
            'title', 'version', 'description', 'terms_of_service', 
            'license_name', 'license_url', 'servers', 'preserve_flask_routes',
            'clear_auto_discovered', 'add_default_responses', 
            'external_docs_url', 'external_docs_description'
        }
        
        filtered_dict = {k: v for k, v in config_dict.items() if k in known_fields}
        
        return cls(
            contact=contact,
            security_schemes=security_schemes,
            **filtered_dict
        )
    
    def add_security_scheme(self, name: str, config: SecuritySchemeConfig) -> None:
        """Add a new security scheme to the configuration."""
        self.security_schemes[name] = config
    
    def add_server(self, url: str, description: str = "") -> None:
        """Add a server to the configuration."""
        self.servers.append({"url": url, "description": description})
    
    def to_openapi_info(self) -> Dict[str, Any]:
        """Convert to OpenAPI info object."""
        info: Dict[str, Any] = {
            "title": self.title,
            "version": self.version
        }
        
        if self.description:
            info["description"] = self.description
        if self.terms_of_service:
            info["termsOfService"] = self.terms_of_service
        if self.contact:
            contact_dict = self.contact.to_dict()
            if contact_dict:
                info["contact"] = contact_dict
        if self.license_name:
            license_info: Dict[str, Any] = {"name": self.license_name}
            if self.license_url:
                license_info["url"] = self.license_url
            info["license"] = license_info
        
        return info
    
    def to_openapi_security_schemes(self) -> Dict[str, Dict[str, Any]]:
        """Convert security schemes to OpenAPI format."""
        return {
            name: config.to_openapi_dict() 
            for name, config in self.security_schemes.items()
        }
    
    def to_openapi_external_docs(self) -> Optional[Dict[str, Any]]:
        """Convert external docs to OpenAPI format."""
        if self.external_docs_url:
            docs: Dict[str, Any] = {"url": self.external_docs_url}
            if self.external_docs_description:
                docs["description"] = self.external_docs_description
            return docs
        return None
