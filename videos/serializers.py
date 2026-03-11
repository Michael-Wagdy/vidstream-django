from rest_framework import serializers
from django.conf import settings
import os
from .models import Video


class VideoSerializer(serializers.ModelSerializer):
    """Serializer for Video model"""
    hls_url = serializers.SerializerMethodField()
    thumbnail_url = serializers.SerializerMethodField()
    file_size_display = serializers.SerializerMethodField()
    duration_display = serializers.SerializerMethodField()
    
    class Meta:
        model = Video
        fields = [
            'id', 'title', 'description', 'status', 'created_at', 'updated_at',
            'hls_url', 'thumbnail_url', 'file_size', 'file_size_display',
            'duration', 'duration_display', 'error_message'
        ]
        read_only_fields = [
            'id', 'status', 'created_at', 'updated_at', 'hls_url',
            'thumbnail_url', 'file_size', 'file_size_display',
            'duration', 'duration_display', 'error_message'
        ]
    
    def get_hls_url(self, obj):
        """Return HLS URL if available"""
        if obj.processed_m3u8 and obj.status == 'completed':
            return obj.hls_url
        return None
    
    def get_thumbnail_url(self, obj):
        """Return thumbnail URL if available"""
        if obj.status == 'completed' and os.path.exists(obj.thumbnail_path):
            return f"{settings.MEDIA_URL}videos/hls/{obj.id}/thumbnail.jpg"
        return None
    
    def get_file_size_display(self, obj):
        """Return human-readable file size"""
        if obj.file_size:
            for unit in ['B', 'KB', 'MB', 'GB']:
                if obj.file_size < 1024.0:
                    return f"{obj.file_size:.1f} {unit}"
                obj.file_size /= 1024.0
            return f"{obj.file_size:.1f} TB"
        return None
    
    def get_duration_display(self, obj):
        """Return formatted duration"""
        if obj.duration:
            hours = int(obj.duration // 3600)
            minutes = int((obj.duration % 3600) // 60)
            seconds = int(obj.duration % 60)
            
            if hours > 0:
                return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
            else:
                return f"{minutes:02d}:{seconds:02d}"
        return None


class VideoUploadSerializer(serializers.ModelSerializer):
    """Serializer for video upload"""
    
    class Meta:
        model = Video
        fields = ['title', 'description', 'original_file']
    
    def validate_original_file(self, value):
        """Validate uploaded video file"""
        if not value.name.lower().endswith('.mp4'):
            raise serializers.ValidationError("Only MP4 files are allowed.")
        
        # Check file size (max 500MB)
        max_size = 500 * 1024 * 1024  # 500MB
        if value.size > max_size:
            raise serializers.ValidationError("File size must be less than 500MB.")
        
        return value
