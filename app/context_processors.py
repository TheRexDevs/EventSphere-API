from flask_login import current_user

from .logging import log_event
from .utils.helpers.user import get_app_user_info
from .extensions import db

def app_context_Processor():
    user_id = current_user.id if current_user.is_authenticated else None
    
    current_user_info = get_app_user_info(user_id)
    
    
    return {
        'CURRENT_USER': current_user_info,
        'SITE_INFO': {
            "site_title": "Folio Builder",
            "site_tagline": "Build and scale beautiful portfolios",
            "currency": "NGN",
        },
    }