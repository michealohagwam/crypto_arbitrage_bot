# Crypto Arbitrage Bot: Detailed Operation

## Overview

The Crypto Arbitrage Bot is an automated trading system designed to exploit price differences for Bitcoin (BTC) between two major cryptocurrency exchanges: **Binance** and **KuCoin**. The bot continuously monitors BTC/USDT prices on both exchanges, identifies arbitrage opportunities, and can execute trades to profit from these price discrepancies. It also provides a modern web dashboard for monitoring, manual trade execution, and reviewing trade history.

---

## Main Components

### 1. **Price Fetching**
- The bot uses official APIs (via `ccxt` for KuCoin and the Binance Python SDK) to fetch the latest BTC/USDT prices from both exchanges.
- It checks both prices at a configurable interval (default: every 5 minutes, can be changed).

### 2. **Arbitrage Opportunity Detection**
- The bot calculates the absolute price difference between Binance and KuCoin.
- If the difference exceeds a configurable threshold (e.g., $10), it considers this an arbitrage opportunity.

### 3. **Trade Execution**
- When an opportunity is detected, the bot determines the direction:
  - If Binance price > KuCoin price: **Buy on KuCoin, Sell on Binance**
  - If KuCoin price > Binance price: **Buy on Binance, Sell on KuCoin**
- It checks available balances (BTC and USDT) on both exchanges to ensure sufficient funds.
- If balances are sufficient and not in dry-run mode, it places market buy and sell orders on the respective exchanges.
- All trades are logged, including simulated trades in dry-run mode.

### 4. **Position Sizing and Risk Management**
- The bot calculates the position size based on a configurable capital and allocation percentage.
- It includes a stop-loss mechanism: if a trade would result in a loss greater than a set threshold, the trade is skipped.

### 5. **Logging and Reporting**
- All trades (real and simulated) are logged to a yearly SQLite database.
- The bot generates metrics such as total trades, total/average profit, and trade history.
- Logs are also written to a file and can be viewed in the dashboard.

### 6. **Web Dashboard**
- Built with Flask and Materialize CSS for a modern look.
- Features:
  - Secure login (users must be created via CLI).
  - Dashboard showing metrics, trade history, and manual trade logs.
  - Manual trade execution (with output/errors shown in the UI).
  - (Admin only) Display of sensitive API keys for debugging (can be disabled for security).

### 7. **Scheduler**
- The bot uses the `schedule` Python library to run arbitrage checks at regular intervals.
- The scheduler runs as a background service (Docker or systemd recommended for production).

### 8. **Configuration**
- All sensitive credentials (API keys, passphrases) and settings are loaded from environment variables via a `.env` file.
- Trading parameters (capital, allocation, thresholds) are configurable in `src/config/settings.py` or via environment variables.

---

## Example Workflow

1. **Startup**
   - Loads environment variables and initializes logging.
   - Checks network connectivity to both exchanges.
   - Initializes exchange clients and the arbitrage trader.

2. **Scheduled Loop**
   - Every N seconds (default: 300), fetches BTC/USDT prices from both exchanges.
   - Checks if the price difference exceeds the arbitrage threshold.
   - If yes, checks balances and executes trades (unless in dry-run mode).
   - Logs the trade and updates metrics.

3. **Web Dashboard**
   - Users log in to view metrics, trade history, and logs.
   - Users can trigger a manual arbitrage check and see the output/errors directly in the UI.

---

## Security Notes

- **API keys and passphrases are highly sensitive.** Never expose the dashboard or logs to untrusted users.
- The dashboard login is required for all access; users must be created via CLI.
- For production, always use HTTPS and strong passwords.

---

## Technologies Used

- **Python 3.12+**
- **Flask** (web dashboard)
- **Flask-Login** (authentication)
- **ccxt** (KuCoin API)
- **binance** (Binance API)
- **SQLite** (trade logging)
- **Docker** (production deployment)
- **Materialize CSS** (dashboard UI)

---

## Extending the Bot

- You can add more exchanges by implementing new client classes in `src/exchanges/`.
- Trading logic (thresholds, position sizing, stop-loss) can be adjusted in `src/config/settings.py` and `src/trading/position.py`.
- The dashboard can be extended with more analytics, notifications, or admin controls. 