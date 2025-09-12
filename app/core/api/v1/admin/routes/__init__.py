"""Admin API v1 routes package.

Import submodules to ensure route registration side-effects run at import time.
"""

# isort: off - explicit import order for route registration
from . import system  # noqa: F401
from . import user_management  # noqa: F401

