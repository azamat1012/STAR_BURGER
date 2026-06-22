#!/bin/bash

set -e

echo "Pulling latest code from Git..."
git pull

echo "Building Docker image..."
docker compose -f docker-compose.prod.yaml build backend

echo "Copying static files to /var/www/frontend..."
sudo mkdir -p /var/www/frontend

docker create --name temp_static star_burger-backend:latest
sudo docker cp temp_static:/app/staticfiles/. /var/www/frontend/
sudo docker cp temp_static:/app/bundles/. /var/www/frontend/
docker rm temp_static

echo "Restarting containers..."
docker compose -f docker-compose.prod.yaml up -d

echo "Applying database migrations..."
docker compose -f docker-compose.prod.yaml exec backend python manage.py migrate --noinput

echo "Deployment complete!"