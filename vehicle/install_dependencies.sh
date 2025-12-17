#!/bin/bash
# Vehicle dependency installation script (Raspberry Pi)
# Fix setuptools issue and install dependencies
# Uses virtual environment to avoid externally-managed-environment error

echo "Installing vehicle dependencies..."

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"
VENV_DIR="$PROJECT_ROOT/venv"

# Check if virtual environment exists
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating virtual environment..."
    python3 -m venv "$VENV_DIR"
    
    # Check if venv was created successfully
    if [ ! -d "$VENV_DIR" ]; then
        echo "Error: Failed to create virtual environment"
        echo "Please install python3-venv: sudo apt install python3-venv python3-full"
        exit 1
    fi
fi

# Activate virtual environment
echo "Activating virtual environment..."
source "$VENV_DIR/bin/activate"

# Upgrade pip, setuptools, and wheel first
echo "Upgrading pip, setuptools, and wheel..."
python3 -m pip install --upgrade pip setuptools wheel

# Install dependencies
echo "Installing dependencies from requirements.txt..."
pip install -r "$SCRIPT_DIR/../requirements.txt"

echo ""
echo "Installation complete!"
echo ""
echo "To use the virtual environment in the future, run:"
echo "  source $VENV_DIR/bin/activate"
echo ""
echo "Then you can run:"
echo "  cd $SCRIPT_DIR"
echo "  python3 main.py [speed_limit]"

