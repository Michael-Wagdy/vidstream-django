from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from .models import Video
from .serializers import VideoSerializer, VideoUploadSerializer
import logging

logger = logging.getLogger('videos')


class VideoViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing videos
    """
    queryset = Video.objects.all()
    serializer_class = VideoSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status']
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'title']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Filter to show only completed videos by default"""
        queryset = Video.objects.all()
        status_filter = self.request.query_params.get('status', 'completed')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        return queryset
    
    @action(detail=True, methods=['get'])
    def stream_info(self, request, pk=None):
        """Return streaming information for a specific video"""
        video = get_object_or_404(Video, pk=pk)
        
        if video.status != 'completed':
            return Response(
                {'error': 'Video is not ready for streaming'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        data = {
            'id': str(video.id),
            'title': video.title,
            'hls_url': video.hls_url,
            'thumbnail_url': f"{request.build_absolute_uri('/')}media/videos/hls/{video.id}/thumbnail.jpg" if video.status == 'completed' else None,
            'duration': video.duration,
            'duration_display': VideoSerializer(video).get_duration_display(video),
        }
        
        return Response(data)
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Return video statistics"""
        stats = {
            'total_videos': Video.objects.count(),
            'completed_videos': Video.objects.filter(status='completed').count(),
            'processing_videos': Video.objects.filter(status='processing').count(),
            'failed_videos': Video.objects.filter(status='failed').count(),
            'pending_videos': Video.objects.filter(status='pending').count(),
        }
        return Response(stats)
