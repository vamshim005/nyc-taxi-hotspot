FROM python:3.11-slim

# Install Java for PySpark
RUN apt-get update && \
    apt-get install -y openjdk-11-jdk && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Set Java home
ENV JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64

# Set working directory
WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY src/ src/
COPY data/ data/

# Create results directory
RUN mkdir -p results

# Set environment variables
ENV PYTHONPATH=/app

# Default command
ENTRYPOINT ["python", "src/main.py"]
CMD ["--scale", "dev"] 