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

# 2. System Dependencies (libsndfile)
echo -e "\n${YELLOW}Checking system dependencies...${NC}"

if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    if ! ldconfig -p | grep -q libsndfile; then
        echo -e "${YELLOW}libsndfile not found. Attempting to identify package manager...${NC}"
        if command -v apt-get &> /dev/null; then
            echo "Detected apt. Please run: sudo apt-get install libsndfile1-dev"
        elif command -v dnf &> /dev/null; then
             echo "Detected dnf. Please run: sudo dnf install libsndfile"
        elif command -v pacman &> /dev/null; then
             echo "Detected pacman. Please run: sudo pacman -S libsndfile"
        else
            echo -e "${RED}Could not identify package manager. Please install 'libsndfile' manually.${NC}"
        fi
        # We don't exit here because checking ldconfig isn't perfect and user might have it elsewhere
        read -p "Press Enter to continue if you have installed libsndfile, or Ctrl+C to abort."
    else
         echo -e "${GREEN}libsndfile appears to be installed.${NC}"
    fi
elif [[ "$OSTYPE" == "darwin"* ]]; then
    if ! brew list libsndfile &> /dev/null; then
        echo "Detected macOS. Please run: brew install libsndfile"
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

# Install project in editable mode
pip install -e .

echo -e "\n${GREEN}Setup complete!${NC}"
echo -e "To start the Web UI, run:"
echo -e "  ${YELLOW}source .venv/bin/activate${NC}"
echo -e "  ${YELLOW}streamlit run src/affirmbeat/web_ui.py${NC}"
echo -e "\nTo use the CLI:"
echo -e "  ${YELLOW}affirmbeat --help${NC}"
