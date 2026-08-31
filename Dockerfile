# Production Multi-Stage Dockerfile for Loglan Bot & Site
# Stage 1: Dependency builder using uv
FROM ghcr.io/astral-sh/uv:latest AS uv_installer
FROM python:3.12-slim AS builder

WORKDIR /app
COPY --from=uv_installer /uv /uvx /bin/

# Copy requirements for layer caching
COPY requirements.txt ./

# Install dependencies into virtual environment
RUN uv venv /opt/venv && \
    uv pip install --no-cache -r requirements.txt --python /opt/venv/bin/python

# Stage 2: Minimal runtime image
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH" \
    PORT=8080

# Create non-root system user
RUN groupadd -r appgroup && useradd -r -g appgroup -d /app -s /sbin/nologin appuser

# Set working directory
WORKDIR /app

# Copy virtual environment and application code
COPY --from=builder /opt/venv /opt/venv
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