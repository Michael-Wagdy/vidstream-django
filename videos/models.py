import logging
import os
import uuid

from django.conf import settings
from django.core.files.storage import default_storage
from django.db import models

logger = logging.getLogger("videos")


def get_video_upload_path(instance, filename):
    """Generate upload path for original video files"""
    ext = filename.split(".")[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    return os.path.join("videos", "original", filename)


def get_hls_upload_path(instance, filename):
    """Generate upload path for HLS files"""
    return os.path.join("videos", "hls", str(instance.id), filename)


class Video(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("processing", "Processing"),
        ("completed", "Completed"),
        ("failed", "Failed"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    original_file = models.FileField(
        upload_to=get_video_upload_path, help_text="Upload MP4 video file"
    )
    processed_m3u8 = models.FileField(
        upload_to=get_hls_upload_path,
        null=True,
        blank=True,
        help_text="Generated HLS playlist file",
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    file_size = models.BigIntegerField(null=True, blank=True)
    duration = models.FloatField(null=True, blank=True)
    error_message = models.TextField(blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title

    @property
    def hls_directory(self):
        """Return the directory path for HLS files"""
        return os.path.join(settings.MEDIA_ROOT, "videos", "hls", str(self.id))

    @property
    def hls_url(self):
        """Return the URL for the HLS playlist"""
        if self.processed_m3u8:
            return self.processed_m3u8.url
        return None

    @property
    def thumbnail_path(self):
        """Return path to thumbnail if it exists"""
        return os.path.join(self.hls_directory, "thumbnail.jpg")

    def save(self, *args, **kwargs):
        """Override save to set file size"""
        is_new = self.pk is None

        if is_new and self.original_file:
            # Set file size
            self.file_size = self.original_file.size

        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """Override delete to clean up files"""
        # Delete HLS directory
        if os.path.exists(self.hls_directory):
            import shutil

            shutil.rmtree(self.hls_directory)

        # Delete original file
        if self.original_file and default_storage.exists(self.original_file.name):
            default_storage.delete(self.original_file.name)

        super().delete(*args, **kwargs)
