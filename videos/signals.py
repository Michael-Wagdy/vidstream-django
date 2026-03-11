from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Video
import logging

logger = logging.getLogger('videos')


@receiver(post_save, sender=Video)
def video_post_save(sender, instance, created, **kwargs):
    """Signal to trigger video processing after creation"""
    if created and instance.original_file:
        from .tasks import process_video_task
        try:
            process_video_task.delay(str(instance.id))
            logger.info(f"Triggered processing for new video {instance.id}")
        except Exception as e:
            logger.error(f"Failed to trigger processing for video {instance.id}: {e}")
            instance.status = 'failed'
            instance.error_message = f"Failed to start processing: {str(e)}"
            instance.save()
