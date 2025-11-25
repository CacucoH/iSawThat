#!/bin/bash

RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m'

catch_ctrl_c() {
    echo "Bye!"
    exit 1
}

trap catch_ctrl_c SIGINT

echo ">> Starting installation..."

echo -n ">> Checking for Python3..."
python3 --version &> /dev/null
[[ $? -ne 0 ]] && { echo -e "${RED}Python3 is not installed. Please install it and try again.${NC}"; exit 1; }
echo -e "${GREEN}found${NC}"

# Install virtual environment and dependencies
echo -n ">> Installing dependencies..."
[[ `ls venv` ]] || python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip &> /dev/null
pip install -r requirements.txt &> /dev/null

[[ $? -ne 0 ]] && { echo -e "${RED}failed${NC}"; echo -e "${RED}Failed to install dependencies. Please check your internet connection and try again.${NC}"; exit 1; }

echo -e "${GREEN}done${NC}"

# Obtain session
echo ">> Obtaining session..."
python3 session-initializer.py

while [[ $? -ne 0 ]]; do
    echo
    echo -n ">> Retrying session initialization..."
    rm -rf ./misc/session/
    python3 session-initializer.py
done

echo -e ">> Installation completed ${GREEN}successfully!${NC}"