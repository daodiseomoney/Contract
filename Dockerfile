# Multi-stage build for optimized production image
FROM node:18-alpine AS ui-build

WORKDIR /app/ui
COPY src/layer3_external_interfaces/ui/package*.json ./
RUN npm ci --only=production

COPY src/layer3_external_interfaces/ui/ ./
RUN npm run build

# Production Python image
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy Python dependencies
COPY pyproject.toml ./
RUN pip install --no-cache-dir -e .

# Copy application code
COPY . .

# Copy built frontend assets from ui-build stage
COPY --from=ui-build /app/ui/static ./src/layer3_external_interfaces/ui/static

# Create non-root user
RUN useradd --create-home --shell /bin/bash app
RUN chown -R app:app /app
USER app

# Expose port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/api/healthz || exit 1

# Production server command
CMD ["gunicorn", "-b", "0.0.0.0:8080", "--workers", "4", "--timeout", "120", "main:app"]