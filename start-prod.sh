if command -v docker-compose &> /dev/null; then
    COMPOSE_CMD="docker-compose"
elif docker compose version &> /dev/null; then
    COMPOSE_CMD="docker compose"
else
    echo "Error :  'docker-compose' or 'docker compose' are not available."
    exit 1
fi

$COMPOSE_CMD -f docker-compose.yml up -d
