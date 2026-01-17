# Use official lightweight Python image
FROM python:3.10-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libgl1-mesa-glx \
    && rm -rf /var/lib/apt/lists/*

# Set work directory
WORKDIR /app

# Copy and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .


# Expose port for Railway
EXPOSE 10000

# Start using Gunicorn
CMD exec gunicorn wsgi:app --bind 0.0.0.0:${PORT:-10000} --workers 3