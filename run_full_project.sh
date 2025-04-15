#!/bin/bash

# Check if API_KEY is set via environment variable or passed as an argument
if [ -z "$API_KEY" ]; then
  echo "Error: API_KEY is not set. Please provide it either as an environment variable or as an argument. You can do this by entering 'export API_KEY='{API_KEY}' in your console."
  exit 1
fi

# Stop and remove existing containers
docker-compose down

# Build the containers and pass the API_KEY build argument
docker-compose build --build-arg API_KEY=$API_KEY

# Start the containers in detached mode
docker-compose up -d