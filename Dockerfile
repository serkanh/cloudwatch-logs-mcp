# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
# If you don't have a requirements.txt, you can install dependencies directly
RUN pip install --no-cache-dir -e .

# Run main.py when the container launches
CMD ["python3", "main.py"]