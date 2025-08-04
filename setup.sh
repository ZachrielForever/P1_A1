#!/usr/bin/env bash

# This script sets up a single, unified environment for the AI Toolkit application.
# It installs all dependencies from all plugins into one virtual environment.

# Exit immediately if a command exits with a non-zero status.
set -e

# --- Color Codes for Output ---
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Starting AI Toolkit Unified Setup...${NC}"

# --- Step 1: Check for Prerequisites ---
echo "Checking for Python 3 and venv module..."
if ! command -v python3 &> /dev/null; then
    echo -e "${YELLOW}ERROR: python3 could not be found. Please install Python 3.${NC}"
    exit 1
fi
if ! python3 -m venv -h &> /dev/null; then
    echo -e "${YELLOW}ERROR: The 'venv' module is not available. Please install python3-venv or equivalent.${NC}"
    exit 1
fi
echo "Prerequisites found."

# --- Step 2: Set up the Main Application Environment ---
VENV_DIR="./venv_main"

if [ ! -d "$VENV_DIR" ]; then
    echo "Creating main virtual environment at $VENV_DIR..."
    python3 -m venv "$VENV_DIR"
else
    echo "Main virtual environment already exists."
fi

# Activate the main environment to install packages into it
source "$VENV_DIR/bin/activate"

echo "Upgrading pip..."
pip install --upgrade pip

echo "Installing core TUI dependency..."
pip install textual

echo "Installing all plugin dependencies into the main environment..."

# Combine all requirements.txt files into one, removing duplicates
cat plugins/*/requirements.txt | sort -u > all_requirements.txt

# Special case for llama-cpp-python to ensure GPU compilation
if grep -q "llama-cpp-python" "all_requirements.txt"; then
    echo "Found llama-cpp-python, installing with GPU support..."

    # --- THIS IS THE FIX ---
    # We now also set CMAKE_INSTALL_RPATH to bake the library path
    # directly into the compiled file. This is the most robust solution.
    CMAKE_ARGS="-DGGML_CUDA=on -DCMAKE_INSTALL_RPATH=/usr/local/cuda/lib64" FORCE_CMAKE=1 pip install --upgrade --force-reinstall llama-cpp-python --no-cache-dir
fi

# Install all other dependencies from our combined list
pip install -r <(grep -v "llama-cpp-python" "all_requirements.txt")

# Clean up the temporary combined file
rm all_requirements.txt

# Deactivate after we're done
deactivate

echo -e "\n${GREEN}Setup complete!${NC}"
echo -e "To run the application, first activate the main environment with:"
echo -e "${YELLOW}source $VENV_DIR/bin/activate${NC}"
echo -e "Then run the main script with:"
echo -e "${YELLOW}python main.py${NC}"
