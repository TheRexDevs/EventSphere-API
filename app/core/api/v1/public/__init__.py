from flask import Blueprint
from .routes import auth, system, media

def create_v1_public_api_blueprint():
    bp = Blueprint("v1_public_api", __name__, url_prefix="/")
    
    auth.register_routes(bp)
    system.register_routes(bp)
    media.register_routes(bp)
    
    return bp
