# Django Video Streaming Demo

A comprehensive Django video streaming application that demonstrates HLS (HTTP Live Streaming) video processing using FFmpeg, Celery for background tasks, and a modern frontend with Video.js.

## Features

- **Video Upload**: Upload MP4 videos through Django admin
- **HLS Processing**: Automatic conversion to HLS format with 10-second segments
- **Background Processing**: Celery with Redis for asynchronous video processing
- **Video Streaming**: HLS streaming with Video.js frontend
- **Status Tracking**: Real-time processing status (Pending, Processing, Completed, Failed)
- **Thumbnail Generation**: Automatic thumbnail extraction
- **REST API**: DRF endpoints for video management
- **Responsive Design**: Modern, mobile-friendly frontend

## Tech Stack

- **Backend**: Django 5.0, Django Rest Framework
- **Task Queue**: Celery with Redis
- **Video Processing**: FFmpeg
- **Database**: PostgreSQL
- **Frontend**: Video.js, Vanilla JavaScript
- **Containerization**: Docker & Docker Compose
- **Dependency Management**: Poetry

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd django-video-streaming
   ```

2. **Copy environment file**
   ```bash
   cp .env.example .env
   ```

3. **Start the services**
   ```bash
   docker-compose up --build
   ```

4. **Create Django superuser** (in a new terminal)
   ```bash
   docker-compose exec web python manage.py createsuperuser
   ```

5. **Access the application**
   - Frontend: http://localhost:8000
   - Admin Panel: http://localhost:8000/admin
   - API: http://localhost:8000/api

## Usage

### Uploading Videos

1. Go to the Django admin panel at http://localhost:8000/admin
2. Login with your superuser credentials
3. Navigate to "Videos" section
4. Click "Add video" and fill in:
   - Title
   - Description (optional)
   - Upload MP4 file
5. Save - the video will automatically start processing

### Monitoring Processing

- The frontend shows real-time status updates
- Processing status changes: Pending → Processing → Completed/Failed
- Auto-refresh every 30 seconds for processing videos
- Check logs: `docker-compose logs worker`

### API Endpoints

- `GET /api/videos/` - List videos (filterable by status)
- `GET /api/videos/{id}/` - Get video details
- `GET /api/videos/{id}/stream_info/` - Get streaming info
- `GET /api/videos/stats/` - Video statistics

## Project Structure

```
django-video-streaming/
├── config/                 # Django project configuration
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   ├── asgi.py
│   └── celery.py
├── videos/                 # Video app
│   ├── migrations/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   ├── serializers.py
│   ├── tasks.py
│   └── signals.py
├── templates/videos/       # Frontend templates
│   └── index.html
├── media/                  # User uploads (created automatically)
├── static/                 # Static files (created automatically)
├── logs/                   # Application logs (created automatically)
├── Dockerfile
├── docker-compose.yml
├── docker-compose.prod.yml
├── pyproject.toml
├── .env.example
└── README.md
```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `SECRET_KEY` | Django secret key | `django-insecure-change-me` |
| `DEBUG` | Debug mode | `True` |
| `DB_NAME` | Database name | `django_video_streaming` |
| `DB_USER` | Database user | `postgres` |
| `DB_PASSWORD` | Database password | `postgres` |
| `REDIS_URL` | Redis connection URL | `redis://redis:6379/0` |
| `MEDIA_ROOT` | Media files directory | `/app/media` |

### Video Processing Settings

- **Segment Duration**: 10 seconds
- **Video Resolution**: 720p (scaled)
- **Video Bitrate**: 1000k
- **Audio Bitrate**: 128k
- **Codecs**: H.264 (video), AAC (audio)

## Development

### Local Development

1. **Install dependencies**
   ```bash
   poetry install
   ```

2. **Start PostgreSQL and Redis**
   ```bash
   docker-compose up db redis -d
   ```

3. **Run migrations**
   ```bash
   python manage.py migrate
   ```

4. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

5. **Start Django server**
   ```bash
   python manage.py runserver
   ```

6. **Start Celery worker** (in another terminal)
   ```bash
   celery -A config worker -l info
   ```

### Running Tests

```bash
python manage.py test
```

### Code Quality

```bash
# Format code
black .

# Sort imports
isort .

# Lint code
flake8 .
```

## Production Deployment

### Using Production Compose

1. **Set production environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with production values
   ```

2. **Deploy with production compose**
   ```bash
   docker-compose -f docker-compose.prod.yml up --build -d
   ```

### Security Considerations

- Change `SECRET_KEY` in production
- Set `DEBUG=False`
- Use strong database passwords
- Configure HTTPS
- Set up proper file permissions
- Use environment variables for sensitive data

## Monitoring and Logging

### Logs

- **Django logs**: `logs/django.log`
- **Celery logs**: `docker-compose logs worker`
- **Application logs**: Available in container logs

### Monitoring

- Video processing status through admin panel
- Celery task monitoring with Flower (optional)
- Database metrics through PostgreSQL logs

## Troubleshooting

### Common Issues

1. **FFmpeg not found**
   - Ensure FFmpeg is installed in the Docker container
   - Check `docker-compose logs worker`

2. **Videos not processing**
   - Check Celery worker status: `docker-compose logs worker`
   - Verify Redis connection: `docker-compose logs redis`

3. **Database connection errors**
   - Check PostgreSQL status: `docker-compose logs db`
   - Verify database credentials in .env

4. **Permission errors**
   - Ensure media directory has proper permissions
   - Check Docker volume mounts

### Performance Optimization

- Use CDN for static files in production
- Implement video transcoding presets for different qualities
- Add Redis caching for API responses
- Use connection pooling for database
- Implement proper file cleanup for old videos

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For issues and questions:
- Check the troubleshooting section
- Review the logs for error messages
- Open an issue on the repository
