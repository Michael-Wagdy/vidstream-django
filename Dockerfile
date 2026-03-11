# Use Python 3.11 slim image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install --no-cache-dir poetry==1.7.1

# Copy poetry files
COPY pyproject.toml ./

# Configure poetry
RUN poetry config virtualenvs.create false

# Install Python dependencies
RUN poetry install --only main --no-interaction --no-ansi

# Copy project
COPY . .

# Create necessary directories
RUN mkdir -p /app/media/videos/original /app/media/videos/hls /app/logs /app/staticfiles

# Collect static files
RUN python manage.py collectstatic --noinput || true

# Expose port
EXPOSE 8000

# Run the application
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
