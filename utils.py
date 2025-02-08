import json
import logging
import os
from geopy.distance import geodesic
from datetime import datetime
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup
from telegram.ext import ConversationHandler
from config import RADIUS_SEARCH, LOCATIONS_FILE, MAX_RESULTS, SUPPORTED_CATEGORIES

# Category Constants
CATEGORY_EMOJIS = {
    "Hotels": "🏨",
    "Restaurants": "🍽️",
    "Cafes": "☕",
    "Shopping": "🛍️",
    "Entertainment": "🎭",
    "Education": "📚",
    "Healthcare": "🏥",
    "Banks": "🏦",
    "Sports": "⚽",
    "Cultural": "🏛️"
}

# Logging Setup
def setup_logger(name):
    if not os.path.exists('logs'):
        os.makedirs('logs')
    
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    
    current_date = datetime.now().strftime('%Y-%m-%d')
    file_handler = logging.FileHandler(f'logs/{current_date}.log', encoding='utf-8')
    error_handler = logging.FileHandler(f'logs/errors_{current_date}.log', encoding='utf-8')
    console_handler = logging.StreamHandler()
    
    log_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(log_format)
    error_handler.setFormatter(log_format)
    console_handler.setFormatter(log_format)
    
    logger.addHandler(file_handler)
    logger.addHandler(error_handler)
    logger.addHandler(console_handler)
    
    return logger

# Location Functions
def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate distance between two points using geopy"""
    return geodesic((lat1, lon1), (lat2, lon2)).meters

def format_distance(meters: float) -> str:
    """Format distance in a human-readable way"""
    if meters < 1000:
        return f"{int(meters)}m"
    else:
        return f"{meters/1000:.1f}km"

def load_locations():
    """Load locations from JSON file"""
    try:
        with open(LOCATIONS_FILE, 'r', encoding='utf-8') as file:
            data = json.load(file)
            locations = data.get('locations', [])
            for location in locations:
                if not validate_location_data(location):
                    logger.warning(f"Invalid location data: {location.get('name', 'Unknown')}")
            return locations
    except Exception as e:
        logger.error(f"Error loading locations: {str(e)}")
        return []

def debug_category_search(category, places):
    """Debug helper for category searches"""
    logger.debug(f"""
    Category Search Debug:
    Category: {category}
    Number of places: {len(places)}
    Places found: {[place['name'] for place in places]}
    Raw data sample: {places[0] if places else 'No places found'}
    """)

def get_nearby_places(latitude: float, longitude: float, max_distance: int = RADIUS_SEARCH) -> tuple:
    """Get nearby places within specified radius. If max_distance is None, return all places with distances."""
    try:
        if not os.path.exists(LOCATIONS_FILE):
            logger.error(f"Locations file not found: {LOCATIONS_FILE}")
            return [], "File not found"

        with open(LOCATIONS_FILE, 'r', encoding='utf-8') as file:
            data = json.load(file)

        nearby_places = []
        total_places = len(data.get('locations', []))
        logger.info(f"Searching through {total_places} locations...")

        for place in data.get('locations', []):
            coords = place.get('coordinates', {})
            if coords:
                try:
                    distance = calculate_distance(
                        latitude,
                        longitude,
                        float(coords['latitude']),
                        float(coords['longitude'])
                    )
                    # Add distance to place data
                    place_copy = place.copy()
                    place_copy['distance'] = int(distance)
                    
                    # If max_distance is None, add all places
                    # Otherwise, only add places within max_distance
                    if max_distance is None or distance <= max_distance:
                        nearby_places.append(place_copy)
                        
                except ValueError as ve:
                    logger.warning(f"Invalid coordinates for place {place.get('name')}: {ve}")
                    continue

        if not nearby_places:
            if max_distance:
                logger.info(f"No places found within {max_distance}m of coordinates ({latitude}, {longitude})")
            else:
                logger.info(f"No places found in the database")
            return [], "No places found"

        # Sort by distance
        nearby_places.sort(key=lambda x: x.get('distance', float('inf')))
        found_places = len(nearby_places)
        logger.info(f"Found {found_places} places{f' within {max_distance}m radius' if max_distance else ''}")
        
        return nearby_places, "OK"

    except json.JSONDecodeError as je:
        logger.error(f"Error parsing locations file: {str(je)}")
        return [], "Invalid locations data"
    except Exception as e:
        logger.error(f"Error getting nearby places: {str(e)}", exc_info=True)
        return [], str(e)

# Navigation Functions
async def show_main_menu(update: Update, context):
    """Show the main menu"""
    try:
        # Simplified menu with only necessary options
        keyboard = [
            [InlineKeyboardButton("🔍 Find Places Nearby", callback_data="nav_findme")],
            [InlineKeyboardButton("📋 Categories", callback_data="nav_categories")],
            [InlineKeyboardButton("ℹ️ Info", callback_data="nav_info")]
        ]
        
        message = (
            "👋 Welcome to Addis Places Bot!\n\n"
            "Discover the best locations in Addis Ababa:\n"
            "• Find nearby places\n"
            "• Browse by category\n"
            "• Get information"
        )
        
        if update.callback_query:
            await update.callback_query.message.edit_text(
                message,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode='Markdown'
            )
        else:
            await update.message.reply_text(
                message,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode='Markdown'
            )
            
    except Exception as e:
        logger.error(f"Menu display error: {str(e)}")
        await handle_error(update, "Could not show menu")

async def show_results(update, places, category=None):
    """Format and display search results"""
    try:
        if not places:
            keyboard = [[InlineKeyboardButton("🔙 Back to Main Menu", callback_data="menu_back")]]
            await update.message.reply_text(
                "No places found.",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
            return

        response = "🎯 Nearby Places:\n\n"
        for place in places:
            emoji = CATEGORY_EMOJIS.get(place.get('category'), "📍")
            response += f"{emoji} *{place['name']}*\n"
            if 'distance' in place:
                response += f"📏 {place['distance']}m away\n"
            if 'description' in place:
                response += f"ℹ️ {place['description']}\n"
            response += "\n"

        keyboard = [
            [InlineKeyboardButton("See More Places", callback_data="more_results")],
            [InlineKeyboardButton("🔙 Back to Main Menu", callback_data="menu_back")]
        ]
        
        await update.message.reply_text(
            response,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )
    
    except Exception as e:
        logger.error(f"Error showing results: {str(e)}", exc_info=True)

# Add to utils.py
logger = setup_logger('utils')

def debug_log(update: Update, handler_name: str):
    """Debug logging helper"""
    try:
        user = update.effective_user
        if update.callback_query:
            logger.debug(f"{handler_name}: Callback from User {user.id} - {update.callback_query.data}")
        elif update.message:
            logger.debug(f"{handler_name}: Message from User {user.id} - {update.message.text}")
    except Exception as e:
        logger.error(f"Error in debug logging: {str(e)}")

# Helper Functions
def get_category_emoji(category):
    return CATEGORY_EMOJIS.get(category, "📍")

def validate_location_data(location):
    """Validate location data structure"""
    required_fields = ['name', 'coordinates', 'category']
    return all(field in location for field in required_fields)

# Error Handling
async def handle_error(update: Update, error_message: str):
    """Handle errors and show appropriate messages to user"""
    logger = setup_logger('error_handler')
    logger.error(f"Error: {error_message}")
    
    try:
        keyboard = [[InlineKeyboardButton("🔙 Back to Main Menu", callback_data="menu_back")]]
        
        if update.callback_query:
            await update.callback_query.message.edit_text(
                f"Sorry, an error occurred: {error_message}",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
            await update.callback_query.answer()
        else:
            await update.effective_message.reply_text(
                f"Sorry, an error occurred: {error_message}",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
    except Exception as e:
        logger.error(f"Error in error handler: {str(e)}", exc_info=True)