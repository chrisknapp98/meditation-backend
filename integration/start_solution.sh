#!/bin/bash

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

# fetch incoming changes
git pull

# create default .env file from .env.template
cp $SCRIPT_DIR/.env.template $SCRIPT_DIR/.env

# rebuild REST server image and restart containers
docker compose -f $SCRIPT_DIR/docker-compose.yml up -d --build --wait