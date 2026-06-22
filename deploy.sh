#!/bin/bash

set -e

echo "Pulling latest code from Git..."
git pull

echo "Building and pulling Docker images..."
docker compose -f docker-compose.yml -f docker-compose.production.yml build

echo "Copying static files to /var/www/frontend..."
sudo mkdir -p /var/www/frontend

docker create --name temp_static star_burger-backend:latest
sudo docker cp temp_static:/app/frontend/. /var/www/frontend/
docker rm temp_static

echo "Restarting containers..."
docker compose -f docker-compose.yml -f docker-compose.production.yml up -d

echo "Applying database migrations..."
docker compose -f docker-compose.yml -f docker-compose.production.yml exec backend python manage.py migrate

echo "Deployment complete!"