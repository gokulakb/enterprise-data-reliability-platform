#!/bin/bash
# Install Python dependencies
pip install --upgrade pip
pip install cython==3.0.0
pip install -r requirements.txt

# Initialize database
python setup.py