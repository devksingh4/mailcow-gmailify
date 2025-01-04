# Use an Alpine base image
FROM python:3.12-alpine

# Install build tools, libmilter, and runtime dependencies
RUN apk add --no-cache \
    gcc \
    libc-dev \
    libffi-dev \
    make \
    musl-dev \
    libmilter-dev \
    python3-dev

# Set working directory
WORKDIR /app

# Copy the milter script to the container
COPY spam_milter.py /app/

# Install Python dependencies
RUN pip install pymilter

# Expose the port the milter listens on
EXPOSE 12345

# Command to run the milter
CMD ["python", "/app/spam_milter.py"]
