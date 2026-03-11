from django.contrib import admin
from .models import Video


@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = ['title', 'status', 'created_at', 'file_size', 'duration']
    list_filter = ['status', 'created_at']
    search_fields = ['title', 'description']
    readonly_fields = ['id', 'created_at', 'updated_at', 'file_size', 'duration', 'error_message']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'original_file')
        }),
        ('Processing Information', {
            'fields': ('status', 'processed_m3u8', 'error_message')
        }),
        ('Metadata', {
            'fields': ('id', 'file_size', 'duration', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        """Override save_model to trigger processing"""
        super().save_model(request, obj, form, change)
        
        # If this is a new video with a file, trigger processing
        if not change and obj.original_file:
            from .tasks import process_video_task
            try:
                process_video_task.delay(str(obj.id))
            except Exception as e:
                obj.status = 'failed'
                obj.error_message = f"Failed to start processing: {str(e)}"
                obj.save()
