import logging
import os
import subprocess

from celery import shared_task

from .models import Video

logger = logging.getLogger("videos")


@shared_task(bind=True, max_retries=3)
def process_video_task(self, video_id):
    """
    Convert MP4 video to HLS format using FFmpeg
    """
    try:
        video = Video.objects.get(id=video_id)

        # Check if video is already being processed or completed
        if video.status in ["processing", "completed"]:
            logger.info(f"Video {video_id} is already {video.status}, skipping")
            return f"Video already {video.status}"

        logger.info(f"Starting video processing for {video_id}")

        # Update status to processing
        video.status = "processing"
        video.error_message = ""
        video.save()

        # Create HLS directory
        hls_dir = video.hls_directory
        os.makedirs(hls_dir, exist_ok=True)

        # Get input file path
        input_path = video.original_file.path

        # Output playlist path
        playlist_filename = f"{video_id}.m3u8"
        playlist_path = os.path.join(hls_dir, playlist_filename)

        # FFmpeg command for HLS conversion with 10-second segments
        ffmpeg_cmd = [
            "ffmpeg",
            "-i",
            input_path,
            "-c:v",
            "libx264",
            "-c:a",
            "aac",
            "-b:v",
            "1000k",
            "-b:a",
            "128k",
            "-vf",
            "scale=-2:720",
            "-f",
            "hls",
            "-hls_time",
            "10",
            "-hls_list_size",
            "0",
            "-hls_segment_filename",
            os.path.join(hls_dir, "segment_%03d.ts"),
            "-y",  # Overwrite output files
            playlist_path,
        ]

        logger.info(f"Running FFmpeg command: {' '.join(ffmpeg_cmd)}")

        # Run FFmpeg
        result = subprocess.run(
            ffmpeg_cmd, capture_output=True, text=True, timeout=3600  # 1 hour timeout
        )

        if result.returncode != 0:
            error_msg = f"FFmpeg failed: {result.stderr}"
            logger.error(error_msg)
            video.status = "failed"
            video.error_message = error_msg
            video.save()
            return

        # Extract thumbnail at 10 seconds
        thumbnail_path = os.path.join(hls_dir, "thumbnail.jpg")
        thumbnail_cmd = [
            "ffmpeg",
            "-i",
            input_path,
            "-ss",
            "00:00:10",
            "-vframes",
            "1",
            "-q:v",
            "2",
            "-y",
            thumbnail_path,
        ]

        subprocess.run(thumbnail_cmd, capture_output=True, text=True)

        # Get video duration
        duration_cmd = [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            input_path,
        ]

        duration_result = subprocess.run(duration_cmd, capture_output=True, text=True)
        if duration_result.returncode == 0:
            try:
                video.duration = float(duration_result.stdout.strip())
            except ValueError:
                pass

        # Update video with processed file
        relative_playlist_path = os.path.join(
            "videos", "hls", str(video_id), playlist_filename
        )
        video.processed_m3u8.name = relative_playlist_path
        video.status = "completed"
        video.save()

        logger.info(f"Successfully processed video {video_id}")

    except Video.DoesNotExist:
        logger.error(f"Video {video_id} not found")
        raise
    except subprocess.TimeoutExpired:
        error_msg = "Video processing timed out"
        logger.error(f"Processing timeout for video {video_id}")
        video.status = "failed"
        video.error_message = error_msg
        video.save()
        raise
    except Exception as e:
        logger.error(f"Error processing video {video_id}: {str(e)}")

        # Update video status to failed
        try:
            video = Video.objects.get(id=video_id)
            video.status = "failed"
            video.error_message = str(e)
            video.save()
        except Video.DoesNotExist:
            pass

        # Retry with exponential backoff
        if self.request.retries < self.max_retries:
            countdown = 2**self.request.retries
            logger.info(f"Retrying video {video_id} processing in {countdown} seconds")
            raise self.retry(countdown=countdown)
        else:
            logger.error(f"Max retries exceeded for video {video_id}")
            raise
