if command -v docker-compose &> /dev/null; then
    COMPOSE_CMD="docker-compose"
elif docker compose version &> /dev/null; then
    COMPOSE_CMD="docker compose"
else
    echo "Erreur : ni 'docker-compose' ni 'docker compose' n'est disponible."
    exit 1
fi

$COMPOSE_CMD -f docker-compose.yml up -d
