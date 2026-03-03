# Use Python 3.11 slim image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copy project
COPY . .

# Make start script executable
RUN chmod +x start.sh

# Collect static files
RUN python manage.py collectstatic --noinput || true

# Expose Railway dynamic port
EXPOSE $PORT

# Start Gunicorn using Railway port
CMD ["gunicorn", "lkc_school.wsgi:application", "--bind", "0.0.0.0:$PORT", "--workers", "2", "--timeout", "120"]