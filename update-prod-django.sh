#!/bin/bash
echo "[START]"
echo "---stopping django and nginx---"
docker-compose stop django nginx
echo "---removing containers---"
docker-compose rm -f
echo "---removing stale volumes---"
docker volume prune -f
echo "---rebuilding django---"
docker-compose build django
echo "---restarting django and nginx---"
docker-compose -f docker-compose.yml up -d --no-deps django nginx
echo "[END]"
