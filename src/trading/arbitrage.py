from datetime import datetime
from exchanges.binance_client import BinanceHandler
from exchanges.kucoin_client import KuCoinHandler
from trading.position import PositionManager
from reporting.trade_logger import TradeLogger
from config.settings import ARBITRAGE_THRESHOLD
from utils.logger import logger

class ArbitrageTrader:
    """
    A class to represent an arbitrage trader that checks for arbitrage opportunities
    between Binance and KuCoin exchanges and executes trades accordingly.
    Attributes
    ----------
    binance : BinanceHandler
        An instance of BinanceHandler to interact with Binance exchange.
    kucoin : KuCoinHandler
        An instance of KuCoinHandler to interact with KuCoin exchange.
    position_manager : PositionManager
        An instance of PositionManager to manage trading positions.
    trade_logger : TradeLogger
        An instance of TradeLogger to log trade details.
    Methods
    -------
    check_arbitrage_opportunity(binance_price, kucoin_price, threshold=ARBITRAGE_THRESHOLD):
        Checks if there is an arbitrage opportunity based on the price difference
        between Binance and KuCoin exchanges.
    execute_trade():
        Executes a trade if an arbitrage opportunity is detected, logs the trade,
        and handles stop-loss conditions.
    """
    def __init__(self):
        logger.info("🔧 Initializing ArbitrageTrader...")
        self.binance = BinanceHandler()
        self.kucoin = KuCoinHandler()
        self.position_manager = PositionManager()
        self.trade_logger = TradeLogger()
        logger.info("✅ ArbitrageTrader initialized successfully")

    def check_arbitrage_opportunity(self, binance_price, kucoin_price, threshold=ARBITRAGE_THRESHOLD):
        logger.info(f"🔍 Checking arbitrage opportunity...")
        logger.info(f"   Binance BTC Price: ${binance_price}")
        logger.info(f"   KuCoin BTC Price: ${kucoin_price}")
        
        if not all([binance_price, kucoin_price]):
            logger.warning("❌ Missing price data from one or both exchanges")
            return False
        
        difference = abs(binance_price - kucoin_price)
        logger.info(f"   Price Difference: ${difference:.2f}")
        logger.info(f"   Threshold: ${threshold}")
        
        if difference >= threshold:
            logger.info(f"🎯 ARBITRAGE OPPORTUNITY DETECTED!")
            logger.info(f"   Binance: ${binance_price}, KuCoin: ${kucoin_price}")
            logger.info(f"   Difference: ${difference:.2f} (>= ${threshold})")
            return True
        
        logger.info(f"⏳ No arbitrage opportunity (difference ${difference:.2f} < threshold ${threshold})")
        return False

    def execute_trade(self, dry_run=False, return_data=False):
        logger.info("=" * 50)
        logger.info(f"🔄 Starting trade execution (DRY RUN: {dry_run})")
        logger.info("=" * 50)
        
        try:
            # Fetch current prices
            logger.info("📊 Fetching current BTC prices...")
            binance_price = self.binance.get_btc_price()
            kucoin_price = self.kucoin.get_btc_price()

            if not all([binance_price, kucoin_price]):
                logger.error("❌ Failed to fetch prices from one or both exchanges")
                logger.error(f"   Binance: {binance_price}")
                logger.error(f"   KuCoin: {kucoin_price}")
                return None if return_data else None

            # Check for arbitrage opportunity
            if self.check_arbitrage_opportunity(binance_price, kucoin_price):
                logger.info("💰 Calculating position size and potential profit...")
                quantity = self.position_manager.calculate_position_size()
                profit = self.position_manager.calculate_profit(
                    binance_price, kucoin_price, quantity)
                
                logger.info(f"   Position Size: {quantity} BTC")
                logger.info(f"   Potential Profit: ${profit:.2f}")

                if self.position_manager.check_stop_loss(profit):
                    logger.warning(f"🛑 Stop-loss triggered! Profit: ${profit:.2f}")
                    return None if return_data else None

                # Determine trading direction
                if binance_price > kucoin_price:
                    logger.info("📈 Strategy: Buy on KuCoin, Sell on Binance")
                    logger.info("🔍 Checking balances...")
                    
                    kucoin_usdt_balance = self.kucoin.check_usdt_balance()
                    binance_btc_balance = self.binance.check_balance()
                    
                    logger.info(f"   KuCoin USDT Balance: ${kucoin_usdt_balance:.2f}")
                    logger.info(f"   Binance BTC Balance: {binance_btc_balance:.8f}")
                    logger.info(f"   Required USDT: ${kucoin_price * quantity:.2f}")
                    logger.info(f"   Required BTC: {quantity:.8f}")
                    
                    if kucoin_usdt_balance < kucoin_price * quantity:
                        logger.error(f"❌ Insufficient USDT on KuCoin (${kucoin_usdt_balance:.2f} < ${kucoin_price * quantity:.2f})")
                        return None if return_data else None
                    if binance_btc_balance < quantity:
                        logger.error(f"❌ Insufficient BTC on Binance ({binance_btc_balance:.8f} < {quantity:.8f})")
                        return None if return_data else None
                    
                    if not dry_run:
                        logger.info("🚀 Executing trades...")
                        buy_result = self.kucoin.place_buy_order('BTC/USDT', quantity)
                        sell_result = self.binance.place_sell_order('BTCUSDT', quantity)
                        logger.info(f"   Buy on KuCoin: {buy_result}")
                        logger.info(f"   Sell on Binance: {sell_result}")
                    else:
                        logger.info("🧪 [DRY RUN] Simulated buy on KuCoin and sell on Binance")
                else:
                    logger.info("📉 Strategy: Buy on Binance, Sell on KuCoin")
                    logger.info("🔍 Checking balances...")
                    
                    binance_usdt_balance = self.binance.check_usdt_balance()
                    kucoin_btc_balance = self.kucoin.check_balance()
                    
                    logger.info(f"   Binance USDT Balance: ${binance_usdt_balance:.2f}")
                    logger.info(f"   KuCoin BTC Balance: {kucoin_btc_balance:.8f}")
                    logger.info(f"   Required USDT: ${binance_price * quantity:.2f}")
                    logger.info(f"   Required BTC: {quantity:.8f}")
                    
                    if binance_usdt_balance < binance_price * quantity:
                        logger.error(f"❌ Insufficient USDT on Binance (${binance_usdt_balance:.2f} < ${binance_price * quantity:.2f})")
                        return None if return_data else None
                    if kucoin_btc_balance < quantity:
                        logger.error(f"❌ Insufficient BTC on KuCoin ({kucoin_btc_balance:.8f} < {quantity:.8f})")
                        return None if return_data else None
                    
                    if not dry_run:
                        logger.info("🚀 Executing trades...")
                        buy_result = self.binance.place_buy_order('BTCUSDT', quantity)
                        sell_result = self.kucoin.place_sell_order('BTC/USDT', quantity)
                        logger.info(f"   Buy on Binance: {buy_result}")
                        logger.info(f"   Sell on KuCoin: {sell_result}")
                    else:
                        logger.info("🧪 [DRY RUN] Simulated buy on Binance and sell on KuCoin")

                # Log the trade
                logger.info("📝 Logging trade details...")
                trade_data = self.trade_logger.log_trade(
                    datetime.now(), binance_price, kucoin_price, 
                    abs(binance_price - kucoin_price), profit, dry_run=dry_run, return_data=return_data)
                
                logger.info("✅ Trade execution completed successfully")
                if return_data:
                    return trade_data
            else:
                logger.info("⏳ No arbitrage opportunity found, skipping trade execution")
                
        except Exception as e:
            logger.error(f"💥 Error in execute_trade: {e}")
            logger.exception("Full traceback:")
            return None if return_data else None
        
        logger.info("=" * 50)
        logger.info("🔄 Trade execution cycle completed")
        logger.info("=" * 50)

