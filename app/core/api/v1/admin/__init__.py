from flask import Blueprint
from .routes import system

def create_v1_admin_api_blueprint():
    bp = Blueprint("v1_admin_api", __name__, url_prefix="/admin")
    system.register_routes(bp)
    return bp
