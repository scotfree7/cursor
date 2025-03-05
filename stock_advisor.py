#!/usr/bin/env python3
"""
Stock Advisor - An intelligent stock analysis assistant

This program helps users analyze stocks, options, and market trends
by answering questions in plain English and providing data-driven insights.
"""

import requests
import json
import re
import webbrowser
from datetime import datetime, timedelta
import time
import os

# Try to load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
    ENV_LOADED = True
except ImportError:
    ENV_LOADED = False

# Try to import required packages
try:
    import quiverquant
    import pandas as pd
    QUIVER_AVAILABLE = True
except ImportError:
    QUIVER_AVAILABLE = False

class StockAdvisor:
    def __init__(self):
        # Alpha Vantage API key - Get from environment variable or default
        self.api_key = os.environ.get("ALPHA_VANTAGE_API_KEY", "QCL62ILQ5PBXK2K6")
        self.base_url = "https://www.alphavantage.co/query"
        
        # News API (using Alpha Vantage News API)
        self.news_url = "https://www.alphavantage.co/query"
        
        # TradingView integration
        self.tradingview_base_url = "https://www.tradingview.com/chart"
        
        # Quiver Quantitative API setup (using official quiverquant package if available)
        self.quiver_api_key = os.environ.get("QUIVER_API_KEY", "")
        self.quiver_enabled = QUIVER_AVAILABLE and self.quiver_api_key != ""
        
        if self.quiver_enabled:
            try:
                self.quiver = quiverquant.quiver(self.quiver_api_key)
            except Exception as e:
                print(f"Warning: Failed to initialize Quiver Quantitative: {str(e)}")
                self.quiver_enabled = False
        
        # Cache for storing data to minimize API calls
        self.cache = {}
        self.cache_expiry = {}
        self.cache_duration = 300  # 5 minutes
        
        # Add context tracking to remember previous option questions
        self.last_option_context = {
            "symbol": None,
            "strike_price": None,
            "option_type": None,
            "expiry_date": None
        }
        
    def get_stock_quote(self, symbol):
        """Get current stock quote data"""
        cache_key = f"quote_{symbol}"
        
        # Check cache first
        if cache_key in self.cache and datetime.now() < self.cache_expiry.get(cache_key, datetime.now()):
            return self.cache[cache_key]
        
        params = {
            "function": "GLOBAL_QUOTE",
            "symbol": symbol,
            "apikey": self.api_key
        }
        
        try:
            response = requests.get(self.base_url, params=params)
            if response.status_code == 200:
                data = response.json()
                
                if "Global Quote" in data and data["Global Quote"]:
                    quote = data["Global Quote"]
                    result = {
                        "symbol": quote.get("01. symbol", symbol),
                        "price": float(quote.get("05. price", 0)),
                        "change": float(quote.get("09. change", 0)),
                        "change_percent": quote.get("10. change percent", "0%").strip("%"),
                        "volume": int(quote.get("06. volume", 0)),
                        "latest_trading_day": quote.get("07. latest trading day", ""),
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                    
                    # Cache the result
                    self.cache[cache_key] = result
                    self.cache_expiry[cache_key] = datetime.now() + timedelta(seconds=self.cache_duration)
                    
                    return result
                elif "Note" in data:
                    return {"error": "API limit reached. Please try again later."}
                else:
                    return {"error": f"No data found for symbol: {symbol}"}
            else:
                return {"error": f"Error fetching data: {response.status_code}"}
        except Exception as e:
            return {"error": f"Error: {str(e)}"}
    
    def get_company_overview(self, symbol):
        """Get company overview data"""
        cache_key = f"overview_{symbol}"
        
        # Check cache first
        if cache_key in self.cache and datetime.now() < self.cache_expiry.get(cache_key, datetime.now()):
            return self.cache[cache_key]
        
        params = {
            "function": "OVERVIEW",
            "symbol": symbol,
            "apikey": self.api_key
        }
        
        try:
            response = requests.get(self.base_url, params=params)
            if response.status_code == 200:
                data = response.json()
                
                if "Symbol" in data:
                    # Cache the result
                    self.cache[cache_key] = data
                    self.cache_expiry[cache_key] = datetime.now() + timedelta(seconds=self.cache_duration)
                    
                    return data
                elif "Note" in data:
                    return {"error": "API limit reached. Please try again later."}
                else:
                    return {"error": f"No company overview found for symbol: {symbol}"}
            else:
                return {"error": f"Error fetching data: {response.status_code}"}
        except Exception as e:
            return {"error": f"Error: {str(e)}"}
    
    def get_stock_news(self, symbol=None, topics=None):
        """Get news about a specific stock or market topics"""
        if symbol:
            cache_key = f"news_{symbol}"
        elif topics:
            cache_key = f"news_{topics}"
        else:
            cache_key = "news_market"
            
        # Check cache first
        if cache_key in self.cache and datetime.now() < self.cache_expiry.get(cache_key, datetime.now()):
            return self.cache[cache_key]
        
        params = {
            "function": "NEWS_SENTIMENT",
            "apikey": self.api_key
        }
        
        if symbol:
            params["tickers"] = symbol
        if topics:
            params["topics"] = topics
            
        try:
            response = requests.get(self.news_url, params=params)
            if response.status_code == 200:
                data = response.json()
                
                if "feed" in data:
                    # Cache the result
                    self.cache[cache_key] = data
                    self.cache_expiry[cache_key] = datetime.now() + timedelta(seconds=self.cache_duration)
                    
                    return data
                elif "Note" in data:
                    return {"error": "API limit reached. Please try again later."}
                else:
                    return {"error": "No news data found"}
            else:
                return {"error": f"Error fetching news: {response.status_code}"}
        except Exception as e:
            return {"error": f"Error: {str(e)}"}
    
    def get_congress_trading(self, symbol):
        """Get congressional trading data using Quiver Quantitative"""
        if not self.quiver_enabled:
            return {"error": "Quiver Quantitative API not configured or package not installed. Run 'pip install quiverquant' and set your API key."}
        
        cache_key = f"congress_{symbol}"
        
        # Check cache first
        if cache_key in self.cache and datetime.now() < self.cache_expiry.get(cache_key, datetime.now()):
            return self.cache[cache_key]
        
        try:
            if symbol:
                data = self.quiver.congress_trading(symbol)
            else:
                data = self.quiver.congress_trading()
                
            # Cache the result
            self.cache[cache_key] = data
            self.cache_expiry[cache_key] = datetime.now() + timedelta(seconds=self.cache_duration)
            
            return data
        except Exception as e:
            return {"error": f"Error fetching congressional trading data: {str(e)}"}
            
    def get_insider_trading(self, symbol):
        """Get insider trading data using Quiver Quantitative"""
        if not self.quiver_enabled:
            return {"error": "Quiver Quantitative API not configured or package not installed. Run 'pip install quiverquant' and set your API key."}
        
        cache_key = f"insider_{symbol}"
        
        # Check cache first
        if cache_key in self.cache and datetime.now() < self.cache_expiry.get(cache_key, datetime.now()):
            return self.cache[cache_key]
        
        try:
            if symbol:
                data = self.quiver.insiders(symbol)
            else:
                data = self.quiver.insiders()
                
            # Cache the result
            self.cache[cache_key] = data
            self.cache_expiry[cache_key] = datetime.now() + timedelta(seconds=self.cache_duration)
            
            return data
        except Exception as e:
            return {"error": f"Error fetching insider trading data: {str(e)}"}
            
    def get_wallstreetbets_data(self, symbol):
        """Get WallStreetBets data using Quiver Quantitative"""
        if not self.quiver_enabled:
            return {"error": "Quiver Quantitative API not configured or package not installed. Run 'pip install quiverquant' and set your API key."}
        
        cache_key = f"wsb_{symbol}"
        
        # Check cache first
        if cache_key in self.cache and datetime.now() < self.cache_expiry.get(cache_key, datetime.now()):
            return self.cache[cache_key]
        
        try:
            if symbol:
                data = self.quiver.wallstreetbets(symbol)
            else:
                data = self.quiver.wallstreetbets()
                
            # Cache the result
            self.cache[cache_key] = data
            self.cache_expiry[cache_key] = datetime.now() + timedelta(seconds=self.cache_duration)
            
            return data
        except Exception as e:
            return {"error": f"Error fetching WallStreetBets data: {str(e)}"}
            
    def get_lobbying_data(self, symbol):
        """Get lobbying data using Quiver Quantitative"""
        if not self.quiver_enabled:
            return {"error": "Quiver Quantitative API not configured or package not installed. Run 'pip install quiverquant' and set your API key."}
        
        cache_key = f"lobbying_{symbol}"
        
        # Check cache first
        if cache_key in self.cache and datetime.now() < self.cache_expiry.get(cache_key, datetime.now()):
            return self.cache[cache_key]
        
        try:
            if symbol:
                data = self.quiver.lobbying(symbol)
            else:
                data = self.quiver.lobbying()
                
            # Cache the result
            self.cache[cache_key] = data
            self.cache_expiry[cache_key] = datetime.now() + timedelta(seconds=self.cache_duration)
            
            return data
        except Exception as e:
            return {"error": f"Error fetching lobbying data: {str(e)}"}
    
    def get_gov_contracts(self, symbol=None):
        """Get government contracts data using Quiver Quantitative"""
        if not self.quiver_enabled:
            return {"error": "Quiver Quantitative API not configured or package not installed. Run 'pip install quiverquant' and set your API key."}
        
        cache_key = f"gov_contracts_{symbol}"
        
        # Check cache first
        if cache_key in self.cache and datetime.now() < self.cache_expiry.get(cache_key, datetime.now()):
            return self.cache[cache_key]
        
        try:
            if symbol:
                data = self.quiver.gov_contracts(symbol)
            else:
                data = self.quiver.gov_contracts()
                
            # Cache the result
            self.cache[cache_key] = data
            self.cache_expiry[cache_key] = datetime.now() + timedelta(seconds=self.cache_duration)
            
            return data
        except Exception as e:
            return {"error": f"Error fetching government contracts data: {str(e)}"}
    
    def get_offexchange_data(self, symbol=None):
        """Get off-exchange short volume data using Quiver Quantitative"""
        if not self.quiver_enabled:
            return {"error": "Quiver Quantitative API not configured or package not installed. Run 'pip install quiverquant' and set your API key."}
        
        cache_key = f"offexchange_{symbol}"
        
        # Check cache first
        if cache_key in self.cache and datetime.now() < self.cache_expiry.get(cache_key, datetime.now()):
            return self.cache[cache_key]
        
        try:
            if symbol:
                data = self.quiver.offexchange(symbol)
            else:
                data = self.quiver.offexchange()
                
            # Cache the result
            self.cache[cache_key] = data
            self.cache_expiry[cache_key] = datetime.now() + timedelta(seconds=self.cache_duration)
            
            return data
        except Exception as e:
            return {"error": f"Error fetching off-exchange short volume data: {str(e)}"}
    
    def get_wikipedia_data(self, symbol=None):
        """Get Wikipedia page views data using Quiver Quantitative"""
        if not self.quiver_enabled:
            return {"error": "Quiver Quantitative API not configured or package not installed. Run 'pip install quiverquant' and set your API key."}
        
        cache_key = f"wikipedia_{symbol}"
        
        # Check cache first
        if cache_key in self.cache and datetime.now() < self.cache_expiry.get(cache_key, datetime.now()):
            return self.cache[cache_key]
        
        try:
            if symbol:
                data = self.quiver.wikipedia(symbol)
            else:
                data = self.quiver.wikipedia()
                
            # Cache the result
            self.cache[cache_key] = data
            self.cache_expiry[cache_key] = datetime.now() + timedelta(seconds=self.cache_duration)
            
            return data
        except Exception as e:
            return {"error": f"Error fetching Wikipedia page views data: {str(e)}"}
    
    def get_twitter_data(self, symbol=None):
        """Get Twitter following data using Quiver Quantitative"""
        if not self.quiver_enabled:
            return {"error": "Quiver Quantitative API not configured or package not installed. Run 'pip install quiverquant' and set your API key."}
        
        cache_key = f"twitter_{symbol}"
        
        # Check cache first
        if cache_key in self.cache and datetime.now() < self.cache_expiry.get(cache_key, datetime.now()):
            return self.cache[cache_key]
        
        try:
            if symbol:
                data = self.quiver.twitter(symbol)
            else:
                data = self.quiver.twitter()
                
            # Cache the result
            self.cache[cache_key] = data
            self.cache_expiry[cache_key] = datetime.now() + timedelta(seconds=self.cache_duration)
            
            return data
        except Exception as e:
            return {"error": f"Error fetching Twitter following data: {str(e)}"}
    
    def get_spacs_data(self, symbol=None):
        """Get r/SPACs discussion data using Quiver Quantitative"""
        if not self.quiver_enabled:
            return {"error": "Quiver Quantitative API not configured or package not installed. Run 'pip install quiverquant' and set your API key."}
        
        cache_key = f"spacs_{symbol}"
        
        # Check cache first
        if cache_key in self.cache and datetime.now() < self.cache_expiry.get(cache_key, datetime.now()):
            return self.cache[cache_key]
        
        try:
            if symbol:
                data = self.quiver.spacs(symbol)
            else:
                data = self.quiver.spacs()
                
            # Cache the result
            self.cache[cache_key] = data
            self.cache_expiry[cache_key] = datetime.now() + timedelta(seconds=self.cache_duration)
            
            return data
        except Exception as e:
            return {"error": f"Error fetching r/SPACs discussion data: {str(e)}"}
    
    def get_flights_data(self, symbol=None):
        """Get corporate private jet flights data using Quiver Quantitative"""
        if not self.quiver_enabled:
            return {"error": "Quiver Quantitative API not configured or package not installed. Run 'pip install quiverquant' and set your API key."}
        
        cache_key = f"flights_{symbol}"
        
        # Check cache first
        if cache_key in self.cache and datetime.now() < self.cache_expiry.get(cache_key, datetime.now()):
            return self.cache[cache_key]
        
        try:
            if symbol:
                data = self.quiver.flights(symbol)
            else:
                data = self.quiver.flights()
                
            # Cache the result
            self.cache[cache_key] = data
            self.cache_expiry[cache_key] = datetime.now() + timedelta(seconds=self.cache_duration)
            
            return data
        except Exception as e:
            return {"error": f"Error fetching corporate private jet flights data: {str(e)}"}
    
    def get_patents_data(self, symbol):
        """Get patents data using Quiver Quantitative"""
        if not self.quiver_enabled:
            return {"error": "Quiver Quantitative API not configured or package not installed. Run 'pip install quiverquant' and set your API key."}
        
        cache_key = f"patents_{symbol}"
        
        # Check cache first
        if cache_key in self.cache and datetime.now() < self.cache_expiry.get(cache_key, datetime.now()):
            return self.cache[cache_key]
        
        try:
            data = self.quiver.patents(symbol)
                
            # Cache the result
            self.cache[cache_key] = data
            self.cache_expiry[cache_key] = datetime.now() + timedelta(seconds=self.cache_duration)
            
            return data
        except Exception as e:
            return {"error": f"Error fetching patents data: {str(e)}"}
            
    def get_gov_contracts_info(self, symbol):
        """Get government contracts information for a stock"""
        contracts = self.get_gov_contracts(symbol)
        
        if "error" in contracts:
            return {
                "response_type": "error",
                "message": contracts["error"]
            }
            
        # If contracts is a pandas DataFrame (expected from Quiver API)
        try:
            if isinstance(contracts, pd.DataFrame) and not contracts.empty:
                recent_contracts = contracts.head(5)  # Get 5 most recent contracts
                
                message = f"Recent government contracts for {symbol}:\n\n"
                
                for _, contract in recent_contracts.iterrows():
                    date = contract.get('Date', 'Unknown date')
                    amount = contract.get('Amount', 0)
                    agency = contract.get('Agency', 'Unknown agency')
                    
                    message += f"- {date}: ${amount:,.2f} from {agency}\n"
                    
                return {
                    "response_type": "gov_contracts",
                    "symbol": symbol,
                    "data": contracts,
                    "message": message
                }
            else:
                return {
                    "response_type": "no_data",
                    "message": f"No government contracts data found for {symbol}."
                }
        except Exception as e:
            return {
                "response_type": "error",
                "message": f"Error processing government contracts data: {str(e)}"
            }
    
    def get_offexchange_info(self, symbol):
        """Get off-exchange short volume information for a stock"""
        offexchange = self.get_offexchange_data(symbol)
        
        if "error" in offexchange:
            return {
                "response_type": "error",
                "message": offexchange["error"]
            }
            
        # If offexchange is a pandas DataFrame (expected from Quiver API)
        try:
            if isinstance(offexchange, pd.DataFrame) and not offexchange.empty:
                recent_data = offexchange.head(10)  # Get 10 most recent records
                
                message = f"Recent off-exchange short volume for {symbol}:\n\n"
                
                for _, data in recent_data.iterrows():
                    date = data.get('Date', 'Unknown date')
                    short_vol = data.get('ShortVolume', 0)
                    total_vol = data.get('TotalVolume', 0)
                    
                    if total_vol > 0:
                        short_pct = (short_vol / total_vol) * 100
                        message += f"- {date}: {short_vol:,.0f} shares shorted ({short_pct:.2f}% of total volume)\n"
                
                return {
                    "response_type": "offexchange",
                    "symbol": symbol,
                    "data": offexchange,
                    "message": message
                }
            else:
                return {
                    "response_type": "no_data",
                    "message": f"No off-exchange short volume data found for {symbol}."
                }
        except Exception as e:
            return {
                "response_type": "error",
                "message": f"Error processing off-exchange short volume data: {str(e)}"
            }
    
    def get_wikipedia_info(self, symbol):
        """Get Wikipedia page views information for a stock"""
        wikipedia = self.get_wikipedia_data(symbol)
        
        if "error" in wikipedia:
            return {
                "response_type": "error",
                "message": wikipedia["error"]
            }
            
        # If wikipedia is a pandas DataFrame (expected from Quiver API)
        try:
            if isinstance(wikipedia, pd.DataFrame) and not wikipedia.empty:
                recent_data = wikipedia.tail(7)  # Get last 7 days data
                
                message = f"Recent Wikipedia page views for {symbol}:\n\n"
                
                for _, data in recent_data.iterrows():
                    date = data.get('Date', 'Unknown date')
                    views = data.get('Views', 0)
                    
                    message += f"- {date}: {views:,.0f} views\n"
                
                # Calculate trend
                if len(recent_data) > 1:
                    first_views = recent_data.iloc[0].get('Views', 0)
                    last_views = recent_data.iloc[-1].get('Views', 0)
                    
                    if first_views > 0:
                        change_pct = ((last_views - first_views) / first_views) * 100
                        trend = "increasing" if change_pct > 0 else "decreasing"
                        message += f"\nWikipedia page views are {trend} by {abs(change_pct):.2f}% over this period."
                
                return {
                    "response_type": "wikipedia",
                    "symbol": symbol,
                    "data": wikipedia,
                    "message": message
                }
            else:
                return {
                    "response_type": "no_data",
                    "message": f"No Wikipedia page views data found for {symbol}."
                }
        except Exception as e:
            return {
                "response_type": "error",
                "message": f"Error processing Wikipedia page views data: {str(e)}"
            }
    
    def get_tradingview_chart_url(self, symbol, timeframe="D"):
        """Generate a TradingView chart URL for a given symbol
        
        Args:
            symbol: Stock ticker symbol
            timeframe: Chart timeframe (D=daily, W=weekly, M=monthly, etc.)
        
        Returns:
            URL to TradingView chart
        """
        # Construct the TradingView URL
        # Default to US stocks
        exchange = "NASDAQ"
        
        # Determine likely exchange based on common prefixes/patterns
        if symbol.startswith("BTC") or symbol.endswith("USD") or symbol.endswith("USDT"):
            exchange = "COINBASE"
        elif symbol.startswith("^"):
            exchange = "DJ"  # Dow Jones indices
        
        # Create the URL with the symbol and timeframe
        url = f"{self.tradingview_base_url}/?symbol={exchange}:{symbol}&interval={timeframe}"
        
        return url
    
    def get_chart_info(self, symbol):
        """Get charting information for a stock"""
        try:
            # Generate TradingView chart URLs for different timeframes
            daily_url = self.get_tradingview_chart_url(symbol, "D")
            weekly_url = self.get_tradingview_chart_url(symbol, "W")
            monthly_url = self.get_tradingview_chart_url(symbol, "M")
            
            message = f"TradingView Charts for {symbol}:\n\n"
            message += f"- [Daily Chart]({daily_url})\n"
            message += f"- [Weekly Chart]({weekly_url})\n"
            message += f"- [Monthly Chart]({monthly_url})\n\n"
            message += "Would you like to open any of these charts? (Please respond with 'daily', 'weekly', or 'monthly')"
            
            return {
                "response_type": "chart",
                "symbol": symbol,
                "data": {
                    "daily_url": daily_url,
                    "weekly_url": weekly_url,
                    "monthly_url": monthly_url
                },
                "message": message
            }
        except Exception as e:
            return {
                "response_type": "error",
                "message": f"Error generating chart links: {str(e)}"
            }

    def analyze_question(self, question):
        """Analyze user question and provide relevant information"""
        original_question = question  # Keep original for reference
        question = question.lower()
        
        # Check for options queries and personal queries
        is_options_query = re.search(r'\b(option|call|put)\b', question)
        is_personal = re.search(r'\b(my|i\s+have|i\s+own|i\s+bought|i\s+purchased|bought\s+a|will\s+it|will\s+my)\b', question)
        personal_option_query = is_options_query and is_personal
        
        found_symbols = []
        
        # Define company name to ticker mapping
        company_to_ticker = {
            'apple': 'AAPL',
            'microsoft': 'MSFT',
            'amazon': 'AMZN',
            'google': 'GOOGL',
            'alphabet': 'GOOGL',
            'facebook': 'META',
            'meta': 'META',
            'tesla': 'TSLA',
            'nvidia': 'NVDA',
            'netflix': 'NFLX',
            'disney': 'DIS',
            'visa': 'V',
            'mastercard': 'MA',
            'jpmorgan': 'JPM',
            'jp morgan': 'JPM',
            'bank of america': 'BAC',
            'walmart': 'WMT',
            'coca cola': 'KO',
            'coca-cola': 'KO',
            'pepsi': 'PEP',
            'pepsico': 'PEP',
            'procter & gamble': 'PG',
            'procter and gamble': 'PG',
            'johnson & johnson': 'JNJ',
            'johnson and johnson': 'JNJ',
            'unitedhealth': 'UNH',
            'home depot': 'HD',
            'ibm': 'IBM',
            'intel': 'INTC',
            'cisco': 'CSCO',
            'oracle': 'ORCL',
            'verizon': 'VZ',
            'att': 'T',
            'at&t': 'T',
            'chevron': 'CVX',
            'exxon': 'XOM',
            'exxonmobil': 'XOM',
            'boeing': 'BA',
            'general electric': 'GE',
            '3m': 'MMM',
            'caterpillar': 'CAT',
            'dupont': 'DD'
        }
        
        # Common tickers to search for
        common_tickers = ['aapl', 'msft', 'amzn', 'googl', 'goog', 'meta', 'tsla', 'nvda', 'nflx', 'dis', 
                         'v', 'ma', 'jpm', 'bac', 'wmt', 'ko', 'pep', 'pg', 'jnj', 'unh', 'hd', 'ibm', 
                         'intc', 'csco', 'orcl', 'vz', 't', 'cvx', 'xom', 'ba', 'ge', 'mmm', 'cat', 'dd']
        
        # Common words to exclude from stock symbol matching
        exclude_words = ['a', 'i', 'an', 'the', 'and', 'or', 'but', 'if', 'then', 'else', 'when',
                         'up', 'down', 'in', 'out', 'on', 'off', 'over', 'under', 'again', 'further',
                         'then', 'once', 'here', 'there', 'when', 'where', 'why', 'how', 'all', 'any',
                         'both', 'each', 'few', 'more', 'most', 'some', 'such', 'no', 'nor', 'not',
                         'only', 'own', 'same', 'so', 'than', 'too', 'very', 's', 't', 'can', 'will',
                         'just', 'don', 'should', 'now', 'my', 'with', 'for', 'by', 'from', 'get',
                         'have', 'has', 'had', 'did', 'do', 'does', 'is', 'are', 'am', 'was', 'were',
                         'be', 'been', 'being', 'call', 'put', 'option', 'stock', 'price', 'mar', 'apr',
                         'jan', 'feb', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec', 'next', 'last',
                         'year', 'month', 'week', 'day', 'that', 'this', 'these', 'those', 'what', 'which',
                         'who', 'whom', 'whose', 'it', 'its', 'he', 'him', 'his', 'she', 'her', 'hers',
                         'they', 'them', 'their', 'theirs', 'we', 'us', 'our', 'ours', 'you', 'your', 'yours',
                         'make', 'makes', 'made', 'one', 'two', 'three', 'many', 'much', 'at', 'to', 'of',
                         'before', 'after', 'during', 'since', 'until', 'till', 'against', 'among', 'between',
                         'into', 'through', 'throughout', 'besides', 'above', 'below', 'around', 'upon', 'within',
                         'about', 'along', 'alongside', 'amid', 'among', 'beyond', 'near', 'toward', 'via', 'yes', 'no']
        
        # For all option queries (personal or not), prioritize company names over everything else
        if is_options_query:
            # First try to match company names in option queries
            for company, ticker in company_to_ticker.items():
                if re.search(r'\b' + re.escape(company) + r'\b', question, re.IGNORECASE):
                    found_symbols = [ticker]  # Replace any previously found symbols
                    break  # Only need one match for options
            
            # If no company name found, look for common ticker symbols
            if not found_symbols:
                for ticker in common_tickers:
                    if re.search(r'\b' + ticker + r'\b', question, re.IGNORECASE):
                        found_symbols = [ticker.upper()]  # Replace any previously found symbols
                        break  # Only need one match for options
            
            # If still no symbols found, it's likely not a valid option query
            if not found_symbols and personal_option_query:
                return {
                    "response_type": "error",
                    "message": "I couldn't identify a stock symbol in your option question. Please specify a company name or ticker symbol, for example: 'Will my TSLA $440 call be profitable?'"
                }
        else:
            # For non-option queries, use the standard approach
            # First try to match company names
            for company, ticker in company_to_ticker.items():
                pattern = r'\b' + re.escape(company) + r'\b'
                match = re.search(pattern, question, re.IGNORECASE)
                if match:
                    found_symbols.append(ticker)
            
            # Then try to match common stock tickers
            if not found_symbols:
                for ticker in common_tickers:
                    pattern = r'\b' + ticker + r'\b'
                    match = re.search(pattern, question, re.IGNORECASE)
                    if match:
                        found_symbols.append(ticker.upper())
            
            # If no common tickers found, try more general pattern but exclude common English words
            if not found_symbols:
                symbols = re.findall(r'(?:^|\s)([a-zA-Z]{1,5})(?:\s|$|\W)', question)
                for symbol in symbols:
                    if symbol.lower() not in exclude_words and len(symbol) >= 2:
                        found_symbols.append(symbol.upper())
        
        # If we found symbols either way, use them
        if found_symbols:
            symbols = found_symbols
        else:
            # If really nothing was found, default to general analysis without a symbol
            return {
                "response_type": "error",
                "message": "I couldn't identify a stock symbol in your question. Please mention a specific stock symbol like AAPL, TSLA, etc."
            }
        
        # Extract dollar amounts for potential strike prices
        # Match both $X and X dollars and standalone numbers that could be strike prices
        strike_prices = re.findall(r'\$(\d+(?:\.\d+)?)|(\d+(?:\.\d+)?)\s*(?:dollars?|usd)|(?:strike|price)[^\d]*?(\d+(?:\.\d+)?)', question)
        strike_price = None
        if strike_prices:
            # Flatten and filter the tuple results from the regex
            flat_prices = [price for group in strike_prices for price in group if price]
            if flat_prices:
                strike_price = flat_prices[0]
        
        # Extract expiry dates - improve to handle multiple formats
        # Example patterns: "21 mar 2025", "march 21 2025", "03/21/25", "21/03/2025", "2025-03-21"
        date_patterns = [
            r'(\d{1,2})\s*(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\s*(\d{2,4})',  # 21 mar 2025
            r'(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\s*(\d{1,2})(?:st|nd|rd|th)?\s*,?\s*(\d{2,4})',  # march 21 2025
            r'(\d{1,2})[/-](\d{1,2})[/-](\d{2,4})',  # 03/21/25 or 21/03/2025
            r'(\d{4})[/-](\d{1,2})[/-](\d{1,2})'     # 2025-03-21
        ]
        
        expiry_date = None
        for pattern in date_patterns:
            dates = re.findall(pattern, question)
            if dates:
                # Format will depend on which pattern matched
                expiry_date = dates[0]  # Take the first match
                break
        
        # If we found a month name but not a complete date, try to extract it differently
        if not expiry_date and re.search(r'\b(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\b', question):
            # Extract month, day, and year separately
            month_match = re.search(r'\b(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\b', question)
            day_match = re.search(r'\b(\d{1,2})(?:st|nd|rd|th)?\b', question)
            year_match = re.search(r'\b(20\d{2})\b', question)  # Assuming years like 2023, 2024, etc.
            
            if month_match and (day_match or year_match):
                month = month_match.group(1)
                day = day_match.group(1) if day_match else "15"  # Default to middle of month
                year = year_match.group(1) if year_match else "2024"  # Default to next year
                expiry_date = (day, month, year)
        
        # Better detection of option types (call vs put)
        option_type = None
        if re.search(r'\b(call|calls)\b', question):
            option_type = 'call'
        elif re.search(r'\b(put|puts)\b', question):
            option_type = 'put'
        
        # Check for personal options inquiries - expanded to catch more variations
        if re.search(r'\b(my|i\s+have|i\s+own|i\s+bought|i\s+purchased|will\s+my)\b.*\b(option|call|put)\b', question):
            # If we have the necessary option details
            if any(symbol in question.upper() for symbol in symbols) and (strike_price or expiry_date or option_type):
                symbol = next((s.upper() for s in symbols if s.upper() in question), symbols[0].upper() if symbols else None)
                
                # Store the context for future questions
                if symbol:
                    self.last_option_context["symbol"] = symbol
                if strike_price:
                    self.last_option_context["strike_price"] = strike_price
                if option_type:
                    self.last_option_context["option_type"] = option_type
                if expiry_date:
                    self.last_option_context["expiry_date"] = expiry_date
                
                # Use stored context if some details are missing
                if not symbol and self.last_option_context["symbol"]:
                    symbol = self.last_option_context["symbol"]
                if not strike_price and self.last_option_context["strike_price"]:
                    strike_price = self.last_option_context["strike_price"]
                if not option_type and self.last_option_context["option_type"]:
                    option_type = self.last_option_context["option_type"]
                if not expiry_date and self.last_option_context["expiry_date"]:
                    expiry_date = self.last_option_context["expiry_date"]
                
                return self.get_personal_option_info(symbol, option_type, strike_price, expiry_date, question)
                
        # Check for options recommendations inquiries
        if re.search(r'\b(which|what|recommend|best|good|profitable)\b.*\b(option|call|put|strike)\b', question) and \
           re.search(r'\b(buy|purchase|get|invest)\b', question):
            
            # Try to extract budget
            budget_match = re.search(r'\$?(\d+(?:,\d+)?(?:\.\d+)?)\s*(?:dollars?|usd|budget)?', question)
            budget = budget_match.group(1).replace(',', '') if budget_match else "1000"
            
            if symbols:
                symbol = symbols[0].upper()
                return self.get_option_recommendations(symbol, budget, question)
        
        # Check for chart request
        if re.search(r'(chart|graph|plot).*?(for|of)\s+(\w+)', question) or re.search(r'show\s+(\w+)\s+(chart|graph)', question):
            symbol_match = re.search(r'(chart|graph|plot).*?(for|of)\s+([A-Za-z]{1,5})', question) or re.search(r'show\s+([A-Za-z]{1,5})\s+(chart|graph)', question)
            
            if symbol_match:
                symbol = symbol_match.group(3).upper() if len(symbol_match.groups()) >= 3 else symbol_match.group(1).upper()
                return self.get_chart_info(symbol)
        
        # Check if open a TradingView chart
        if question in ['daily', 'weekly', 'monthly'] and hasattr(self, 'last_response') and self.last_response.get("response_type") == "chart":
            url = self.last_response["data"].get(f"{question}_url")
            if url:
                webbrowser.open(url)
                return {
                    "response_type": "info",
                    "message": f"Opening {question} chart for {self.last_response['symbol']}..."
                }
        
        # Check for government contracts
        if re.search(r'(government|gov|federal).*?(contract|contracts)', question):
            symbol_match = re.search(r'for ([A-Za-z]{1,5})', question)
            
            if symbol_match:
                symbol = symbol_match.group(1).upper()
                return self.get_gov_contracts_info(symbol)
        
        # Check for off-exchange/short volume
        if re.search(r'(off[- ]exchange|short volume|short interest)', question):
            symbol_match = re.search(r'for ([A-Za-z]{1,5})', question)
            
            if symbol_match:
                symbol = symbol_match.group(1).upper()
                return self.get_offexchange_info(symbol)
        
        # Check for Wikipedia page views
        if re.search(r'(wikipedia|wiki).*?(views|traffic|visits)', question):
            symbol_match = re.search(r'for ([A-Za-z]{1,5})', question)
            
            if symbol_match:
                symbol = symbol_match.group(1).upper()
                return self.get_wikipedia_info(symbol)
        
        # Add checks for other methods here...
        
        # Check if this is a follow-up question about a previously mentioned option
        if (re.search(r'(chance|chances|likelihood|probability|odds|will).*?(hit|reach).*?(strike|price)', question) or 
            re.search(r'what are the chances', question)) and self.last_option_context["symbol"] is not None:
            
            # Use the context from the previous option question
            return self.get_prediction_info(
                self.last_option_context["symbol"], 
                f"Will {self.last_option_context['symbol']} reach ${self.last_option_context['strike_price']} by {self.last_option_context['expiry_date']}?"
            )
        
        # Check if the question is about options recommendations
        if re.search(r'which (call|put) options? (should|to) (buy|purchase)', question) or \
           re.search(r'(recommend|suggest).*options', question) or \
           re.search(r'options?.*(with|for) \$\d+', question):
            symbol_match = re.search(r'for ([A-Za-z]{1,5})', question)
            budget_match = re.search(r'\$(\d+)', question)
            
            if symbol_match:
                symbol = symbol_match.group(1).upper()
                budget = budget_match.group(1) if budget_match else None
                return self.get_option_recommendations(symbol, budget, question)
        
        # Check if the question is about option profitability
        if re.search(r'will.*option be profitable', question) or \
           re.search(r'(profit|make money|gain).*option', question):
            symbol_match = re.search(r'(call|put).*?([A-Za-z]{1,5})', question)
            price_match = re.search(r'\$(\d+)', question)
            date_match = re.search(r'(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\s+\d{1,2},?\s+\d{4}', question)
            
            if not symbol_match:
                symbol_match = re.search(r'([A-Za-z]{1,5})\s+(call|put)', question)
            
            if symbol_match:
                symbol = symbol_match.group(2).upper() if symbol_match.group(1) in ['call', 'put'] else symbol_match.group(1).upper()
                option_type = "call" if "call" in question else "put" if "put" in question else "unknown"
                strike_price = price_match.group(1) if price_match else "unknown"
                expiry_date = date_match.group(0) if date_match else "unknown"
                
                return self.get_option_profitability(symbol, option_type, strike_price, expiry_date, question)
        
        # Check if the question is about price prediction (reaching a target price)
        if re.search(r'will\s+\w+\s+(hit|reach|get to|go to|go up to|go above|exceed|cross)\s+\$\d+', question) or \
           re.search(r'(hit|reach|get to|go to|go up to|go above|exceed|cross)\s+\$\d+\s+(?:by|before|until)', question):
            # Check for common stock symbols first
            common_symbols = ['aapl', 'msft', 'amzn', 'googl', 'goog', 'meta', 'tsla', 'nvda', 'nflx', 'dis']
            for symbol in common_symbols:
                if symbol.lower() in question.lower():
                    return self.get_prediction_info(symbol.upper(), question)
            
            # Then try different pattern
            symbol_match = re.search(r'will\s+(\w{1,5})\s+(hit|reach)', question, re.IGNORECASE)
            if not symbol_match:
                symbol_match = re.search(r'(hit|reach|get to|go to)\s+\$\d+\s+(?:by|before|until).*?(\w{1,5})', question, re.IGNORECASE)
            
            if symbol_match:
                symbol = symbol_match.group(1).upper()
                return self.get_prediction_info(symbol, question)
        
        # Extract stock symbols (look for uppercase words or words after "about", "for", etc.)
        symbols = re.findall(r'\b[A-Z]{1,5}\b', question.upper())  # Look for uppercase symbols in the uppercase question
        if not symbols:
            # First look for common stock symbols
            common_symbols = ['AAPL', 'MSFT', 'AMZN', 'GOOGL', 'GOOG', 'META', 'TSLA', 'NVDA', 'NFLX', 'DIS', 
                             'JPM', 'BAC', 'WMT', 'KO', 'PEP', 'PG', 'JNJ', 'UNH', 'HD', 'V', 'MA']
            for symbol in common_symbols:
                if symbol.lower() in question.lower():
                    symbols = [symbol]
                    break
            
            # If still no symbols found, try more pattern matching
            if not symbols:
                # Look for stock names after certain keywords
                symbol_patterns = [
                    r'(?:about|for|on|regarding|of|is|)\s+([a-zA-Z]{1,5})(?:\s+stock|\s+shares|\s+price|\s+option)',
                    r'([a-zA-Z]{1,5})(?:\s+stock|\s+shares|\s+price|\s+option)',
                    r'\b([a-zA-Z]{1,5})\b'  # Try to match any word that could be a symbol
                ]
                
                for pattern in symbol_patterns:
                    matches = re.findall(pattern, question)
                    if matches:
                        # Filter out common English words that might be mistaken for stock symbols
                        common_words = ['the', 'and', 'for', 'a', 'an', 'in', 'on', 'at', 'to', 'is', 'are', 'was', 'were', 'will', 'would', 'can', 'could', 'by']
                        filtered_matches = [match for match in matches if match.lower() not in common_words]
                        if filtered_matches:
                            symbols = filtered_matches
                            break
        
        # Default to a popular stock if no symbol found
        if not symbols:
            return {
                "response_type": "no_symbol",
                "message": "I couldn't identify a specific stock symbol in your question. Please mention a stock symbol like AAPL, MSFT, or TSLA."
            }
            
        symbol = symbols[0].upper()
        
        # Determine the type of question
        if any(keyword in question for keyword in ["congress", "senator", "representative", "political", "politicians", "government officials"]):
            return self.get_congress_trading_info(symbol)
        elif any(keyword in question for keyword in ["insider", "ceo", "executive", "board", "director"]):
            return self.get_insider_info(symbol)
        elif any(keyword in question for keyword in ["reddit", "wallstreetbets", "wsb", "social media", "retail"]):
            return self.get_wallstreetbets_info(symbol)
        elif any(keyword in question for keyword in ["lobby", "lobbying", "political spending", "influence"]):
            return self.get_lobbying_info(symbol)
        elif any(keyword in question for keyword in ["price", "worth", "value", "cost", "trading at"]):
            return self.get_price_info(symbol)
        elif any(keyword in question for keyword in ["company", "what is", "who is", "about", "overview"]):
            return self.get_company_info(symbol)
        elif any(keyword in question for keyword in ["news", "happening", "recent", "development"]):
            return self.get_news_info(symbol)
        elif any(keyword in question for keyword in ["predict", "forecast", "future", "will", "expect", "projection"]):
            return self.get_prediction_info(symbol, question)
        elif any(keyword in question for keyword in ["option", "call", "put", "strike", "expiry"]):
            return self.get_options_info(symbol, question)
        else:
            # General analysis
            return self.get_general_analysis(symbol)
    
    def get_price_info(self, symbol):
        """Get price information for a stock"""
        quote = self.get_stock_quote(symbol)
        
        if "error" in quote:
            return {
                "response_type": "error",
                "message": quote["error"]
            }
            
        price = quote["price"]
        change = quote["change"]
        change_percent = quote["change_percent"]
        
        direction = "up" if float(change) > 0 else "down" if float(change) < 0 else "unchanged"
        
        # Generate TradingView chart link
        tradingview_link = f"https://www.tradingview.com/chart/?symbol={symbol}"
        
        message = f"The current price of {symbol} is ${price}.\n"
        message += f"Today's change: {direction} ${abs(float(change)):.2f} ({change_percent}%).\n\n"
        message += f"View detailed chart on TradingView: {tradingview_link}\n\n"
        message += "You can ask for more information like:\n"
        message += f"- Tell me more about {symbol}\n"
        message += f"- Any recent news for {symbol}?\n"
        message += f"- What's the analysis for {symbol}?"
        
        return {
            "response_type": "price",
            "symbol": symbol,
            "data": quote,
            "message": message
        }
    
    def get_company_info(self, symbol):
        """Get company information"""
        overview = self.get_company_overview(symbol)
        
        if "error" in overview:
            return {
                "response_type": "error",
                "message": overview["error"]
            }
            
        return {
            "response_type": "company",
            "symbol": symbol,
            "data": overview,
            "message": f"{overview.get('Name', symbol)} ({symbol}) is a {overview.get('Sector', 'company')} company in the {overview.get('Industry', '')} industry. {overview.get('Description', '')[:200]}..."
        }
    
    def get_news_info(self, symbol):
        """Get news information for a stock"""
        news = self.get_stock_news(symbol=symbol)
        
        if "error" in news:
            return {
                "response_type": "error",
                "message": news["error"]
            }
            
        news_items = []
        if "feed" in news:
            for item in news["feed"][:3]:  # Get top 3 news items
                news_items.append({
                    "title": item.get("title", ""),
                    "summary": item.get("summary", ""),
                    "url": item.get("url", ""),
                    "time_published": item.get("time_published", ""),
                    "sentiment": item.get("overall_sentiment_label", "")
                })
                
        return {
            "response_type": "news",
            "symbol": symbol,
            "data": news_items,
            "message": f"Here are the latest news for {symbol}:\n" + "\n".join([
                f"- {item['title']} (Sentiment: {item['sentiment']})" for item in news_items
            ]) if news_items else f"No recent news found for {symbol}"
        }
        
    def get_congress_trading_info(self, symbol):
        """Get congressional trading information for a stock"""
        congress_data = self.get_congress_trading(symbol)
        
        if "error" in congress_data:
            return {
                "response_type": "error",
                "message": congress_data["error"]
            }
            
        # Format the response
        trades = congress_data[:5] if isinstance(congress_data, list) else []
        
        if not trades:
            return {
                "response_type": "congress",
                "symbol": symbol,
                "message": f"No recent congressional trading activity found for {symbol}."
            }
            
        message = f"Recent congressional trading activity for {symbol}:\n"
        for trade in trades:
            message += f"- {trade.get('Representative', 'Unknown')} ({trade.get('Party', '')}): {trade.get('Transaction', '')} "
            message += f"${trade.get('Amount', 'Unknown')} on {trade.get('Date', 'Unknown')}\n"
            
        return {
            "response_type": "congress",
            "symbol": symbol,
            "data": trades,
            "message": message
        }
        
    def get_insider_info(self, symbol):
        """Get insider trading information for a stock"""
        insider_data = self.get_insider_trading(symbol)
        
        if "error" in insider_data:
            return {
                "response_type": "error",
                "message": insider_data["error"]
            }
            
        # Format the response
        trades = insider_data[:5] if isinstance(insider_data, list) else []
        
        if not trades:
            return {
                "response_type": "insider",
                "symbol": symbol,
                "message": f"No recent insider trading activity found for {symbol}."
            }
            
        message = f"Recent insider trading activity for {symbol}:\n"
        for trade in trades:
            message += f"- {trade.get('Name', 'Unknown')} ({trade.get('Position', '')}): {trade.get('TransactionType', '')} "
            message += f"{trade.get('Shares', '0')} shares at ${trade.get('Price', '0')} on {trade.get('Date', 'Unknown')}\n"
            
        return {
            "response_type": "insider",
            "symbol": symbol,
            "data": trades,
            "message": message
        }
        
    def get_wallstreetbets_info(self, symbol):
        """Get WallStreetBets discussion information for a stock"""
        wsb_data = self.get_wallstreetbets_data(symbol)
        
        if "error" in wsb_data:
            return {
                "response_type": "error",
                "message": wsb_data["error"]
            }
            
        # Format the response
        mentions = wsb_data[:5] if isinstance(wsb_data, list) else []
        
        if not mentions:
            return {
                "response_type": "wallstreetbets",
                "symbol": symbol,
                "message": f"No recent WallStreetBets discussion found for {symbol}."
            }
            
        message = f"Recent WallStreetBets discussion for {symbol}:\n"
        for mention in mentions:
            message += f"- {mention.get('Date', 'Unknown')}: {mention.get('Mentions', '0')} mentions\n"
            
        return {
            "response_type": "wallstreetbets",
            "symbol": symbol,
            "data": mentions,
            "message": message
        }
        
    def get_lobbying_info(self, symbol):
        """Get lobbying information for a stock"""
        lobbying_data = self.get_lobbying_data(symbol)
        
        if "error" in lobbying_data:
            return {
                "response_type": "error",
                "message": lobbying_data["error"]
            }
            
        # Format the response
        lobbying = lobbying_data[:5] if isinstance(lobbying_data, list) else []
        
        if not lobbying:
            return {
                "response_type": "lobbying",
                "symbol": symbol,
                "message": f"No recent lobbying activity found for {symbol}."
            }
            
        message = f"Recent lobbying activity for {symbol}:\n"
        for activity in lobbying:
            message += f"- {activity.get('Date', 'Unknown')}: ${activity.get('Amount', '0')} "
            message += f"on {activity.get('Issue', 'Unknown')}\n"
            
        return {
            "response_type": "lobbying",
            "symbol": symbol,
            "data": lobbying,
            "message": message
        }
    
    def get_personal_option_info(self, symbol, option_type, strike_price, expiry_date, question):
        """Analyze personal option position based on user input"""
        # First get current stock price
        quote = self.get_stock_quote(symbol)
        
        if "error" in quote:
            return {
                "response_type": "error",
                "message": f"Error retrieving current price for {symbol}: {quote['error']}"
            }
        
        current_price = float(quote["price"])
        
        # Format the expiry date nicely for display
        formatted_date = expiry_date
        if isinstance(expiry_date, tuple) or isinstance(expiry_date, list):
            # Handle different date patterns based on the tuple structure
            if len(expiry_date) == 2:  # Format like (21, 2025) for "21 mar 2025"
                day, year = expiry_date
                # Here we're making an assumption about the month from context
                # In a real implementation, we would parse this more carefully
                month_match = re.search(r'(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*', question.lower())
                month = month_match.group(0) if month_match else "mar"  # Default if not found
                formatted_date = f"{day} {month} {year}"
            elif len(expiry_date) == 3:  # Format like (3, 21, 25) for MM/DD/YY
                # For simplicity assuming US date format where applicable
                if int(expiry_date[0]) <= 12:  # Likely MM/DD/YY
                    month, day, year = expiry_date
                    formatted_date = f"{month}/{day}/{year}" 
                else:  # Likely DD/MM/YY or YYYY/MM/DD
                    if int(expiry_date[0]) > 1000:  # YYYY/MM/DD
                        year, month, day = expiry_date
                    else:  # DD/MM/YY
                        day, month, year = expiry_date
                    formatted_date = f"{day}/{month}/{year}"
        # At this point, if formatted_date is still a tuple/list, convert it to string
        if isinstance(formatted_date, (tuple, list)):
            formatted_date = " ".join(str(x) for x in formatted_date)
        
        # Get absolute strike price from string
        try:
            strike_price = float(strike_price)
        except ValueError:
            strike_price = 0  # Default if we couldn't parse it
        
        # Determine if option is in the money or out of the money
        if option_type == "call":
            status = "in the money" if current_price > strike_price else "out of the money"
            needed_movement = abs(strike_price - current_price)
            direction = "fall" if current_price > strike_price else "rise"
        else:  # put
            status = "in the money" if current_price < strike_price else "out of the money"
            needed_movement = abs(strike_price - current_price)
            direction = "rise" if current_price < strike_price else "fall"
        
        # Create a TradingView link
        tradingview_link = self.get_tradingview_chart_url(symbol)
        
        # Check if this is a prediction question (will it be profitable)
        if re.search(r'will.*profitable|profit|make money|gain', question, re.IGNORECASE):
            # Get company overview for additional insights
            overview = self.get_company_overview(symbol)
            
            message = f"Analysis of your {symbol} ${strike_price} {option_type} option expiring on {formatted_date}:\n\n"
            message += f"Current {symbol} price: ${current_price:.2f}\n"
            message += f"Strike price: ${strike_price:.2f}\n"
            message += f"Status: Currently {status}\n\n"
            
            if option_type == "call":
                message += f"For your call option to be profitable at expiration, {symbol} needs to be above ${strike_price:.2f}. "
                if status == "in the money":
                    message += f"It's currently ${(current_price - strike_price):.2f} in the money.\n\n"
                else:
                    message += f"It needs to rise at least ${(strike_price - current_price):.2f} (or {((strike_price - current_price)/current_price*100):.1f}%) from the current price.\n\n"
            else:  # put
                message += f"For your put option to be profitable at expiration, {symbol} needs to be below ${strike_price:.2f}. "
                if status == "in the money":
                    message += f"It's currently ${(strike_price - current_price):.2f} in the money.\n\n"
                else:
                    message += f"It needs to fall at least ${(current_price - strike_price):.2f} (or {((current_price - strike_price)/current_price*100):.1f}%) from the current price.\n\n"
            
            # Add insights based on company fundamentals if available
            if "error" not in overview:
                pe_ratio = overview.get("PERatio", "N/A")
                eps = overview.get("EPS", "N/A")
                
                message += "Key factors that might influence this stock by your expiration date:\n"
                
                if pe_ratio != "N/A" and float(pe_ratio) > 40:
                    message += f"- The stock has a high P/E ratio of {pe_ratio}, suggesting high growth expectations\n"
                elif pe_ratio != "N/A" and float(pe_ratio) < 15:
                    message += f"- The stock has a relatively low P/E ratio of {pe_ratio}, which could indicate it's undervalued\n"
                    
                message += f"- Earnings per share (EPS): ${eps}\n"
                message += f"- Recent news and upcoming earnings reports could significantly impact the stock price\n"
                message += f"- Market volatility and broader economic factors will also play a role\n\n"
            
            message += "Important considerations:\n"
            message += "- Options can lose value due to time decay (theta) even if the stock price doesn't change\n"
            message += "- Implied volatility changes can affect option pricing before expiration\n"
            message += f"- The break-even price at expiration is approximately ${(strike_price + 0):.2f} (excluding the premium you paid)\n\n"
            
            message += f"View the latest {symbol} chart on TradingView: {tradingview_link}\n\n"
            message += "Remember that stock movements are unpredictable, and this analysis is for educational purposes only."
            
            return {
                "response_type": "personal_option",
                "symbol": symbol,
                "option_type": option_type,
                "strike_price": strike_price,
                "expiry_date": formatted_date,
                "current_price": current_price,
                "status": status,
                "message": message
            }
        
        # Standard option analysis (not specifically asking about profitability)
        message = f"Your {symbol} ${strike_price} {option_type} option expiring on {formatted_date}:\n\n"
        message += f"Current {symbol} price: ${current_price:.2f}\n"
        message += f"Strike price: ${strike_price:.2f}\n"
        message += f"Status: Currently {status}\n"
        
        if option_type == "call":
            message += f"For this call option to be in the money at expiration, {symbol} needs to be above ${strike_price:.2f}.\n"
        else:  # put
            message += f"For this put option to be in the money at expiration, {symbol} needs to be below ${strike_price:.2f}.\n"
        
        message += f"\nView the latest {symbol} chart: {tradingview_link}"
        
        return {
            "response_type": "personal_option",
            "symbol": symbol,
            "option_type": option_type,
            "strike_price": strike_price,
            "expiry_date": formatted_date,
            "current_price": current_price,
            "status": status,
            "message": message
        }
    
    def get_prediction_info(self, symbol, question):
        """
        Get prediction information
        Note: This is a simplified version and doesn't actually predict stock prices
        """
        quote = self.get_stock_quote(symbol)
        
        if "error" in quote:
            return {
                "response_type": "error",
                "message": quote["error"]
            }
            
        # Try to extract specific price targets from the question
        price_target_match = re.search(r'\$(\d+)', question)
        time_frame_match = re.search(r'(by|before|until)\s+(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\s+\d{1,2},?\s+\d{4}', question) or \
                         re.search(r'in\s+(\d+)\s+(day|week|month|year)s?', question)
        
        current_price = quote["price"]
        company_overview = self.get_company_overview(symbol)
        company_name = company_overview.get("Name", symbol) if not "error" in company_overview else symbol
        
        # Generate TradingView chart link with technical indicators
        tradingview_link = f"https://www.tradingview.com/chart/?symbol={symbol}&studies=RSI@tv-basicstudies,MACD@tv-basicstudies,BB@tv-basicstudies"
        
        if price_target_match:
            price_target = float(price_target_match.group(1))
            price_change = price_target - float(current_price)
            percent_change = (price_change / float(current_price)) * 100
            
            if time_frame_match:
                time_frame = time_frame_match.group(0)
                message = f"You're asking if {company_name} ({symbol}) will reach ${price_target:.2f} {time_frame}.\n\n"
            else:
                message = f"You're asking if {company_name} ({symbol}) will reach ${price_target:.2f}.\n\n"
            
            message += f"Current price: ${current_price}\n"
            message += f"Target price: ${price_target:.2f}\n"
            message += f"Required change: ${abs(price_change):.2f} ({abs(percent_change):.2f}% {'increase' if price_change > 0 else 'decrease'})\n\n"
            
            # Add a brief analysis based on the size of the move
            if price_change > 0:
                if percent_change < 5:
                    volatility = "This represents a relatively small movement for most stocks."
                elif percent_change < 20:
                    volatility = "This represents a moderate movement that is certainly possible with the right catalysts."
                else:
                    volatility = "This represents a significant movement that would typically require major news or events."
            else:
                if percent_change > -5:
                    volatility = "This represents a relatively small movement for most stocks."
                elif percent_change > -20:
                    volatility = "This represents a moderate movement that is certainly possible with the right catalysts."
                else:
                    volatility = "This represents a significant movement that would typically require major news or events."
            
            message += f"{volatility}\n\n"
        else:
            message = f"Regarding the future price of {company_name} ({symbol}):\n\n"
            message += f"Current price: ${current_price}\n\n"
        
        message += "Important Disclaimer: I cannot predict with certainty whether a stock will reach a specific price target. "
        message += "Stock price movements are influenced by countless factors including company performance, market conditions, economic indicators, and unexpected events.\n\n"
        
        message += "For a more informed perspective, I recommend examining the following:\n"
        message += f"- View technical indicators on TradingView: {tradingview_link}\n"
        message += "- Review recent analyst price targets and recommendations\n"
        message += "- Examine upcoming company events (earnings reports, product launches)\n"
        message += "- Consider overall market trends and economic conditions\n"
        message += "- Consult with a financial advisor for personalized investment advice"
        
        return {
            "response_type": "prediction",
            "symbol": symbol,
            "data": {
                "current_price": current_price,
                "target_price": price_target if price_target_match else None,
                "time_frame": time_frame_match.group(0) if time_frame_match else None
            },
            "message": message
        }
    
    def get_options_info(self, symbol, question):
        """
        Get options information
        Note: Alpha Vantage free tier doesn't provide options data
        """
        # Extract potential strike prices and expiry dates from the question
        strike_match = re.search(r'\$(\d+)', question)
        expiry_match = re.search(r'(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\s+\d{1,2},?\s+\d{4}', question)
        option_type = "call" if "call" in question.lower() else "put" if "put" in question.lower() else None
        
        strike_price = strike_match.group(1) if strike_match else None
        expiry_date = expiry_match.group(0) if expiry_match else None
        
        # Get current stock price for context
        quote = self.get_stock_quote(symbol)
        if "error" in quote:
            return {
                "response_type": "error",
                "message": quote["error"]
            }
            
        current_price = quote["price"]
        
        # Craft a response based on what we could extract
        message = f"Regarding {symbol} options"
        if option_type:
            message += f" ({option_type}s)"
        if strike_price:
            message += f" with strike price ${strike_price}"
        if expiry_date:
            message += f" expiring around {expiry_date}"
        message += ":\n\n"
        
        message += f"{symbol} is currently trading at ${current_price:.2f}.\n\n"
        
        if strike_price and option_type:
            strike_price_float = float(strike_price)
            if option_type == "call":
                if current_price < strike_price_float:
                    upside_needed = ((strike_price_float - current_price) / current_price) * 100
                    message += f"To reach the strike price of ${strike_price}, {symbol} would need to increase by ${strike_price_float - current_price:.2f} ({upside_needed:.2f}%).\n\n"
                else:
                    message += f"This option is currently in the money by ${current_price - strike_price_float:.2f}.\n\n"
            else:  # put
                if current_price > strike_price_float:
                    downside_needed = ((current_price - strike_price_float) / current_price) * 100
                    message += f"To reach the strike price of ${strike_price}, {symbol} would need to decrease by ${current_price - strike_price_float:.2f} ({downside_needed:.2f}%).\n\n"
                else:
                    message += f"This option is currently in the money by ${strike_price_float - current_price:.2f}.\n\n"
        
        message += "I don't have direct access to options pricing data with the current API. For detailed options information, including prices, Greeks, open interest, and implied volatility, you might want to check your brokerage platform or a specialized options analysis tool."
            
        return {
            "response_type": "options",
            "symbol": symbol,
            "message": message
        }
    
    def get_general_analysis(self, symbol):
        """Get general analysis for a stock"""
        quote = self.get_stock_quote(symbol)
        overview = self.get_company_overview(symbol)
        
        if "error" in quote:
            return {
                "response_type": "error",
                "message": quote["error"]
            }
            
        current_price = quote["price"]
        company_name = overview.get("Name", symbol) if "error" not in overview else symbol
        
        # Basic technical analysis indicators
        if "error" not in overview:
            pe_ratio = overview.get("PERatio", "N/A")
            eps = overview.get("EPS", "N/A")
            dividend_yield = overview.get("DividendYield", "N/A")
            fifty_two_week_high = overview.get("52WeekHigh", "N/A")
            fifty_two_week_low = overview.get("52WeekLow", "N/A")
            sector = overview.get("Sector", "N/A")
            industry = overview.get("Industry", "N/A")
        else:
            pe_ratio = eps = dividend_yield = fifty_two_week_high = fifty_two_week_low = sector = industry = "N/A"
        
        # Generate TradingView chart links
        tradingview_chart = f"https://www.tradingview.com/chart/?symbol={symbol}"
        tradingview_ideas = f"https://www.tradingview.com/symbols/{symbol}/ideas/"
        
        message = f"Analysis for {company_name} ({symbol}) at ${current_price}:\n\n"
        
        if "error" not in overview:
            message += f"Sector: {sector}\n"
            message += f"Industry: {industry}\n"
            message += f"P/E Ratio: {pe_ratio}\n"
            message += f"EPS: {eps}\n"
            message += f"Dividend Yield: {dividend_yield}\n"
            message += f"52-Week Range: ${fifty_two_week_low} - ${fifty_two_week_high}\n\n"
        
        message += "Technical Analysis Resources:\n"
        message += f"- View interactive chart: {tradingview_chart}\n"
        message += f"- See trading ideas from TradingView users: {tradingview_ideas}\n\n"
        
        message += "For more specific information, you can ask:\n"
        message += f"- What's the news for {symbol}?\n"
        message += f"- Any insider trading for {symbol}?\n"
        message += f"- Tell me about {symbol} options"
        
        return {
            "response_type": "analysis",
            "symbol": symbol,
            "data": {
                "price_data": quote,
                "company_data": overview if "error" not in overview else None
            },
            "message": message
        }

    def get_option_profitability(self, symbol, option_type, strike_price, expiry_date, question):
        """
        Analyze potential profitability of an option
        """
        # Get the current stock price
        quote = self.get_stock_quote(symbol)
        
        if "error" in quote:
            return {
                "response_type": "error",
                "message": quote["error"]
            }
            
        current_price = quote["price"]
        
        # Get company overview for additional context
        overview = self.get_company_overview(symbol)
        company_name = overview.get("Name", symbol) if not "error" in overview else symbol
        
        # Prepare the strike price information
        if strike_price == "unknown":
            message = f"To properly assess the profitability of a {symbol} {option_type} option, I need more details:\n\n"
            message += "1. What is the strike price of the option?\n"
            message += "2. What is the expiration date?\n"
            message += "3. What was the premium paid for the option?\n\n"
            message += f"Currently, {company_name} ({symbol}) is trading at ${current_price:.2f}."
            
            return {
                "response_type": "option_profitability",
                "symbol": symbol,
                "message": message
            }
            
        # Convert strike price to number
        strike_price = int(strike_price)
        
        # Calculate basic metrics for the option
        if option_type == "call":
            in_the_money = current_price > strike_price
            distance_from_strike = abs(current_price - strike_price)
            percentage_from_strike = (distance_from_strike / strike_price) * 100
            direction_needed = "rise" if current_price < strike_price else "stay above"
            
            message = f"Regarding the profitability of a {symbol} ${strike_price} {option_type} option"
            if expiry_date != "unknown":
                message += f" expiring {expiry_date}"
            message += ":\n\n"
            
            message += f"{company_name} ({symbol}) is currently trading at ${current_price:.2f}, "
            if in_the_money:
                message += f"which is ${distance_from_strike:.2f} ({percentage_from_strike:.2f}%) above your strike price of ${strike_price}.\n\n"
                message += "This option is currently in-the-money. "
            else:
                message += f"which is ${distance_from_strike:.2f} ({percentage_from_strike:.2f}%) below your strike price of ${strike_price}.\n\n"
                message += "This option is currently out-of-the-money. "
                
            message += f"For your option to be profitable at expiration, {symbol} would need to {direction_needed} the strike price of ${strike_price} by enough to offset the premium you paid.\n\n"
            
        else:  # put
            in_the_money = current_price < strike_price
            distance_from_strike = abs(current_price - strike_price)
            percentage_from_strike = (distance_from_strike / strike_price) * 100
            direction_needed = "fall" if current_price > strike_price else "stay below"
            
            message = f"Regarding the profitability of a {symbol} ${strike_price} {option_type} option"
            if expiry_date != "unknown":
                message += f" expiring {expiry_date}"
            message += ":\n\n"
            
            message += f"{company_name} ({symbol}) is currently trading at ${current_price:.2f}, "
            if in_the_money:
                message += f"which is ${distance_from_strike:.2f} ({percentage_from_strike:.2f}%) below your strike price of ${strike_price}.\n\n"
                message += "This option is currently in-the-money. "
            else:
                message += f"which is ${distance_from_strike:.2f} ({percentage_from_strike:.2f}%) above your strike price of ${strike_price}.\n\n"
                message += "This option is currently out-of-the-money. "
                
            message += f"For your option to be profitable at expiration, {symbol} would need to {direction_needed} the strike price of ${strike_price} by enough to offset the premium you paid.\n\n"
            
        # General options education
        message += "Factors that affect option profitability:\n\n"
        message += "1. **Price Movement**: How much the underlying stock price moves (and in which direction)\n"
        message += "2. **Time Decay**: Options lose value as they approach expiration (theta decay)\n"
        message += "3. **Implied Volatility**: Changes in market volatility can significantly impact option prices\n"
        message += "4. **Premium Paid**: Your break-even point is determined by the premium you paid\n\n"
        
        message += "Since I don't have access to options pricing data or your entry price, I can't calculate the exact break-even point or probability of profit. For precise analysis, consider using your brokerage platform's tools or options calculators that incorporate current pricing data."
        
        return {
            "response_type": "option_profitability",
            "symbol": symbol,
            "data": {
                "current_price": current_price,
                "strike_price": strike_price,
                "option_type": option_type,
                "expiry": expiry_date,
                "in_the_money": in_the_money
            },
            "message": message
        }
        
    def get_option_recommendations(self, symbol, budget, question):
        """
        Provide educated options recommendations based on user's budget and market context
        """
        # Get the current stock price
        quote = self.get_stock_quote(symbol)
        
        if "error" in quote:
            return {
                "response_type": "error",
                "message": quote["error"]
            }
            
        current_price = quote["price"]
        
        # Get company overview for additional context
        overview = self.get_company_overview(symbol)
        company_name = overview.get("Name", symbol) if not "error" in overview else symbol
        
        # Create budget string if available
        budget_str = f" with a budget of ${budget}" if budget else ""
        
        message = f"Regarding options recommendations for {company_name} ({symbol}){budget_str}:\n\n"
        message += f"{symbol} is currently trading at ${current_price:.2f}.\n\n"
        
        # Educational content about option selection
        message += "When selecting options, consider these key factors:\n\n"
        
        message += "1. **Strike Price Selection**:\n"
        message += f"   - At-the-money (ATM): Strike price near the current price (around ${current_price:.2f})\n"
        message += f"   - In-the-money (ITM): For calls, strikes below ${current_price:.2f}; for puts, strikes above ${current_price:.2f}\n"
        message += f"   - Out-of-the-money (OTM): For calls, strikes above ${current_price:.2f}; for puts, strikes below ${current_price:.2f}\n\n"
        
        message += "2. **Expiration Timeline**:\n"
        message += "   - Short-term (weekly/monthly): Higher risk, lower cost, faster time decay\n"
        message += "   - Medium-term (3-6 months): Balanced approach, moderates time decay\n"
        message += "   - LEAPS (>6 months): Lower risk, higher cost, more time for your thesis to play out\n\n"
        
        message += "3. **Strategy Selection Based on Market Outlook**:\n"
        message += "   - Bullish: Consider call options or bull call spreads\n"
        message += "   - Bearish: Consider put options or bear put spreads\n"
        message += "   - Neutral: Consider iron condors or butterfly spreads\n"
        message += "   - Volatile: Consider straddles or strangles\n\n"
        
        message += "4. **Risk Management**:\n"
        message += "   - Only allocate what you can afford to lose (typically 1-5% of portfolio per trade)\n"
        message += "   - Consider using spreads to limit maximum loss\n"
        message += "   - Have clear exit points for both profit taking and loss management\n\n"
        
        message += "Unfortunately, I can't provide specific strike prices or option contracts without current options chain data. For personalized recommendations, I suggest:\n\n"
        
        message += "1. Check your brokerage platform for current option chains with pricing\n"
        message += "2. Look for options with adequate liquidity (open interest >100, tight bid-ask spreads)\n"
        message += "3. Consider implied volatility (IV) - high IV makes options more expensive\n"
        message += f"4. Calculate your break-even point (for calls: strike price + premium; for puts: strike price - premium)\n\n"
        
        message += "Remember that options trading involves significant risk and isn't suitable for all investors. Consider consulting with a financial advisor before making investment decisions."
        
        return {
            "response_type": "option_recommendations",
            "symbol": symbol,
            "data": {
                "current_price": current_price,
                "budget": budget
            },
            "message": message
        }

def main():
    print("\n=== Stock Advisor - Your Intelligent Trading Assistant ===\n")
    print("Ask me questions about stocks, market trends, or company information.")
    print("Examples:")
    print("- What is the current price of AAPL?")
    print("- Tell me about Tesla stock")
    print("- What's the latest news for MSFT?")
    print("- Give me an analysis of AMZN")
    print("- Show me a chart for TSLA")
    print("- What government contracts does LMT have?")
    print("- What's the short volume for GME?")
    print("- How many Wikipedia page views does MSFT have?")
    print("- Any insider trading for NVDA?")
    print("- Have any congress members traded GOOGL?")
    print("- Will my TSLA $440 call option be profitable?")
    print("- Which options should I buy for AAPL with $1000?")
    print("\nType 'exit' to quit.\n")
    
    advisor = StockAdvisor()
    
    # Check if Quiver API is available
    if not advisor.quiver_enabled:
        print("\nNote: Quiver Quantitative API not configured or package not installed. Some features will be limited.")
        
        missing_package = not QUIVER_AVAILABLE
        missing_api_key = advisor.quiver_api_key == ""
        missing_dotenv = not globals().get('ENV_LOADED', False)
        
        if missing_package:
            print("To enable Quiver Quantitative features:")
            print("1. Install the required packages:")
            print("   pip install quiverquant pandas python-dotenv")
            
        if missing_api_key:
            print("\nTo access congressional trading, insider transactions, and more:")
            print("1. Get an API key from: https://api.quiverquant.com/")
            print("2. Set your API key using ONE of these methods:")
            print("   a) Create/edit .env file in the project directory with:")
            print("      QUIVER_API_KEY=your_key_here")
            print("   b) Set environment variable:")
            print("      export QUIVER_API_KEY='your_key_here'")
            
        if missing_dotenv and not missing_package:
            print("\nNote: python-dotenv is not installed, so .env file cannot be loaded.")
            print("To use .env file for configuration:")
            print("   pip install python-dotenv")
            
        print("")
    
    while True:
        question = input("\nWhat would you like to know? ").strip()
        
        if question.lower() in ['exit', 'quit', 'q']:
            print("\nThank you for using Stock Advisor!")
            break
            
        if not question:
            continue
            
        print("\nAnalyzing your question...")
        result = advisor.analyze_question(question)
        
        # Store last response for context in chart opening
        advisor.last_response = result
        
        if result["response_type"] == "error":
            print(f"\nError: {result['message']}")
        else:
            print(f"\n{result['message']}")
            
            # Offer to open news URLs if available
            if result["response_type"] == "news" and "data" in result and result["data"]:
                open_news = input("\nWould you like to open any of these news articles? (y/n): ").lower()
                if open_news == 'y':
                    for i, item in enumerate(result["data"]):
                        print(f"{i+1}. {item['title']}")
                    
                    choice = input("\nEnter the number of the article to open (or 0 to skip): ")
                    try:
                        choice = int(choice)
                        if 1 <= choice <= len(result["data"]):
                            webbrowser.open(result["data"][choice-1]["url"])
                            print(f"Opening {result['data'][choice-1]['title']}...")
                    except ValueError:
                        pass

if __name__ == "__main__":
    main() 