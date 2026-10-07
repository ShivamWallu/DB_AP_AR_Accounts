# Multi-stage, production-optimized Dockerfile for AWS Deployment
FROM python:3.11-slim as builder

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python requirements
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Final runtime stage
FROM python:3.11-slim

WORKDIR /app

# Install runtime libpq for PostgreSQL / RDS
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy installed wheels from builder
COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Copy application files
COPY . .

# Create necessary directories for storage
RUN mkdir -p uploads data_files

# Expose port 8000
EXPOSE 8000

# Healthcheck for AWS Load Balancer / ECS Target Group
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD curl -f http://localhost:8000/api/dashboard/stats || exit 1

# Launch using Gunicorn with Uvicorn workers for high concurrency on AWS
CMD ["gunicorn", "app.main:app", "--workers", "4", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000", "--timeout", "120", "--keep-alive", "5"]
