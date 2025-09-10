"""
Utility functions for Media Service.

Author: Emmanuel Olowu
Link: https://github.com/zeddyemy
Package: Folio Builder
"""

import os
from datetime import date

from ...utils.helpers.basics import generate_random_string
from ...utils.helpers.loggers import console_log, log_exception


def generate_folio_folder_path(folio_handle: str) -> str:
    """Generate organized folder path: folio_handle/yy/mm."""
    today = date.today()
    year = str(today.year)
    month = str(today.month).zfill(2)
    return f"{folio_handle}/{year}/{month}"


def generate_unique_filename(base_name: str, extension: str) -> str:
    """Generate a unique filename with random string."""
    rand_string = generate_random_string(8)
    name_without_ext = os.path.splitext(base_name)[0]
    return f"{name_without_ext}-{rand_string}{extension}"


def get_file_size_mb(file_size_bytes: int) -> float:
    """Convert file size from bytes to MB."""
    return file_size_bytes / (1024 * 1024)


def is_valid_filename(filename: str) -> bool:
    """Validate filename format."""
    from werkzeug.utils import secure_filename
    return secure_filename(filename) == filename


# Re-export logging functions for convenience
__all__ = [
    'generate_folio_folder_path',
    'generate_unique_filename',
    'get_file_size_mb',
    'is_valid_filename',
    'console_log',
    'log_exception'
]
