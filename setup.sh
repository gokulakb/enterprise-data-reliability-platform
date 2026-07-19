#!/bin/bash
# Setup script for Render deployment

echo "======================================"
echo "Setting up Enterprise Data Reliability Platform"
echo "Using Python version: $(python --version)"
echo "======================================"

# Upgrade pip
pip install --upgrade pip

# Install Cython first
echo "Installing Cython..."
pip install cython==0.29.36

# Install all dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Initialize and seed database
echo "Setting up database..."
python setup.py

echo "======================================"
echo "Setup complete!"
echo "======================================"
