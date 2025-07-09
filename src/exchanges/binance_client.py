from binance.client import Client
from config.settings import BINANCE_API_KEY, BINANCE_API_SECRET
from utils.logger import logger

class BinanceHandler:
    """
    A handler class for interacting with the Binance exchange API.

    Methods
    -------
    __init__():
        Initializes the BinanceHandler with API credentials.

    get_btc_price():
        Fetches the current price of BTC in USDT from Binance.

    check_balance():
        Checks the BTC balance in the Binance account.

    place_sell_order(symbol, quantity):
        Places a market sell order on Binance for a given symbol and quantity.
    """
    def __init__(self):
        try:
            # Initialize client without automatic ping to avoid network issues during startup
            self.client = Client(BINANCE_API_KEY, BINANCE_API_SECRET)
            # Test connection only when needed, not during initialization
            logger.info("Binance client initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing Binance client: {e}")
            self.client = None

    def _check_client(self):
        """Check if client is available"""
        if self.client is None:
            logger.error("Binance client not initialized")
            return False
        return True

    def get_btc_price(self):
        if not self._check_client():
            return None
            
        try:
            ticker = self.client.get_symbol_ticker(symbol='BTCUSDT')
            return float(ticker['price'])
        except Exception as e:
            logger.error(f"Error fetching Binance BTC price: {e}")
            return None

    def check_balance(self):
        if not self._check_client():
            return 0.0
            
        try:
            account_info = self.client.get_account()
            btc_balance = next((item for item in account_info['balances'] 
                              if item['asset'] == 'BTC'), None)
            return float(btc_balance['free']) if btc_balance else 0.0
        except Exception as e:
            logger.error(f"Error fetching Binance balance: {e}")
            return 0.0

    def check_usdt_balance(self):
        if not self._check_client():
            return 0.0
            
        try:
            account_info = self.client.get_account()
            usdt_balance = next((item for item in account_info['balances'] 
                              if item['asset'] == 'USDT'), None)
            return float(usdt_balance['free']) if usdt_balance else 0.0
        except Exception as e:
            logger.error(f"Error fetching Binance USDT balance: {e}")
            return 0.0

    def place_sell_order(self, symbol, quantity):
        if not self._check_client():
            return None
            
        try:
            order = self.client.create_order(
                symbol=symbol,
                side='SELL',
                type='MARKET',
                quantity=quantity
            )
            logger.info(f"Sell order placed on Binance: {order}")
            return order
        except Exception as e:
            logger.error(f"Error placing sell order on Binance: {e}")
            return None

    def place_buy_order(self, symbol, quantity):
        if not self._check_client():
            return None
            
        try:
            order = self.client.create_order(
                symbol=symbol,
                side='BUY',
                type='MARKET',
                quantity=quantity
            )
            logger.info(f"Buy order placed on Binance: {order}")
            return order
        except Exception as e:
            logger.error(f"Error placing buy order on Binance: {e}")
            return None
