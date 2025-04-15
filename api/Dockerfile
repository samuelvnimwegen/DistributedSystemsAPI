# Use Python 3.12 as the base image
FROM python:3.12

# Declare build argument
ARG API_KEY

# Set environment variable from the build argument
ENV API_KEY=${API_KEY}

# Set the working directory inside the container
WORKDIR /app

RUN apt update
RUN apt-get update
RUN apt-get install -y postgresql postgresql-contrib postgresql-client libpq-dev locales gnupg ca-certificates
RUN apt-get clean

COPY .env.docker .env

# Copy the project files
COPY . .

# Install dependencies
RUN pip install -r requirements.txt

# Expose the port that the application will run on
EXPOSE 5000

# Run the application
CMD ["sh", "-c", "alembic upgrade head && gunicorn src.wsgi:app -b 0.0.0.0:5000 --timeout 3600"]
