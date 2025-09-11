from flask import Blueprint
from .routes import system, event, attendance, certificate, feedback

def create_v1_admin_api_blueprint():
    bp = Blueprint("v1_admin_api", __name__, url_prefix="/admin")
    system.register_routes(bp)
    event.register_routes(bp)
    attendance.register_routes(bp)
    certificate.register_routes(bp)
    feedback.register_routes(bp)
    return bp
