#!/bin/bash

# UTF-8 설정
export LANG=C.UTF-8

# 경고 메시지 색상 설정
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Checking Docker Compose configuration...${NC}"
if [ ! -f docker-compose.yml ]; then
    echo -e "${RED}docker-compose.yml not found in the current directory. Exiting...${NC}"
    exit 1
fi
echo -e "${GREEN}docker-compose.yml found.${NC}"

echo -e "${GREEN}Checking Docker daemon status...${NC}"
if ! sudo docker info > /dev/null 2>&1; then
    echo -e "${YELLOW}Docker daemon is not running. Starting Docker...${NC}"
    sudo systemctl start docker
    echo "Waiting for Docker to start..."
    sleep 10
    echo "Re-checking Docker daemon status..."
    if ! sudo docker info > /dev/null 2>&1; then
        echo -e "${RED}Failed to start Docker daemon. Exiting...${NC}"
        exit 1
    else
        echo -e "${GREEN}Docker daemon started successfully.${NC}"
    fi
else
    echo -e "${GREEN}Docker daemon is already running.${NC}"
fi
echo

echo -e "${GREEN}Stopping and removing Docker Compose services...${NC}"
if ! sudo docker-compose down -v; then
    echo -e "${RED}Failed to execute docker-compose down. Exiting...${NC}"
    exit 1
fi
echo

echo -e "${GREEN}Removing old Docker images...${NC}"
sudo docker images -q --filter "dangling=false" | xargs -r sudo docker rmi -f
echo

echo -e "${GREEN}Removing __pycache__ folders in ./fastapi...${NC}"
find ./fastapi/ -type d -name "__pycache__" -exec sudo rm -rf {} +
echo

echo -e "${GREEN}Removing old logs...${NC}"
find ./fastapi/src/logs -type f -name "*.log" -exec sudo rm -f {} +
echo

echo -e "${GREEN}Building and starting Docker Compose services...${NC}"
if ! sudo docker-compose up --build -d; then
    echo -e "${RED}Failed to execute docker-compose up. Exiting...${NC}"
    exit 1
fi

echo -e "${GREEN}Docker Compose services started successfully.${NC}"
exit 0
