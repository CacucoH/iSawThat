#!/bin/bash

YELLOW='\033[0;33m'
RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m'


echo -e "${YELLOW}                           === WARNING ===${NC}"
echo -e "${YELLOW}This script will REINSTALL the application, removing all existing data!${NC}"
echo -n "Do you want to proceed? (y/n): "
read -r response
if [[ $response != "y" ]]; then
    echo "Reinstallation cancelled."
    exit 0
fi

echo ">> Proceeding with reinstallation..."

echo -n "  >> Removing existing virtual environment..."
rm -rf venv/
echo -e "${GREEN}done${NC}"
    
echo -n "  >> Removing existing session data..."
rm -f ./misc/session/*
echo -e "${GREEN}done${NC}"

echo -n "  >> Removing DB and user data..."
sudo rm -rf ./misc/data/*
echo -e "${GREEN}done${NC}"

echo -n "  >> Flush logs..."
rm -f ./misc/logs/*
echo -e "${GREEN}done${NC}"

echo ">> Starting fresh installation..."
bash install.sh