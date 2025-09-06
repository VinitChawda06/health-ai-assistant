# Universal frontend Dockerfile - Cross-platform compatible
FROM python:3.11-slim

# Set environment variables for consistent behavior
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV LANG=C.UTF-8
ENV LC_ALL=C.UTF-8

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

# Copy frontend code
COPY . .

# Expose Streamlit port
EXPOSE 8501

# Health check for frontend
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8501/_stcore/health || exit 1

# Run frontend with proper configuration
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0", "--server.enableCORS=false", "--server.enableXsrfProtection=false"]
