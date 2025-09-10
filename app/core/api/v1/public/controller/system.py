from __future__ import annotations

from flask import Response

from app.utils.helpers.http_response import success_response

class SystemController:
    @staticmethod
    def get_public_root() -> Response:
        data = {
            "service": "public",
            "version": "v1",
        }
        return success_response("ok", 200, data)
    
    @staticmethod
    def get_public_health() -> Response:
        data = {
            "healthy": True
        }
        return success_response("ok", 200, data)