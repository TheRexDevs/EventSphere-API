"""
File validation functions for Media Service.

Author: Emmanuel Olowu
Link: https://github.com/zeddyemy
Package: EventSphere
"""

import os
import mimetypes
from typing import Dict, Any
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename
import uuid

from ...extensions import db
from ...models import Event
from .constants import (
    IMAGE_EXTENSIONS, VIDEO_EXTENSIONS, DOCUMENT_EXTENSIONS,
    MAX_FILE_SIZE, MAX_IMAGE_SIZE, MAX_VIDEO_SIZE
)


class MediaValidator:
    """File validation utilities."""

    @staticmethod
    def validate_file(file: FileStorage, event_id: uuid.UUID) -> Dict[str, Any]:
        """
        Comprehensive file validation.

        Args:
            file: The uploaded file
            event_id: Event ID for ownership validation

        Returns:
            Dict with validation results and metadata
        """
        try:
            # Basic file checks
            if not file or not file.filename:
                return {'valid': False, 'error': 'No file provided'}

            filename = secure_filename(file.filename)
            file_size = len(file.read())
            file.seek(0)  # Reset file pointer

            # Size validation
            if file_size > MAX_FILE_SIZE:
                return {'valid': False, 'error': f'File too large. Maximum size: {MAX_FILE_SIZE/1024/1024}MB'}

            # Get file extension and type
            _, ext = os.path.splitext(filename.lower())
            mime_type, _ = mimetypes.guess_type(filename)

            if not mime_type:
                mime_type = file.mimetype or 'application/octet-stream'

            # Determine file type
            if ext in IMAGE_EXTENSIONS:
                file_type = 'image'
                if file_size > MAX_IMAGE_SIZE:
                    return {'valid': False, 'error': f'Image too large. Maximum size: {MAX_IMAGE_SIZE/1024/1024}MB'}
            elif ext in VIDEO_EXTENSIONS:
                file_type = 'video'
                if file_size > MAX_VIDEO_SIZE:
                    return {'valid': False, 'error': f'Video too large. Maximum size: {MAX_VIDEO_SIZE/1024/1024}MB'}
            elif ext in DOCUMENT_EXTENSIONS:
                file_type = 'document'
            else:
                return {'valid': False, 'error': f'Unsupported file type: {ext}'}

            # Event ownership validation
            event = Event.query.filter_by(id=event_id).first()
            if not event:
                return {'valid': False, 'error': 'Invalid event'}

            return {
                'valid': True,
                'filename': filename,
                'original_filename': file.filename,
                'file_size': file_size,
                'file_type': file_type,
                'mime_type': mime_type,
                'extension': ext,
                'event': event
            }

        except Exception as e:
            from .utils import log_exception
            log_exception("File validation failed", e)
            return {'valid': False, 'error': 'Validation failed'}
