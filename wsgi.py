#!/usr/bin/env python3
"""
WSGI entry point for production deployment with Gunicorn
"""
import os
import sys
from dotenv import load_dotenv

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Load environment variables
load_dotenv()

from src.main import create_flask_app
from src.trading.arbitrage import ArbitrageTrader
from src.utils.logger import logger

def create_app():
    """Create Flask app for production"""
    try:
        # Initialize trader (dry run mode for safety)
        trader = ArbitrageTrader()
        logger.info("🚀 Creating Flask app for production deployment")
        
        # Create Flask app with dry run mode
        app = create_flask_app(trader, dry_run=True)
        
        logger.info("✅ Flask app created successfully for production")
        return app
        
    except Exception as e:
        logger.error(f"❌ Failed to create Flask app: {e}")
        raise

# Create the application instance for Gunicorn
application = create_app()

if __name__ == "__main__":
    # For local testing
    application.run(host='0.0.0.0', port=5000) 