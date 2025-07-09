from datetime import datetime
from utils.db import TradeDB
from tabulate import tabulate

class TradeLogger:
    """
    A class used to log trade information and save it to the database.
    Attributes
    ----------
    db : TradeDB
        An instance of TradeDB to manage database operations.
    headers : list
        A list of headers for the trade data.
    Methods
    -------
    __init__()
        Initializes the TradeLogger with a TradeDB and headers.
    log_trade(time, binance_price, kucoin_price, difference, profit)
        Logs trade information, prints it in a table format, and saves it to the database.
    """
    def __init__(self):
        self.db = TradeDB()
        self.headers = ["Time", "Binance Price", "KuCoin Price", 
                       "Difference", "Profit", "Result", "Recommendation"]

    def log_trade(self, time, binance_price, kucoin_price, difference, profit, dry_run=False, return_data=False):
        result = "DRY RUN" if dry_run else ("Successful" if profit >= 0.01 else "Failed")
        recommendation = ('Buy on KuCoin and sell on Binance' 
                         if binance_price > kucoin_price 
                         else 'Buy on Binance and sell on KuCoin')

        data = [
            time.strftime('%Y-%m-%d %H:%M:%S'),
            float(binance_price),
            float(kucoin_price),
            float(difference),
            float(profit),
            result,
            recommendation
        ]

        # Print results in table format
        table_data = [self.headers, [
            data[0], f'${data[1]}', f'${data[2]}', f'${data[3]:.2f}', f'${data[4]:.2f}', data[5], data[6]
        ]]
        print(tabulate(table_data, headers="firstrow", tablefmt="grid"))

        if not dry_run:
            self.db.insert_trade(*data)
        if return_data:
            return table_data[1]

    def get_trades(self, since_days=None):
        return self.db.get_trades(since_days=since_days)

    def get_metrics(self, since_days=None):
        return self.db.get_metrics(since_days=since_days)
