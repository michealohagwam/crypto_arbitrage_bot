import schedule
import time
from trading.arbitrage import ArbitrageTrader
from utils.file_handler import FileHandler
from config.settings import TRADING_INTERVAL, DASHBOARD_SECRET_KEY, BINANCE_API_KEY, KUCOIN_API_KEY, KUCOIN_API_PASSPHRASE
import argparse
import sys

# Web dashboard import
from flask import Flask, render_template_string, request, jsonify, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import threading
import os
from utils.db import TradeDB
import sqlite3
import requests
from utils.logger import logger
from urllib.parse import unquote

def check_network_connectivity():
    """Check if we can reach the exchange APIs"""
    test_urls = [
        'https://api.binance.com',
        'https://api.kucoin.com'
    ]
    
    logger.info("🌐 Checking network connectivity...")
    for url in test_urls:
        try:
            response = requests.get(url, timeout=5)
            logger.info(f"✅ {url} - Status: {response.status_code}")
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ {url} - Error: {e}")
            return False
    return True

# User model for Flask-Login
class User(UserMixin):
    def __init__(self, id, username, password_hash):
        self.id = id
        self.username = username
        self.password_hash = password_hash

    @staticmethod
    def get_by_username(username):
        db = TradeDB()
        user = db.get_user_by_username(username)
        if user:
            return User(user[0], user[1], user[2])
        return None

    @staticmethod
    def get_by_id(user_id):
        db = TradeDB()
        user = db.get_user_by_id(user_id)
        if user:
            return User(user[0], user[1], user[2])
        return None

# Extend TradeDB for user management
setattr(TradeDB, 'init_user_table', lambda self: self._init_user_table())
def _init_user_table(self):
    with sqlite3.connect(self.db_path) as conn:
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password_hash TEXT
        )''')
        conn.commit()
setattr(TradeDB, '_init_user_table', _init_user_table)

def create_user(username, password):
    logger.info(f"👤 Creating user: {username}")
    db = TradeDB()
    db.init_user_table()
    password_hash = generate_password_hash(password)
    with sqlite3.connect(db.db_path) as conn:
        c = conn.cursor()
        try:
            c.execute('INSERT INTO users (username, password_hash) VALUES (?, ?)', (username, password_hash))
            conn.commit()
            logger.info(f"✅ User '{username}' created successfully.")
        except sqlite3.IntegrityError:
            logger.warning(f"⚠️ User '{username}' already exists.")

def get_user_by_username(self, username):
    with sqlite3.connect(self.db_path) as conn:
        c = conn.cursor()
        c.execute('SELECT id, username, password_hash FROM users WHERE username = ?', (username,))
        return c.fetchone()
setattr(TradeDB, 'get_user_by_username', get_user_by_username)

def get_user_by_id(self, user_id):
    with sqlite3.connect(self.db_path) as conn:
        c = conn.cursor()
        c.execute('SELECT id, username, password_hash FROM users WHERE id = ?', (user_id,))
        return c.fetchone()
setattr(TradeDB, 'get_user_by_id', get_user_by_id)

def run_scheduler(trader, dry_run):
    logger.info(f"⏰ Starting scheduler with {TRADING_INTERVAL}s interval (DRY RUN: {dry_run})")
    
    def job():
        logger.info("🕐 Scheduled trade execution triggered")
        trader.execute_trade(dry_run=dry_run)
    
    schedule.every(TRADING_INTERVAL).seconds.do(job)
    logger.info(f"✅ Scheduler configured to run every {TRADING_INTERVAL} seconds")
    
    while True:
        schedule.run_pending()
        time.sleep(1)

def run_web_dashboard(trader, dry_run):
    logger.info("🌐 Starting web dashboard...")
    
    app = create_flask_app(trader, dry_run)
    logger.info("✅ Web dashboard started successfully")
    app.run(debug=True, use_reloader=False, host='0.0.0.0', port=5000)

def create_flask_app(trader, dry_run):
    """Create and configure Flask app for both development and production"""
    app = Flask(__name__)
    app.secret_key = DASHBOARD_SECRET_KEY
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'login'
    trade_logger = trader.trade_logger

    @login_manager.user_loader
    def load_user(user_id):
        return User.get_by_id(user_id)

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            logger.info(f"🔐 Login attempt for user: {username}")
            
            user = User.get_by_username(username)
            if user and check_password_hash(user.password_hash, password):
                login_user(user)
                logger.info(f"✅ Successful login for user: {username}")
                return redirect(url_for('dashboard'))
            else:
                logger.warning(f"❌ Failed login attempt for user: {username}")
                flash('Invalid username or password')
        return render_template_string('''
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Login - Crypto Arbitrage Dashboard</title>
            <link href="https://fonts.googleapis.com/icon?family=Material+Icons" rel="stylesheet">
            <link href="https://cdnjs.cloudflare.com/ajax/libs/materialize/1.0.0/css/materialize.min.css" rel="stylesheet">
            <style>
                body { background: linear-gradient(135deg, #ff6f00 0%, #f50057 100%); min-height: 100vh; }
                .card { margin-top: 8vh; }
                .brand-logo { font-weight: bold; }
            </style>
        </head>
        <body>
        <nav class="pink accent-3">
            <div class="nav-wrapper container">
                <a href="/" class="brand-logo">Crypto Arbitrage</a>
            </div>
        </nav>
        <div class="container">
            <div class="row">
                <div class="col s12 m6 offset-m3">
                    <div class="card white z-depth-3">
                        <div class="card-content">
                            <span class="card-title center-align pink-text text-accent-3">Login</span>
                            <form method="post">
                                <div class="input-field">
                                    <input id="username" name="username" type="text" required>
                                    <label for="username">Username</label>
                                </div>
                                <div class="input-field">
                                    <input id="password" name="password" type="password" required>
                                    <label for="password">Password</label>
                                </div>
                                <div class="center-align">
                                    <button class="btn waves-effect waves-light pink accent-3" type="submit">Login
                                        <i class="material-icons right">login</i>
                                    </button>
                                </div>
                            </form>
                            {% with messages = get_flashed_messages() %}
                              {% if messages %}
                                <ul class="collection red-text">
                                  {% for m in messages %}<li class="collection-item">{{ m }}</li>{% endfor %}
                                </ul>
                              {% endif %}
                            {% endwith %}
                        </div>
                    </div>
                </div>
            </div>
        </div>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/materialize/1.0.0/js/materialize.min.js"></script>
        </body>
        </html>
        ''')

    @app.route('/logout')
    @login_required
    def logout():
        logger.info(f"👋 User logout: {current_user.username}")
        logout_user()
        return redirect(url_for('login'))

    @app.route('/')
    @login_required
    def dashboard():
        logger.info(f"📊 Dashboard accessed by user: {current_user.username}")
        
        # Get metrics and trades with error handling
        try:
            metrics = trade_logger.get_metrics()
            trades = trade_logger.get_trades(since_days=30)
        except Exception as e:
            logger.error(f"Error fetching dashboard data: {e}")
            metrics = {'trade_count': 0, 'total_profit': 0.0, 'avg_profit': 0.0}
            trades = []
        
        manual_trade_log = request.args.get('manual_trade_log', None)
        if manual_trade_log:
            manual_trade_log = unquote(manual_trade_log)
        
        # Fetch current account balances
        try:
            binance_btc_balance = trader.binance.check_balance()
            binance_usdt_balance = trader.binance.check_usdt_balance()
            kucoin_btc_balance = trader.kucoin.check_balance()
            kucoin_usdt_balance = trader.kucoin.check_usdt_balance()
        except Exception as e:
            logger.error(f"Error fetching balances: {e}")
            binance_btc_balance = binance_usdt_balance = kucoin_btc_balance = kucoin_usdt_balance = "Error"
        
        # Pass API keys to the template (WARNING: this is sensitive info)
        return render_template_string('''
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Crypto Arbitrage Dashboard</title>
            <link href="https://fonts.googleapis.com/icon?family=Material+Icons" rel="stylesheet">
            <link href="https://cdnjs.cloudflare.com/ajax/libs/materialize/1.0.0/css/materialize.min.css" rel="stylesheet">
            <style>
                body { background: linear-gradient(135deg, #00bcd4 0%, #ffeb3b 100%); min-height: 100vh; }
                .brand-logo { font-weight: bold; }
                .card { margin-top: 4vh; }
                .metrics-list li { font-size: 1.2em; }
                .table-container { overflow-x: auto; }
                .log-box { background: #fff3e0; border: 1px solid #ff9800; color: #bf360c; padding: 1em; margin-bottom: 1em; border-radius: 6px; font-family: monospace; white-space: pre-wrap; }
                .sensitive-box { background: #ffebee; border: 1px solid #e57373; color: #b71c1c; padding: 1em; margin-bottom: 1em; border-radius: 6px; font-family: monospace; }
                .balance-box { background: #e8f5e8; border: 1px solid #4caf50; color: #2e7d32; padding: 1em; margin-bottom: 1em; border-radius: 6px; }
                .balance-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 1em; }
                .balance-item { background: white; padding: 1em; border-radius: 4px; border-left: 4px solid #4caf50; }
            </style>
        </head>
        <body>
        <nav class="cyan accent-4">
            <div class="nav-wrapper container">
                <a href="/" class="brand-logo">Crypto Arbitrage</a>
                <ul id="nav-mobile" class="right hide-on-med-and-down">
                    <li><a href="/logout"><i class="material-icons left">logout</i>Logout</a></li>
                </ul>
            </div>
        </nav>
        <div class="container">
            <div class="row">
                <div class="col s12 m10 offset-m1">
                    <div class="card white z-depth-3">
                        <div class="card-content">
                            <span class="card-title cyan-text text-accent-4 center-align">Dashboard</span>
                            {% if manual_trade_log %}
                            <div class="log-box">
                                <b>Manual Trade Output:</b><br>
                                {{ manual_trade_log|safe }}
                            </div>
                            {% endif %}
                            <div class="balance-box">
                                <h6 class="green-text text-darken-2"><i class="material-icons left">account_balance_wallet</i>Account Balances</h6>
                                <div class="balance-grid">
                                    <div class="balance-item">
                                        <h6 class="blue-text">Binance</h6>
                                        <p><b>BTC:</b> {{ binance_btc_balance }}</p>
                                        <p><b>USDT:</b> ${{ binance_usdt_balance }}</p>
                                    </div>
                                    <div class="balance-item">
                                        <h6 class="orange-text">KuCoin</h6>
                                        <p><b>BTC:</b> {{ kucoin_btc_balance }}</p>
                                        <p><b>USDT:</b> ${{ kucoin_usdt_balance }}</p>
                                    </div>
                                </div>
                            </div>
                            <form method="post" action="/run-trade" class="center-align" style="margin-bottom: 2em;">
                                <button class="btn-large waves-effect waves-light pink accent-3" type="submit">
                                    <i class="material-icons left">autorenew</i>Run Arbitrage Check
                                </button>
                            </form>
                            <h5 class="cyan-text text-accent-4">Metrics (last 30 days)</h5>
                            <ul class="metrics-list">
                                <li><b>Total Trades:</b> {{ metrics.trade_count }}</li>
                                <li><b>Total Profit:</b> <span class="green-text">${{ '%.2f' % metrics.total_profit }}</span></li>
                                <li><b>Average Profit:</b> <span class="blue-text">${{ '%.2f' % metrics.avg_profit }}</span></li>
                            </ul>
                            <h5 class="cyan-text text-accent-4">Trade History (last 30 days)</h5>
                            <div class="table-container">
                                <table class="striped responsive-table">
                                    <thead>
                                        <tr class="yellow lighten-4">
                                            <th>Time</th>
                                            <th>Binance Price</th>
                                            <th>KuCoin Price</th>
                                            <th>Difference</th>
                                            <th>Profit</th>
                                            <th>Result</th>
                                            <th>Recommendation</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {% for trade in trades %}
                                        <tr>
                                            {% for item in trade[1:] %}
                                            <td>{{ item }}</td>
                                            {% endfor %}
                                        </tr>
                                        {% endfor %}
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/materialize/1.0.0/js/materialize.min.js"></script>
        </body>
        </html>
        ''', metrics=metrics, trades=trades, manual_trade_log=manual_trade_log,
        binance_api_key=BINANCE_API_KEY, kucoin_api_key=KUCOIN_API_KEY, kucoin_passphrase=KUCOIN_API_PASSPHRASE,
        binance_btc_balance=binance_btc_balance, binance_usdt_balance=binance_usdt_balance,
        kucoin_btc_balance=kucoin_btc_balance, kucoin_usdt_balance=kucoin_usdt_balance)

    @app.route('/run-trade', methods=['POST'])
    @login_required
    def run_trade():
        logger.info(f"🚀 Manual trade execution triggered by user: {current_user.username}")
        import io
        import logging
        log_stream = io.StringIO()
        stream_handler = logging.StreamHandler(log_stream)
        stream_handler.setLevel(logging.INFO)
        logging.getLogger().addHandler(stream_handler)
        try:
            result = trader.execute_trade(dry_run=dry_run, return_data=True)
        except Exception as e:
            logger.error(f"Manual trade error: {e}")
        finally:
            logging.getLogger().removeHandler(stream_handler)
        log_contents = log_stream.getvalue()
        log_stream.close()
        # Show logs/errors on dashboard
        from urllib.parse import quote
        return redirect(url_for('dashboard', manual_trade_log=quote(log_contents)))

    return app

def main():
    parser = argparse.ArgumentParser(description='Crypto Arbitrage Bot')
    parser.add_argument('--web', action='store_true', help='Run web dashboard')
    parser.add_argument('--dry-run', action='store_true', help='Simulate trades without executing them')
    parser.add_argument('--create-user', nargs=2, metavar=('username', 'password'), help='Create a dashboard user')
    parser.add_argument('--skip-network-check', action='store_true', help='Skip network connectivity check')
    parser.add_argument('--trading-interval', type=int, help='Override trading interval in seconds')
    args = parser.parse_args()

    # Override trading interval if specified
    global TRADING_INTERVAL
    if args.trading_interval:
        TRADING_INTERVAL = args.trading_interval
        logger.info(f"⏰ Trading interval overridden to {TRADING_INTERVAL} seconds")

    if args.create_user:
        username, password = args.create_user
        create_user(username, password)
        sys.exit(0)

    # Check network connectivity unless skipped
    if not args.skip_network_check:
        if not check_network_connectivity():
            logger.warning("⚠️ Network connectivity issues detected. The bot may not work properly.")
            logger.info("You can use --skip-network-check to bypass this check.")
            response = input("Continue anyway? (y/N): ")
            if response.lower() != 'y':
                sys.exit(1)

    logger.info("🧹 Clearing old log files...")
    FileHandler.clear_files()
    
    logger.info("🤖 Initializing ArbitrageTrader...")
    trader = ArbitrageTrader()

    if args.web:
        logger.info("🌐 Starting in web dashboard mode...")
        run_web_dashboard(trader, args.dry_run)
    else:
        logger.info("⏰ Starting in scheduler mode...")
        run_scheduler(trader, args.dry_run)

if __name__ == "__main__":
    main()