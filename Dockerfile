# Use multi-stage build for smaller final image
FROM python:3.10-slim as builder

# Set working directory
WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy only the files needed for installation
COPY pyproject.toml setup.cfg README.md ./
COPY src ./src

# Create virtual environment and install dependencies
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --no-cache-dir -e .

# Final stage
FROM python:3.10-slim

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv

# Set environment variables
ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Create non-root user
RUN useradd -m -s /bin/bash dashboard

# Create necessary directories and set permissions
RUN mkdir -p /home/dashboard/.config/process-dashboard/logs \
    && chown -R dashboard:dashboard /home/dashboard/.config

# Switch to non-root user
USER dashboard
WORKDIR /home/dashboard

# Add entrypoint script
COPY --chown=dashboard:dashboard docker-entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

# Set default command
ENTRYPOINT ["docker-entrypoint.sh"]
CMD ["process-dashboard"]
