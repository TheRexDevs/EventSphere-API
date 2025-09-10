"""
Enhanced Media Service Package for Folio Builder.

This package provides comprehensive media management including organized Cloudinary storage,
image optimization, thumbnail generation, and file validation with proper error handling.

Features:
- Organized folder structure: folio_handle/yy/mm/file
- Image optimization and resizing
- Thumbnail generation
- File type validation
- Comprehensive error handling
- Performance optimizations

Author: Emmanuel Olowu
Link: https://github.com/zeddyemy
Package: Folio Builder
"""

import os
import uuid
from datetime import datetime
from typing import Dict, Any, Optional, List

from werkzeug.datastructures import FileStorage

from ...extensions import db
from ...models import Media
from .validators import MediaValidator
from .uploaders import CloudinaryUploader
from .processors import MediaProcessor
from .utils import (
    generate_folio_folder_path,
    generate_unique_filename,
    console_log,
    log_exception
)


class MediaService:
    """Enhanced media service with organization and optimization."""

    @staticmethod
    def validate_file(file: FileStorage, folio_id: uuid.UUID) -> Dict[str, Any]:
        """Validate uploaded file."""
        return MediaValidator.validate_file(file, folio_id)

    @staticmethod
    def upload_to_cloudinary(
        file: FileStorage,
        public_id: str,
        folder: str,
        resource_type: str = 'auto',
        optimization: bool = True
    ) -> Dict[str, Any]:
        """Upload file to Cloudinary."""
        return CloudinaryUploader.upload_to_cloudinary(
            file, public_id, folder, resource_type, optimization
        )

    @staticmethod
    def generate_image_versions(public_id: str, folder: str) -> Dict[str, str]:
        """Generate optimized image versions."""
        return CloudinaryUploader.generate_image_versions(public_id, folder)

    @staticmethod
    def extract_file_metadata(file_path: str, file_type: str) -> Dict[str, Any]:
        """Extract metadata from file."""
        return MediaProcessor.extract_file_metadata(file_path, file_type)

    @staticmethod
    def save_media_record(
        folio_id: uuid.UUID,
        filename: str,
        original_filename: str,
        cloudinary_result: Dict[str, Any],
        file_metadata: Dict[str, Any]
    ) -> Media:
        """Save media record to database."""
        try:
            media = Media()
            media.folio_id = folio_id
            media.filename = filename
            media.original_filename = original_filename
            media.file_path = cloudinary_result['public_id']
            media.file_url = cloudinary_result['secure_url']
            media.file_size = cloudinary_result['bytes']
            media.file_type = cloudinary_result['resource_type']
            media.mime_type = file_metadata.get('mime_type', cloudinary_result.get('format', 'unknown'))
            media.file_extension = file_metadata.get('extension', '')
            media.cloudinary_public_id = cloudinary_result['public_id']
            media.cloudinary_folder = '/'.join(cloudinary_result['public_id'].split('/')[:-1])

            # Image/video specific metadata
            if 'width' in cloudinary_result:
                media.width = cloudinary_result['width']
            if 'height' in cloudinary_result:
                media.height = cloudinary_result['height']
            if 'duration' in cloudinary_result:
                media.duration = cloudinary_result['duration']

            # Optimized versions
            media.optimized_versions = cloudinary_result.get('optimized_versions', {})
            if media.optimized_versions and 'thumbnail' in media.optimized_versions:
                media.thumbnail_url = media.optimized_versions['thumbnail']

            db.session.add(media)
            db.session.commit()

            console_log("Media saved", {
                'id': str(media.id),
                'filename': filename,
                'size': media.file_size
            })

            return media

        except Exception as e:
            db.session.rollback()
            log_exception("Database save failed", e)
            raise e

    @staticmethod
    def upload_media_file(
        file: FileStorage,
        folio_id: uuid.UUID,
        custom_filename: Optional[str] = None,
        optimization: bool = True
    ) -> Media:
        """
        Complete media upload process with validation and optimization.

        Args:
            file: Uploaded file
            folio_id: Target folio ID
            custom_filename: Optional custom filename
            optimization: Whether to apply optimizations

        Returns:
            Media instance

        Raises:
            ValueError: For validation errors
            Exception: For upload/storage errors
        """
        try:
            # Step 1: Validate file
            validation = MediaService.validate_file(file, folio_id)
            if not validation['valid']:
                raise ValueError(validation['error'])

            # Step 2: Generate organized folder path
            folder_path = generate_folio_folder_path(validation['folio'].handle)

            # Step 3: Generate unique filename
            base_name = custom_filename or validation['filename']
            public_id = f"{folder_path}/{generate_unique_filename(base_name, validation['extension'])}"

            # Step 4: Upload to Cloudinary
            cloudinary_result = MediaService.upload_to_cloudinary(
                file=file,
                public_id=public_id,
                folder=folder_path,
                resource_type=validation['file_type'],
                optimization=optimization
            )

            # Step 5: Extract additional metadata
            metadata = {}
            if file.filename:
                metadata = MediaService.extract_file_metadata(
                    file.filename, validation['file_type']
                )
            metadata.update(validation)

            # Step 6: Save to database
            media = MediaService.save_media_record(
                folio_id=folio_id,
                filename=f"{os.path.splitext(base_name)[0]}-{generate_unique_filename(base_name, '')}{validation['extension']}",
                original_filename=validation['original_filename'],
                cloudinary_result=cloudinary_result,
                file_metadata=metadata
            )

            return media

        except Exception as e:
            log_exception("Media upload failed", e)
            raise e

    @staticmethod
    def delete_media(media_id: uuid.UUID, folio_id: uuid.UUID) -> bool:
        """Delete media from Cloudinary and database."""
        try:
            media = Media.query.filter_by(id=media_id, folio_id=folio_id).first()
            if not media:
                return False

            # Delete from Cloudinary
            success = CloudinaryUploader.delete_from_cloudinary(media.cloudinary_public_id)
            if not success:
                log_exception("Cloudinary deletion failed", Exception("Cloudinary deletion returned false"))

            # Delete from database
            db.session.delete(media)
            db.session.commit()

            return True

        except Exception as e:
            db.session.rollback()
            log_exception("Media deletion failed", e)
            return False

    @staticmethod
    def get_media_usage_stats(folio_id: uuid.UUID) -> Dict[str, Any]:
        """Get media usage statistics for a folio."""
        try:
            from sqlalchemy import func

            stats = db.session.query(
                Media.file_type,
                func.count(Media.id).label('count'),
                func.sum(Media.file_size).label('total_size'),
                func.avg(Media.usage_count).label('avg_usage')
            ).filter(Media.folio_id == folio_id).group_by(Media.file_type).all()

            # Calculate totals manually since stat.count and stat.total_size are SQLAlchemy result objects
            total_files = 0
            total_size = 0
            by_type = {}

            for stat in stats:
                count = getattr(stat, 'count', 0) or 0
                size = getattr(stat, 'total_size', 0) or 0
                avg_usage = getattr(stat, 'avg_usage', 0) or 0

                total_files += count
                total_size += size

                by_type[stat.file_type] = {
                    'count': count,
                    'total_size': size,
                    'avg_usage': avg_usage
                }

            return {
                'total_files': total_files,
                'total_size': total_size,
                'by_type': by_type
            }

        except Exception as e:
            log_exception("Stats retrieval failed", e)
            return {}

    @staticmethod
    def bulk_delete_unused_media(folio_id: uuid.UUID, days_old: int = 30) -> int:
        """Delete media files that haven't been used recently."""
        try:
            from datetime import timedelta
            from sqlalchemy import and_, or_

            cutoff_date = datetime.utcnow() - timedelta(days=days_old)

            # Find media with low usage that's old
            unused_media = Media.query.filter(
                and_(
                    Media.folio_id == folio_id,
                    Media.usage_count == 0,
                    Media.created_at < cutoff_date,
                    or_(Media.file_type == 'image', Media.file_type == 'document')
                )
            ).all()

            deleted_count = 0
            for media in unused_media:
                if MediaService.delete_media(media.id, folio_id):
                    deleted_count += 1

            return deleted_count

        except Exception as e:
            log_exception("Bulk deletion failed", e)
            return 0


# Export main service class and key components
__all__ = [
    'MediaService',
    'MediaValidator',
    'CloudinaryUploader',
    'MediaProcessor'
]
