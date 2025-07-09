FROM python:3.10-slim

WORKDIR /app

# Install system-level dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    g++ \
    python3-dev \
    libffi-dev \
    libssl-dev \
    libgeos-dev \
    libproj-dev \
    proj-data \
    proj-bin \
    libspatialindex-dev \
    libgdal-dev \
    libpq-dev \
    curl \
    git \
    cmake \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python packages
COPY requirements.txt .

# Upgrade pip and install build-time Python dependencies first
RUN pip install --upgrade pip setuptools wheel && \
    pip install jinja2 markupsafe cython && \
    pip install --no-cache-dir -r requirements.txt

# Copy the app source code
COPY . .

EXPOSE 8501

# Optional: Health check (comment out if not needed)
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health || exit 1

# Launch the Streamlit app
ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]

