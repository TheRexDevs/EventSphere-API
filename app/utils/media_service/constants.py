"""
Constants and configuration for Media Service.

Author: Emmanuel Olowu
Link: https://github.com/zeddyemy
Package: Folio Builder
"""

# File type constants
IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.webp', '.svg', '.gif', '.bmp'}
VIDEO_EXTENSIONS = {'.mp4', '.avi', '.mov', '.flv', '.wmv', '.mkv'}
DOCUMENT_EXTENSIONS = {'.pdf', '.doc', '.docx', '.txt', '.rtf'}

# Size limits
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
MAX_IMAGE_SIZE = 25 * 1024 * 1024  # 25MB for images
MAX_VIDEO_SIZE = 100 * 1024 * 1024  # 100MB for videos

# Image optimization settings
THUMBNAIL_SIZE = (300, 300)
MEDIUM_SIZE = (800, 600)
LARGE_SIZE = (1200, 900)
