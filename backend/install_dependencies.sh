#!/bin/bash
# Backend dependency installation script (Linux/Mac)
# Fix setuptools issue and install dependencies

echo "Installing backend dependencies..."

# Upgrade pip, setuptools, and wheel first
python3 -m pip install --upgrade pip setuptools wheel

# Install dependencies
pip install -r requirements.txt

echo "Installation complete!"

