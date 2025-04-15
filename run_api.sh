#!/bin/bash

# Check if API_KEY is set via environment variable or passed as an argument
if [ -z "$API_KEY" ]; then
  echo "Error: API_KEY is not set. Please provide it either as an environment variable or as an argument. You can do this by entering 'EXPORT API_KEY='{API_KEY}' in your console."
  exit 1
fi

# Check if PostgreSQL is installed
if ! command -v psql &> /dev/null
then
  echo "❌ PostgreSQL is not installed. Please install PostgreSQL before proceeding."
  exit 1
fi

# PostgreSQL connection info
DB_NAME="ds_db"
DB_USER="ds_user"
DB_PASSWORD="password"
DB_HOST="localhost"
DB_PORT="5432"

# Export password so psql can login non-interactively
export PGPASSWORD=$DB_PASSWORD

echo "Checking if database '$DB_NAME' exists..."

# Try to create the database if it doesn't exist
psql -U "$DB_USER" -h "$DB_HOST" -p "$DB_PORT" -d "postgres" -tc "SELECT 1 FROM pg_database WHERE datname = '$DB_NAME'" | grep -q 1 || \
psql -U "$DB_USER" -h "$DB_HOST" -p "$DB_PORT" -d "postgres" -c "CREATE DATABASE \"$DB_NAME\""

if [ $? -ne 0 ]; then
  echo "❌ Failed to connect to PostgreSQL or create database."
  exit 1
fi

echo "✅ Database checked/created."

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

# Upgrade alembic
alembic upgrade head

# Run the Python app with API_KEY passed as argument
echo "Running app with API_KEY=$API_KEY..."
python app.py --key "$API_KEY"