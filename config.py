import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Bot token from environment variable
TOKEN = os.getenv("TOKEN")

# Constants
RADIUS_SEARCH = 2000  # 2km radius for Addis context
MAX_RESULTS = 5
SUPPORTED_CATEGORIES = [
    "Hotels",
    "Restaurants",
    "Cafes",
    "Shopping",
    "Entertainment",
    "Education",
    "Healthcare",
    "Banks",
    "Sports",
    "Cultural"
]

# Path to JSON data file
LOCATIONS_FILE = "data/locations.json"