#!/bin/bash
set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}Starting AffirmBeat Studio setup...${NC}"

# 1. Check Python version
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: python3 is not installed.${NC}"
    exit 1
fi

PY_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
REQUIRED_VERSION="3.10"

if (( $(echo "$PY_VERSION < $REQUIRED_VERSION" | bc -l) )); then
    echo -e "${RED}Error: Python 3.10 or higher is required. Found $PY_VERSION.${NC}"
    exit 1
fi

echo -e "Found Python $PY_VERSION"

# 2. System Dependencies (libsndfile + espeak-ng)
echo -e "\n${YELLOW}Checking system dependencies...${NC}"

install_pkg() {
    PKG=$1
    if command -v apt-get &> /dev/null; then
        echo "Detected apt. Running: sudo apt-get install -y $PKG"
        sudo apt-get install -y "$PKG"
    elif command -v dnf &> /dev/null; then
         echo "Detected dnf. Running: sudo dnf install -y $PKG"
         sudo dnf install -y "$PKG"
    elif command -v pacman &> /dev/null; then
         echo "Detected pacman. Running: sudo pacman -S --noconfirm $PKG"
         sudo pacman -S --noconfirm "$PKG"
    else
        echo -e "${RED}Could not identify package manager. Please install '$PKG' manually.${NC}"
    fi
}

# Check libsndfile
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    if ! ldconfig -p | grep -q libsndfile; then
        echo -e "${YELLOW}libsndfile not found.${NC}"
        install_pkg "libsndfile1-dev" || install_pkg "libsndfile"
    else
         echo -e "${GREEN}libsndfile appears to be installed.${NC}"
    fi
    
    # Check espeak-ng
    if ! command -v espeak-ng &> /dev/null && ! command -v espeak &> /dev/null; then
        echo -e "${YELLOW}espeak-ng not found (required for TTS).${NC}"
        install_pkg "espeak-ng"
    else
        echo -e "${GREEN}espeak found.${NC}"
    fi

elif [[ "$OSTYPE" == "darwin"* ]]; then
    if ! brew list libsndfile &> /dev/null; then
        echo "Detected macOS. Installing libsndfile..."
        brew install libsndfile
    fi
    if ! brew list espeak &> /dev/null; then
        echo "Detected macOS. Installing espeak..."
        brew install espeak
    fi
fi

# 3. Virtual Environment
echo -e "\n${YELLOW}Setting up virtual environment...${NC}"
VENV_DIR=".venv"

if [ ! -d "$VENV_DIR" ]; then
    python3 -m venv "$VENV_DIR"
    echo "Created virtual environment in $VENV_DIR"
else
    echo "Virtual environment already exists."
fi

# 4. Install Dependencies
echo -e "\n${YELLOW}Installing Python dependencies...${NC}"
source "$VENV_DIR/bin/activate"

# Upgrade pip
pip install --upgrade pip

# Install core project
pip install -e .

# 5. Optional AI Dependencies
echo -e "\n${YELLOW}AI Music Generation (Optional)${NC}"
echo "Stable Audio Open requires installing heavy dependencies (Torch, stable-audio-tools)."
read -p "Do you want to install these AI components now? [y/N] " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}Installing AI dependencies (this may take a while)...${NC}"
    pip install -e ".[ai]"
    echo -e "${GREEN}AI components installed.${NC}"
else
    echo "Skipping AI components."
fi

echo -e "\n${GREEN}Setup complete!${NC}"
echo -e "To start the Web UI, run:"
echo -e "  ${YELLOW}source .venv/bin/activate${NC}"
echo -e "  ${YELLOW}streamlit run src/affirmbeat/web_ui.py${NC}"
