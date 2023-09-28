#!/bin/bash
echo "[START]"
echo "---stopping django and caddy---"
docker-compose stop django caddy
echo "---removing containers---"
docker-compose rm -f
echo "---removing stale volumes---"
docker volume prune -f
echo "---rebuilding django---"
docker-compose build django
echo "---restarting django and caddy---"
docker compose -f docker-compose.yml up -d --no-deps django caddy
echo "[END]"
