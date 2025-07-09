from config.settings import TRADING_CAPITAL, ALLOCATION_PERCENTAGE, STOP_LOSS_THRESHOLD


class PositionManager:
    """
    PositionManager class provides methods to manage trading positions, calculate position size, fees, profit, and check stop loss.
    Methods:
        calculate_position_size(capital=TRADING_CAPITAL, allocation_percentage=ALLOCATION_PERCENTAGE):
            Calculates the position size based on the given capital and allocation percentage.
            Args:
                capital (float): The total trading capital.
                allocation_percentage (float): The percentage of capital to allocate.
            Returns:
                float: The calculated position size.
            Raises:
                ValueError: If allocation_percentage is not between 0 and 100.
        calculate_fees(price, exchange):
            Calculates the trading fees based on the given price and exchange.
            Args:
                price (float): The price of the asset.
                exchange (str): The name of the exchange.
            Returns:
                float: The calculated fee.
        calculate_profit(binance_price, kucoin_price, quantity):
            Calculates the profit from arbitrage trading between Binance and KuCoin.
            Args:
                binance_price (float): The price of the asset on Binance.
                kucoin_price (float): The price of the asset on KuCoin.
                quantity (float): The quantity of the asset being traded.
            Returns:
                float: The calculated profit.
        check_stop_loss(current_profit_loss, threshold=STOP_LOSS_THRESHOLD):
            Checks if the current profit/loss has reached the stop loss threshold.
            Args:
                current_profit_loss (float): The current profit or loss.
                threshold (float): The stop loss threshold.
            Returns:
                bool: True if the current profit/loss is less than or equal to the threshold, False otherwise.
    """
    @staticmethod
    def calculate_position_size(capital=TRADING_CAPITAL, 
                              allocation_percentage=ALLOCATION_PERCENTAGE):
        if allocation_percentage < 0 or allocation_percentage > 100:
            raise ValueError("Allocation percentage should be between 0 and 100.")
        return capital * (allocation_percentage / 100)

    @staticmethod
    def calculate_fees(price, exchange):
        fee_rate = 0.001  # 0.1% fee
        return price * fee_rate

    @staticmethod
    def calculate_profit(binance_price, kucoin_price, quantity):
        if binance_price > kucoin_price:
            # Binance is more expensive: Buy on KuCoin, Sell on Binance
            buy_amount = kucoin_price * quantity
            buy_fee = buy_amount * 0.001  # 0.1% fee
            total_buy_cost = buy_amount + buy_fee
            
            sell_amount = binance_price * quantity
            sell_fee = sell_amount * 0.001  # 0.1% fee
            total_sell_revenue = sell_amount - sell_fee
            
            profit = total_sell_revenue - total_buy_cost
        else:
            # KuCoin is more expensive: Buy on Binance, Sell on KuCoin
            buy_amount = binance_price * quantity
            buy_fee = buy_amount * 0.001  # 0.1% fee
            total_buy_cost = buy_amount + buy_fee
            
            sell_amount = kucoin_price * quantity
            sell_fee = sell_amount * 0.001  # 0.1% fee
            total_sell_revenue = sell_amount - sell_fee
            
            profit = total_sell_revenue - total_buy_cost
            
        return profit

    @staticmethod
    def check_stop_loss(current_profit_loss, threshold=STOP_LOSS_THRESHOLD):
        return current_profit_loss <= threshold
