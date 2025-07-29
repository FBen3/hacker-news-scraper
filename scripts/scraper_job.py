#!/usr/bin/env python3
"""Standalone scraper job that runs 
independently of the Flask web server.

This script can be executed by cron or systemd timers to perform
the scheduled scraping without tying up the web server.

Includes file locking to prevent overlapping executions.
"""
import sys
import time
import fcntl
import logging
from pathlib import Path

from src.scraper.config import WEBSITES
from src.scraper.scraper import parse_pages
from src.scraper.mongo_db import save_scraped_data


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler('/var/log/scraper_job.log'),
        logging.StreamHandler(sys.stdout)
    ]
)


logger = logging.getLogger(__name__)


def acquire_lock():
    try:
        lock_file = open('/tmp/scraper.lock', 'w')

        fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)

        lock_file.write(str(time.time()))
        lock_file.flush()

        return lock_file
    
    except (IOError, OSError):
        return None


def run_scraper():
    """Perform the scraping operation with lock protection.
    """
    lock_file = acquire_lock()
    if not lock_file:
        logger.warning("Another scraper instance is already running. Exiting.")
        return True  # don't error, just skip this run
    
    try:
        logger.info("Starting scrape via cron...")
        data = parse_pages(WEBSITES)

        if not data.get("saves"):
            logger.info("No articles found matching keywords")
            return True
        
        save_scraped_data(data)

        return True
        
    except Exception as e:
        logger.error(f"Scrape job failed: {e}", exc_info=True)
        return False
    
    finally:
        if lock_file:  # release the lock
            fcntl.flock(lock_file.fileno(), fcntl.LOCK_UN)
            lock_file.close()

            try:
                Path('/tmp/scraper.lock').unlink()

            except FileNotFoundError:
                pass


if __name__ == "__main__":
    success = run_scraper()
    sys.exit(0 if success else 1)
