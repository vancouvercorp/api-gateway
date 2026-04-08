"""
Centralized error handling middleware for API Gateway.
Provides consistent error response formatting across all endpoints.
"""

import logging
import traceback
from functools import wraps
from flask import jsonify, request

logger = logging.getLogger(__name__)


class APIError(Exception):
    """Base exception class for API errors."""

    def __init__(self, message, status_code=400, payload=None):
        super().__init__()
        self.message = message
        self.status_code = status_code
        self.payload = payload or {}

    def to_dict(self):
        rv = dict(self.payload or {})
        rv["error"] = self.message
        rv["status_code"] = self.status_code
        return rv


class NotFoundError(APIError):
    def __init__(self, message="Resource not found"):
        super().__init__(message, status_code=404)


class UnauthorizedError(APIError):
    def __init__(self, message="Unauthorized"):
        super().__init__(message, status_code=401)


class ForbiddenError(APIError):
    def __init__(self, message="Forbidden"):
        super().__init__(message, status_code=403)


class ValidationError(APIError):
    def __init__(self, message="Validation error", errors=None):
        super().__init__(message, status_code=422)
        if errors:
            self.payload["errors"] = errors


class RateLimitError(APIError):
    def __init__(self, message="Rate limit exceeded"):
        super().__init__(message, status_code=429)


def handle_api_error(error):
    """Flask error handler for APIError exceptions."""
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    logger.warning(f"API Error: {error.message} [{error.status_code}] - Path: {request.path}")
    return response


def handle_unexpected_error(error):
    """Flask error handler for unexpected exceptions."""
    logger.error(f"Unexpected error: {traceback.format_exc()}")
    response = jsonify({
        "error": "An unexpected error occurred",
        "status_code": 500,
    })
    response.status_code = 500
    return response


def register_error_handlers(app):
    """Register all error handlers on the Flask app."""
    app.register_error_handler(APIError, handle_api_error)
    app.register_error_handler(Exception, handle_unexpected_error)


def catch_errors(f):
    """Decorator to catch and properly format errors in route handlers."""
    @wraps(f)
    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except APIError:
            raise
        except Exception as e:
            logger.error(f"Unhandled exception in {f.__name__}: {traceback.format_exc()}")
            raise APIError(
                message="An internal error occurred",
                status_code=500,
            )
    return wrapper
