#!/bin/bash

# Check if API_KEY is set via environment variable or passed as an argument
if [ -z "$API_KEY" ]; then
  echo "Error: API_KEY is not set. Please provide it either as an environment variable or as an argument. You can do this by entering 'export API_KEY='{API_KEY}' in your console."
  exit 1
fi

# Move into the api directory
cd api || { echo "api directory not found"; exit 1; }

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
  echo "Creating virtual environment..."
  python3 -m venv .venv
fi

# Activate the virtual environment
source .venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Run the test script
sleep 1
echo "Running the 'consume_api.py' script"
python consume_api.py
