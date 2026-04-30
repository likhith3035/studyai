FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies required for FAISS and compiling Python packages
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    git \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Copy local dependencies file and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
# Ensure explicitly required libraries that might not be in requirements.txt directly are installed
RUN pip install --no-cache-dir pandas

# Copy all local project files to the container
COPY . .

# Expose Streamlit's default port
EXPOSE 8501

# Add healthcheck to ensure the container verifies Streamlit is running
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health || exit 1

# Start Streamlit application
ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
