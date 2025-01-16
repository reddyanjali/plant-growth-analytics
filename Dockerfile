# Use the official Python image
FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /app

# Install system dependencies for psycopg2, curl, and dos2unix
RUN apt-get update && \
    apt-get install -y build-essential libpq-dev curl dos2unix && \
    rm -rf /var/lib/apt/lists/*

# Download wait-for-it script and make it executable
RUN curl -L https://github.com/vishnubob/wait-for-it/releases/download/v2.3.2/wait-for-it.sh -o /usr/local/bin/wait-for-it && \
    chmod +x /usr/local/bin/wait-for-it && \
    dos2unix /usr/local/bin/wait-for-it

# Copy the requirements file into the container
COPY requirements.txt requirements.txt

# Install dependencies in the container
RUN pip install --no-cache-dir -r requirements.txt

# Copy the FastAPI app code into the container
COPY . .

# Expose the FastAPI port
EXPOSE 8000

# Command to run FastAPI using uvicorn and wait for PostgreSQL to be ready
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]