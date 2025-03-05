import os
import sys
from dotenv import load_dotenv

# Try to load environment variables from .env file
load_dotenv()

print("Testing Quiver Quantitative API")
print("-------------------------------")

try:
    import quiverquant
    print("✓ Successfully imported quiverquant package")
except ImportError as e:
    print(f"✗ Failed to import quiverquant: {e}")
    sys.exit(1)

# Check for API key
api_key = os.getenv('QUIVER_API_KEY')
if api_key:
    print("✓ QUIVER_API_KEY found in environment variables")
else:
    print("! No QUIVER_API_KEY found in environment variables")
    print("! Will attempt to connect with a placeholder key (will likely fail)")
    api_key = "placeholder_key"

# Test API connection
try:
    quiver = quiverquant.quiver(api_key)
    print("✓ Successfully created Quiver instance")
    
    # Try to fetch some data
    print("\nAttempting to fetch congressional trading data...")
    stocks = quiver.congress_trading()
    
    if stocks is not None and not stocks.empty:
        print("✓ Successfully fetched data from Quiver API!")
        print("\nSample data:")
        print(stocks.head())
    else:
        print("✗ API returned empty data")
except Exception as e:
    print(f"✗ Error testing API: {str(e)}")
    
print("\nAPI test complete") 