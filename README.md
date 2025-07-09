# Crypto Arbitrage Bot

[➡️ **Detailed Bot Operation & Architecture**](docs/BOT_DETAILS.md)

This project is a crypto arbitrage bot that trades Bitcoin (BTC) between Binance and KuCoin exchanges to take advantage of price differentials.

## Features

- Fetches BTC/USDT prices from Binance and KuCoin.
- Calculates arbitrage opportunities.
- Executes trades automatically.
- Logs successful and failed trades.
- Generates daily, weekly, and monthly trade summaries.
- Implements stop-loss mechanism to minimize losses.

## Requirements

- Python 3.12.4
- Binance and KuCoin API keys
- Flask, Flask-Login, Werkzeug (see requirements.txt)

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
    KUCOIN_API_KEY=your_kucoin_api_key
    KUCOIN_API_SECRET=your_kucoin_api_secret
    KUCOIN_API_PASSPHRASE=your_kucoin_api_passphrase
    DASHBOARD_SECRET_KEY=your_dashboard_secret_key
    ```

    **Required variables:**
    - `BINANCE_API_KEY` and `BINANCE_API_SECRET`: Your Binance API credentials
    - `KUCOIN_API_KEY`, `KUCOIN_API_SECRET`, and `KUCOIN_API_PASSPHRASE`: Your KuCoin API credentials
    - `DASHBOARD_SECRET_KEY`: Secret key for Flask session management (optional, defaults to 'supersecret')

## Usage

1. **Run the bot in CLI mode:**
    ```bash
    python src/main.py
    ```

2. **Run the bot in dry run mode (no real trades):**
    ```bash
    python src/main.py --dry-run
    ```

3. **Run the web dashboard:**
    ```bash
    python src/main.py --web
    ```
    - You can also combine with dry run:
    ```bash
    python src/main.py --web --dry-run
    ```

4. **Create a dashboard user (for login):**
    ```bash
    python src/main.py --create-user <username> <password>
    ```
    - You must create at least one user before accessing the dashboard.

## Web Dashboard & Authentication

- The dashboard is protected by login. Only users created via the CLI can log in.
- No registration is available from the web interface.
- Metrics (total trades, total/average profit) and trade history (last 30 days) are shown on the dashboard.

## Logging and Database

- All trades are logged to yearly SQLite databases (`db/trades_YYYY.sqlite3`).
- Database files are automatically created for each year (e.g., `trades_2024.sqlite3`, `trades_2025.sqlite3`).
- Old trades (older than 6 months) are automatically cleared from the current year's database.
- Metrics and trade history queries can span multiple years automatically.
- You can archive old database files to reduce storage usage.

## Production Deployment

### Docker Deployment (Recommended)

For production deployment on a server, use Docker with Gunicorn WSGI server:

1. **Clone the repository on your server:**
    ```bash
    git clone https://github.com/your-username/crypto_arbitrage_bot.git
    cd crypto_arbitrage_bot
    ```

2. **Create your .env file:**
    ```bash
    cp .env.example .env
    # Edit .env with your API credentials
    ```

3. **Create persistent directories:**
    ```bash
    sudo mkdir -p /var/www/crypto_arbitrage_bot/{db,logs}
    sudo chown -R $USER:$USER /var/www/crypto_arbitrage_bot
    ```

4. **Start the services:**
    ```bash
    # Start both scheduler and web dashboard
    docker compose up -d
    ```

**Services:**
- `crypto-arbitrage-scheduler`: Runs the trading bot with scheduled arbitrage checks
- `crypto-arbitrage-web`: Serves the web dashboard using Gunicorn WSGI server

**Production Features:**
- Uses Gunicorn WSGI server instead of Flask development server
- Separate services for trading and web dashboard
- Automatic health checks and restart policies
- Persistent data storage with volume mounts

**Note:**
- If you want to expose the dashboard to the internet, configure your own nginx or reverse proxy manually. This app no longer auto-configures nginx or provides an nginx.conf.

### Manual Server Setup

1. **Install dependencies on your server:**
    ```bash
    sudo apt update
    sudo apt install python3 python3-pip python3-venv nginx
    ```

2. **Set up the application:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    ```

3. **Create a systemd service:**
    ```bash
    sudo nano /etc/systemd/system/crypto-bot.service
    ```
    
    Add the following content:
    ```ini
    [Unit]
    Description=Crypto Arbitrage Bot
    After=network.target

    [Service]
    Type=simple
    User=your-username
    WorkingDirectory=/path/to/crypto_arbitrage_bot
    Environment=PATH=/path/to/crypto_arbitrage_bot/venv/bin
    ExecStart=/path/to/crypto_arbitrage_bot/venv/bin/python src/main.py --web
    Restart=always
    RestartSec=10

    [Install]
    WantedBy=multi-user.target
    ```

4. **Start the service:**
    ```bash
    sudo systemctl daemon-reload
    sudo systemctl enable crypto-bot
    sudo systemctl start crypto-bot
    ```

### SSL Certificate Setup

For production, replace the self-signed certificate with a proper SSL certificate:

1. **Using Let's Encrypt (free):**
    ```bash
    sudo apt install certbot python3-certbot-nginx
    sudo certbot --nginx -d your-domain.com
    ```

2. **Update your nginx config with your certificate paths**

### Security Considerations

- **Use strong passwords** for dashboard access
- **Generate a secure DASHBOARD_SECRET_KEY**
- **Use a proper domain name** instead of localhost
- **Set up firewall rules** to restrict access
- **Regular backups** of the database directory
- **Monitor logs** for suspicious activity

### Server Requirements

- **Minimum:** 1GB RAM, 1 CPU, 10GB storage
- **Recommended:** 2GB RAM, 2 CPU, 20GB storage
- **OS:** Ubuntu 20.04+ or CentOS 8+
- **Network:** Stable internet connection for API access

### Monitoring and Maintenance

- **View logs:** `docker compose logs -f` or `journalctl -u crypto-bot -f`
- **Database backup:** `cp -r db/ backup-$(date +%Y%m%d)/`
- **Update application:** Pull latest code and restart containers
- **Health checks:** Monitor the dashboard endpoint for availability

## Contributing

If you wish to contribute to this project, please fork the repository and submit a pull request. Make sure to add tests for new features or bug fixes.

## License

This project is licensed under the MIT License.
