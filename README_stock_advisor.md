# Stock Advisor

An intelligent stock analysis assistant that answers questions about stocks in plain English.

## Features

- Ask questions about stocks in natural language
- Get real-time stock quotes and price information
- View company overviews and fundamental data
- Read the latest news about specific stocks
- Analyze market trends and stock performance
- *NEW*: Access alternative data sources (requires Quiver API key):
  - Congressional trading activity
  - Insider transactions
  - Corporate lobbying
  - WallStreetBets discussion

## Requirements

- Python 3.6+
- requests library

## Installation

1. Clone this repository or download the files
2. Create a virtual environment:
   ```
   python3 -m venv stock_env
   ```
3. Activate the virtual environment:
   - On macOS/Linux:
     ```
     source stock_env/bin/activate
     ```
   - On Windows:
     ```
     stock_env\Scripts\activate
     ```
4. Install required packages:
   ```
   pip install requests
   ```

## Usage

1. Run the program:
   ```
   python stock_advisor.py
   ```
2. Ask questions in plain English about stocks, such as:
   - "What is the current price of AAPL?"
   - "Tell me about Tesla stock"
   - "What's the latest news for MSFT?"
   - "Give me an analysis of AMZN"
   - "Any insider trading for NVDA?" (requires Quiver API key)
   - "Have any congress members traded GOOGL?" (requires Quiver API key)
   - "What's the Reddit sentiment for GME?" (requires Quiver API key)
   - "How much lobbying has AMZN done?" (requires Quiver API key)

## API Keys

The program uses two API services:

### 1. Alpha Vantage API
Used for basic stock data, company information and news. The current implementation uses your API key.

#### Alpha Vantage API Limitations:
- Free API keys are limited to 25 requests per day
- Premium plans are available for more intensive usage

### 2. Quiver Quantitative API (Optional)
Used for alternative data sources like congressional trading and insider transactions. This requires a paid subscription.

#### Setting up Quiver Quantitative API:
1. Visit [Quiver Quantitative API](https://api.quiverquant.com/) to register for an API key
2. Pricing starts at $10/month for access to all datasets
3. Once you have your API key, update the `self.quiver_api_key = ""` line in the code with your actual key

## Limitations

- The free Alpha Vantage API has a limit of 25 requests per day
- Alternative data sources require a paid Quiver Quantitative API key
- The program doesn't have predictive capabilities for stock prices
- Options data is not available with the free API
- The natural language processing is basic and may not understand complex queries

## Future Enhancements

- Integration with additional financial data providers
- Advanced technical analysis and chart pattern recognition
- Machine learning-based price prediction
- Options data analysis
- Portfolio management features
- Enhanced natural language processing for more complex queries

## License

This project is open source and available under the [MIT License](LICENSE). 