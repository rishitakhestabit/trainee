#!/usr/bin/env bash
set -e

echo "Deploying production stack..."
sudo docker compose -f docker-compose.prod.yml --env-file .env down
sudo docker compose -f docker-compose.prod.yml --env-file .env up -d --build

echo "Containers:"
sudo docker compose -f docker-compose.prod.yml ps

echo "Open in browser: https://${DOMAIN}:${HTTPS_PORT}"
