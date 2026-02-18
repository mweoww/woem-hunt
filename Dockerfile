FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest
COPY . .

# Create data directory
RUN mkdir -p /app/data

# Run with unbuffered output
CMD ["python", "-u", "main.py"]
