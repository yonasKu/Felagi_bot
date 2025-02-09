import schedule
import time
from utils.osm_fetcher import update_locations_data
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def scheduled_update():
    """Run scheduled update of locations data"""
    logger.info("Running scheduled location data update")
    if update_locations_data():
        logger.info("Scheduled update completed successfully")
    else:
        logger.error("Scheduled update failed")

def main():
    # Schedule updates to run daily at 3 AM
    schedule.every().day.at("03:00").do(scheduled_update)
    
    # Run initial update
    scheduled_update()
    
    # Keep the script running
    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    main() 