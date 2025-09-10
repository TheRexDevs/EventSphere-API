"""
Example usage of the Flask OpenAPI Documentation Package.

This example demonstrates how to use the package to create comprehensive
API documentation with minimal configuration.
"""

from flask import Flask
from pydantic import BaseModel
from typing import Optional

# Import the docs package
from docs import FlaskOpenAPISpec, DocsConfig, ContactInfo, SecurityScheme, endpoint


# Define Pydantic models
class CreateUserRequest(BaseModel):
    username: str
    email: str
    password: str
    full_name: Optional[str] = None


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    full_name: Optional[str]
    created_at: str


class ApiResponse(BaseModel):
    status: str
    message: str
    data: Optional[dict] = None


# Create custom configuration
config = DocsConfig(
    title="Example API",
    version="1.0.0",
    description="A sample API demonstrating the Flask OpenAPI Documentation Package",
    contact=ContactInfo(
        email="example@api.com",
        name="Example API Team",
        url="https://example.com"
    ),
    preserve_flask_routes=True,  # Use <string:param> format
    clear_auto_discovered=True,  # Remove duplicates
    add_default_responses=True   # Add default response schemas
)

# Add security schemes
config.add_security_scheme("BearerAuth", {
    "name": "BearerAuth",
    "scheme_type": "apiKey",
    "location": "header",
    "parameter_name": "Authorization",
    "description": "JWT Bearer token authentication"
})

# Add servers
config.add_server("https://api.example.com", "Production")
config.add_server("http://localhost:5000", "Development")

# Create the spec instance
spec_instance = FlaskOpenAPISpec(config)
spec = spec_instance.spec  # For @spec.validate compatibility

# Create Flask app
app = Flask(__name__)


# Define routes with comprehensive documentation
@app.post("/users")
@endpoint(
    request_body=CreateUserRequest,
    security=SecurityScheme.BEARER_AUTH,
    tags=["User Management"],
    summary="Create New User",
    description="Creates a new user account with validation and returns user details"
)
def create_user():
    """Create a new user account."""
    return {"status": "success", "message": "User created successfully"}


@app.get("/users/<string:user_id>")
@endpoint(
    security=SecurityScheme.BEARER_AUTH,
    tags=["User Management"],
    summary="Get User Details",
    description="Retrieve detailed information about a specific user by ID"
)
def get_user(user_id: str):
    """Get user by ID."""
    return {"status": "success", "data": {"id": user_id, "username": "example"}}


@app.put("/users/<string:user_id>")
@endpoint(
    request_body=CreateUserRequest,
    security=SecurityScheme.BEARER_AUTH,
    tags=["User Management"],
    summary="Update User",
    description="Update user information with validation"
)
def update_user(user_id: str):
    """Update user information."""
    return {"status": "success", "message": "User updated successfully"}


@app.delete("/users/<string:user_id>")
@endpoint(
    security=SecurityScheme.BEARER_AUTH,
    tags=["User Management"],
    summary="Delete User",
    description="Permanently delete a user account"
)
def delete_user(user_id: str):
    """Delete user account."""
    return {"status": "success", "message": "User deleted successfully"}


@app.get("/health")
@endpoint(
    tags=["System"],
    summary="Health Check",
    description="Check the health status of the API"
)
def health_check():
    """API health check endpoint."""
    return {"status": "healthy", "message": "API is running"}


@app.get("/")
@endpoint(
    tags=["General"],
    summary="API Information",
    description="Get basic information about the API"
)
def api_info():
    """Get API information."""
    return {
        "name": "Example API",
        "version": "1.0.0",
        "description": "Sample API with comprehensive documentation"
    }


# Initialize the documentation
spec_instance.init_app(app)


if __name__ == "__main__":
    print("Starting Example API...")
    print("Swagger UI: http://localhost:5000/apidoc/swagger")
    print("Redoc: http://localhost:5000/apidoc/redoc")
    app.run(debug=True)
