# Use Python 3.12 as the base image
FROM python:3.12

# Set the working directory inside the container
WORKDIR /app

# Copy the project files
COPY . .

# Install dependencies
RUN pip install --upgrade pip && \
    pip install pylint mypy

# Run linting and type checking
CMD pylint . && mypy .
