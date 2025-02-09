from telegram import (
    Update,
    KeyboardButton,
    ReplyKeyboardMarkup,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ReplyKeyboardRemove,
)
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    CommandHandler,
    CallbackQueryHandler,
    filters,
)
from utils import setup_logger, get_nearby_places, handle_error, format_distance
from config import RADIUS_SEARCH, SUPPORTED_CATEGORIES
import json
import os
from math import radians, sin, cos, sqrt, atan2

logger = setup_logger("findme_handler")

# Constants
ITEMS_PER_PAGE = 6  # Number of items per page

# States
LOCATION = 1
CATEGORY_SELECTION = 2


class FindMeHandler:
    """Handler for Find Nearby Places functionality"""

    def __init__(self):
        self.locations = self.load_locations()

    @staticmethod
    def load_locations():
        """Load locations from JSON file"""
        try:
            with open("data/locations.json", "r", encoding="utf-8") as f:
                return json.load(f)["locations"]
        except Exception as e:
            logger.error(f"Error loading locations: {str(e)}")
            return []

    @staticmethod
    def calculate_distance(lat1, lon1, lat2, lon2):
        """Calculate distance between two points in kilometers"""
        R = 6371  # Earth's radius in kilometers

        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
        dlat = lat2 - lat1
        dlon = lon2 - lon1

        a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))
        distance = R * c

        return distance

    @staticmethod
    def get_nearby_places(latitude, longitude, radius_meters):
        """Get nearby places within specified radius"""
        try:
            handler = FindMeHandler()
            nearby_places = []
            radius_km = radius_meters / 1000  # Convert to kilometers

            for place in handler.locations:
                if not place.get("coordinates"):
                    continue

                distance = handler.calculate_distance(
                    latitude,
                    longitude,
                    place["coordinates"]["latitude"],
                    place["coordinates"]["longitude"],
                )

                if distance <= radius_km:
                    place_copy = place.copy()
                    place_copy["distance"] = distance
                    nearby_places.append(place_copy)

            # Sort by distance
            nearby_places.sort(key=lambda x: x["distance"])
            return nearby_places, "OK"

        except Exception as e:
            logger.error(f"Error getting nearby places: {str(e)}")
            return [], "ERROR"

    @staticmethod
    async def start_findme(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Start the findme flow via command or button"""
        try:
            user = update.effective_user
            logger.info(f"Find Nearby Places initiated by User {user.id}")

            keyboard = [[KeyboardButton("📍 Share Location", request_location=True)]]
            reply_markup = ReplyKeyboardMarkup(
                keyboard, resize_keyboard=True, one_time_keyboard=True
            )

            message = (
                "📍 Please share your location to find nearby places.\n\n"
                "I'll show you the closest places within "
                f"{RADIUS_SEARCH / 1000:.1f}km of your location."
            )

            if update.callback_query:
                await update.callback_query.answer()
                await update.callback_query.message.edit_reply_markup(reply_markup=None)
                await update.callback_query.message.reply_text(
                    message, reply_markup=reply_markup
                )
            else:
                await update.message.reply_text(message, reply_markup=reply_markup)

            return LOCATION

        except Exception as e:
            logger.error(f"Error in start_findme: {str(e)}", exc_info=True)
            await handle_error(update, "Failed to start location search")
            return ConversationHandler.END

    @staticmethod
    async def process_location(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Process the received location"""
        try:
            user = update.effective_user
            logger.info(f"Processing location for User {user.id}")

            if not update.message or not update.message.location:
                await update.message.reply_text(
                    "⚠️ Please use the Share Location button.",
                    reply_markup=ReplyKeyboardMarkup(
                        [[KeyboardButton("📍 Share Location", request_location=True)]],
                        one_time_keyboard=True,
                    ),
                )
                return LOCATION

            location = update.message.location
            # Store location in context for category search
            context.user_data["last_location"] = {
                "latitude": location.latitude,
                "longitude": location.longitude,
            }

            logger.info(
                f"Received location: lat={location.latitude}, lon={location.longitude}"
            )

            # Remove location keyboard and show processing message
            await update.message.reply_text(
                "🔍 Finding places near you...", reply_markup=ReplyKeyboardRemove()
            )

            # Get nearby places
            places, status = FindMeHandler.get_nearby_places(
                location.latitude, location.longitude, RADIUS_SEARCH
            )

            if status == "OK" and places:
                # Show first page of results
                page = 1
                start_idx = (page - 1) * ITEMS_PER_PAGE
                end_idx = start_idx + ITEMS_PER_PAGE
                current_places = places[start_idx:end_idx]
                total_pages = (len(places) + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE

                response = (
                    f"🎯 *Nearest Places to You*\nPage {page} of {total_pages}\n\n"
                )
                for place in current_places:
                    response += f"📍 *{place['name']}*\n"
                    response += f"🏢 Category: {place['category']}\n"
                    response += f"📏 Distance: {place['distance']:.1f}km\n"
                    if place.get("description"):
                        response += f"ℹ️ {place['description']}\n"
                    if place.get("opening_hours"):
                        response += f"🕒 {place['opening_hours']}\n"
                    if place.get("contact"):
                        contact = place["contact"]
                        if contact.get("phone"):
                            response += f"📞 {contact['phone']}\n"
                        if contact.get("website"):
                            response += f"🌐 {contact['website']}\n"
                    response += "\n"

                # Create navigation buttons
                keyboard = []
                nav_row = []

                if page < total_pages:
                    nav_row.append(
                        InlineKeyboardButton(
                            "See More ▶️", callback_data=f"page_all_{page + 1}"
                        )
                    )

                if nav_row:
                    keyboard.append(nav_row)

                # Add category and menu buttons
                keyboard.extend(
                    [
                        [
                            InlineKeyboardButton(
                                "📋 Browse by Category", callback_data="show_categories"
                            )
                        ],
                        [
                            InlineKeyboardButton(
                                "🔍 Search Again", callback_data="nav_findme"
                            )
                        ],
                        [
                            InlineKeyboardButton(
                                "🔙 Back to Menu", callback_data="menu_back"
                            )
                        ],
                    ]
                )

                await update.message.reply_text(
                    response,
                    reply_markup=InlineKeyboardMarkup(keyboard),
                    parse_mode="Markdown",
                )
                return CATEGORY_SELECTION

            else:
                error_msg = (
                    "😔 No places found within 2km.\n\n"
                    "Would you like to:\n"
                    "• Browse places by category (shows all distances)\n"
                    "• Try a different location"
                )
                keyboard = [
                    [
                        InlineKeyboardButton(
                            "📋 Browse Categories", callback_data="show_categories"
                        )
                    ],
                    [InlineKeyboardButton("🔍 Try Again", callback_data="nav_findme")],
                ]
                await update.message.reply_text(
                    error_msg, reply_markup=InlineKeyboardMarkup(keyboard)
                )
                return CATEGORY_SELECTION

        except Exception as e:
            logger.error(f"Error processing location: {str(e)}", exc_info=True)
            await handle_error(update, "Failed to process location")
            return ConversationHandler.END

    @staticmethod
    async def show_categories(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show available categories"""
        try:
            query = update.callback_query
            await query.answer()

            # Get unique categories from locations
            handler = FindMeHandler()
            categories = sorted(
                list(
                    set(
                        loc["category"]
                        for loc in handler.locations
                        if "category" in loc
                    )
                )
            )

            keyboard = []
            for category in categories:
                keyboard.append(
                    [
                        InlineKeyboardButton(
                            f"📍 {category}", callback_data=f"cat_{category}_1"
                        )
                    ]
                )
            keyboard.append(
                [InlineKeyboardButton("🔙 Back", callback_data="nav_findme")]
            )

            await query.message.edit_text(
                "Select a category to see the nearest places:",
                reply_markup=InlineKeyboardMarkup(keyboard),
            )
            return CATEGORY_SELECTION

        except Exception as e:
            logger.error(f"Error showing categories: {str(e)}", exc_info=True)
            await handle_error(update, "Failed to show categories")
            return ConversationHandler.END

    @staticmethod
    async def handle_pagination(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle pagination for all places or category-specific places"""
        try:
            query = update.callback_query
            await query.answer()

            # Parse callback data
            _, type_, page = query.data.split("_")  # page_all_2 or page_category_2
            page = int(page)

            location = context.user_data.get("last_location")
            if not location:
                await query.message.edit_text(
                    "Please share your location first.",
                    reply_markup=InlineKeyboardMarkup(
                        [[InlineKeyboardButton("🔙 Back", callback_data="nav_findme")]]
                    ),
                )
                return LOCATION

            # Get places based on type
            if type_ == "all":
                places, _ = FindMeHandler.get_nearby_places(
                    location["latitude"], location["longitude"], RADIUS_SEARCH
                )
            else:
                # Handle category-specific pagination
                places, _ = FindMeHandler.get_nearby_places(
                    location["latitude"], location["longitude"], RADIUS_SEARCH
                )
                places = [p for p in places if p["category"] == type_]

            # Calculate pagination
            total_pages = (len(places) + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE
            start_idx = (page - 1) * ITEMS_PER_PAGE
            end_idx = start_idx + ITEMS_PER_PAGE
            current_places = places[start_idx:end_idx]

            # Format message
            response = f"🎯 *{'All' if type_ == 'all' else type_} Places Near You*\n"
            response += f"Page {page} of {total_pages}\n\n"

            for place in current_places:
                response += f"📍 *{place['name']}*\n"
                response += f"🏢 Category: {place['category']}\n"
                response += f"📏 Distance: {place['distance']:.1f}km\n"
                if place.get("description"):
                    response += f"ℹ️ {place['description']}\n"
                if place.get("opening_hours"):
                    response += f"🕒 {place['opening_hours']}\n"
                if place.get("contact"):
                    contact = place["contact"]
                    if contact.get("phone"):
                        response += f"📞 {contact['phone']}\n"
                    if contact.get("website"):
                        response += f"🌐 {contact['website']}\n"
                response += "\n"

            # Create navigation buttons
            keyboard = []
            nav_row = []

            if page > 1:
                nav_row.append(
                    InlineKeyboardButton(
                        "◀️ Previous", callback_data=f"page_{type_}_{page - 1}"
                    )
                )

            if page < total_pages:
                nav_row.append(
                    InlineKeyboardButton(
                        "Next ▶️", callback_data=f"page_{type_}_{page + 1}"
                    )
                )

            if nav_row:
                keyboard.append(nav_row)

            # Add other navigation buttons
            keyboard.extend(
                [
                    [
                        InlineKeyboardButton(
                            "📋 Categories", callback_data="show_categories"
                        )
                    ],
                    [InlineKeyboardButton("🔍 New Search", callback_data="nav_findme")],
                    [InlineKeyboardButton("🔙 Main Menu", callback_data="menu_back")],
                ]
            )

            await query.message.edit_text(
                response,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode="Markdown",
            )
            return CATEGORY_SELECTION

        except Exception as e:
            logger.error(f"Error handling pagination: {str(e)}", exc_info=True)
            await handle_error(update, "Failed to show more places")
            return ConversationHandler.END

    @staticmethod
    async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Cancel the conversation"""
        try:
            message = "❌ Location search cancelled."
            if update.callback_query:
                await update.callback_query.answer()
                await update.callback_query.message.edit_text(
                    message,
                    reply_markup=InlineKeyboardMarkup(
                        [
                            [
                                InlineKeyboardButton(
                                    "🔙 Back to Menu", callback_data="menu_back"
                                )
                            ]
                        ]
                    ),
                )
            else:
                await update.message.reply_text(
                    message, reply_markup=ReplyKeyboardRemove()
                )
            return ConversationHandler.END
        except Exception as e:
            logger.error(f"Error in cancel: {str(e)}", exc_info=True)
            return ConversationHandler.END

    @staticmethod
    def get_handler():
        """Return the handler for this functionality"""
        return ConversationHandler(
            entry_points=[
                CommandHandler("findme", FindMeHandler.start_findme),
                CallbackQueryHandler(
                    FindMeHandler.start_findme, pattern="^nav_findme$"
                ),
            ],
            states={
                LOCATION: [
                    MessageHandler(filters.LOCATION, FindMeHandler.process_location),
                    MessageHandler(
                        filters.TEXT & ~filters.COMMAND, FindMeHandler.process_location
                    ),
                ],
                CATEGORY_SELECTION: [
                    CallbackQueryHandler(
                        FindMeHandler.show_categories, pattern="^show_categories$"
                    ),
                    CallbackQueryHandler(
                        FindMeHandler.handle_pagination, pattern="^page_"
                    ),
                    CallbackQueryHandler(
                        FindMeHandler.handle_pagination, pattern="^cat_"
                    ),
                ],
            },
            fallbacks=[
                CommandHandler("cancel", FindMeHandler.cancel),
                CallbackQueryHandler(FindMeHandler.cancel, pattern="^menu_back$"),
            ],
            name="findme_conversation",
        )
