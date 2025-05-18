#!/bin/bash

# List of directories to check
PROJECT_DIRS=("logging_api" "movie_api" "rating_api", "user_api")

for DIR in "${PROJECT_DIRS[@]}"; do
  echo "🔍 Entering $DIR..."

  if [ ! -d "$DIR" ]; then
    echo "❌ Directory $DIR not found"
    exit 1
  fi

  cd "$DIR" || exit 1

  # Install dependencies
  echo "Installing dependencies in $DIR..."
  if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
  else
    echo "❌ requirements.txt not found in $DIR"
    exit 1
  fi

  echo "Running pylint..."
  pylint src/ tests/
  if [ $? -ne 0 ]; then
    echo "❌ Linting failed in $DIR."
    exit 1
  fi

  echo "✅ Linting passed in $DIR."

  echo "Running mypy..."
  mypy src/
  if [ $? -ne 0 ]; then
    echo "❌ Type checking failed in $DIR."
    exit 1
  fi

  echo "✅ Type checking passed in $DIR."

  echo "Running tests..."
  pytest tests/
  if [ $? -ne 0 ]; then
    echo "❌ Tests failed in $DIR."
    exit 1
  fi

  echo "✅ All tests passed in $DIR."
  echo "🔙 Returning to root..."
  cd - >/dev/null
done

echo "🎉 All checks passed for all directories!"
