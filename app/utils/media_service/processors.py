"""
Image processing and metadata extraction for Media Service.

Author: Emmanuel Olowu
Link: https://github.com/zeddyemy
Package: Folio Builder
"""

from typing import Dict, Any
from PIL import Image

from .utils import log_exception

# Use numeric value for resampling to avoid PIL version compatibility issues
RESAMPLE_FILTER = 3  # BICUBIC resampling (works across all PIL/Pillow versions)


class MediaProcessor:
    """Media processing utilities."""

    @staticmethod
    def extract_file_metadata(file_path: str, file_type: str) -> Dict[str, Any]:
        """Extract metadata from file (dimensions, duration, etc.)."""
        metadata = {}

        try:
            if file_type == 'image':
                with Image.open(file_path) as img:
                    metadata['width'] = img.width
                    metadata['height'] = img.height
                    metadata['format'] = img.format

            # Add more metadata extraction for videos, PDFs, etc. as needed

        except Exception as e:
            log_exception("Metadata extraction failed", e)

        return metadata

    @staticmethod
    def optimize_image(image_path: str, output_path: str, max_width: int = 1920, quality: int = 85) -> Dict[str, Any]:
        """Optimize image for web delivery."""
        try:
            with Image.open(image_path) as img:
                # Convert to RGB if necessary
                if img.mode in ('RGBA', 'LA', 'P'):
                    img = img.convert('RGB')

                # Resize if too large
                if img.width > max_width:
                    ratio = max_width / img.width
                    new_height = int(img.height * ratio)
                    img = img.resize((max_width, new_height), RESAMPLE_FILTER)

                # Save optimized version
                img.save(output_path, 'JPEG', quality=quality, optimize=True)

                return {
                    'width': img.width,
                    'height': img.height,
                    'format': 'JPEG',
                    'quality': quality
                }

        except Exception as e:
            log_exception("Image optimization failed", e)
            return {}
