# Use a lean Python base image
FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /app

# Copy and install ONLY the necessary system dependencies FIRST
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        netcat-openbsd \
        libmagic-dev \
        libgl1-mesa-glx \
        tesseract-ocr \
        poppler-utils && \
    rm -rf /var/lib/apt/lists/*
    
# Copy the Python requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Create persistent directories (though volumes usually handle this)
RUN mkdir -p /app/course_materials
RUN mkdir -p /app/chroma_db

# Expose the ports used by FastAPI (8000) and Streamlit (8501)
EXPOSE 8000
EXPOSE 8501

# Default command to run the FastAPI backend
CMD ["python3", "-m", "uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]