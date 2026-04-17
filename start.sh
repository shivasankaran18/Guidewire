#!/bin/bash

# GigPulse Sentinel - Complete Startup Script
# This script starts all services in the correct order

set -e  # Exit on any error

echo "======================================================"
echo "🛡️  GigPulse Sentinel - Startup Script"
echo "======================================================"
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

pause_if_interactive() {
    # Match start.bat pause behavior when the script runs in an interactive shell.
    if [ -t 0 ]; then
        read -r -p "Press Enter to continue..." _
    fi
}

# Check if Docker is running
if ! docker info >/dev/null 2>&1; then
    echo -e "${RED}❌ Error: Docker is not running!${NC}"
    echo "Please start Docker Desktop and try again."
    pause_if_interactive
    exit 1
fi
echo -e "${GREEN}[OK] Docker is running${NC}"
echo ""

# Check if .env exists
if [ ! -f ".env" ]; then
    echo -e "${RED}[ERROR] .env file not found!${NC}"
    echo "Creating .env file from template..."
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo -e "${GREEN}[OK] .env file created from .env.example${NC}"
    else
        cat > .env << 'EOF'
# GigPulse Sentinel Environment Variables
SECRET_KEY=dev-secret-key-change-in-production
JWT_SECRET=dev-jwt-secret-change-in-production
JWT_ALGORITHM=HS256
JWT_EXPIRY_HOURS=24
DATABASE_URL=sqlite+aiosqlite:///./gigpulsesentinel.db
USE_MOCK_APIS=true
DEBUG=true
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
VITE_API_BASE_URL=http://localhost:8000

# Email (SMTP)
# Gmail recommended settings (use an App Password for SMTP_PASSWORD)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_STARTTLS=true
SMTP_USER=
SMTP_PASSWORD=
# For Gmail, keep FROM equal to SMTP_USER (or a configured alias)
SMTP_FROM=
EOF
        echo -e "${GREEN}[OK] .env file created${NC}"
    fi
fi
echo ""

echo -e "${BLUE}Step 1/5: Stopping any existing containers...${NC}"
docker-compose down 2>/dev/null || true
echo ""

echo -e "${BLUE}Step 2/5: Ensuring Docker volume exists...${NC}"
if ! docker volume inspect gigpulsesentinel_backend_data >/dev/null 2>&1; then
    docker volume create gigpulsesentinel_backend_data >/dev/null
    echo -e "${GREEN}[OK] Created volume: gigpulsesentinel_backend_data${NC}"
else
    echo -e "${GREEN}[OK] Volume exists: gigpulsesentinel_backend_data${NC}"
fi
echo ""

echo -e "${BLUE}Step 3/5: Building Docker images...${NC}"
echo "Building backend and frontend..."
docker-compose build backend frontend
if [ $? -ne 0 ]; then
    echo -e "${RED}[ERROR] Failed to build Docker images!${NC}"
    pause_if_interactive
    exit 1
fi
echo -e "${GREEN}[OK] Docker images built successfully${NC}"
echo ""

echo -e "${BLUE}Step 4/5: Starting backend...${NC}"
docker-compose up -d backend
if [ $? -ne 0 ]; then
    echo -e "${RED}[ERROR] Failed to start backend service.${NC}"
    pause_if_interactive
    exit 1
fi
echo -e "${YELLOW}⏳ Waiting for backend to be ready (10 seconds)...${NC}"
sleep 10
echo ""

echo -e "${BLUE}Step 5/5: Starting frontend...${NC}"
docker-compose up -d frontend
if [ $? -ne 0 ]; then
    echo -e "${RED}[ERROR] Failed to start frontend service.${NC}"
    pause_if_interactive
    exit 1
fi
echo ""

# Verify services are running
echo "Verifying services..."
docker-compose ps
echo ""

echo -e "${GREEN}=====================================================${NC}"
echo -e "${GREEN}✅ All services started successfully!${NC}"
echo -e "${GREEN}=====================================================${NC}"
echo ""
echo "📋 Service URLs:"
echo "   Frontend:     http://localhost:5173"
echo "   Backend API:  http://localhost:8000"
echo "   API Docs:     http://localhost:8000/docs"
echo "   Health Check: http://localhost:8000/health"
echo ""
echo "📊 To view logs:"
echo "   All services:  docker-compose logs -f"
echo "   Backend only:  docker-compose logs -f backend"
echo "   Frontend only: docker-compose logs -f frontend"
echo ""
echo "🛑 To stop all services:"
echo "   docker-compose down"
echo ""
echo "🔄 To restart:"
echo "   docker-compose restart"
echo ""

pause_if_interactive
