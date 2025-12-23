$ErrorActionPreference = "Stop"

Write-Host "Initializing DocQA-MS infrastructure..." -ForegroundColor Green

$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptPath

Write-Host "Starting database services..." -ForegroundColor Yellow
docker-compose up -d postgres rabbitmq redis

Write-Host "Waiting for PostgreSQL to be ready..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

Write-Host "Running database migrations..." -ForegroundColor Yellow
docker-compose up db-migrations

Write-Host "Initializing FAISS index..." -ForegroundColor Yellow
docker-compose --profile init run --rm faiss-init

Write-Host "Starting all services..." -ForegroundColor Yellow
docker-compose up -d

Write-Host "Initialization completed successfully!" -ForegroundColor Green
Write-Host "Services are starting. Check status with: docker-compose ps" -ForegroundColor Cyan

