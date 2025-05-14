# This runs the check script for the project.

cd api || { echo "api directory not found"; exit 1; }

pylint src/ tests/

if [ $? -ne 0 ]; then
  echo "❌ Linting failed."
  exit 1
fi

echo "✅ Linting passed."
echo "Running type checker..."

mypy src/

if [ $? -ne 0 ]; then
  echo "❌ Type checking failed."
  exit 1
fi

echo "✅ Type checking passed."

echo "Running tests..."
pytest tests/

if [ $? -ne 0 ]; then
  echo "❌ Tests failed."
  exit 1
fi

echo "✅ All tests passed."