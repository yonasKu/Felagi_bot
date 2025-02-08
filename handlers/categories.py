from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    ContextTypes,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters
)
from utils import (
    setup_logger,
    get_nearby_places,
    show_results,
    handle_error,
    CATEGORY_EMOJIS,
    get_category_emoji,
    debug_log
)
from config import SUPPORTED_CATEGORIES

logger = setup_logger('categories_handler')

class CategoriesHandler:
    """Handler for categories functionality"""
    
    @staticmethod
    async def show_categories(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show available categories"""
        try:
            user = update.effective_user
            logger.info(f"Showing categories to User {user.id}")
            
            # Create category buttons - 2 per row
            keyboard = []
            for i in range(0, len(SUPPORTED_CATEGORIES), 2):
                row = []
                for category in SUPPORTED_CATEGORIES[i:i+2]:
                    emoji = get_category_emoji(category)
                    row.append(InlineKeyboardButton(
                        f"{emoji} {category}",
                        callback_data=f"cat_{category.lower()}"
                    ))
                keyboard.append(row)
            
            # Add back button
            keyboard.append([InlineKeyboardButton("🔙 Back to Main Menu", callback_data="menu_back")])
            
            message = (
                "🏢 *Categories*\n\n"
                "Browse places by category:\n"
                "Select a category to view places"
            )
            
            if update.callback_query:
                await update.callback_query.message.edit_text(
                    message,
                    reply_markup=InlineKeyboardMarkup(keyboard),
                    parse_mode='Markdown'
                )
                await update.callback_query.answer()
            else:
                await update.message.reply_text(
                    message,
                    reply_markup=InlineKeyboardMarkup(keyboard),
                    parse_mode='Markdown'
                )
                
        except Exception as e:
            logger.error(f"Error showing categories: {str(e)}", exc_info=True)
            await handle_error(update, "Failed to show categories")
    
    @staticmethod
    async def handle_category_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle category selection"""
        try:
            query = update.callback_query
            category = query.data.replace("cat_", "").title()
            
            # Debug logging
            logger.debug(f"Processing category selection: {category}")
            
            # Get places for this category
            places, status = get_nearby_places(category=category)
            
            logger.debug(f"Found {len(places)} places for category {category}")
            
            if status == "OK" and places:
                # Format the response
                response = f"📍 *{category} in Addis Ababa*\n\n"
                
                for place in places:
                    emoji = get_category_emoji(category)
                    response += f"{emoji} *{place['name']}*\n"
                    if 'description' in place and place['description']:
                        response += f"ℹ️ {place['description']}\n"
                    if 'opening_hours' in place and place['opening_hours']:
                        response += f"🕒 {place['opening_hours']}\n"
                    if 'amenities' in place and place['amenities']:
                        response += f"✨ {', '.join(place['amenities'][:3])}\n"
                    response += "\n"
                
                keyboard = [
                    [InlineKeyboardButton("🔙 Back to Categories", callback_data="nav_categories")],
                    [InlineKeyboardButton("🏠 Main Menu", callback_data="menu_back")]
                ]
                
                try:
                    await query.message.edit_text(
                        response,
                        reply_markup=InlineKeyboardMarkup(keyboard),
                        parse_mode='Markdown'
                    )
                    logger.debug(f"Successfully sent response for category {category}")
                except Exception as e:
                    logger.error(f"Error sending category response: {str(e)}")
                    await handle_error(update, "Failed to display category results")
            else:
                keyboard = [[InlineKeyboardButton("🔙 Back to Categories", callback_data="nav_categories")]]
                await query.message.edit_text(
                    f"No places found in category: {category}",
                    reply_markup=InlineKeyboardMarkup(keyboard)
                )
                logger.debug(f"No places found for category {category}")
            
            await query.answer()
            
        except Exception as e:
            logger.error(f"Error handling category selection: {str(e)}", exc_info=True)
            await handle_error(update, "Failed to process category selection")

    @staticmethod
    def get_handlers():
        """Return the handlers for this functionality"""
        return [
            CommandHandler("categories", CategoriesHandler.show_categories),
            MessageHandler(
                filters.Regex("^📋 Categories$"),
                CategoriesHandler.show_categories
            ),
            CallbackQueryHandler(
                CategoriesHandler.handle_category_selection,
                pattern="^cat_"
            )
        ]