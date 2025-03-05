#!/usr/bin/env python3
"""
A simple script to fetch stock data using Yahoo Finance (yfinance)
"""

import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

def get_stock_data(ticker, period="1mo"):
    """
    Fetch stock data for the specified ticker and period
    
    Parameters:
    ticker (str): Stock ticker symbol (e.g., 'AAPL', 'MSFT')
    period (str): Time period of data to fetch (e.g., '1d', '1mo', '1y')
    
    Returns:
    DataFrame: Historical stock data
    """
    stock = yf.Ticker(ticker)
    hist = stock.history(period=period)
    return hist

def get_stock_info(ticker):
    """
    Fetch basic information about a stock
    
    Parameters:
    ticker (str): Stock ticker symbol
    
    Returns:
    dict: Stock information
    """
    stock = yf.Ticker(ticker)
    info = stock.info
    return info

def print_stock_summary(ticker):
    """
    Print a summary of stock data and information
    
    Parameters:
    ticker (str): Stock ticker symbol
    """
    print(f"\n{'='*50}")
    print(f"Stock Summary for {ticker}")
    print(f"{'='*50}")
    
    # Get stock info
    try:
        info = get_stock_info(ticker)
        print(f"Company: {info.get('shortName', 'N/A')}")
        print(f"Industry: {info.get('industry', 'N/A')}")
        print(f"52-Week High: ${info.get('fiftyTwoWeekHigh', 'N/A')}")
        print(f"52-Week Low: ${info.get('fiftyTwoWeekLow', 'N/A')}")
        print(f"Market Cap: ${info.get('marketCap', 'N/A'):,}")
        print(f"P/E Ratio: {info.get('trailingPE', 'N/A')}")
        print(f"Dividend Yield: {info.get('dividendYield', 'N/A') * 100 if info.get('dividendYield') else 'N/A'}%")
    except Exception as e:
        print(f"Could not get detailed info: {e}")
    
    # Get recent stock data
    try:
        hist = get_stock_data(ticker, period="1mo")
        latest = hist.iloc[-1]
        prev = hist.iloc[-2]
        
        print(f"\nLatest price (as of {hist.index[-1].date()}): ${latest['Close']:.2f}")
        day_change = (latest['Close'] - prev['Close']) / prev['Close'] * 100
        print(f"Day change: {day_change:.2f}%")
        
        month_change = (latest['Close'] - hist.iloc[0]['Close']) / hist.iloc[0]['Close'] * 100
        print(f"30-day change: {month_change:.2f}%")
        
        print(f"\nRecent trading volume: {int(latest['Volume']):,}")
        print(f"30-day average volume: {int(hist['Volume'].mean()):,}")
    except Exception as e:
        print(f"Could not get historical data: {e}")

def main():
    """Main function to demonstrate yfinance usage"""
    print("Yahoo Finance Stock Data Demo\n")
    
    # List of popular stocks to analyze
    tickers = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA']
    
    for ticker in tickers:
        print_stock_summary(ticker)
    
    # Interactive mode
    while True:
        custom_ticker = input("\nEnter a stock ticker to analyze (or 'q' to quit): ").strip().upper()
        if custom_ticker.lower() == 'q':
            break
        try:
            print_stock_summary(custom_ticker)
        except Exception as e:
            print(f"Error analyzing {custom_ticker}: {e}")

if __name__ == "__main__":
    main() 