# import os
# from dotenv import load_dotenv
# from telegram import Update, KeyboardButton, ReplyKeyboardMarkup
# from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
# import logging
# from math import radians, sin, cos, sqrt, atan2

# # Load environment variables
# load_dotenv()
# TOKEN = os.getenv("TOKEN")

# # Set up logging
# logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
# logger = logging.getLogger(__name__)

# locations = {
#     # Southwest Addis (includes areas like Akaki Kaliti, Nifas Silk-Lafto)
#     "Southwest Addis": [
#         {"name": "Akaki Kaliti Subcity", "coordinates": (8.90, 38.79)},
#         {"name": "Akaki Kaliti Market", "coordinates": (8.90, 38.78)},
#         {"name": "Akaki River", "coordinates": (8.89, 38.77)},
#         {"name": "Kaliti Park", "coordinates": (8.91, 38.79)},
#         {"name": "Addis Ababa Ceramic Factory", "coordinates": (8.90, 38.81)},
#         {"name": "Akaki Kaliti Police Station", "coordinates": (8.91, 38.78)},
#         {"name": "Eastern Industrial Zone", "coordinates": (8.89, 38.80)},
#         {"name": "Dembel City Mall", "coordinates": (8.91, 38.79)},
#         {"name": "Nifas Silk-Lafto Subcity", "coordinates": (9.03, 38.75)},
#         {"name": "Lafto Market", "coordinates": (9.02, 38.76)},
#         {"name": "Hawassa Street", "coordinates": (9.03, 38.75)},
#         {"name": "Megenagna", "coordinates": (9.03, 38.77)},
#         {"name": "Nifas Silk Park", "coordinates": (9.03, 38.77)},
#         {"name": "Lafto Church", "coordinates": (9.02, 38.77)},
#         {"name": "Bole Subcity Shopping Center", "coordinates": (9.02, 38.76)},
#         {"name": "Lafto Club", "coordinates": (9.02, 38.76)},
#         {"name": "Nifas Silk-Lafto Stadium", "coordinates": (9.03, 38.76)},
#         {"name": "Lafto Community Center", "coordinates": (9.02, 38.76)},
#         {"name": "Akaki Kaliti Health Center", "coordinates": (8.90, 38.79)},
#         {"name": "Lafto Industrial Park", "coordinates": (9.02, 38.77)},
#         {"name": "Dembel Commercial Complex", "coordinates": (8.91, 38.78)},
#         {"name": "Gurd Shola", "coordinates": (9.02, 38.75)},
#         {"name": "Bole Bridge", "coordinates": (9.03, 38.75)},
#         {"name": "Bole International Hotel", "coordinates": (9.02, 38.77)},
#     ],

 
#     "Western Addis": [
#         {"name": "Gullele Botanical Garden", "coordinates": (9.03, 38.83)},
#         {"name": "Entoto Park", "coordinates": (9.04, 38.83)},
#         {"name": "Entoto Hill", "coordinates": (9.02, 38.83)},
#         {"name": "Mount Entoto", "coordinates": (9.03, 38.84)},
#         {"name": "Gullele Subcity Market", "coordinates": (9.03, 38.83)},
#         {"name": "Addis Ababa Observatory", "coordinates": (9.03, 38.84)},
#         {"name": "Entoto Palace", "coordinates": (9.03, 38.82)},
#         {"name": "Entoto Natural Park", "coordinates": (9.03, 38.84)},
#         {"name": "Addis Ababa Memorial Park", "coordinates": (9.03, 38.82)},
#         {"name": "Gullele Community Hall", "coordinates": (9.03, 38.83)},
#         {"name": "Yeka Subcity", "coordinates": (9.03, 38.84)},
#         {"name": "Bole Bulbula", "coordinates": (9.03, 38.84)},
#         {"name": "Yeka Orthodox Church", "coordinates": (9.03, 38.85)},
#         {"name": "Yeka Town Center", "coordinates": (9.03, 38.83)},
#         {"name": "Fitawrari Haile Selassie Avenue", "coordinates": (9.03, 38.85)},
#         {"name": "Dembel City Center", "coordinates": (9.02, 38.84)},
#         {"name": "Bole Hills", "coordinates": (9.02, 38.85)},
#         {"name": "Yeka Park", "coordinates": (9.03, 38.84)},
#         {"name": "Lalibela Restaurant", "coordinates": (9.03, 38.84)},
#         {"name": "Yeka Subcity Hospital", "coordinates": (9.03, 38.84)},
#         {"name": "Entoto Mountains", "coordinates": (9.03, 38.85)},
#         {"name": "Gullele High School", "coordinates": (9.02, 38.83)},
#         {"name": "Addis Ababa's Peace Park", "coordinates": (9.02, 38.84)},
#         {"name": "Addis Ababa University - Entoto Campus", "coordinates": (9.04, 38.82)},
#     ],

#     "Eastern Addis": [
#         {"name": "Piazza", "coordinates": (9.03, 38.74)},
#         {"name": "St. George's Cathedral", "coordinates": (9.02, 38.75)},
#         {"name": "National Museum of Ethiopia", "coordinates": (9.03, 38.74)},
#         {"name": "Ethnological Museum", "coordinates": (9.03, 38.75)},
#         {"name": "Addis Ababa University", "coordinates": (9.03, 38.75)},
#         {"name": "Lion of Judah Monument", "coordinates": (9.03, 38.75)},
#         {"name": "Commercial Bank of Ethiopia", "coordinates": (9.03, 38.74)},
#         {"name": "Addis Ababa Railway Station", "coordinates": (9.02, 38.74)},
#         {"name": "Lideta Church", "coordinates": (9.02, 38.74)},
#         {"name": "Chamber of Commerce Building", "coordinates": (9.02, 38.75)},
#         {"name": "Arada Subcity", "coordinates": (9.03, 38.74)},
#         {"name": "Kirkos Subcity", "coordinates": (9.03, 38.74)},
#         {"name": "Addis Ketema Subcity", "coordinates": (9.03, 38.75)},
#         {"name": "Sar Bet Kidane Meheret Church", "coordinates": (9.04, 38.76)},
#         {"name": "Lideta Market", "coordinates": (9.02, 38.74)},
#         {"name": "Megenagna", "coordinates": (9.03, 38.77)},
#         {"name": "Addis Ababa City Hall", "coordinates": (9.03, 38.74)},
#         {"name": "Gulale Market", "coordinates": (9.02, 38.74)},
#         {"name": "Abyssinia Park", "coordinates": (9.03, 38.75)},
#         {"name": "Merkato", "coordinates": (9.03, 38.74)},
#         {"name": "Addis Ababa Stadium", "coordinates": (9.03, 38.76)},
#     ],

#     # Northern Addis (includes areas like Bole, Yeka, and parts of Gulele)
#     "Northern Addis": [
#         {"name": "Bole Medhanialem Church", "coordinates": (9.02, 38.77)},
#         {"name": "Bole International Hotel", "coordinates": (9.02, 38.77)},
#         {"name": "Edna Mall", "coordinates": (9.02, 38.75)},
#         {"name": "Friendship Mall", "coordinates": (9.02, 38.76)},
#         {"name": "Bole Subcity Market", "coordinates": (9.03, 38.75)},
#         {"name": "Bole Atlas", "coordinates": (9.02, 38.77)},
#         {"name": "Addis Ababa Bole International Airport", "coordinates": (9.03, 38.8)},
#         {"name": "Kenyatta Avenue", "coordinates": (9.03, 38.77)},
#         {"name": "Zefmesh Grand Mall", "coordinates": (9.02, 38.76)},
#         {"name": "Bole Dembel", "coordinates": (9.03, 38.75)},
#         {"name": "Gullele Museum", "coordinates": (9.03, 38.83)},
#         {"name": "Yeka Town Center", "coordinates": (9.03, 38.84)},
#         {"name": "Bole Hills", "coordinates": (9.02, 38.85)},
#         {"name": "Gurd Shola", "coordinates": (9.02, 38.75)},
#         {"name": "Megenagna", "coordinates": (9.03, 38.77)},
#     ],

#     # Central Addis (includes core locations such as Piazza, Arada, Lideta, Kirkos)
#     "Central Addis": [
#         {"name": "Piazza", "coordinates": (9.03, 38.74)},
#         {"name": "St. George's Cathedral", "coordinates": (9.02, 38.75)},
#         {"name": "National Museum of Ethiopia", "coordinates": (9.03, 38.74)},
#         {"name": "Ethnological Museum", "coordinates": (9.03, 38.75)},
#         {"name": "Addis Ababa University", "coordinates": (9.03, 38.75)},
#         {"name": "Lion of Judah Monument", "coordinates": (9.03, 38.75)},
#         {"name": "Commercial Bank of Ethiopia", "coordinates": (9.03, 38.74)},
#         {"name": "Addis Ababa Railway Station", "coordinates": (9.02, 38.74)},
#         {"name": "Lideta Church", "coordinates": (9.02, 38.74)},
#         {"name": "Chamber of Commerce Building", "coordinates": (9.02, 38.75)},
#         {"name": "Arada Subcity", "coordinates": (9.03, 38.74)},
#         {"name": "Kirkos Subcity", "coordinates": (9.03, 38.74)},
#         {"name": "Addis Ketema Subcity", "coordinates": (9.03, 38.75)},
#         {"name": "Sar Bet Kidane Meheret Church", "coordinates": (9.04, 38.76)},
#         {"name": "Lideta Market", "coordinates": (9.02, 38.74)},
#         {"name": "Addis Ababa City Hall", "coordinates": (9.03, 38.74)},
#         {"name": "National Theater", "coordinates": (9.02, 38.75)},
#         {"name": "Merkato", "coordinates": (9.03, 38.74)},
#         {"name": "Meskel Square", "coordinates": (9.03, 38.75)},
#         {"name": "Addis Ababa Cultural Center", "coordinates": (9.03, 38.74)},
#     ]
# }
# # Subcity centers with their coordinates
# subcities = {
#     'Bole': (9.0300, 38.7400),  # Example for Bole center (latitude, longitude)
#     'Addis Ketema': (9.0273, 38.7461),
#     'Akaki Kaliti': (8.8958, 38.7892),
#     'Arada': (9.0292, 38.7461),
#     'Gullele': (9.0373, 38.8350),
#     'Kirkos': (9.0273, 38.7461),
#     'Kolfe Keranio': (9.0273, 38.7461),
#     'Lideta': (9.0273, 38.7461),
#     'Nifas Silk-Lafto': (9.0273, 38.7461),
#     'Yeka': (9.0373, 38.8350),
#     'Lemi-Kura': (9.0273, 38.7461)
# }


# # Function to calculate the distance using Haversine formula
# def haversine(lat1, lon1, lat2, lon2):
#     # Radius of the Earth in kilometers
#     R = 6371.0

#     # Convert latitude and longitude from degrees to radians
#     lat1 = radians(lat1)
#     lon1 = radians(lon1)
#     lat2 = radians(lat2)
#     lon2 = radians(lon2)

#     # Differences in coordinates
#     dlat = lat2 - lat1
#     dlon = lon2 - lon1

#     # Haversine formula
#     a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
#     c = 2 * atan2(sqrt(a), sqrt(1 - a))

#     # Distance in kilometers
#     distance = R * c
#     return distance

# # Function to get places by category
# def get_places_by_category(category: str) -> list:
#     results = []
#     for area, places in locations.items():
#         for place in places:
#             if place.get("category") == category:
#                 results.append({**place, "area": area})
#     return results

# # Function to find nearby places
# def find_nearby_places(latitude: float, longitude: float, radius: float = 2.0) -> list:
#     nearby = []
#     for area, places in locations.items():
#         for place in places:
#             distance = haversine(latitude, longitude, *place["coordinates"])
#             if distance <= radius:
#                 nearby.append((place, distance, area))
#     return sorted(nearby, key=lambda x: x[1])  # Sort by distance


# # Function to find the nearest location and corresponding area
# def find_nearest_location_and_area(user_lat, user_lon):
#     nearest_location = None
#     nearest_distance = float('inf')
#     nearest_area = None

#     # Loop through all areas and locations
#     for area, locations_list in locations.items():
#         for location in locations_list:
#             loc_name = location["name"]
#             loc_lat, loc_lon = location["coordinates"]
#             distance = haversine(user_lat, user_lon, loc_lat, loc_lon)
            
#             if distance < nearest_distance:
#                 nearest_location = loc_name
#                 nearest_distance = distance
#                 nearest_area = area

#     return nearest_area, nearest_location, nearest_distance

# # Function to find the nearest subcity based on user's coordinates
# def find_nearest_subcity(user_lat, user_lon):
#     # Calculate the distance to each subcity and store them
#     distances = {subcity: haversine(user_lat, user_lon, lat, lon) for subcity, (lat, lon) in subcities.items()}
    
#     # Find the subcity with the minimum distance
#     nearest_subcity = min(distances, key=distances.get)
#     nearest_distance = distances[nearest_subcity]

#     return nearest_subcity, nearest_distance

# # Handle location sharing with area, subcity, and nearest location info
# async def handle_location(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     if update.message.location:
#         location = update.message.location
#         latitude = location.latitude
#         longitude = location.longitude

#         # Fallback for username if not available
#      # Log location receipt
#         user = update.message.from_user
#         logger.info(f"Location received from {user.first_name}: {latitude}, {longitude}")
            
#         # Find the nearest subcity based on location
#         subcity, subcity_distance = find_nearest_subcity(latitude, longitude)
#         nearby_places = find_nearby_places(latitude, longitude)
#         # Find the nearest area, location, and distance based on location
#         area, nearest_location, location_distance = find_nearest_location_and_area(latitude, longitude)

#         # Log the results
#         logging.info(f"User {username}'s location: Latitude={latitude}, Longitude={longitude}, Nearest Subcity={subcity}, Nearest Location={nearest_location}, Area={area}, Subcity Distance={subcity_distance:.2f} km, Location Distance={location_distance:.2f} km")

#         response = (
#             f"📍 **Your Location Details**:\n"
#             f"Latitude: `{latitude}`\n"
#             f"Longitude: `{longitude}`\n\n"
#             f"**Nearest Subcity:** {subcity} ({subcity_distance:.2f} km away)\n"
#             f"**Nearest Area:** {area}\n"
#             f"**Nearest Landmark:** {nearest_location} ({location_distance:.2f} km away)"
#         )
#         initial_response = (
#                 f"📍 *Your Location:* `{latitude:.4f}, {longitude:.4f}`\n\n"
#                 f"I found {len(nearby_places)} places within 2km of your location.\n\n"
#                 "*Nearby Places:*\n"
#             )
            
#             # Add details for up to 5 nearest places
#             for place, distance, area in nearby_places[:5]:
#                 initial_response += (
#                     f"\n🏢 *{place['name']}*\n"
#                     f"📍 {area}\n"
#                     f"📏 {distance:.1f}km away\n"
#                     f"🏷 {place['category']}\n"
#                     f"⏰ {place['opening_hours']}\n"
#                 )
#                 if 'price_range' in place:
#                     initial_response += f"💰 {place['price_range']}\n"
            
#             # Create category filter buttons
#             keyboard = [
#                 [InlineKeyboardButton("Show More Places", callback_data="more_places")],
#                 [InlineKeyboardButton("Filter by Category", callback_data="show_categories")]
#             ]
#             reply_markup = InlineKeyboardMarkup(keyboard)
            
#             await update.message.reply_text(
#                 initial_response,
#                 reply_markup=reply_markup,
#                 parse_mode='Markdown'
#             )
#         else:
#             await update.message.reply_text(
#                 "❌ I couldn't get your location. Please try sharing your location again."
#             )
            
#     except Exception as e:
#         logger.error(f"Error in handle_location: {str(e)}")
#         await update.message.reply_text(
#             "❌ Sorry, something went wrong. Please try again later."
#         )
# # Start command handler
# async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     user = update.message.from_user
#     logger.info(f"User {user.first_name} started the bot")
    
#     welcome_message = (
#         f"👋 Hello {user.first_name}!\n\n"
#         "Welcome to the Addis Ababa City Guide Bot. I can help you discover places around Addis Ababa.\n\n"
#         "Available commands:\n"
#         "/start - Start the bot\n"
#         "/help - Show help information\n"
#         "/categories - Show place categories\n\n"
#         "To get started, please share your location using the button below 📍"
#     )
    
#     location_button = KeyboardButton("Share Your Location 📍", request_location=True)
#     reply_markup = ReplyKeyboardMarkup([[location_button]], resize_keyboard=True, one_time_keyboard=True)
    
#     await update.message.reply_text(welcome_message, reply_markup=reply_markup)
# async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     help_text = """
# 🤖 *Addis Ababa City Guide Bot Help*

# *Available Commands:*
# /start - Start the bot
# /help - Show this help message
# /categories - Show all place categories

# *Features:*
# • Find nearby places based on your location
# • Filter places by category
# • Get detailed information about places
# • View opening hours and contact details
# • Find amenities and facilities

# *How to Use:*
# 1. Share your location using the button
# 2. Browse nearby places
# 3. Use category filters to find specific places
# 4. Tap on places to get more details

# *Categories Available:*
# • Hotels 🏨
# • Restaurants 🍽
# • Cafes ☕
# • Shopping & Entertainment 🛍
# • Museums 🏛
# • Parks & Recreation 🌳
# • Historical Sites 🏺
# • Religious Sites ⛪
# • Business Centers 🏢
# • Medical Facilities 🏥

# For any issues or feedback, contact: @YourBotSupport
#     """
#     await update.message.reply_text(help_text, parse_mode='Markdown')

# # Categories command handler
# async def categories_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     keyboard = []
#     for category in PLACE_CATEGORIES:
#         keyboard.append([InlineKeyboardButton(category, callback_data=f"category_{category}")])
    
#     reply_markup = InlineKeyboardMarkup(keyboard)
    
#     await update.message.reply_text(
#         "Select a category to view places:",
#         reply_markup=reply_markup
#     )
# async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     query = update.callback_query
#     await query.answer()
    
#     try:
#         if query.data.startswith("category_"):
#             category = query.data.replace("category_", "")
#             places = get_places_by_category(category)
            
#             response = f"📍 *{category} Locations:*\n\n"
#             for place in places[:5]:
#                 response += (
#                     f"🏢 *{place['name']}*\n"
#                     f"📍 Area: {place['area']}\n"
#                     f"ℹ️ {place['description']}\n"
#                     f"⏰ {place['opening_hours']}\n"
#                 )
#                 if 'contact' in place:
#                     response += f"📞 {place['contact']}\n"
#                 if 'price_range' in place:
#                     response += f"💰 {place['price_range']}\n"
#                 response += "\n"
            
#             keyboard = [[InlineKeyboardButton("Back to Categories", callback_data="show_categories")]]
#             reply_markup = InlineKeyboardMarkup(keyboard)
            
#             await query.message.edit_text(
#                 response,
#                 reply_markup=reply_markup,
#                 parse_mode='Markdown'
#             )
            
#         elif query.data == "show_categories":
#             keyboard = []
#             for category in PLACE_CATEGORIES:
#                 keyboard.append([InlineKeyboardButton(category, callback_data=f"category_{category}")])
            
#             reply_markup = InlineKeyboardMarkup(keyboard)
            
#             await query.message.edit_text(
#                 "Select a category to view places:",
#                 reply_markup=reply_markup
#             )
            
#     except Exception as e:
#         logger.error(f"Error in button_callback: {str(e)}")
#         await query.message.reply_text(
#             "❌ Sorry, something went wrong. Please try again later."
#         )

# # Error handler
# async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     logger.error(f"Update {update} caused error {context.error}")
#     try:
#         if update.message:
#             await update.message.reply_text(
#                 "❌ Sorry, something went wrong. Please try again later."
#             )
#     except:
#         pass
# # Main function
# if __name__ == "__main__":
#     # Create the bot application
#     app = Application.builder().token(TOKEN).build()

#     # Add handlers
#     app.add_handler(CommandHandler("start", start_command))  # Start command
#     app.add_handler(MessageHandler(filters.LOCATION, handle_location))  # Handle location sharing
#     app.add_handler(CommandHandler("help", help_command))
#     app.add_handler(CommandHandler("categories", categories_command))
#     app.add_handler(MessageHandler(filters.LOCATION, handle_location))
#     app.add_handler(CallbackQueryHandler(button_callback))
    
#     app.add_error_handler(error_handler)
    
#     # Start the bot
#     print("Bot is running...")
#     # Start polling
#     logger.info("Bot started successfully!")
#     app.run_polling(allowed_updates=Update.ALL_TYPES)
    



import os
import logging
from math import radians, sin, cos, sqrt, atan2
from datetime import datetime
from dotenv import load_dotenv
from telegram import (
    Update, 
    KeyboardButton, 
    ReplyKeyboardMarkup,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
    CallbackQueryHandler
)

# Load environment variables
load_dotenv()
TOKEN = os.getenv("TOKEN")

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Location data with expanded categories
locations = {
    "Bole Area": [
        {
            "name": "Bole International Airport",
            "coordinates": (8.9778, 38.7993),
            "category": "Transportation",
            "description": "Main international gateway to Ethiopia",
            "opening_hours": "24/7",
            "amenities": ["ATMs", "VIP Lounges", "Duty Free"]
        },
        {
            "name": "St. Paul's Hospital",
            "coordinates": (8.9800, 38.7900),
            "category": "Medical Facilities 🏥",
            "description": "General hospital with emergency services",
            "opening_hours": "24/7",
            "contact": "+251-116-181-818"
        }
    ],
    "Piazza Area": [
        {
            "name": "Holy Trinity Cathedral",
            "coordinates": (9.0350, 38.7570),
            "category": "Religious Sites ⛪",
            "description": "Burial site of Emperor Haile Selassie",
            "opening_hours": "8:00-18:00",
            "entrance_fee": "200 ETB"
        }
    ],
    "Meskel Square": [
        {
            "name": "Addis Ababa Stadium",
            "coordinates": (9.0167, 38.7633),
            "category": "Sports",
            "description": "Main sports stadium",
            "capacity": "35,000 seats"
        }
    ]
}

# Category list for filtering
CATEGORIES = [
    "Hotels 🏨", "Restaurants 🍽", "Cafes ☕",
    "Shopping & Entertainment 🛍", "Museums 🏛",
    "Parks & Recreation 🌳", "Historical Sites 🏺",
    "Religious Sites ⛪", "Business Centers 🏢",
    "Medical Facilities 🏥"
]

def haversine(lat1, lon1, lat2, lon2):
    """Calculate distance between two coordinates"""
    R = 6371  # Earth radius in km
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat/2)**2 + cos(lat1)*cos(lat2)*sin(dlon/2)**2
    return R * 2 * atan2(sqrt(a), sqrt(1 - a))

def find_nearby(lat, lon, radius=2.0):
    """Find places within given radius"""
    nearby = []
    for area, places in locations.items():
        for place in places:
            distance = haversine(lat, lon, *place["coordinates"])
            if distance <= radius:
                nearby.append((place, distance, area))
    return sorted(nearby, key=lambda x: x[1])

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    user = update.message.from_user
    welcome_msg = (
        f"👋 Welcome {user.first_name}!\n\n"
        "I'm your Addis Ababa Guide Bot. Here's what I can do:\n"
        "/findme - Get location-based assistance\n"
        "/guide - City information and tips\n"
        "/categories - Browse places by category"
    )
    await update.message.reply_text(welcome_msg)

async def findme_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /findme command for location assistance"""
    response = (
        "📍 **Location Assistance**\n\n"
        "Share your location to find:\n"
        "- Nearby landmarks\n"
        "- Emergency services\n"
        "- Helpful locations\n\n"
        "Please share your location:"
    )
    location_btn = KeyboardButton("Share Location 📍", request_location=True)
    reply_markup = ReplyKeyboardMarkup([[location_btn]], resize_keyboard=True)
    await update.message.reply_text(response, reply_markup=reply_markup)

async def handle_location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Process shared location"""
    try:
        location = update.message.location
        lat, lon = location.latitude, location.longitude
        nearby = find_nearby(lat, lon)
        
        response = "📍 **Nearby Locations**\n\n"
        for place, dist, area in nearby[:5]:
            response += (
                f"🏷 {place['name']}\n"
                f"📏 {dist:.1f}km | 📍 {area}\n"
                f"📌 {place['description']}\n"
            )
            if 'contact' in place:
                response += f"📞 {place['contact']}\n"
            response += "\n"
        
        await update.message.reply_text(response)
        
    except Exception as e:
        logger.error(f"Location error: {e}")
        await update.message.reply_text("❌ Error processing location")

async def guide_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /guide command"""
    keyboard = [
        [InlineKeyboardButton("Top Attractions", callback_data="guide_attractions")],
        [InlineKeyboardButton("Safety Tips", callback_data="guide_safety")],
        [InlineKeyboardButton("Transportation", callback_data="guide_transport")]
    ]
    response = (
        "🏙 **City Guide**\n\n"
        "Choose a category:\n"
        "1. Key attractions\n"
        "2. Safety information\n"
        "3. Transport options"
    )
    await update.message.reply_text(response, reply_markup=InlineKeyboardMarkup(keyboard))

async def handle_callbacks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle all callback queries"""
    query = update.callback_query
    await query.answer()
    
    if query.data.startswith("guide_"):
        category = query.data[6:]
        content = {
            "attractions": (
                "🌟 **Top Attractions**\n\n"
                "1. National Museum\n"
                "2. Entoto Mountain\n"
                "3. Merkato Market"
            ),
            "safety": (
                "🛡 **Safety Tips**\n\n"
                "1. Use registered taxis\n"
                "2. Emergency: 991\n"
                "3. Keep valuables secure"
            ),
            "transport": (
                "🚕 **Transportation**\n\n"
                "1. Blue-white taxis are safest\n"
                "2. Ride apps available\n"
                "3. Public buses available"
            )
        }.get(category, "Information not available")
        
        await query.edit_message_text(content)

async def categories_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /categories command"""
    keyboard = [[InlineKeyboardButton(cat, callback_data=f"cat_{cat}")] for cat in CATEGORIES]
    await update.message.reply_text(
        "🏙 **Categories**\nChoose a category:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle errors"""
    logger.error(f"Error: {context.error}")
    if update.message:
        await update.message.reply_text("❌ An error occurred")

def main():
    """Run the bot"""
    app = Application.builder().token(TOKEN).build()
    
    # Command handlers
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("findme", findme_command))
    app.add_handler(CommandHandler("guide", guide_command))
    app.add_handler(CommandHandler("categories", categories_command))
    
    # Message handlers
    app.add_handler(MessageHandler(filters.LOCATION, handle_location))
    app.add_handler(CallbackQueryHandler(handle_callbacks))
    
    # Error handler
    app.add_error_handler(error_handler)
    
    logger.info("Bot running...")
    app.run_polling()

if __name__ == "__main__":
    main()