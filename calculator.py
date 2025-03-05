import requests
import json
from datetime import datetime
import time

def add(x, y):
    return x + y

def subtract(x, y):
    return x - y

def multiply(x, y):
    return x * y

def divide(x, y):
    if y == 0:
        raise ValueError("Cannot divide by zero")
    return x / y

def power(x, y):
    return x ** y

def square_root(x):
    if x < 0:
        raise ValueError("Cannot calculate square root of a negative number")
    return x ** 0.5

def factorial(n):
    if not float(n).is_integer():
        raise ValueError("Factorial is only defined for integers")
    if n < 0:
        raise ValueError("Factorial is not defined for negative numbers")
    if n > 170:  # Python's float limit for factorial
        raise ValueError("Number too large for factorial calculation")
    result = 1
    for i in range(1, int(n) + 1):
        result *= i
    return result

def get_stock_data(symbol):
    """
    Fetch real-time market data using Alpha Vantage API
    """
    try:
        # Alpha Vantage API endpoint with a demo API key
        # For production use, get your free API key from: https://www.alphavantage.co/support/#api-key
        # Note: Free API keys are limited to 25 requests per day
        api_key = "QCL62ILQ5PBXK2K6"  # Your Alpha Vantage API key
        base_url = "https://www.alphavantage.co/query"
        
        # Parameters for the API request
        params = {
            "function": "GLOBAL_QUOTE",
            "symbol": symbol,
            "apikey": api_key
        }
        
        # Make the API request
        response = requests.get(base_url, params=params)
        
        if response.status_code == 200:
            data = response.json()
            
            # Check if we got valid data
            if "Global Quote" in data and data["Global Quote"]:
                quote = data["Global Quote"]
                return {
                    "symbol": quote.get("01. symbol", symbol),
                    "price": quote.get("05. price", "N/A"),
                    "change": quote.get("09. change", "N/A"),
                    "change_percent": quote.get("10. change percent", "N/A"),
                    "volume": quote.get("06. volume", "N/A"),
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
            elif "Note" in data:
                # API limit reached
                return f"API limit reached. Please get your own API key from https://www.alphavantage.co/support/#api-key"
            else:
                return f"No data found for symbol: {symbol}"
        else:
            return f"Error fetching data: {response.status_code}"
            
    except Exception as e:
        return f"Error: {str(e)}"

def get_valid_number(prompt):
    while True:
        try:
            return float(input(prompt))
        except ValueError:
            print("Please enter a valid number")

def main():
    print("\n=== Advanced Calculator & Market Data ===")
    print("1. Add")
    print("2. Subtract")
    print("3. Multiply")
    print("4. Divide")
    print("5. Power (x^y)")
    print("6. Square Root")
    print("7. Factorial (n!)")
    print("8. Get Stock Data")
    print("q. Quit")
    
    while True:
        choice = input("\nEnter your choice: ").lower()
        
        if choice == 'q':
            print("\nThank you for using the calculator!")
            break
            
        if choice not in ['1', '2', '3', '4', '5', '6', '7', '8']:
            print("Invalid input. Please try again.")
            continue
        
        try:
            if choice == '8':
                symbol = input("Enter stock symbol (e.g., AAPL, MSFT, IBM): ").upper()
                print("\nFetching stock data...")
                stock_data = get_stock_data(symbol)
                if isinstance(stock_data, dict):
                    print(f"\nStock Data for {stock_data['symbol']}:")
                    print(f"Price: ${stock_data['price']}")
                    print(f"Change: {stock_data['change']} ({stock_data['change_percent']})")
                    print(f"Volume: {stock_data['volume']}")
                    print(f"Time: {stock_data['timestamp']}")
                else:
                    print(stock_data)
            elif choice == '6':
                num = get_valid_number("Enter a number: ")
                result = square_root(num)
                print(f"√{num} = {result:.4f}")
            elif choice == '7':
                num = get_valid_number("Enter a number: ")
                result = factorial(num)
                print(f"{num}! = {result}")
            else:
                num1 = get_valid_number("Enter first number: ")
                num2 = get_valid_number("Enter second number: ")
                
                if choice == '1':
                    result = add(num1, num2)
                    print(f"{num1} + {num2} = {result:.4f}")
                elif choice == '2':
                    result = subtract(num1, num2)
                    print(f"{num1} - {num2} = {result:.4f}")
                elif choice == '3':
                    result = multiply(num1, num2)
                    print(f"{num1} × {num2} = {result:.4f}")
                elif choice == '4':
                    result = divide(num1, num2)
                    print(f"{num1} ÷ {num2} = {result:.4f}")
                elif choice == '5':
                    result = power(num1, num2)
                    print(f"{num1} ^ {num2} = {result:.4f}")
                    
        except ValueError as e:
            print(f"Error: {str(e)}")
        except Exception as e:
            print(f"An unexpected error occurred: {str(e)}")

if __name__ == "__main__":
    main() 