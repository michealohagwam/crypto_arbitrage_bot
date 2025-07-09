from dotenv import load_dotenv
import os

load_dotenv()

def get_env_var(var_name, default=None):
    value = os.getenv(var_name)
    if value is None:
        if default is not None:
            return default
        raise ValueError(f"Please set the {var_name} environment variable")
    return value

# Exchange API credentials
BINANCE_API_KEY = get_env_var('BINANCE_API_KEY')
BINANCE_API_SECRET = get_env_var('BINANCE_API_SECRET')
KUCOIN_API_KEY = get_env_var('KUCOIN_API_KEY')
KUCOIN_API_SECRET = get_env_var('KUCOIN_API_SECRET')
KUCOIN_API_PASSPHRASE = get_env_var('KUCOIN_API_PASSPHRASE')

# Dashboard configuration
DASHBOARD_SECRET_KEY = get_env_var('DASHBOARD_SECRET_KEY', 'supersecret')

# Trading parameters - Increased intervals for testing
TRADING_CAPITAL = 50
ALLOCATION_PERCENTAGE = 50
ARBITRAGE_THRESHOLD = 10
STOP_LOSS_THRESHOLD = -5
TRADING_INTERVAL = 10  # 10 seconds instead of 5 seconds for testing

# Logging configuration
LOG_LEVEL = get_env_var('LOG_LEVEL', 'INFO')
LOG_FILE = get_env_var('LOG_FILE', 'crypto_arbitrage_bot.log')
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
