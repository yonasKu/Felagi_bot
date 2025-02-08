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


# Updated CATEGORIES with consistent naming and emojis
CATEGORIES = [
    ("Hotels 🏨", "Hotels"),
    ("Restaurants 🍽", "Restaurants"),
    ("Cafes ☕", "Cafes"),
    ("Shopping & Entertainment 🛍", "Shopping"),
    ("Museums 🏛", "Museums"),
    ("Parks & Recreation 🌳", "Parks"),
    ("Historical Sites 🏺", "Historical"),
    ("Religious Sites ⛪", "Religious"),
    ("Business Centers 🏢", "Business"),
    ("Medical Facilities 🏥", "Medical"),
    ("Transportation 🚆", "Transportation"),
    ("Sports ⚽", "Sports")
]

CATEGORY_DISPLAY = {key: display for display, key in CATEGORIES}
CATEGORY_MAPPING = {key: display for display, key in CATEGORIES}

# Updated locations to use consistent category keys from CATEGORIES
locations = {
    "Bole Area": [
        {
            "name": "Bole International Airport",
            "coordinates": (8.9778, 38.7993),
            "category": "Transportation",  # Fixed to match CATEGORIES
            "description": "Main international gateway to Ethiopia",
            "opening_hours": "24/7",
            "amenities": ["ATMs", "VIP Lounges", "Duty Free"]
        },
        {
            "name": "St. Paul's Hospital",
            "coordinates": (8.9800, 38.7900),
            "category": "Medical",  # Fixed to match CATEGORIES
            "description": "General hospital with emergency services",
            "opening_hours": "24/7",
            "contact": "+251-116-181-818"
        }
    ],
    "Piazza Area": [
        {
            "name": "Holy Trinity Cathedral",
            "coordinates": (9.0350, 38.7570),
            "category": "Religious",  # Fixed to match CATEGORIES
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
    """Handle all callback queries including category selection"""
    query = update.callback_query
    await query.answer()
    
    if query.data.startswith("guide_"):
        guide_content = {
            "guide_attractions": (
                "🎯 **Top Attractions**\n\n"
                "1. Unity Park\n"
                "2. National Museum\n"
                "3. Entoto Park\n"
                "4. Holy Trinity Cathedral\n"
                "5. Merkato Market"
            ),
            "guide_safety": (
                "🛡️ **Safety Tips**\n\n"
                "• Keep valuables secure\n"
                "• Use registered taxis\n"
                "• Stay aware in crowded areas\n"
                "• Keep emergency numbers handy\n"
                "• Carry minimal cash"
            ),
            "guide_transport": (
                "🚗 **Transportation Options**\n\n"
                "• Light Rail Transit\n"
                "• City Buses\n"
                "• Ride-sharing services\n"
                "• Blue and white taxis\n"
                "• Car rentals"
            )
        }
        content = guide_content.get(query.data, "❌ Invalid guide section")
        await query.edit_message_text(content, parse_mode="Markdown")
    elif query.data.startswith("cat_"):
        try:
            category_key = query.data[4:]
            category_display = CATEGORY_MAPPING.get(category_key)
            if not category_display:
                raise ValueError(f"Invalid category: {category_key}")
            
            places_list = []
            for area, places in locations.items():
                for place in places:
                    if place.get("category") == category_key:
                        places_list.append((place, area))
            
            if not places_list:
                await query.edit_message_text(
                    f"🚫 No places found in category: {category_display}",
                    parse_mode="Markdown"
                )
                return
            
            response = f"📍 **{category_display}**\n\n"
            for place, area in places_list:
                response += (
                    f"🏷 *{place['name']}* ({area})\n"
                    f"📌 {place['description']}\n"
                )
                if 'opening_hours' in place:
                    response += f"🕒 {place['opening_hours']}\n"
                if 'contact' in place:
                    response += f"📞 {place['contact']}\n"
                response += "\n"
            
            await query.edit_message_text(response, parse_mode="Markdown")
        except Exception as e:
            logger.error(f"Category handling error: {e}")
            await query.edit_message_text(
                "❌ Error processing category request",
                parse_mode="Markdown"
            )
    else:
        await query.edit_message_text(
            "❌ Unknown option selected",
            parse_mode="Markdown"
        )

async def categories_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /categories command with improved layout"""
    buttons = [
        InlineKeyboardButton(CATEGORY_DISPLAY[key], callback_data=f"cat_{key}")
        for _, key in CATEGORIES
    ]
    # Arrange buttons in two columns per row
    keyboard = [buttons[i:i+2] for i in range(0, len(buttons), 2)]
    
    await update.message.reply_text(
        "🏙 **Categories**\nChoose a category:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle errors"""
    logger.error(f"Error: {context.error}")
    if update.message:
        await update.message.reply_text("❌ An error occurred")

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle callback queries"""
    query = update.callback_query
    await query.answer()
    
    try:
        if query.data.startswith("category_"):
            category = query.data.replace("category_", "")
            places = get_places_by_category(category)
            
            if not places:
                response = f"📍 No locations found for *{category}*"
                keyboard = [[InlineKeyboardButton("◀️ Back to Categories", callback_data="show_categories")]]
            else:
                response = f"📍 *{category} Locations:*\n\n"
                for place in places[:5]:
                    response += (
                        f"🏢 *{place['name']}*\n"
                        f"📍 Area: {place['area']}\n"
                    )
                    if 'description' in place:
                        response += f"ℹ️ {place['description']}\n"
                    if 'opening_hours' in place:
                        response += f"⏰ {place['opening_hours']}\n"
                    if 'contact' in place:
                        response += f"📞 {place['contact']}\n"
                    response += "\n"
                
                keyboard = [
                    [InlineKeyboardButton("◀️ Back to Categories", callback_data="show_categories")],
                    [InlineKeyboardButton("🔄 Show More", callback_data=f"more_category_{category}")]
                ]

        elif query.data.startswith("more_category_"):
            category = query.data.replace("more_category_", "")
            places = get_places_by_category(category)
            offset = context.user_data.get(f"offset_{category}", 5)
            
            response = f"📍 *{category} Locations (Continued):*\n\n"
            for place in places[offset:offset+5]:
                response += (
                    f"🏢 *{place['name']}*\n"
                    f"📍 Area: {place['area']}\n"
                )
                if 'description' in place:
                    response += f"ℹ️ {place['description']}\n"
                if 'opening_hours' in place:
                    response += f"⏰ {place['opening_hours']}\n"
                if 'contact' in place:
                    response += f"📞 {place['contact']}\n"
                response += "\n"
            
            context.user_data[f"offset_{category}"] = offset + 5
            
            keyboard = [
                [InlineKeyboardButton("◀️ Previous", callback_data=f"prev_category_{category}")],
                [InlineKeyboardButton("🏠 Main Menu", callback_data="back_to_main")],
                [InlineKeyboardButton("▶️ Next", callback_data=f"more_category_{category}")]
            ]
            
            if offset + 5 >= len(places):
                keyboard.pop()  # Remove "Next" button if no more places
            if offset <= 5:
                keyboard.pop(0)  # Remove "Previous" button if at start

        elif query.data.startswith("prev_category_"):
            category = query.data.replace("prev_category_", "")
            offset = context.user_data.get(f"offset_{category}", 5)
            context.user_data[f"offset_{category}"] = max(0, offset - 10)
            return await button_callback(update, context)  # Reuse more_category logic

        elif query.data.startswith("subcity_"):
            subcity = query.data.replace("subcity_", "")
            response = get_subcity_info(subcity)
            keyboard = [
                [InlineKeyboardButton("🏠 Main Menu", callback_data="back_to_main")],
                [InlineKeyboardButton("📍 Nearby Places", callback_data=f"nearby_subcity_{subcity}")]
            ]

        elif query.data == "show_categories":
            keyboard = []
            for category in PLACE_CATEGORIES:
                keyboard.append([InlineKeyboardButton(category, callback_data=f"category_{category}")])
            keyboard.append([InlineKeyboardButton("🏠 Main Menu", callback_data="back_to_main")])
            response = "🏷 *Select a category to view places:*"

        elif query.data == "back_to_main":
            response = (
                "🏙 *Welcome to Addis Ababa City Guide!*\n\n"
                "What would you like to do?\n\n"
                "• Browse places by category\n"
                "• Find nearby places\n"
                "• Get subcity information\n"
                "• View area details"
            )
            keyboard = [
                [InlineKeyboardButton("🏷 Categories", callback_data="show_categories")],
                [InlineKeyboardButton("📍 Share Location", callback_data="request_location")],
                [InlineKeyboardButton("ℹ️ Help", callback_data="show_help")]
            ]

        elif query.data == "request_location":
            response = (
                "📍 *Share Your Location*\n\n"
                "Please use the button below to share your location:"
            )
            location_button = KeyboardButton("Share Location 📍", request_location=True)
            keyboard = [[location_button]]
            reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
            await query.message.reply_text(response, reply_markup=reply_markup, parse_mode='Markdown')
            return

        else:
            response = "❌ Invalid selection"
            keyboard = [[InlineKeyboardButton("🏠 Main Menu", callback_data="back_to_main")]]

        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.edit_text(
            response,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
            
    except Exception as e:
        logger.error(f"Callback error: {str(e)}")
        error_keyboard = [[InlineKeyboardButton("🏠 Main Menu", callback_data="back_to_main")]]
        await query.message.edit_text(
            "❌ Error processing request. Please try again.",
            reply_markup=InlineKeyboardMarkup(error_keyboard),
            parse_mode='Markdown'
        )

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