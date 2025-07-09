import csv
import os
from datetime import datetime

# DEPRECATED: CSV logging will be replaced by SQLite database logging.
class FileHandler:
    @staticmethod
    def save_to_csv(filename, data, headers=None):
        mode = 'a' if os.path.exists(filename) else 'w'
        with open(filename, mode=mode, newline='') as file:
            writer = csv.writer(file)
            if mode == 'w' and headers:
                writer.writerow(headers)
            writer.writerow(data)

    @staticmethod
    def clear_files():
        files = [
            'crypto_arbitrage_bot.log',
            'daily_trades.csv',
            f'weekly_trades_week_{datetime.now().isocalendar()[1]}.csv',
            f'monthly_trades_{datetime.now().strftime("%Y-%m")}.csv'
        ]
        for file in files:
            if os.path.exists(file):
                open(file, 'w').close()
