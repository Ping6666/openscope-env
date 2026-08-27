#!/bin/bash

MODE=${1}

echo "Mode: $MODE"

if [ "$MODE" == "dev" ]; then
    cp .dockerignore.dev .dockerignore
    docker compose --env-file .env.dev build
    rm .dockerignore

elif [ "$MODE" == "prod" ]; then
    cp .dockerignore.prod .dockerignore
    docker compose --env-file .env.prod build
    rm .dockerignore

else
    echo "Mode error"

fi
