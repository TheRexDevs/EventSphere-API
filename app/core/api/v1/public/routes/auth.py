from __future__ import annotations

from ..controller import AuthController
from flask_pydantic_spec import Response
from app.docs import spec, endpoint, SecurityScheme, QueryParameter
from app.schemas.common import ApiResponse
from app.schemas.auth import (
    VerifyEmailRequest,
    SignUpRequest,
    LoginRequest,
    ResendCodeRequest,
    ValidateTokenRequest,
    CheckEmailRequest,
    CheckUsernameRequest,
    ForgotPasswordRequest,
    ValidateResetTokenRequest,
    ResetPasswordRequest,
)

def register_routes(bp):
    @bp.post("/auth/login")
    @endpoint(
        request_body=LoginRequest,
        tags=["Authentication"],
        summary="User Login",
        description="Authenticate user with email/username and password to receive access token"
    )
    @spec.validate(resp=Response(HTTP_200=ApiResponse, HTTP_400=ApiResponse, HTTP_401=ApiResponse))
    def login():
        """Authenticate and return access token."""
        return AuthController.login()

    @bp.post("/auth/signup")
    @endpoint(
        request_body=SignUpRequest,
        tags=["Authentication"],
        summary="User Registration",
        description="Create new user account and send email verification code"
    )
    @spec.validate(resp=Response(HTTP_200=ApiResponse, HTTP_400=ApiResponse, HTTP_409=ApiResponse))
    def sign_up():
        """Create a new account."""
        return AuthController.sign_up()


    @bp.post("/auth/verify-email")
    @endpoint(
        request_body=VerifyEmailRequest,
        tags=["Authentication"],
        summary="Email Verification",
        description="Verify email with code to complete registration"
    )
    @spec.validate(resp=Response(HTTP_200=ApiResponse, HTTP_400=ApiResponse, HTTP_409=ApiResponse))
    def verify_email():
        """Verify emailed code and finalize registration."""
        return AuthController.verify_email()


    @bp.post("/auth/resend-code")
    @endpoint(
        request_body=ResendCodeRequest,
        tags=["Authentication"],
        summary="Resend Verification Code",
        description="Resend email verification code for pending registration"
    )
    @spec.validate(resp=Response(HTTP_200=ApiResponse, HTTP_400=ApiResponse, HTTP_429=ApiResponse))
    def resend_verification_code():
        """Resend verification code for pending registration."""
        return AuthController.resend_verification_code()


    @bp.post("/auth/validate-token")
    @endpoint(
        security=SecurityScheme.PUBLIC_BEARER,
        tags=["Authentication"],
        summary="Validate JWT Token",
        description="Check if a JWT token is valid and not expired"
    )
    @spec.validate(resp=Response(HTTP_200=ApiResponse))
    def validate_token():
        """Validate if a JWT token is valid and not expired."""
        return AuthController.validate_token()


    @bp.post("/auth/refresh-token")
    @endpoint(
        security=SecurityScheme.PUBLIC_BEARER,
        tags=["Authentication"],
        summary="Refresh Access Token",
        description="Generate new access token using existing valid token"
    )
    @spec.validate(resp=Response(HTTP_200=ApiResponse, HTTP_401=ApiResponse, HTTP_404=ApiResponse))
    def refresh_token():
        """Refresh an access token."""
        return AuthController.refresh_token()


    @bp.post("/auth/check-email")
    @endpoint(
        request_body=CheckEmailRequest,
        tags=["Utilities"],
        summary="Check Email Availability",
    )
    @spec.validate(resp=Response(HTTP_200=ApiResponse, HTTP_400=ApiResponse))
    def check_email_availability():
        """Check if an email is already taken."""
        return AuthController.check_email_availability()


    @bp.post("/auth/check-username")
    @endpoint(
        request_body=CheckUsernameRequest,
        tags=["Utilities"],
        summary="Check Username Availability",
    )
    @spec.validate(resp=Response(HTTP_200=ApiResponse, HTTP_400=ApiResponse))
    def check_username_availability():
        """Check if a username is already taken."""
        return AuthController.check_username_availability()


    @bp.post("/auth/forgot-password")
    @endpoint(
        request_body=ForgotPasswordRequest,
        tags=["Authentication"],
        summary="Request Password Reset",
        description="Request a password reset link to be sent to the provided email address. Always returns success to prevent email enumeration."
    )
    @spec.validate(resp=Response(HTTP_200=ApiResponse, HTTP_400=ApiResponse))
    def forgot_password():
        """Request a password reset."""
        return AuthController.forgot_password()


    @bp.get("/auth/pwd-reset-token")
    @endpoint(
        tags=["Authentication"],
        summary="Validate Password Reset Token",
        description="Validate a password reset token from query parameter. Used by frontend to check token validity before showing reset form.",
        query_params=[
            QueryParameter("token", "string", required=True, description="JWT password reset token")
        ]
    )
    @spec.validate(resp=Response(HTTP_200=ApiResponse, HTTP_400=ApiResponse, HTTP_429=ApiResponse))
    def validate_reset_token():
        """Validate a password reset token."""
        return AuthController.validate_reset_token()


    @bp.post("/auth/reset-password")
    @endpoint(
        request_body=ResetPasswordRequest,
        tags=["Authentication"],
        summary="Reset Password",
        description="Reset user password using a valid reset token. Token is invalidated after successful reset."
    )
    @spec.validate(resp=Response(HTTP_200=ApiResponse, HTTP_400=ApiResponse, HTTP_404=ApiResponse, HTTP_429=ApiResponse, HTTP_500=ApiResponse))
    def reset_password():
        """Reset user password."""
        return AuthController.reset_password()