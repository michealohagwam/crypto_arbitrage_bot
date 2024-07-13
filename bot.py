import os
import logging
import schedule
import time
from datetime import datetime
from binance.client import Client as BinanceClient
from bybit import bybit
from tabulate import tabulate
import requests.exceptions
import csv
import ccxt
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(filename='crypto_arbitrage_bot.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Function to fetch environment variables
def get_env_var(var_name):
    value = os.getenv(var_name)
    if value is None:
        logging.error(f"Environment variable {var_name} not set")
        raise ValueError(f"Please set the {var_name} environment variable")
    return value

# Fetch API keys from environment variables
binance_api_key = get_env_var('BINANCE_API_KEY')
binance_api_secret = get_env_var('BINANCE_API_SECRET')

# Get API key, secret, and passphrase from environment variables
api_key = os.getenv('KUCOIN_API_KEY')
api_secret = os.getenv('KUCOIN_API_SECRET')
api_passphrase = os.getenv('KUCOIN_API_PASSPHRASE')

# Initialize Binance client
binance_client = BinanceClient(api_key=binance_api_key, api_secret=binance_api_secret)

# Initialize KuCoin client
kucoin = ccxt.kucoin({
    'apiKey': api_key,
    'secret': api_secret,
    'password': api_passphrase,
})

# Fetch account balance
balance = kucoin.fetch_balance()

# Print only the BTC balance
btc_balance = balance['total'].get('BTC', 0.0)
print(f"BTC Balance: {btc_balance}")

# Function to check Binance balance
def check_balance_binance():
    try:
        account_info = binance_client.get_account()
        balances = account_info['balances']
        btc_balance = next((item for item in balances if item['asset'] == 'BTC'), None)
        if btc_balance:
            print(f"Binance BTC Balance: {btc_balance['free']}")
            logging.info(f"Binance BTC Balance: {btc_balance['free']}")
        else:
            print("No BTC balance found on Binance.")
            logging.info("No BTC balance found on Binance.")
    except Exception as e:
        print(f"Error fetching Binance balance: {e}")
        logging.error(f"Error fetching Binance balance: {e}")
        
# Initialize KuCoin client
api_key = os.getenv('KUCOIN_API_KEY')
api_secret = os.getenv('KUCOIN_API_SECRET')
api_passphrase = os.getenv('KUCOIN_API_PASSPHRASE')

kucoin_client = ccxt.kucoin({
    'apiKey': api_key,
    'secret': api_secret,
    'password': api_passphrase,
})

def check_balance_kucoin():
    try:
        balance = kucoin_client.fetch_balance()
        btc_balance = balance['total'].get('BTC', 0.0)
        logging.info(f"KuCoin BTC Balance: {btc_balance}")
        return btc_balance
    except Exception as e:
        logging.error(f"Error fetching KuCoin balance: {e}")
        return 0.0

# Example usage
#if __name__ == "__main__":
 #   btc_balance = check_balance_kucoin()
  #  print(f"BTC Balance: {btc_balance}")
    
# Check balances at startup
check_balance_kucoin()
check_balance_binance()

# Function to fetch Binance BTC price
def get_binance_btc_price():
    try:
        ticker = binance_client.get_symbol_ticker(symbol='BTCUSDT')
        return float(ticker['price'])
    except Exception as e:
        logging.error(f"Error fetching Binance BTC price: {e}")
        return None

# Function to fetch KuCoin BTC price
def get_kucoin_btc_price():
    try:
        ticker = kucoin.fetch_ticker('BTC/USDT')
        return float(ticker['last'])
    except Exception as e:
        logging.error(f"Error fetching KuCoin BTC price: {e}")
        return None

# Function to calculate trading fees for Binance and KuCoin (0.1% each)
def calculate_fees(price, exchange):
    fee_rate = 0.001  # 0.1% fee for each trade
    fee = price * fee_rate
    logging.info(f'{exchange} trading fee: ${fee:.2f}')
    return fee

# Function to handle network failure
def handle_network_failure(exchange):
    logging.error(f"Network failure detected on {exchange}. Retrying...")
    # Implement retry logic or alert mechanism as needed

# Function to handle insufficient funds
def handle_insufficient_funds(exchange):
    logging.error(f"Insufficient funds on {exchange}. Cannot proceed with the trade.")
    # Implement alert mechanism as needed

# Function to place sell order on Binance
def place_binance_sell_order(symbol, quantity, price):
    try:
        # Replace these with actual Binance API calls based on their documentation
        # Example:
        order = binance_client.create_order(
            symbol=symbol,
            side='SELL',
            type='LIMIT',
            quantity=quantity,
            price=price,
            timeInForce='GTC'  # Good till cancelled
        )
        logging.info(f"Sell order placed on Binance: {order}")
        return order
    except Exception as e:
        logging.error(f"Error placing sell order on Binance: {e}")
        return None

# Function to place stop order on KuCoin
def place_kucoin_stop_order(symbol, stop_price, quantity, side):
    try:
        # Replace these with actual KuCoin API calls based on their documentation
        params = {
            'symbol': symbol,
            'stop': stop_price,
            'type': 'stop',
            'size': quantity,
            'side': side,
            # Add any additional parameters as required by the KuCoin API
        }
        order = kucoin.private_post_orders(params=params)
        logging.info(f"Stop order placed on KuCoin: {order}")
        return order
    except Exception as e:
        logging.error(f"Error placing stop order on KuCoin: {e}")
        return None

# Function to place sell order on Binance
def place_binance_sell_order(binance_client, symbol, quantity):
    try:
        # Construct the order parameters
        order_params = {
            'symbol': symbol,
            'quantity': quantity,
            'side': 'SELL',
            'type': 'MARKET',  # Example: Market order type
            # Add any additional parameters as required by the Binance API
        }
        
        # Make the API call to place the order
        order_response = binance_client.create_order(**order_params)
        
        # Log the order response
        logging.info(f"Sell order placed on Binance: {order_response}")
        
        return order_response
    
    except Exception as e:
        logging.error(f"Error placing sell order on Binance: {e}")
        return None

# Function to place sell order on KuCoin
def place_kucoin_sell_order(kucoin_client, symbol, quantity):
    try:
        # Construct the order parameters
        order_params = {
            'symbol': symbol,
            'size': quantity,
            'side': 'sell',
            'type': 'market',  # Example: Market order type
            # Add any additional parameters as required by the KuCoin API
        }
        
        # Make the API call to place the order
        order_response = kucoin_client.create_order(**order_params)
        
        # Log the order response
        logging.info(f"Sell order placed on KuCoin: {order_response}")
        
        return order_response
    
    except Exception as e:
        logging.error(f"Error placing sell order on KuCoin: {e}")
        return None

# Function to calculate profit after fees on Binance or KuCoin
def calculate_profit(binance_price, kucoin_price, quantity):
    binance_profit = calculate_profit_binance(binance_price, kucoin_price, quantity)
    kucoin_profit = calculate_profit_kucoin(binance_price, kucoin_price, quantity)
    
    # Compare profits from both exchanges and return the greater profit
    return max(binance_profit, kucoin_profit)

# Function to calculate profit after fees on Binance
def calculate_profit_binance(binance_price, kucoin_price, quantity):
    binance_fee = calculate_fees(binance_price, 'Binance')
    kucoin_fee = calculate_fees(kucoin_price, 'KuCoin')

    if binance_price > kucoin_price + kucoin_fee:
        # Buy on KuCoin and sell on Binance
        profit = (binance_price - (kucoin_price * (1 + kucoin_fee))) * quantity
        return profit
    elif kucoin_price > binance_price + binance_fee:
        # Buy on Binance and sell on KuCoin
        profit = (kucoin_price - (binance_price * (1 + binance_fee))) * quantity
        return profit
    else:
        return 0

# Function to calculate profit after fees on KuCoin
def calculate_profit_kucoin(binance_price, kucoin_price, quantity):
    binance_fee = calculate_fees(binance_price, 'Binance')
    kucoin_fee = calculate_fees(kucoin_price, 'KuCoin')

    if binance_price > kucoin_price + kucoin_fee:
        # Buy on KuCoin and sell on Binance
        profit = (binance_price - (kucoin_price * (1 + kucoin_fee))) * quantity
        return profit
    elif kucoin_price > binance_price + binance_fee:
        # Buy on Binance and sell on KuCoin
        profit = (kucoin_price - (binance_price * (1 + binance_fee))) * quantity
        return profit
    else:
        return 0


# Function to calculate position size based on capital and percentage allocation
def calculate_position_size(capital, allocation_percentage):
    if allocation_percentage < 0 or allocation_percentage > 100:
        raise ValueError("Allocation percentage should be between 0 and 100.")
    return capital * (allocation_percentage / 100)

# Function to implement stop-loss mechanism
def stop_loss_check(current_profit_loss):
    stop_loss_threshold = -5  # $5 loss threshold
    if current_profit_loss <= stop_loss_threshold:
        return True
    return False

# Initialize trade summaries and totals
successful_trades = 0
failed_trades = 0
total_profit = 0
amount_used = 0
total_losses = 0

# Initialize KuCoin client
kucoin_client = ccxt.kucoin()

def get_binance_btc_price():
    try:
        ticker = binance_client.get_ticker(symbol='BTCUSDT')  # Use the correct method for fetching the ticker
        return float(ticker['lastPrice'])
    except Exception as e:
        print(f"Error fetching Binance BTC price: {e}")
        handle_network_failure('Binance')  # Ensure 'Binance' is passed as the argument
        return None

# Threshold function to determine arbitrage opportunity between Binance and KuCoin
def is_arbitrage_opportunity(binance_price, kucoin_price, threshold=20):
    difference = abs(binance_price - kucoin_price)
    if difference >= threshold:
        logging.info(f'Arbitrage opportunity detected! Binance: ${binance_price}, KuCoin: ${kucoin_price}, Difference: ${difference:.2f}')
        return True
    return False

# Function to log and print results in table format
def log_and_print_results(binance_price, kucoin_price, profit):
    global successful_trades, failed_trades, total_profit, amount_used, total_losses

    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    difference = abs(binance_price - kucoin_price)
    if profit >= 0.01:
        result = "Successful"
        successful_trades += 1
        total_profit += profit
    else:
        result = "Failed"
        failed_trades += 1
        if profit < 0:
            total_losses += abs(profit)

    # Determine recommendation
    if binance_price > kucoin_price:
        recommendation = 'Buy on Kucoin and sell on Binance'
    else:
        recommendation = 'Buy on Binance and sell on Kucoin'

    # Print and log results in table format
    table_data = [
        ["Time", "Binance BTC/USDT Price", "Kucoin BTC/USDT Price", "Difference", "Profit", "Result", "Recommendation"],
        [current_time, f'${binance_price}', f'${kucoin_price}', f'${difference:.2f}', f'${profit:.2f}', result, recommendation]
    ]
    print(tabulate(table_data, headers="firstrow", tablefmt="grid"))
    logging.info(f'{current_time} - Binance: ${binance_price}, Kucoin: ${kucoin_price}, Difference: ${difference:.2f}, Profit: ${profit:.2f}, Result: {result}, Recommendation: {recommendation}')

    # Update amount used (example)
    amount_used += 50  # Adjust based on your trading logic

    # Print trade summaries and totals
    print("\nTrade Summaries:")
    print(f"Successful Trades: {successful_trades}")
    print(f"Failed Trades: {failed_trades}")
    print(f"Total Profit: ${total_profit:.2f}")
    print(f"Total Losses: ${total_losses:.2f}")
    print(f"Amount Used for Trading: ${amount_used}")
    print(f"Total Profit after Fees and Costs: ${total_profit - amount_used:.2f}")

    # Save results to logs
    save_to_daily_log(current_time, binance_price, kucoin_price, difference, profit, result, recommendation)
    save_to_weekly_log(current_time, binance_price, kucoin_price, difference, profit, result, recommendation)
    save_to_monthly_log(current_time, binance_price, kucoin_price, difference, profit, result, recommendation)

# Function to save results to daily, weekly, and monthly logs
def save_to_daily_log(current_time, binance_price, kucoin_price, difference, profit, result, recommendation):
    with open('daily_trades.csv', mode='a', newline='') as file:
        writer = csv.writer(file)
        if file.tell() == 0:  # Check if file is empty to write headers
            writer.writerow(["Time", "Binance BTC/USDT Price", "kucoin BTC/USDT Price", "Difference", "Profit", "Result", "Recommendation"])
        writer.writerow([current_time, f'${binance_price}', f'${kucoin_price}', f'${difference:.2f}', f'${profit:.2f}', result, recommendation])

def save_to_weekly_log(current_time, binance_price, kucoin_price, difference, profit, result, recommendation):
    week_number = datetime.now().isocalendar()[1]
    week_file = f'weekly_trades_week_{week_number}.csv'
    with open(week_file, mode='a', newline='') as file:
        writer = csv.writer(file)
        if file.tell() == 0:  # Check if file is empty to write headers
            writer.writerow(["Time", "Binance BTC/USDT Price", "Kucoin BTC/USDT Price", "Difference", "Profit", "Result", "Recommendation"])
        writer.writerow([current_time, f'${binance_price}', f'${kucoin_price}', f'${difference:.2f}', f'${profit:.2f}', result, recommendation])

def save_to_monthly_log(current_time, binance_price, kucoin_price, difference, profit, result, recommendation):
    month_year = datetime.now().strftime('%Y-%m')
    month_file = f'monthly_trades_{month_year}.csv'
    with open(month_file, mode='a', newline='') as file:
        writer = csv.writer(file)
        if file.tell() == 0:  # Check if file is empty to write headers
            writer.writerow(["Time", "Binance BTC/USDT Price", "Kucoin BTC/USDT Price", "Difference", "Profit", "Result", "Recommendation"])
        writer.writerow([current_time, f'${binance_price}', f'${kucoin_price}', f'${difference:.2f}', f'${profit:.2f}', result, recommendation])

# Function to calculate total profit for a given log file
def calculate_totals(log_file):
    total_profit = 0
    if os.path.exists(log_file):
        with open(log_file, mode='r', newline='') as file:
            reader = csv.DictReader(file)
            for row in reader:
                total_profit += float(row['Profit'].replace('$', ''))
    return total_profit

# Function to calculate trade summaries from log files
def calculate_trade_summaries(log_file):
    total_profit = 0
    successful_trades = 0
    failed_trades = 0
    total_losses = 0

    if os.path.exists(log_file):
        with open(log_file, mode='r', newline='') as file:
            reader = csv.DictReader(file)
            for row in reader:
                profit = float(row['Profit'].replace('$', ''))
                total_profit += profit
                if profit >= 0.01:
                    successful_trades += 1
                else:
                    failed_trades += 1
                    if profit < 0:
                        total_losses += abs(profit)
    return total_profit, successful_trades, failed_trades, total_losses

# Function to log totals for daily, weekly, and monthly periods
def log_totals():
    daily_total, daily_successful, daily_failed, daily_losses = calculate_trade_summaries('daily_trades.csv')
    weekly_file = f'weekly_trades_week_{datetime.now().isocalendar()[1]}.csv'
    weekly_total, weekly_successful, weekly_failed, weekly_losses = calculate_trade_summaries(weekly_file)
    monthly_file = f'monthly_trades_{datetime.now().strftime("%Y-%m")}.csv'
    monthly_total, monthly_successful, monthly_failed, monthly_losses = calculate_trade_summaries(monthly_file)

    logging.info(f"Daily Total Profit: ${daily_total:.2f}, Successful Trades: {daily_successful}, Failed Trades: {daily_failed}, Total Losses: ${daily_losses:.2f}")
    logging.info(f"Weekly Total Profit: ${weekly_total:.2f}, Successful Trades: {weekly_successful}, Failed Trades: {weekly_failed}, Total Losses: ${weekly_losses:.2f}")
    logging.info(f"Monthly Total Profit: ${monthly_total:.2f}, Successful Trades: {monthly_successful}, Failed Trades: {monthly_failed}, Total Losses: ${monthly_losses:.2f}")

# Function to execute arbitrage trading logic
def execute_arbitrage():
    try:
        binance_price = get_binance_btc_price()
        kucoin_price = get_kucoin_btc_price()

        if binance_price is not None and kucoin_price is not None:
            logging.info(f'Binance BTC/USDT Price: ${binance_price}')
            logging.info(f'Kucoin BTC/USDT Price: ${kucoin_price}')

            # Check if there's an arbitrage opportunity
            if is_arbitrage_opportunity(binance_price, kucoin_price, threshold=10):
                # Calculate profit after fees
                capital = 50  # Example capital amount, adjust as needed
                allocation_percentage = 50  # Allocate 100% of capital per trade
                quantity = calculate_position_size(capital, allocation_percentage)
                profit = calculate_profit(binance_price, kucoin_price, quantity)

                # Check for stop-loss
                if stop_loss_check(profit):
                    logging.info('Stop-loss triggered! Loss exceeds $5.')
                    return

                # Check for insufficient funds (this should be implemented based on actual API responses)
                if capital < quantity:
                    handle_insufficient_funds('Binance' if binance_price > kucoin_price else 'Kucoin')
                    return

                # Log and print results
                log_and_print_results(binance_price, kucoin_price, profit)

                # Save to weekly and monthly logs
                save_to_weekly_log(datetime.now().strftime('%Y-%m-%d %H:%M:%S'), binance_price, kucoin_price, abs(binance_price - kucoin_price), profit, "Successful" if profit >= 0.01 else "Failed", 'Buy on KuCoin and sell on Binance' if binance_price > kucoin_price else 'Buy on Binance and sell on KuCoin')
                save_to_monthly_log(datetime.now().strftime('%Y-%m-%d %H:%M:%S'), binance_price, kucoin_price, abs(binance_price - kucoin_price), profit, "Successful" if profit >= 0.01 else "Failed", 'Buy on KuCoin and sell on Binance' if binance_price > kucoin_price else 'Buy on Binance and sell on KuCoin')
        else:
            logging.error("Failed to fetch prices from one or both exchanges")
            handle_network_failure('Binance' if binance_price is None else 'KuCoin')
    except Exception as e:
        logging.error(f"Unexpected error in execute_arbitrage: {e}")
        handle_network_failure('Arbitrage Execution')


# Function to run the job periodically
def job():
    execute_arbitrage()
    log_totals()  # Log totals after each execution

# Schedule the job every 1 second (adjust as needed)
schedule.every(5).seconds.do(job)

def clear_all_logs_and_csv_files():
    # List of log and CSV files to clear
    log_files = ['crypto_arbitrage_bot.log']
    csv_files = [
        'daily_trades.csv', 
        f'weekly_trades_week_{datetime.now().isocalendar()[1]}.csv', 
        f'monthly_trades_{datetime.now().strftime("%Y-%m")}.csv'
    ]

    # Clear log files
    for log_file in log_files:
        if os.path.exists(log_file):
            open(log_file, 'w').close()  # Truncate file
            logging.info(f"Cleared log file: {log_file}")

    # Clear CSV files
    for csv_file in csv_files:
        if os.path.exists(csv_file):
            open(csv_file, 'w').close()  # Truncate file
            logging.info(f"Cleared CSV file: {csv_file}")

# Call this function to clear logs and CSV files
# Uncomment the following line to clear logs and CSV files when the script starts
# clear_all_logs_and_csv_files()
clear_all_logs_and_csv_files()

# Main loop to run the scheduler
while True:
    schedule.run_pending()
    time.sleep(1)


