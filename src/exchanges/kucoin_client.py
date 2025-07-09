import ccxt
from config.settings import KUCOIN_API_KEY, KUCOIN_API_SECRET, KUCOIN_API_PASSPHRASE
from utils.logger import logger

class KuCoinHandler:
    """
    KuCoinHandler class to interact with KuCoin exchange using ccxt library.
    Methods:
        __init__:
            Initializes the KuCoinHandler with API credentials.
        get_btc_price:
            Fetches the current BTC/USDT price from KuCoin.
            Returns:
                float: The last traded price of BTC/USDT.
                None: If an error occurs while fetching the price.
        check_balance:
            Fetches the total BTC balance from KuCoin.
            Returns:
                float: The total BTC balance.
                0.0: If an error occurs while fetching the balance.
        place_sell_order:
            Places a market sell order on KuCoin.
            Parameters:
                symbol (str): The trading pair symbol (e.g., 'BTC/USDT').
                quantity (float): The amount of the asset to sell.
            Returns:
                dict: The order details if the order is successfully placed.
                None: If an error occurs while placing the order.
        place_buy_order:
            Placeholder method for placing a buy order.
    """
    def __init__(self):
        try:
            self.client = ccxt.kucoin({
                'apiKey': KUCOIN_API_KEY,
                'secret': KUCOIN_API_SECRET,
                'password': KUCOIN_API_PASSPHRASE,
            })
            logger.info("KuCoin client initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing KuCoin client: {e}")
            self.client = None

    def _check_client(self):
        """Check if client is available"""
        if self.client is None:
            logger.error("KuCoin client not initialized")
            return False
        return True

    def get_btc_price(self):
        if not self._check_client():
            return None
            
        try:
            ticker = self.client.fetch_ticker('BTC/USDT')
            return float(ticker['last'])
        except Exception as e:
            logger.error(f"Error fetching KuCoin BTC price: {e}")
            return None

    def check_balance(self):
        if not self._check_client():
            return 0.0
            
        try:
            balance = self.client.fetch_balance()
            return balance['total'].get('BTC', 0.0)
        except Exception as e:
            logger.error(f"Error fetching KuCoin balance: {e}")
            return 0.0

    def check_usdt_balance(self):
        if not self._check_client():
            return 0.0
            
        try:
            balance = self.client.fetch_balance()
            return balance['total'].get('USDT', 0.0)
        except Exception as e:
            logger.error(f"Error fetching KuCoin USDT balance: {e}")
            return 0.0

    def place_sell_order(self, symbol, quantity):
        if not self._check_client():
            return None
            
        try:
            order = self.client.create_order(
                symbol=symbol,
                type='market',
                side='sell',
                amount=quantity
            )
            logger.info(f"Sell order placed on KuCoin: {order}")
            return order
        except Exception as e:
            logger.error(f"Error placing sell order on KuCoin: {e}")
            return None

    def place_buy_order(self, symbol, quantity):
        if not self._check_client():
            return None
            
        try:
            order = self.client.create_order(
                symbol=symbol,
                type='market',
                side='buy',
                amount=quantity
            )
            logger.info(f"Buy order placed on KuCoin: {order}")
            return order
        except Exception as e:
            logger.error(f"Error placing buy order on KuCoin: {e}")
            return None

    