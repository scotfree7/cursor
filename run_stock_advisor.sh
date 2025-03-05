#!/bin/bash

# Activate the virtual environment
source calculator_env/bin/activate

# Set your Quiver API key here
# You should replace the placeholder with your actual API key from https://api.quiverquant.com/
export QUIVER_API_KEY="your_api_key_here"

# Run the stock advisor
python stock_advisor.py 