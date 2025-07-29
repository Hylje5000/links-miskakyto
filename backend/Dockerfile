# Multi-stage build for better caching
FROM python:3.12-slim as base

# Install system dependencies once
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Dependencies stage
FROM base as dependencies
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Runtime stage
FROM dependencies as runtime
WORKDIR /app

# Copy application code (this layer changes most often)
COPY . .

# Create directory for database
RUN mkdir -p /app/data

# Ensure alembic.ini database path is configured for container environment
RUN if [ -f alembic.ini ]; then \
    sed -i 's|sqlalchemy.url = sqlite:///./links.db|sqlalchemy.url = sqlite:///data/links.db|g' alembic.ini; \
    echo "✅ alembic.ini configured for container environment"; \
    fi

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/health || exit 1

# Run the application (migrations will run automatically via init_db)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
