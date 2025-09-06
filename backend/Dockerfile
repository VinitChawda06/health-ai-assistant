# Universal backend Dockerfile - Cross-platform compatible
FROM python:3.11-slim

# Set environment variables for consistent behavior
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV LANG=C.UTF-8
ENV LC_ALL=C.UTF-8

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip to latest version
RUN pip install --upgrade pip

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies with no cache for smaller image
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY . .

# Create data directory
RUN mkdir -p data

# Expose port for FastAPI
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Start backend with proper configuration
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
