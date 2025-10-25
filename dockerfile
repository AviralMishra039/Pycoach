# Dockerfile

# Use a lean Python base image
FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /app

COPY requirements.txt .

# Install dependencies
# Using --no-cache-dir saves space
# We must install the full requirements for RAG, FastAPI, and Streamlit
RUN pip install --no-cache-dir -r requirements.txt

RUN apt-get update && apt-get install -y netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*


COPY . .


RUN mkdir -p /app/course_materials
RUN mkdir -p /app/chroma_db

# Expose the ports used by FastAPI (8000) and Streamlit (8501)
EXPOSE 8000
EXPOSE 8501


# We will let docker-compose handle the commands, so use a simpler entry point:
CMD ["python3", "-m", "uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]