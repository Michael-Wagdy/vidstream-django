# 🚀 Quick Start Guide

## ✅ Status: Application is Running Successfully!

All services are up and running:
- **Web Server**: http://localhost:8000 ✅
- **Admin Panel**: http://localhost:8000/admin ✅  
- **API**: http://localhost:8000/api ✅
- **Database**: PostgreSQL on port 5433 ✅
- **Redis**: On port 6380 ✅
- **Celery Worker**: Running ✅

## 🎯 Next Steps

### 1. Access the Application

**Frontend**: http://localhost:8000
- View video gallery
- Monitor processing status
- Watch HLS videos

**Admin Panel**: http://localhost:8000/admin
- Username: `root` (or whatever you set)
- Password: (what you created)

### 2. Upload Your First Video

1. Go to http://localhost:8000/admin
2. Login with your superuser credentials
3. Click "Videos" → "Add video"
4. Fill in:
   - **Title**: Your video title
   - **Description**: Optional description
   - **Original File**: Choose an MP4 file
5. Click "Save"

### 3. Watch the Magic Happen

- Video status: **Pending** → **Processing** → **Completed**
- Automatic HLS conversion with 10-second segments
- Thumbnail generation
- Ready for streaming!

### 4. Monitor Processing

Check the Celery worker logs:
```bash
sudo docker compose logs worker -f
```

## 📊 Test the API

```bash
# List all videos
curl http://localhost:8000/api/videos/

# Get video statistics
curl http://localhost:8000/api/videos/stats/

# Check specific video (after upload)
curl http://localhost:8000/api/videos/{video-id}/
```

## 🔧 Useful Commands

```bash
# Check all services status
sudo docker compose ps

# View logs for specific service
sudo docker compose logs web
sudo docker compose logs worker
sudo docker compose logs db

# Stop all services
sudo docker compose down

# Restart services
sudo docker compose restart

# Create new superuser
sudo docker compose exec web python manage.py createsuperuser
```

## 🎬 Video Processing Details

- **Input**: MP4 files (max 500MB)
- **Output**: HLS format with 10-second segments
- **Resolution**: 720p (scaled)
- **Video Codec**: H.264
- **Audio Codec**: AAC
- **Thumbnails**: Extracted at 10 seconds

## 📁 File Structure

Videos are stored in:
- **Originals**: `/media/videos/original/`
- **HLS Files**: `/media/videos/hls/{video-id}/`
- **Thumbnails**: `/media/videos/hls/{video-id}/thumbnail.jpg`

## 🚨 Troubleshooting

### Video Not Processing?
```bash
# Check worker logs
sudo docker compose logs worker

# Check Redis connection
sudo docker compose exec redis redis-cli ping

# Restart worker
sudo docker compose restart worker
```

### Can't Access Admin?
```bash
# Create new superuser
sudo docker compose exec web python manage.py createsuperuser
```

### Database Issues?
```bash
# Check database logs
sudo docker compose logs db

# Reset database (WARNING: Deletes all data)
sudo docker compose down -v
sudo docker compose up --build
```

## 🎉 Success!

Your Django video streaming platform is ready! Upload videos through the admin panel and watch them automatically process into HLS format for smooth streaming.

The frontend will automatically refresh to show processing progress and completed videos ready for playback.
