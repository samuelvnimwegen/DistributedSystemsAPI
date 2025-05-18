# Use Python 3.12 as the base image
FROM python:3.12

# Declare build argument
ARG API_KEY

# Set environment variable from the build argument
ENV API_KEY=${API_KEY}

# Set the working directory inside the container
WORKDIR /app

# Install system dependencies (combine updates to avoid redundant layers)
RUN apt-get update && \
    apt-get install -y postgresql postgresql-contrib postgresql-client libpq-dev locales gnupg ca-certificates && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copy only requirements first for better pip caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy environment file early if needed in build
COPY .env.docker .env

# Copy the rest of the project files
COPY . .

# Expose the port that the application will run on
EXPOSE 5003

# Set default command to run the app
CMD ["sh", "-c", "alembic upgrade head && gunicorn src.wsgi:app -b 0.0.0.0:5003 --timeout 3600"]
