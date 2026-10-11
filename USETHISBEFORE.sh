#!/bin/bash

# Colori per un output più pulito
GREEN="\033[0;32m"
RED="\033[0;31m"
YELLOW="\033[1;33m"
NC="\033[0m" # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}      Linux For Everyone - Bootstrap    ${NC}"
echo -e "${GREEN}========================================${NC}"

# 1. Controllo se siamo su Arch Linux
if [ ! -f /etc/arch-release ]; then
    echo -e "${RED}[!] Error: This script is intended for Arch Linux only.${NC}"
    exit 1
fi

# 2. Controllo dei privilegi di root (sudo)
if [ "$EUID" -ne 0 ]; then
    if ! command -v sudo &> /dev/null; then
        echo -e "${RED}[!] Error: This script requires root privileges or 'sudo' installed.${NC}"
        exit 1
    }
    SUDO="sudo"
else
    SUDO=""
fi

echo -e "${YELLOW}[*] Updating package databases and installing Python & Git...${NC}"
$SUDO pacman -Sy --noconfirm --needed python python-pip git base-devel

# 3. Controllo ed installazione di dipendenze Python extra (se presenti)
if [ -f "requirements.txt" ]; then
    echo -e "${YELLOW}[*] Found requirements.txt. Installing Python libraries...${NC}"
    # Usa --break-system-packages per evitare blocchi sui sistemi Arch moderni con pip esterno
    if python3 -m pip install --break-system-packages -r requirements.txt; then
        echo -e "${GREEN}[*] Python libraries installed successfully via pip.${NC}"
    else
        echo -e "${YELLOW}[!] Warning: pip installation had issues, trying user-space or virtualenv...${NC}"
        python3 -m pip install --user -r requirements.txt
    fi
else
    echo -e "${YELLOW}[*] No requirements.txt found, skipping pip dependencies.${NC}"
fi

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}      Setup completed successfully!     ${NC}"
echo -e "${GREEN}  You can now run: python3 main.py      ${NC}"
echo -e "${GREEN}========================================${NC}"
