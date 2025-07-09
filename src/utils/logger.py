import logging
import os
from config.settings import LOG_LEVEL, LOG_FILE, LOG_FORMAT

def setup_logger():
    # Create logs directory if it doesn't exist
    log_dir = os.path.dirname(LOG_FILE)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # Configure logging with more detailed format
    logging.basicConfig(
        level=getattr(logging, LOG_LEVEL.upper()),
        format=LOG_FORMAT,
        handlers=[
            logging.FileHandler(LOG_FILE),
            logging.StreamHandler()  # Also log to console
        ]
    )
    
    # Create logger instance
    logger = logging.getLogger(__name__)
    
    # Log startup information
    logger.info("=" * 60)
    logger.info("🚀 Crypto Arbitrage Bot Starting")
    logger.info(f"📁 Log file: {os.path.abspath(LOG_FILE)}")
    logger.info(f"🔧 Log level: {LOG_LEVEL}")
    logger.info(f"⏰ Trading interval: {os.getenv('TRADING_INTERVAL', '300')} seconds")
    logger.info("=" * 60)
    
    return logger

logger = setup_logger()
