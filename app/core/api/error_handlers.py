"""
Reusable error handler attachment for API blueprints.

Attaches common handlers (HTTP, DB, JWT, generic) to a given blueprint so
endpoints can avoid repetitive try/except blocks and always return JSON.
"""

from __future__ import annotations

from typing import Any

from flask import Blueprint, request
from werkzeug.exceptions import HTTPException, UnsupportedMediaType
from sqlalchemy.exc import (
    IntegrityError,
    DataError,
    DatabaseError,
    InvalidRequestError,
    OperationalError,
)

from app.logging import log_error
from app.utils.helpers.http_response import error_response

try:
    from email_validator import EmailNotValidError
except Exception:  # pragma: no cover
    EmailNotValidError = type("EmailNotValidError", (), {})  # type: ignore

try:
    from pydantic import ValidationError as PydanticValidationError  # type: ignore
except Exception:  # pragma: no cover
    PydanticValidationError = type("PydanticValidationError", (), {})  # type: ignore

try:
    from pydantic_core import ValidationError as CoreValidationError  # type: ignore
except Exception:  # pragma: no cover
    CoreValidationError = type("CoreValidationError", (), {})  # type: ignore

try:  # jwt-related exceptions are optional at import time
    from flask_jwt_extended.exceptions import (
        JWTDecodeError,
        NoAuthorizationError,
        InvalidHeaderError,
        WrongTokenError,
        RevokedTokenError,
        FreshTokenRequired,
        CSRFError,
    )
except Exception:  # pragma: no cover - package presence varies
    JWTDecodeError = type("JWTDecodeError", (), {})  # type: ignore
    NoAuthorizationError = type("NoAuthorizationError", (), {})  # type: ignore
    InvalidHeaderError = type("InvalidHeaderError", (), {})  # type: ignore
    WrongTokenError = type("WrongTokenError", (), {})  # type: ignore
    RevokedTokenError = type("RevokedTokenError", (), {})  # type: ignore
    FreshTokenRequired = type("FreshTokenRequired", (), {})  # type: ignore
    CSRFError = type("CSRFError", (), {})  # type: ignore

try:
    from jwt import ExpiredSignatureError
except Exception:  # pragma: no cover
    ExpiredSignatureError = type("ExpiredSignatureError", (), {})  # type: ignore


def attach_api_error_handlers(bp: Blueprint) -> None:
    """Register common JSON error handlers on the given blueprint."""

    # HTTPException → use provided code/description
    def _handle_http_exception(err: HTTPException):
        log_error("HTTP exception", err, path=request.path)
        status = err.code or 500
        description = err.description or err.name
        return error_response(description, status)

    bp.register_error_handler(HTTPException, _handle_http_exception)

    # 415 Unsupported Media Type
    def _handle_unsupported_media_type(err: UnsupportedMediaType):
        log_error("Unsupported media type", err, path=request.path)
        return error_response("unsupported media type", 415)

    bp.register_error_handler(UnsupportedMediaType, _handle_unsupported_media_type)

    # JWT / auth errors → 401/403
    def _handle_jwt_decode(err: JWTDecodeError):  # type: ignore[name-defined]
        log_error("Invalid token", err, path=request.path)
        return error_response("invalid token", 401)

    def _handle_expired(err: ExpiredSignatureError):  # type: ignore[name-defined]
        log_error("Token expired", err, path=request.path)
        return error_response("token expired", 401)

    def _handle_no_auth(err: NoAuthorizationError):  # type: ignore[name-defined]
        log_error("Authorization missing", err, path=request.path)
        return error_response("authorization required", 401)

    def _handle_invalid_header(err: InvalidHeaderError):  # type: ignore[name-defined]
        log_error("Invalid auth header", err, path=request.path)
        return error_response("invalid authorization header", 401)

    def _handle_wrong_token(err: WrongTokenError):  # type: ignore[name-defined]
        log_error("Wrong token", err, path=request.path)
        return error_response("wrong token type", 401)

    def _handle_revoked(err: RevokedTokenError):  # type: ignore[name-defined]
        log_error("Revoked token", err, path=request.path)
        return error_response("token revoked", 401)

    def _handle_fresh_required(err: FreshTokenRequired):  # type: ignore[name-defined]
        log_error("Fresh token required", err, path=request.path)
        return error_response("fresh token required", 401)

    def _handle_csrf(err: CSRFError):  # type: ignore[name-defined]
        log_error("CSRF error", err, path=request.path)
        return error_response("csrf error", 401)

    bp.register_error_handler(JWTDecodeError, _handle_jwt_decode)  # type: ignore[arg-type]
    bp.register_error_handler(ExpiredSignatureError, _handle_expired)  # type: ignore[arg-type]
    bp.register_error_handler(NoAuthorizationError, _handle_no_auth)  # type: ignore[arg-type]
    bp.register_error_handler(InvalidHeaderError, _handle_invalid_header)  # type: ignore[arg-type]
    bp.register_error_handler(WrongTokenError, _handle_wrong_token)  # type: ignore[arg-type]
    bp.register_error_handler(RevokedTokenError, _handle_revoked)  # type: ignore[arg-type]
    bp.register_error_handler(FreshTokenRequired, _handle_fresh_required)  # type: ignore[arg-type]
    bp.register_error_handler(CSRFError, _handle_csrf)  # type: ignore[arg-type]

    # Email validation errors → 400 with message
    def _handle_email_invalid(err: EmailNotValidError):  # type: ignore[name-defined]
        log_error("Invalid email", err, path=request.path)
        return error_response(str(err), 400)

    bp.register_error_handler(EmailNotValidError, _handle_email_invalid)  # type: ignore[arg-type]

    # Pydantic validation errors → 400 with structured details
    def _serialize_pydantic_errors(err: Any) -> list[dict[str, Any]]:
        try:
            return [
                {
                    "loc": list(getattr(e, "loc", ())),
                    "msg": getattr(e, "msg", str(e)),
                    "type": getattr(e, "type", "value_error"),
                }
                for e in err.errors()  # type: ignore[attr-defined]
            ]
        except Exception:
            return [{"msg": str(err)}]

    def _handle_pydantic_validation(err: PydanticValidationError):  # type: ignore[name-defined]
        log_error("Validation error", err, path=request.path)
        return error_response("validation error", 400, {"errors": _serialize_pydantic_errors(err)})

    def _handle_core_validation(err: CoreValidationError):  # type: ignore[name-defined]
        log_error("Validation error", err, path=request.path)
        return error_response("validation error", 400, {"errors": _serialize_pydantic_errors(err)})

    bp.register_error_handler(PydanticValidationError, _handle_pydantic_validation)  # type: ignore[arg-type]
    bp.register_error_handler(CoreValidationError, _handle_core_validation)  # type: ignore[arg-type]

    # Database errors → rollback and return appropriate code
    def _rollback():
        try:
            from app.extensions import db  # lazy import to avoid circulars
            db.session.rollback()
        except Exception:
            pass

    def _handle_integrity(err: IntegrityError):
        _rollback()
        log_error("Integrity error", err, path=request.path)
        return error_response("conflict with existing data", 409)

    def _handle_data(err: DataError):
        _rollback()
        log_error("Invalid data", err, path=request.path)
        return error_response("invalid data", 400)

    def _handle_invalid_request(err: InvalidRequestError):
        _rollback()
        log_error("Invalid request", err, path=request.path)
        return error_response("invalid request", 400)

    def _handle_db_operational(err: OperationalError):
        _rollback()
        log_error("Database operational error", err, path=request.path)
        return error_response("database error", 500)

    def _handle_db_generic(err: DatabaseError):
        _rollback()
        log_error("Database error", err, path=request.path)
        return error_response("database error", 500)

    bp.register_error_handler(IntegrityError, _handle_integrity)
    bp.register_error_handler(DataError, _handle_data)
    bp.register_error_handler(InvalidRequestError, _handle_invalid_request)
    bp.register_error_handler(OperationalError, _handle_db_operational)
    bp.register_error_handler(DatabaseError, _handle_db_generic)

    # Catch-all → 500
    def _handle_unexpected(err: Exception):
        _rollback()
        log_error("Unhandled exception", err, path=request.path)
        return error_response("internal server error", 500)

    bp.register_error_handler(Exception, _handle_unexpected)


