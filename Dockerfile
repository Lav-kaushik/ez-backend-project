```
# Use an official Python runtime as a parent image
FROM python:3.9-slim-buster

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container at /app
COPY requirements.txt /app/

# Install any needed packages specified in requirements.txt
# This will include fastapi, uvicorn, sqlalchemy, psycopg2-binary, boto3, etc.
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your application code into the container at /app
COPY . /app/

# Expose the port that Uvicorn will listen on
EXPOSE 8000

# Command to run the FastAPI application using Uvicorn
# Assumes your main FastAPI app is in 'main.py' and the FastAPI instance is named 'app'
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

# For development with auto-reloading (if you want to build a dev-specific image):
# CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
```
