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
from geopy.distance import geodesic

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

    @staticmethod
    def calculate_distance(lat1, lon1, lat2, lon2) -> float:
        """
        Calculate precise distance between two points using geopy's geodesic distance.
        
        Args:
            lat1 (float): Latitude of first point
            lon1 (float): Longitude of first point
            lat2 (float): Latitude of second point
            lon2 (float): Longitude of second point
            
        Returns:
            float: Distance in kilometers
        """
        try:
            point1 = (lat1, lon1)
            point2 = (lat2, lon2)
            distance = geodesic(point1, point2).kilometers
            return round(distance, 2)  # Round to 2 decimal places
        except Exception as e:
            logger.error(f"Error calculating distance: {str(e)}")
            return float('inf')  # Return infinity for invalid calculations

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

    async def show_nearest_hubs(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        """Show nearest transport hubs based on user location"""
        try:
            if not update or not update.message:
                logger.error("Update or message object is missing")
                await handle_error(update, context, "Invalid request. Please try again.")
                return ConversationHandler.END

            user_location = update.message.location
            if not user_location:
                await update.message.reply_text(
                    "❌ No location received. Please share your location using the button provided.",
                    reply_markup=ReplyKeyboardMarkup([
                        [KeyboardButton("📍 Share Location", request_location=True)],
                        [KeyboardButton("❌ Cancel")]
                    ], resize_keyboard=True)
                )
                return LOCATION

            nearest_hubs = []
            user_coords = (user_location.latitude, user_location.longitude)

            for hub in self.hubs_data:
                if not hub.get('coordinates') or \
                   'latitude' not in hub['coordinates'] or \
                   'longitude' not in hub['coordinates']:
                    continue

                hub_coords = (hub['coordinates']['latitude'], hub['coordinates']['longitude'])
                distance = self.calculate_distance(
                    user_location.latitude,
                    user_location.longitude,
                    hub['coordinates']['latitude'],
                    hub['coordinates']['longitude']
                )
                
                if distance != float('inf'):
                    nearest_hubs.append((hub, distance))

            if not nearest_hubs:
                await update.message.reply_text(
                    "⚠️ No hubs found near your location.",
                    reply_markup=InlineKeyboardMarkup([[
                        InlineKeyboardButton("🔙 Back to Transport Hubs", callback_data="nav_transporthubs")
                    ]])
                )
                return ConversationHandler.END

            # Sort hubs by distance and get top 5
            nearest_hubs.sort(key=lambda x: x[1])
            nearest_hubs = nearest_hubs[:5]

            message = "🎯 *Nearest Transport Hubs:*\n\n"
            for hub, distance in nearest_hubs:
                message += (
                    f"🏢 *{hub['name']}*\n"
                    f"📍 Distance: {distance} km\n"
                )
                
                # Add walking time estimate (assuming average walking speed of 5 km/h)
                walking_time = (distance / 5) * 60  # Convert to minutes
                message += f"👣 Est. Walking Time: {int(walking_time)} mins\n"
                
                # Add driving time estimate (assuming average speed of 30 km/h)
                driving_time = (distance / 30) * 60  # Convert to minutes
                message += f"🚗 Est. Driving Time: {int(driving_time)} mins\n"
                
                # Add optional information
                if hub.get('operating_hours'):
                    message += f"🕒 Operating Hours: {hub['operating_hours']}\n"
                if hub.get('services'):
                    message += f"🚍 Services: {', '.join(hub['services'])}\n"
                if hub.get('description'):
                    message += f"📝 {hub['description']}\n"
                message += "\n"

            # Remove location keyboard and show results
            await update.message.reply_text(
                message,
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🔙 Back to Transport Hubs", callback_data="nav_transporthubs")
                ]]),
                parse_mode="Markdown"
            )
            
            # Clean up by removing the location keyboard
            await update.message.reply_text(
                "Location search completed.",
                reply_markup=ReplyKeyboardRemove()
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
                        "🔙 Back to Categories", callback_data="explore_hubs"
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
