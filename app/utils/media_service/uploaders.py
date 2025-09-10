"""
Cloudinary upload functions for Media Service.

Author: Emmanuel Olowu
Link: https://github.com/zeddyemy
Package: Folio Builder
"""

from typing import Dict, Any
from werkzeug.datastructures import FileStorage
import cloudinary
import cloudinary.uploader
import cloudinary.api

from config import Config
from .constants import THUMBNAIL_SIZE, MEDIUM_SIZE, LARGE_SIZE
from .utils import log_exception

# Cloudinary configuration
cloudinary.config(
    cloud_name=Config.CLOUDINARY_CLOUD_NAME,
    api_key=Config.CLOUDINARY_API_KEY,
    api_secret=Config.CLOUDINARY_API_SECRET
)


class CloudinaryUploader:
    """Cloudinary upload utilities."""

    @staticmethod
    def upload_to_cloudinary(
        file: FileStorage,
        public_id: str,
        folder: str,
        resource_type: str = 'auto',
        optimization: bool = True
    ) -> Dict[str, Any]:
        """
        Upload file to Cloudinary with optimization.

        Args:
            file: File to upload
            public_id: Unique public ID
            folder: Cloudinary folder path
            resource_type: auto, image, video, raw
            optimization: Whether to apply optimizations

        Returns:
            Cloudinary upload result
        """
        try:
            upload_options = {
                'public_id': public_id,
                'folder': folder,
                'resource_type': resource_type,
                'overwrite': True,
                'invalidate': True
            }

            # Add optimization for images
            if resource_type == 'image' and optimization:
                upload_options.update({
                    'quality': 'auto',
                    'fetch_format': 'auto',
                    'width': 1920,
                    'height': 1080,
                    'crop': 'limit'
                })

            result = cloudinary.uploader.upload(file, **upload_options)

            # Generate optimized versions for images
            if resource_type == 'image':
                result['optimized_versions'] = CloudinaryUploader.generate_image_versions(
                    result['public_id'], folder
                )

            return result

        except Exception as e:
            log_exception("Cloudinary upload failed", e)
            raise e

    @staticmethod
    def generate_image_versions(public_id: str, folder: str) -> Dict[str, str]:
        """Generate thumbnail and optimized versions of uploaded image."""
        try:
            versions = {}

            # Thumbnail version
            thumbnail = cloudinary.api.resource(public_id, transformation=[
                {'width': THUMBNAIL_SIZE[0], 'height': THUMBNAIL_SIZE[1], 'crop': 'fill'},
                {'quality': 'auto'}
            ])
            versions['thumbnail'] = thumbnail['secure_url']

            # Medium version
            medium = cloudinary.api.resource(public_id, transformation=[
                {'width': MEDIUM_SIZE[0], 'height': MEDIUM_SIZE[1], 'crop': 'limit'},
                {'quality': 'auto'}
            ])
            versions['medium'] = medium['secure_url']

            # Large version
            large = cloudinary.api.resource(public_id, transformation=[
                {'width': LARGE_SIZE[0], 'height': LARGE_SIZE[1], 'crop': 'limit'},
                {'quality': 'auto'}
            ])
            versions['large'] = large['secure_url']

            return versions

        except Exception as e:
            log_exception("Image version generation failed", e)
            return {}

    @staticmethod
    def delete_from_cloudinary(public_id: str) -> bool:
        """Delete file from Cloudinary."""
        try:
            result = cloudinary.uploader.destroy(public_id)
            return result.get('result') == 'ok'
        except Exception as e:
            log_exception("Cloudinary deletion failed", e)
            return False
