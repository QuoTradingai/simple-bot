#!/bin/bash
set -e

echo "Installing git..."
apt-get update && apt-get install -y git

echo "Cloning repository..."
git clone https://github.com/Quotraders/simple-bot.git /tmp/repo

echo "Copying files..."
cp -r /tmp/repo/cloud-api/* /app/

echo "Installing dependencies..."
pip install --no-cache-dir -r /app/requirements-azure.txt

echo "Starting server..."
cd /app
gunicorn main:app --workers 2 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
