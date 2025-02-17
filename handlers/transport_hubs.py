import json
from telegram import (
    Update,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    KeyboardButton,
)
from telegram.ext import (
    ContextTypes,
    CommandHandler,
    CallbackQueryHandler,
    ConversationHandler,
    MessageHandler,
    filters,
)
from utils import setup_logger, handle_error
from math import radians, sin, cos, sqrt, atan2

logger = setup_logger("transport_hubs_handler")

# Conversation states
LOCATION = 1


class TransportHubsHandler:
    """Handler for transport hubs functionality"""

    def __init__(self):
        self.hubs_data = self.load_hubs_data()

    @staticmethod
    def load_hubs_data():
        """Load transport hubs data from JSON file"""
        try:
            with open("data/transport_hubs.json", "r", encoding="utf-8") as f:
                data = json.load(f)["hubs"]
                logger.debug("Transport hubs data loaded successfully")
                return data
        except Exception as e:
            logger.error(f"Error loading transport hubs data: {str(e)}")
            return []

    async def show_main_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show main menu for transport hubs"""
        try:
            keyboard = [
                [InlineKeyboardButton("🔍 Explore Hubs", callback_data="explore_hubs")],
                [
                    InlineKeyboardButton(
                        "📍 Find Nearest Hubs", callback_data="find_nearest"
                    )
                ],
                [
                    InlineKeyboardButton(
                        "🔙 Back to Main Menu", callback_data="menu_back"
                    )
                ],
            ]

            text = (
                "🚉 *Transport Hubs*\n\n"
                "Choose how you want to explore transport hubs:\n\n"
                "• *Explore Hubs* - Browse all transport hubs by category\n"
                "• *Find Nearest* - Find hubs closest to your location"
            )

            if update.callback_query:
                await update.callback_query.message.edit_text(
                    text,
                    reply_markup=InlineKeyboardMarkup(keyboard),
                    parse_mode="Markdown",
                )
            else:
                await update.message.reply_text(
                    text,
                    reply_markup=InlineKeyboardMarkup(keyboard),
                    parse_mode="Markdown",
                )

        except Exception as e:
            logger.error(f"Error showing main menu: {str(e)}")
            await handle_error(update, context, "Could not show transport hubs menu")

    async def show_categories(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show transport hub categories"""
        try:
            categories = {
                "🚖 Taxi Stand": "taxi_stand",
                "🚉 Transit Hub": "transit_hub",
                "🚌 Bus Terminal": "bus_terminal",
                "🚂 Train Station": "train_station",
                "✈️ Airport Terminal": "airport_terminal",
                "🔄 All Options": "all_hubs",
            }

            keyboard = [
                [InlineKeyboardButton(name, callback_data=f"hub_category_{data}_0")]
                for name, data in categories.items()
            ]
            keyboard.append(
                [InlineKeyboardButton("🔙 Back", callback_data="nav_transporthubs")]
            )

            await update.callback_query.message.edit_text(
                "Select a transport hub category to explore:",
                reply_markup=InlineKeyboardMarkup(keyboard),
            )

        except Exception as e:
            logger.error(f"Error showing categories: {str(e)}")
            await handle_error(update, context, "Could not show categories")

    async def request_location(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        """Request user location"""
        try:
            reply_keyboard = [
                [KeyboardButton("📍 Share Location", request_location=True)],
                [KeyboardButton("❌ Cancel")],
            ]

            await update.callback_query.message.reply_text(
                "Please share your location to find the nearest transport hubs:",
                reply_markup=ReplyKeyboardMarkup(
                    reply_keyboard, one_time_keyboard=True, resize_keyboard=True
                ),
            )
            return LOCATION

        except Exception as e:
            logger.error(f"Error requesting location: {str(e)}")
            await handle_error(update, context, "Could not request location")
            return ConversationHandler.END

    def calculate_distance(self, lat1, lon1, lat2, lon2):
        """Calculate distance between two points using Haversine formula"""
        R = 6371  # Earth's radius in kilometers

        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
        dlat = lat2 - lat1
        dlon = lon2 - lon1

        a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))
        distance = R * c

        return distance

    async def show_nearest_hubs(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        """Show nearest transport hubs based on user location"""
        try:
            user_location = update.message.location
            nearest_hubs = []

            for hub in self.hubs_data:
                if "coordinates" in hub:
                    distance = self.calculate_distance(
                        user_location.latitude,
                        user_location.longitude,
                        hub["coordinates"]["latitude"],
                        hub["coordinates"]["longitude"],
                    )
                    nearest_hubs.append((hub, distance))

            # Sort hubs by distance and get top 5
            nearest_hubs.sort(key=lambda x: x[1])
            nearest_hubs = nearest_hubs[:5]

            message = "🎯 *Nearest Transport Hubs:*\n\n"
            for hub, distance in nearest_hubs:
                message += (
                    f"🏢 *{hub['name']}*\n"
                    f"📍 Distance: {distance:.1f} km\n"
                    f"🕒 Operating Hours: {hub.get('operating_hours', 'Not specified')}\n"
                    f"🚍 Services: {', '.join(hub.get('services', ['Not specified']))}\n\n"
                )

            keyboard = [
                [
                    InlineKeyboardButton(
                        "🔙 Back to Transport Hubs", callback_data="nav_transporthubs"
                    )
                ]
            ]

            await update.message.reply_text(
                message,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode="Markdown",
            )
            return ConversationHandler.END

        except Exception as e:
            logger.error(f"Error showing nearest hubs: {str(e)}")
            await handle_error(update, context, "Could not show nearest hubs")
            return ConversationHandler.END

    async def cancel(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Cancel the conversation"""
        await update.message.reply_text(
            "Operation cancelled.", reply_markup=ReplyKeyboardRemove()
        )
        return ConversationHandler.END

    async def show_hubs(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show transport hubs based on selected category with pagination"""
        try:
            query = update.callback_query
            await query.answer()

            # Extract category and page from callback data
            data = query.data[len("hub_category_") :]
            if "_" in data:
                category, page = data.rsplit("_", 1)
                page = int(page)
            else:
                category = data
                page = 0

            # Get hubs for selected category
            if category == "all_hubs":
                filtered_hubs = self.hubs_data
            else:
                filtered_hubs = [
                    hub for hub in self.hubs_data if hub["category"] == category
                ]

            # Pagination
            items_per_page = 3
            start_idx = page * items_per_page
            end_idx = start_idx + items_per_page
            current_hubs = filtered_hubs[start_idx:end_idx]
            total_pages = (len(filtered_hubs) + items_per_page - 1) // items_per_page

            if not filtered_hubs:
                message = "No transport hubs found in this category."
            else:
                # Format message
                message = (
                    f"🚏 *Transport Hubs - {category.replace('_', ' ').title()}*\n"
                )
                message += f"Page {page + 1} of {total_pages}\n\n"

                for hub in current_hubs:
                    message += (
                        f"🏢 *{hub['name']}*\n"
                        f"📝 {hub.get('description', 'No description available')}\n"
                        f"🕒 Operating Hours: {hub.get('operating_hours', 'Not specified')}\n"
                    )
                    if "services" in hub:
                        message += f"🚍 Services: {', '.join(hub['services'])}\n"
                    if "coordinates" in hub:
                        message += f"📍 Location: {hub['coordinates']['latitude']}, {hub['coordinates']['longitude']}\n"
                    message += "\n"

            # Create navigation buttons
            keyboard = []

            # Add pagination buttons if needed
            if len(filtered_hubs) > items_per_page:
                nav_row = []
                if page > 0:
                    nav_row.append(
                        InlineKeyboardButton(
                            "◀️ Previous",
                            callback_data=f"hub_category_{category}_{page - 1}",
                        )
                    )
                if end_idx < len(filtered_hubs):
                    nav_row.append(
                        InlineKeyboardButton(
                            "Next ▶️",
                            callback_data=f"hub_category_{category}_{page + 1}",
                        )
                    )
                if nav_row:
                    keyboard.append(nav_row)

            # Add navigation buttons
            keyboard.append(
                [
                    InlineKeyboardButton(
                        "�� Back to Categories", callback_data="explore_hubs"
                    )
                ]
            )
            keyboard.append(
                [
                    InlineKeyboardButton(
                        "🔙 Back to Main Menu", callback_data="menu_back"
                    )
                ]
            )

            await query.message.edit_text(
                message,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode="Markdown",
            )

        except Exception as e:
            logger.error(f"Error showing hubs: {str(e)}")
            await handle_error(update, context, "Could not show transport hubs")

    @staticmethod
    def get_handlers():
        """Return the handlers for this functionality"""
        handler = TransportHubsHandler()

        # Create conversation handler for location-based search
        location_conv = ConversationHandler(
            entry_points=[
                CallbackQueryHandler(handler.request_location, pattern="^find_nearest$")
            ],
            states={
                LOCATION: [
                    MessageHandler(filters.LOCATION, handler.show_nearest_hubs),
                    MessageHandler(filters.Regex("^❌ Cancel$"), handler.cancel),
                ]
            },
            fallbacks=[MessageHandler(filters.Regex("^❌ Cancel$"), handler.cancel)],
        )

        return [
            CommandHandler("transporthubs", handler.show_main_menu),
            CallbackQueryHandler(handler.show_main_menu, pattern="^nav_transporthubs$"),
            CallbackQueryHandler(handler.show_categories, pattern="^explore_hubs$"),
            CallbackQueryHandler(handler.show_hubs, pattern="^hub_category_"),
            location_conv,
        ]
