import sqlite3
from datetime import datetime, timedelta
import os
import shutil

DB_DIR = os.path.join(os.path.dirname(__file__), '../../db')
if not os.path.exists(DB_DIR):
    os.makedirs(DB_DIR)

def get_current_db_path():
    current_year = datetime.now().year
    return os.path.join(DB_DIR, f'trades_{current_year}.sqlite3')

class TradeDB:
    def __init__(self, db_path=None):
        if db_path is None:
            self.db_path = get_current_db_path()
        else:
            self.db_path = db_path
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            c = conn.cursor()
            c.execute('''
                CREATE TABLE IF NOT EXISTS trades (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    time TEXT,
                    binance_price REAL,
                    kucoin_price REAL,
                    difference REAL,
                    profit REAL,
                    result TEXT,
                    recommendation TEXT
                )
            ''')
            conn.commit()

    def insert_trade(self, time, binance_price, kucoin_price, difference, profit, result, recommendation):
        # Check if we need to rotate to a new year's database
        self._check_and_rotate_db()
        
        with sqlite3.connect(self.db_path) as conn:
            c = conn.cursor()
            c.execute('''
                INSERT INTO trades (time, binance_price, kucoin_price, difference, profit, result, recommendation)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (time, binance_price, kucoin_price, difference, profit, result, recommendation))
            conn.commit()

    def _check_and_rotate_db(self):
        """Check if we need to rotate to a new year's database"""
        current_db_path = get_current_db_path()
        if current_db_path != self.db_path:
            # We're in a new year, switch to the new database
            self.db_path = current_db_path
            self._init_db()

    def get_trades(self, since_days=None, include_old_dbs=True):
        """Get trades from current database and optionally from previous years"""
        trades = []
        
        # Get from current database
        with sqlite3.connect(self.db_path) as conn:
            c = conn.cursor()
            if since_days:
                since = (datetime.now() - timedelta(days=since_days)).strftime('%Y-%m-%d %H:%M:%S')
                c.execute('SELECT * FROM trades WHERE time >= ? ORDER BY time DESC', (since,))
            else:
                c.execute('SELECT * FROM trades ORDER BY time DESC')
            trades.extend(c.fetchall())
        
        # Optionally include trades from previous year databases
        if include_old_dbs and since_days:
            since = (datetime.now() - timedelta(days=since_days)).strftime('%Y-%m-%d %H:%M:%S')
            current_year = datetime.now().year
            
            for year in range(current_year - 1, current_year - 10, -1):  # Check last 10 years
                old_db_path = os.path.join(DB_DIR, f'trades_{year}.sqlite3')
                if os.path.exists(old_db_path):
                    try:
                        with sqlite3.connect(old_db_path) as conn:
                            c = conn.cursor()
                            c.execute('SELECT * FROM trades WHERE time >= ? ORDER BY time DESC', (since,))
                            old_trades = c.fetchall()
                            trades.extend(old_trades)
                    except sqlite3.Error:
                        # Skip corrupted databases
                        continue
        
        return trades

    def get_metrics(self, since_days=None):
        """Get metrics from current database and optionally from previous years"""
        total_count = 0
        total_profit = 0.0
        profit_count = 0
        
        # Get from current database
        with sqlite3.connect(self.db_path) as conn:
            c = conn.cursor()
            if since_days:
                since = (datetime.now() - timedelta(days=since_days)).strftime('%Y-%m-%d %H:%M:%S')
                c.execute('SELECT COUNT(*), SUM(profit) FROM trades WHERE time >= ?', (since,))
            else:
                c.execute('SELECT COUNT(*), SUM(profit) FROM trades')
            count, profit = c.fetchone()
            if count:
                total_count += count
                if profit:
                    total_profit += profit
                    profit_count += count
        
        # Optionally include from previous year databases
        if since_days:
            since = (datetime.now() - timedelta(days=since_days)).strftime('%Y-%m-%d %H:%M:%S')
            current_year = datetime.now().year
            
            for year in range(current_year - 1, current_year - 10, -1):
                old_db_path = os.path.join(DB_DIR, f'trades_{year}.sqlite3')
                if os.path.exists(old_db_path):
                    try:
                        with sqlite3.connect(old_db_path) as conn:
                            c = conn.cursor()
                            c.execute('SELECT COUNT(*), SUM(profit) FROM trades WHERE time >= ?', (since,))
                            count, profit = c.fetchone()
                            if count:
                                total_count += count
                                if profit:
                                    total_profit += profit
                                    profit_count += count
                    except sqlite3.Error:
                        continue
        
        avg_profit = total_profit / profit_count if profit_count > 0 else 0.0
        return {
            'trade_count': total_count,
            'total_profit': total_profit,
            'avg_profit': avg_profit
        }

    def clear_old_trades(self, months=6):
        """Clear old trades from current database only"""
        cutoff = (datetime.now() - timedelta(days=30*months)).strftime('%Y-%m-%d %H:%M:%S')
        with sqlite3.connect(self.db_path) as conn:
            c = conn.cursor()
            c.execute('DELETE FROM trades WHERE time < ?', (cutoff,))
            conn.commit()

    def rotate_db(self):
        """Manually trigger database rotation"""
        self._check_and_rotate_db()

    def get_available_years(self):
        """Get list of years that have database files"""
        years = []
        for filename in os.listdir(DB_DIR):
            if filename.startswith('trades_') and filename.endswith('.sqlite3'):
                try:
                    year = int(filename[7:-8])  # Extract year from 'trades_YYYY.sqlite3'
                    years.append(year)
                except ValueError:
                    continue
        return sorted(years)

    def archive_old_dbs(self, keep_years=5):
        """Archive databases older than keep_years to a backup directory"""
        backup_dir = os.path.join(DB_DIR, 'archive')
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)
        
        current_year = datetime.now().year
        for year in range(current_year - keep_years, current_year - 100, -1):
            old_db_path = os.path.join(DB_DIR, f'trades_{year}.sqlite3')
            if os.path.exists(old_db_path):
                backup_path = os.path.join(backup_dir, f'trades_{year}.sqlite3')
                shutil.move(old_db_path, backup_path) 