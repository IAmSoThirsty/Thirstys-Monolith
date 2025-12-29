# Dockerfile for Thirsty's Monolith
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application
COPY . .

# Create data directory for audit logs
RUN mkdir -p data

# Set Python path
ENV PYTHONPATH=/app

# Default command - run the schematic guardian
CMD ["python", "-c", "from src.app.agents.codex_deus_maximus import create_codex; agent = create_codex(); print(agent.run_schematic_enforcement())"]
