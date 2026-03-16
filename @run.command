#!/bin/bash
# Get the directory where the script is located
cd "$(dirname "$0")"

# Run the python script using the 'tss' conda environment
# 'conda run' is more robust for scripts than 'conda activate'
conda run -n tss --no-capture-output python twscreener.py

# Keep the window open if there's an error
echo "Process finished. Press any key to close..."
read -n 1
