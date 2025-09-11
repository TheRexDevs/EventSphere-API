from flask import Blueprint
from .routes import auth, system, media, event, registration, certificate, feedback

def create_v1_public_api_blueprint():
    bp = Blueprint("v1_public_api", __name__, url_prefix="/")
    
    auth.register_routes(bp)
    system.register_routes(bp)
    media.register_routes(bp)
    event.register_routes(bp)
    registration.register_routes(bp)
    certificate.register_routes(bp)
    feedback.register_routes(bp)
    
    return bp
