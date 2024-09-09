#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

# Function to check if a command exists
command_exists() {
    command -v "$1" &> /dev/null
}

# Update and install required dependencies
echo "Updating package lists..."

# Install Python3 if not installed
if ! command_exists python3; then
    echo "Installing Python3..."
    sudo apt-get install -y python3
else
    echo "✅Python3 is already installed."
fi

# Install pip3 if not installed
if ! command_exists pip3; then
    echo "Installing pip3..."
    sudo apt-get install -y python3-pip
else
    echo "✅pip3 is already installed."
fi

# Install browser utilities for opening URLs
if ! command_exists xdg-open && ! command_exists gnome-open; then
    echo "Installing xdg-utils for opening URLs..."
    sudo apt-get install -y xdg-utils
else
    echo "✅xdg-open or gnome-open is already installed."
fi

# Check if requirements.txt exists and install packages
if [ -f "requirements.txt" ]; then
    echo "Installing required Python packages from requirements.txt..."
    pip3 install -r requirements.txt
else
    echo "❌requirements.txt not found, skipping package installation."
fi

# Navigate to the Flask app directory
cd src/flask_app

# Run the Flask app in the background
echo "Starting Flask app..."
python3 app.py &

# Open the browser to the specified URL
echo "Opening browser at https://lessflix.vercel.app"
if command_exists xdg-open; then
    xdg-open https://lessflix.vercel.app
elif command_exists gnome-open; then
    gnome-open https://lessflix.vercel.app
else
    echo "Could not detect the web browser to open. Please manually navigate to https://lessflix.vercel.app"
fi
