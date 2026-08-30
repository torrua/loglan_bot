# Production Dockerfile for Loglan Bot & Site
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PORT=8080

# Create non-root system user
RUN groupadd -r appgroup && useradd -r -g appgroup -d /app -s /sbin/nologin appuser

# Set working directory
WORKDIR /app

# Copy dependency files first for layer caching
COPY requirements.txt pyproject.toml ./

# Install python dependencies
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Copy application source code
COPY app/ ./app/
COPY main.py ./

# Ensure correct permissions
RUN chown -R appuser:appgroup /app

# Switch to non-root user
USER appuser

# Expose service port
EXPOSE 8080

# Run with ASGI server Hypercorn
CMD ["hypercorn", "-b", "0.0.0.0:8080", "main:app"]