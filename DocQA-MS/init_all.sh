#!/bin/bash

set -e

echo "Initializing DocQA-MS infrastructure..."

cd "$(dirname "$0")"

echo "Starting database services..."
docker-compose up -d postgres rabbitmq redis

echo "Waiting for PostgreSQL to be ready..."
sleep 10

echo "Running database migrations..."
docker-compose up db-migrations

echo "Initializing FAISS index..."
docker-compose --profile init run --rm faiss-init

echo "Starting all services..."
docker-compose up -d

echo "Initialization completed successfully!"
echo "Services are starting. Check status with: docker-compose ps"

