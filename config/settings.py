"""
Global settings and configuration for the stock trading system.
These settings will be version controlled and shared across devices.
"""

import os
from pathlib import Path

# Base Paths
BASE_DIR = Path(__file__).resolve().parent.parent
CONFIG_DIR = BASE_DIR / 'config'
DATA_DIR = BASE_DIR / 'data'

# Create necessary directories if they don't exist
os.makedirs(DATA_DIR, exist_ok=True)

# Trading Parameters
TRADING_SETTINGS = {
    'default_position_size': 100,  # Default position size in dollars
    'max_position_size': 1000,    # Maximum position size in dollars
    'stop_loss_percentage': 2.0,  # Default stop loss percentage
    'take_profit_percentage': 5.0 # Default take profit percentage
}

# Technical Analysis Settings
TECHNICAL_ANALYSIS = {
    'default_ma_periods': [20, 50, 200],  # Moving average periods
    'rsi_period': 14,                     # RSI calculation period
    'volume_ma_period': 20,               # Volume moving average period
    'bollinger_band_period': 20,          # Bollinger Bands period
    'bollinger_band_std': 2               # Number of standard deviations for Bollinger Bands
}

# Risk Management Rules
RISK_MANAGEMENT = {
    'max_daily_loss': 3.0,        # Maximum daily loss percentage
    'max_position_risk': 1.0,     # Maximum risk per position percentage
    'max_correlated_positions': 3 # Maximum number of correlated positions
}

# Data Sources Configuration
DATA_SOURCES = {
    'primary': 'alpha_vantage',    # Primary data source
    'secondary': 'yfinance',       # Backup data source
    'alternative': 'quiver_quant', # Alternative data source
    'real_time': 'thinkorswim'    # Real-time data source (when available)
}

# Notification Settings
NOTIFICATIONS = {
    'enabled': True,
    'price_alerts': True,
    'trade_alerts': True,
    'risk_alerts': True,
    'email_notifications': False  # Set to True when email is configured
}

# Logging Configuration
LOGGING = {
    'level': 'INFO',
    'log_trades': True,
    'log_alerts': True,
    'log_file': str(DATA_DIR / 'trading.log')
}

# Strategy Parameters
STRATEGY_PARAMS = {
    'trend_following': {
        'enabled': True,
        'ma_cross_periods': [9, 21],
        'minimum_trend_strength': 25
    },
    'mean_reversion': {
        'enabled': True,
        'lookback_period': 20,
        'std_dev_threshold': 2.0
    },
    'momentum': {
        'enabled': True,
        'rsi_oversold': 30,
        'rsi_overbought': 70
    }
}

# Watchlist Configuration
DEFAULT_WATCHLIST = [
    'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META',
    'NVDA', 'TSLA', 'JPM', 'V', 'WMT'
]

# Scanner Settings
SCANNER_SETTINGS = {
    'volume_min': 500000,         # Minimum daily volume
    'price_min': 5.0,            # Minimum price
    'market_cap_min': 1000000000 # Minimum market cap in dollars
}

def get_setting(category, key):
    """
    Retrieve a specific setting value.
    
    Args:
        category (str): The settings category (e.g., 'TRADING_SETTINGS')
        key (str): The specific setting key
        
    Returns:
        The setting value if found, None otherwise
    """
    return globals().get(category, {}).get(key)

def update_setting(category, key, value):
    """
    Update a specific setting value.
    
    Args:
        category (str): The settings category (e.g., 'TRADING_SETTINGS')
        key (str): The specific setting key
        value: The new value
    """
    if category in globals() and isinstance(globals()[category], dict):
        globals()[category][key] = value 