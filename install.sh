#!/bin/bash

RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m'

catch_ctrl_c() {
    echo "Bye!"
    exit 1
}

echo ">> Updating repo..."
git pull &> /dev/null
[[ $? -ne 0 ]] && { echo -e "${RED}Failed to update repo. Proceed anyway? (y/n)${NC}"; read -r answer; if [[ $answer != "y" ]]; then exit 1; fi; }
echo -e "${GREEN}done${NC}"

trap catch_ctrl_c SIGINT

echo ">> Starting installation..."

echo -n ">> Checking for Python3..."
python3 --version &> /dev/null
[[ $? -ne 0 ]] && { echo -e "${RED}Python3 is not installed. Please install it and try again.${NC}"; exit 1; }
echo -e "${GREEN}found${NC}"

# Install virtual environment and dependencies
echo -n ">> Installing dependencies..."
[[ `ls venv &> /dev/null` ]] || python3 -m venv venv &> /dev/null
source venv/bin/activate &> /dev/null
pip install --upgrade pip &> /dev/null
pip install -r requirements.txt &> /dev/null

[[ $? -ne 0 ]] && { echo -e "${RED}failed${NC}"; echo -e "${RED}Failed to install dependencies. Please check your internet connection and try again.${NC}"; exit 1; }

echo -e "${GREEN}done${NC}"

# Obtain session
echo ">> Obtaining session..."
python3 session-initializer.py

count=0
while [[ $? -ne 0 ]]; do
    echo
    echo -n ">> Retrying session initialization..."
    rm -rf ./misc/session/
    python3 session-initializer.py
    count=$((count + 1))
    if [[ $count -ge 5 ]]; then
        echo -e "${RED}Failed to initialize session after 5 attempts. Please check your configuration and try again.${NC}"
        exit 1
    fi
done

echo -e ">> Installation completed ${GREEN}successfully!${NC}"