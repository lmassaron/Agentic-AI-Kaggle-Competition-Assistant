#!/bin/bash
set -e

# Check if uv is installed
if ! command -v uv &> /dev/null
then
    echo "Error: uv is not installed."
    echo "Please install it first by running: pip install uv"
    exit 1
fi

# Check if .venv directory exists
if [ ! -d ".venv" ]; then
    echo "Virtual environment not found. Creating one with uv..."
    uv venv
else
    echo "Virtual environment already exists."
fi

echo "Installing dependencies from requirements.txt..."
uv pip install -r requirements.txt

echo "Setup complete. You can activate the virtual environment with:"
echo "source .venv/bin/activate"