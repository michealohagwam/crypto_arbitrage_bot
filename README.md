# Crypto Arbitrage Bot

This project is a crypto arbitrage bot that trades Bitcoin (BTC) between Binance and Bybit exchanges to take advantage of price differentials.

## Features

- Fetches BTC/USDT prices from Binance and Bybit.
- Calculates arbitrage opportunities.
- Executes trades automatically.
- Logs successful and failed trades.
- Generates daily, weekly, and monthly trade summaries.
- Implements stop-loss mechanism to minimize losses.

## Requirements

- Python 3.12.4
- Binance and Bybit API keys

## Setup

1. **Clone the repository:**
    ```bash
    git clone https://github.com/your-username/crypto_arbitrage_bot.git
    cd crypto_arbitrage_bot
    ```

2. **Create a virtual environment and activate it:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3. **Install the required packages:**
    ```bash
    pip install -r requirements.txt
    ```

4. **Set up environment variables:**

    Create a `.env` file in the root directory of the project and add your API keys:
    ```ini
    BINANCE_API_KEY=your_binance_api_key
    BINANCE_API_SECRET=your_binance_api_secret
    BYBIT_API_KEY=your_bybit_api_key
    BYBIT_API_SECRET=your_bybit_api_secret
    ```

## Usage

1. **Run the bot:**
    ```bash
    python bot.py
    ```

## Logging and Trade Summaries

- Logs are stored in `crypto_arbitrage_bot.log`.
- Trade summaries are stored in `daily_trades.csv`, `weekly_trades.csv`, and `monthly_trades.csv`.

## Contributing

If you wish to contribute to this project, please fork the repository and submit a pull request. Make sure to add tests for new features or bug fixes.

## License

This project is licensed under the MIT License.
