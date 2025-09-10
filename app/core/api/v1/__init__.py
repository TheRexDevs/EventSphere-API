from flask import Blueprint

def create_v1_api_blueprint():
    """Blueprint root for API v1."""
    v1_api = Blueprint("v1_api", __name__, url_prefix="/v1")

    # Ensure route modules are imported so view functions are registered
    import app.core.api.v1.public.routes  # noqa: F401,E402
    import app.core.api.v1.admin.routes  # noqa: F401,E402

    return v1_api
