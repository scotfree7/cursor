#!/usr/bin/env python3
"""
Alpha Vantage API Key Helper

This script helps users get their own Alpha Vantage API key and update the calculator.py file.
"""

import os
import sys
import webbrowser
import re

def main():
    print("\n=== Alpha Vantage API Key Helper ===\n")
    print("This script will help you get your own Alpha Vantage API key and update the calculator.py file.")
    print("\nSteps:")
    print("1. Open the Alpha Vantage API key registration page")
    print("2. Fill out the form and get your API key")
    print("3. Enter your API key in this script to update the calculator.py file")
    
    # Ask if the user wants to open the registration page
    open_page = input("\nWould you like to open the Alpha Vantage API key registration page? (y/n): ")
    if open_page.lower() == 'y':
        webbrowser.open("https://www.alphavantage.co/support/#api-key")
        print("\nRegistration page opened in your browser.")
    
    # Ask for the API key
    api_key = input("\nEnter your Alpha Vantage API key (or press Enter to skip): ")
    if not api_key:
        print("\nNo API key entered. Exiting without making changes.")
        return
    
    # Validate the API key format (basic validation)
    if not re.match(r'^[A-Za-z0-9]+$', api_key):
        print("\nInvalid API key format. API keys typically contain only letters and numbers.")
        return
    
    # Check if calculator.py exists
    if not os.path.exists("calculator.py"):
        print("\nError: calculator.py not found in the current directory.")
        return
    
    # Read the calculator.py file
    try:
        with open("calculator.py", "r") as file:
            content = file.read()
        
        # Replace the API key
        updated_content = re.sub(
            r'api_key = "demo"  # Replace with your API key for more requests',
            f'api_key = "{api_key}"  # Your Alpha Vantage API key',
            content
        )
        
        # Write the updated content back to the file
        with open("calculator.py", "w") as file:
            file.write(updated_content)
        
        print("\nAPI key successfully updated in calculator.py!")
        print("You can now run the calculator with your own API key.")
        
    except Exception as e:
        print(f"\nError updating the API key: {str(e)}")

if __name__ == "__main__":
    main() 