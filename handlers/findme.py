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

logger = setup_logger("findme_handler")

# States
LOCATION = 1
CATEGORY_SELECTION = 2


class FindMeHandler:
    """Handler for Find Nearby Places functionality"""

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

            # Get nearby places within 2km radius
            places, status = get_nearby_places(
                location.latitude, location.longitude, RADIUS_SEARCH
            )

            if status == "OK" and places:
                response = "🎯 *Nearest Places to You:*\n\n"
                for place in places[:5]:  # Show top 5 nearest places
                    response += f"📍 *{place['name']}*\n"
                    if "area" in place:
                        response += f"📌 Area: {place['area']}\n"
                    if "distance" in place:
                        response += f"📏 {format_distance(place['distance'])}\n"
                    if "description" in place:
                        response += f"ℹ️ {place['description']}\n"
                    if "opening_hours" in place:
                        response += f"🕒 {place['opening_hours']}\n"
                    if "contact" in place:
                        contact = place["contact"]
                        if "phone" in contact:
                            response += f"📞 {contact['phone']}\n"
                        if "website" in contact:
                            response += f"🌐 {contact['website']}\n"
                    response += "\n"

                keyboard = [
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

            keyboard = []
            for category in SUPPORTED_CATEGORIES:
                keyboard.append(
                    [
                        InlineKeyboardButton(
                            f"📍 {category}", callback_data=f"cat_{category}"
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
    async def handle_category_selection(
        update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        """Handle category selection"""
        try:
            query = update.callback_query
            await query.answer()

            category = query.data.replace("cat_", "")
            last_location = context.user_data.get("last_location")

            if not last_location:
                await query.message.edit_text(
                    "⚠️ Please share your location first.",
                    reply_markup=InlineKeyboardMarkup(
                        [
                            [
                                InlineKeyboardButton(
                                    "🔍 Share Location", callback_data="nav_findme"
                                )
                            ]
                        ]
                    ),
                )
                return ConversationHandler.END

            # Get ALL places with distances calculated
            places, status = get_nearby_places(
                last_location["latitude"],
                last_location["longitude"],
                max_distance=None,  # This will return all places with distances
            )

            if status == "OK" and places:
                # Filter by category and sort by distance
                category_places = [p for p in places if p.get("category") == category]
                if category_places:
                    response = f"📍 *Nearest {category} Places:*\n\n"
                    # Show top 3 nearest places in the category
                    for place in category_places[:3]:
                        response += f"*{place['name']}*\n"
                        if "area" in place:
                            response += f"📌 Area: {place['area']}\n"
                        if "distance" in place:
                            response += f"📏 {format_distance(place['distance'])}\n"
                        if "description" in place:
                            response += f"ℹ️ {place['description']}\n"
                        if "opening_hours" in place:
                            response += f"🕒 {place['opening_hours']}\n"
                        if "contact" in place:
                            contact = place["contact"]
                            if "phone" in contact:
                                response += f"📞 {contact['phone']}\n"
                            if "website" in contact:
                                response += f"🌐 {contact['website']}\n"
                        response += "\n"

                    keyboard = [
                        [
                            InlineKeyboardButton(
                                "📋 Other Categories", callback_data="show_categories"
                            )
                        ],
                        [
                            InlineKeyboardButton(
                                "🔍 New Search", callback_data="nav_findme"
                            )
                        ],
                        [
                            InlineKeyboardButton(
                                "🔙 Back to Menu", callback_data="menu_back"
                            )
                        ],
                    ]

                    await query.message.edit_text(
                        response,
                        reply_markup=InlineKeyboardMarkup(keyboard),
                        parse_mode="Markdown",
                    )
                    return CATEGORY_SELECTION

                else:
                    await query.message.edit_text(
                        f"No {category} places found in the database.\nTry another category:",
                        reply_markup=InlineKeyboardMarkup(
                            [
                                [
                                    InlineKeyboardButton(
                                        "📋 Show Categories",
                                        callback_data="show_categories",
                                    )
                                ]
                            ]
                        ),
                    )
                    return CATEGORY_SELECTION

            else:
                await query.message.edit_text(
                    "No places found in the database.",
                    reply_markup=InlineKeyboardMarkup(
                        [[InlineKeyboardButton("🔙 Back", callback_data="nav_findme")]]
                    ),
                )
                return ConversationHandler.END

        except Exception as e:
            logger.error(f"Error handling category selection: {str(e)}", exc_info=True)
            await handle_error(update, "Failed to process category selection")
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
                        FindMeHandler.handle_category_selection, pattern="^cat_"
                    ),
                ],
            },
            fallbacks=[
                CommandHandler("cancel", FindMeHandler.cancel),
                CallbackQueryHandler(FindMeHandler.cancel, pattern="^menu_back$"),
                MessageHandler(
                    filters.Regex("^🔙 Back to Menu$"), FindMeHandler.cancel
                ),
            ],
            name="findme_conversation",
        )
