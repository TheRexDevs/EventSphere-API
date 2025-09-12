"""
User Management Controller for Admin API

Handles user management operations including listing, searching, role management,
and user status updates for administrators.

Author: Emmanuel Olowu
Link: https://github.com/zeddyemy
Package: EventSphere
"""

from __future__ import annotations

import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

from flask import request, g
from sqlalchemy import or_, and_, func
from sqlalchemy.orm import joinedload
from pydantic import ValidationError

from app.extensions import db
from app.models.user import AppUser, Profile, Address
from app.models.role import Role, UserRole
from app.enums.auth import RoleNames
from app.utils.helpers.http_response import success_response, error_response
from app.utils.date_time import DateTimeUtils, to_gmt1_or_none
from app.schemas.user_management import (
    UserListResponse, UserDetails, UserStatsResponse,
    UpdateUserRolesRequest, UpdateUserStatusRequest,
    UpdateUserProfileRequest, UpdateUserAddressRequest,
    UserSummary
)


class UserManagementController:
    """Controller for user management operations."""

    @staticmethod
    def list_users():
        """List users with pagination and optional filtering."""
        try:
            # Get query parameters
            page = int(request.args.get('page', 1))
            per_page = int(request.args.get('per_page', 20))
            role_filter = request.args.get('role_filter')
            status_filter = request.args.get('status_filter')
            search = request.args.get('search')

            # Base query
            query = AppUser.query

            # Apply search filter
            if search:
                query = AppUser.add_search_filters(query, search)

            # Apply role filter
            if role_filter:
                role = Role.query.filter_by(name=RoleNames(role_filter)).first()
                if role:
                    # Filter users who have the specific role
                    query = query.filter(
                        AppUser.id.in_(
                            db.session.query(UserRole.app_user_id)\
                                     .filter(UserRole.role_id == role.id)
                        )
                    )

            # Apply status filter (assuming we add is_active field later if needed)
            # For now, we'll just return all users

            # Get total count
            total = query.count()

            # Apply pagination
            users = query.offset((page - 1) * per_page)\
                        .limit(per_page)\
                        .all()

            # Convert to response format
            user_summaries = []
            for user in users:
                # Get profile data
                profile = user.profile if hasattr(user, 'profile') and user.profile else None
                summary = UserSummary(
                    id=user.id,
                    username=user.username,
                    email=user.email,
                    firstname=profile.firstname if profile else None,
                    lastname=profile.lastname if profile else None,
                    date_joined=DateTimeUtils.format_datetime(to_gmt1_or_none(user.date_joined) or DateTimeUtils.aware_utcnow(), "%Y-%m-%d %H:%M:%S") if user.date_joined else None,
                    roles=user.role_names,
                    is_active=True  # Assuming all users are active for now
                )
                user_summaries.append(summary)

            # Calculate pagination info
            total_pages = (total + per_page - 1) // per_page

            response_data = UserListResponse(
                users=user_summaries,
                total=total,
                page=page,
                per_page=per_page,
                total_pages=total_pages
            )

            return success_response("Users retrieved successfully", 200, response_data.model_dump())

        except ValueError as e:
            return error_response(f"Invalid parameter: {e}", 400)
        except Exception as e:
            return error_response(f"Error retrieving users: {str(e)}", 500)

    @staticmethod
    def get_user_details(user_id: str):
        """Get detailed information about a specific user."""
        try:
            user_uuid = uuid.UUID(user_id)

            # Get user with all related data
            user = AppUser.query.filter_by(id=user_uuid).first()

            if not user:
                return error_response("User not found", 404)

            # Convert to response format
            user_details = UserDetails(
                id=user.id,
                username=user.username,
                email=user.email,
                date_joined=DateTimeUtils.format_datetime(to_gmt1_or_none(user.date_joined) or DateTimeUtils.aware_utcnow(), "%Y-%m-%d %H:%M:%S") if user.date_joined else None,
                profile=user.profile.to_dict() if user.profile else {},
                address=user.address.to_dict() if user.address else {},
                wallet=user.wallet.to_dict() if user.wallet else {},
                roles=user.role_names,
                is_active=True  # Assuming all users are active for now
            )

            return success_response("User details retrieved successfully", 200, user_details.model_dump())

        except ValueError:
            return error_response("Invalid user ID format", 400)
        except Exception as e:
            return error_response(f"Error retrieving user details: {str(e)}", 500)

    @staticmethod
    def update_user_roles(user_id: str):
        """Update user roles (add/remove roles)."""
        try:
            user_uuid = uuid.UUID(user_id)

            # Get current user (admin performing the action)
            current_user = g.user
            if not current_user:
                return error_response("Authentication required", 401)

            # Validate request data
            payload = UpdateUserRolesRequest.model_validate(request.get_json())

            # Get target user
            user = AppUser.query.filter_by(id=user_uuid).first()
            if not user:
                return error_response("User not found", 404)

            # Process roles to add
            for role_name in payload.roles_to_add:
                try:
                    role_enum = RoleNames(role_name)
                    role = Role.query.filter_by(name=role_enum).first()
                    if role:
                        UserRole.assign_role(user, role, current_user)
                except ValueError:
                    return error_response(f"Invalid role name: {role_name}", 400)

            # Process roles to remove
            for role_name in payload.roles_to_remove:
                try:
                    role_enum = RoleNames(role_name)
                    role = Role.query.filter_by(name=role_enum).first()
                    if role:
                        UserRole.revoke_role(user, role, current_user)
                except ValueError:
                    return error_response(f"Invalid role name: {role_name}", 400)

            # Refresh user data
            db.session.refresh(user)

            return success_response(
                "User roles updated successfully",
                200,
                {"roles": user.role_names}
            )

        except ValidationError as e:
            return error_response(f"Validation error: {e}", 400)
        except ValueError:
            return error_response("Invalid user ID format", 400)
        except Exception as e:
            return error_response(f"Error updating user roles: {str(e)}", 500)

    @staticmethod
    def update_user_status(user_id: str):
        """Update user active status."""
        try:
            user_uuid = uuid.UUID(user_id)

            # Validate request data
            payload = UpdateUserStatusRequest.model_validate(request.get_json())

            # Get user
            user = AppUser.query.filter_by(id=user_uuid).first()
            if not user:
                return error_response("User not found", 404)

            # For now, we'll just return success since we don't have an is_active field
            # In a real implementation, you'd update the user's active status
            return success_response(
                f"User {'activated' if payload.is_active else 'deactivated'} successfully",
                200,
                {"user_id": user_id, "is_active": payload.is_active}
            )

        except ValidationError as e:
            return error_response(f"Validation error: {e}", 400)
        except ValueError:
            return error_response("Invalid user ID format", 400)
        except Exception as e:
            return error_response(f"Error updating user status: {str(e)}", 500)

    @staticmethod
    def update_user_profile(user_id: str):
        """Update user profile information."""
        try:
            user_uuid = uuid.UUID(user_id)

            # Validate request data
            payload = UpdateUserProfileRequest.model_validate(request.get_json())

            # Get user with profile
            user = AppUser.query.filter_by(id=user_uuid).first()
            if not user:
                return error_response("User not found", 404)

            # Create profile if it doesn't exist
            if not user.profile:
                user.profile = Profile()
                db.session.add(user.profile)

            # Update profile fields
            update_data = payload.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                setattr(user.profile, field, value)

            db.session.commit()

            return success_response(
                "User profile updated successfully",
                200,
                {"profile": user.profile.to_dict()}
            )

        except ValidationError as e:
            return error_response(f"Validation error: {e}", 400)
        except ValueError:
            return error_response("Invalid user ID format", 400)
        except Exception as e:
            return error_response(f"Error updating user profile: {str(e)}", 500)

    @staticmethod
    def update_user_address(user_id: str):
        """Update user address information."""
        try:
            user_uuid = uuid.UUID(user_id)

            # Validate request data
            payload = UpdateUserAddressRequest.model_validate(request.get_json())

            # Get user with address
            user = AppUser.query.filter_by(id=user_uuid).first()
            if not user:
                return error_response("User not found", 404)

            # Create address if it doesn't exist
            if not user.address:
                user.address = Address()
                db.session.add(user.address)

            # Update address fields
            update_data = payload.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                setattr(user.address, field, value)

            db.session.commit()

            return success_response(
                "User address updated successfully",
                200,
                {"address": user.address.to_dict()}
            )

        except ValidationError as e:
            return error_response(f"Validation error: {e}", 400)
        except ValueError:
            return error_response("Invalid user ID format", 400)
        except Exception as e:
            return error_response(f"Error updating user address: {str(e)}", 500)

    @staticmethod
    def get_user_statistics():
        """Get user statistics for admin dashboard."""
        try:
            # Get total counts
            total_users = AppUser.query.count()

            # Count users by role
            role_counts = db.session.query(
                Role.name,
                func.count(UserRole.app_user_id).label('count')
            ).join(UserRole).group_by(Role.name).all()

            # Convert to dict
            role_count_dict = {str(role_name): count for role_name, count in role_counts}

            # Get recent registrations (last 30 days)
            thirty_days_ago = datetime.utcnow() - timedelta(days=30)
            recent_registrations = AppUser.query.filter(
                AppUser.date_joined >= thirty_days_ago
            ).count()

            # For now, assuming all users are active
            active_users = total_users
            inactive_users = 0

            stats = UserStatsResponse(
                total_users=total_users,
                active_users=active_users,
                inactive_users=inactive_users,
                admin_users=role_count_dict.get('Admin', 0),
                organizer_users=role_count_dict.get('Organizer', 0),
                participant_users=role_count_dict.get('Participant', 0),
                visitor_users=role_count_dict.get('Visitor', 0),
                recent_registrations=recent_registrations
            )

            return success_response("User statistics retrieved successfully", 200, stats.model_dump())

        except Exception as e:
            return error_response(f"Error retrieving user statistics: {str(e)}", 500)
