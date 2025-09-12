"""
User Management Routes for Admin API

Defines all user management endpoints for administrators including
user listing, role management, profile updates, and user statistics.

Author: Emmanuel Olowu
Link: https://github.com/zeddyemy
Package: EventSphere
"""

from __future__ import annotations

from ..controller import UserManagementController
from flask_pydantic_spec import Response
from app.docs import spec, endpoint, QueryParameter, SecurityScheme
from app.utils.decorators.auth import roles_required
from app.schemas.common import ApiResponse
from app.schemas.user_management import (
    UpdateUserRolesRequest,
    UpdateUserStatusRequest,
    UpdateUserProfileRequest,
    UpdateUserAddressRequest
)


def register_routes(bp):
    """Register user management routes."""

    # User Statistics
    @bp.get("/users/stats")
    @roles_required('admin')
    @endpoint(
        security=SecurityScheme.ADMIN_BEARER,
        tags=["User Management"],
        summary="Get User Statistics",
        description="Get comprehensive user statistics for admin dashboard"
    )
    @spec.validate(resp=Response(HTTP_200=ApiResponse, HTTP_401=ApiResponse, HTTP_403=ApiResponse))
    def get_user_statistics():
        """Get user statistics."""
        return UserManagementController.get_user_statistics()

    # List Users
    @bp.get("/users")
    @roles_required('admin')
    @endpoint(
        security=SecurityScheme.ADMIN_BEARER,
        tags=["User Management"],
        summary="List Users",
        description="List users with pagination, filtering, and search",
        query_params=[
            QueryParameter("page", "integer", required=False, description="Page number", default=1),
            QueryParameter("per_page", "integer", required=False, description="Items per page", default=20),
            QueryParameter("role_filter", "string", required=False, description="Filter by role (Admin, Organizer, Participant, Visitor)"),
            QueryParameter("status_filter", "string", required=False, description="Filter by status (active, inactive)"),
            QueryParameter("search", "string", required=False, description="Search in username, email, firstname, lastname"),
        ]
    )
    @spec.validate(resp=Response(HTTP_200=ApiResponse, HTTP_401=ApiResponse, HTTP_403=ApiResponse))
    def list_users():
        """List users with pagination and filtering."""
        return UserManagementController.list_users()

    # Get User Details
    @bp.get("/users/<string:user_id>")
    @roles_required('admin')
    @endpoint(
        security=SecurityScheme.ADMIN_BEARER,
        tags=["User Management"],
        summary="Get User Details",
        description="Get detailed information about a specific user"
    )
    @spec.validate(resp=Response(HTTP_200=ApiResponse, HTTP_404=ApiResponse, HTTP_401=ApiResponse, HTTP_403=ApiResponse))
    def get_user_details(user_id: str):
        """Get detailed user information."""
        return UserManagementController.get_user_details(user_id)

    # Update User Roles
    @bp.patch("/users/<string:user_id>/roles")
    @roles_required('admin')
    @endpoint(
        request_body=UpdateUserRolesRequest,
        security=SecurityScheme.ADMIN_BEARER,
        tags=["User Management"],
        summary="Update User Roles",
        description="Add or remove roles from a user"
    )
    @spec.validate(resp=Response(HTTP_200=ApiResponse, HTTP_400=ApiResponse, HTTP_404=ApiResponse, HTTP_401=ApiResponse, HTTP_403=ApiResponse))
    def update_user_roles(user_id: str):
        """Update user roles."""
        return UserManagementController.update_user_roles(user_id)

    # Update User Status
    @bp.patch("/users/<string:user_id>/status")
    @roles_required('admin')
    @endpoint(
        request_body=UpdateUserStatusRequest,
        security=SecurityScheme.ADMIN_BEARER,
        tags=["User Management"],
        summary="Update User Status",
        description="Activate or deactivate a user account"
    )
    @spec.validate(resp=Response(HTTP_200=ApiResponse, HTTP_400=ApiResponse, HTTP_404=ApiResponse, HTTP_401=ApiResponse, HTTP_403=ApiResponse))
    def update_user_status(user_id: str):
        """Update user active status."""
        return UserManagementController.update_user_status(user_id)

    # Update User Profile
    @bp.patch("/users/<string:user_id>/profile")
    @roles_required('admin')
    @endpoint(
        request_body=UpdateUserProfileRequest,
        security=SecurityScheme.ADMIN_BEARER,
        tags=["User Management"],
        summary="Update User Profile",
        description="Update user's profile information"
    )
    @spec.validate(resp=Response(HTTP_200=ApiResponse, HTTP_400=ApiResponse, HTTP_404=ApiResponse, HTTP_401=ApiResponse, HTTP_403=ApiResponse))
    def update_user_profile(user_id: str):
        """Update user profile information."""
        return UserManagementController.update_user_profile(user_id)

    # Update User Address
    @bp.patch("/users/<string:user_id>/address")
    @roles_required('admin')
    @endpoint(
        request_body=UpdateUserAddressRequest,
        security=SecurityScheme.ADMIN_BEARER,
        tags=["User Management"],
        summary="Update User Address",
        description="Update user's address information"
    )
    @spec.validate(resp=Response(HTTP_200=ApiResponse, HTTP_400=ApiResponse, HTTP_404=ApiResponse, HTTP_401=ApiResponse, HTTP_403=ApiResponse))
    def update_user_address(user_id: str):
        """Update user address information."""
        return UserManagementController.update_user_address(user_id)
