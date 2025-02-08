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
                        callback_data=f"cat_{category.lower()}_1"
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
            await query.answer()

            # Extract category and page number from callback data
            data = query.data.split('_')
            category = data[1].title()  # Convert to title case
            page = int(data[2]) if len(data) > 2 else 1
            
            logger.debug(f"Processing category: {category}, page: {page}")
            
            # Get all places for this category
            places, status = get_nearby_places(None, None, max_distance=None)
            if status == "OK" and places:
                # Filter places by category
                category_places = [p for p in places if p.get('category') == category]
                
                if category_places:
                    # Pagination
                    items_per_page = 6
                    start_idx = (page - 1) * items_per_page
                    end_idx = start_idx + items_per_page
                    current_places = category_places[start_idx:end_idx]
                    total_pages = (len(category_places) + items_per_page - 1) // items_per_page
                    
                    # Format response
                    emoji = get_category_emoji(category)
                    response = f"{emoji} *{category} Places*\n"
                    response += f"Page {page} of {total_pages}\n\n"
                    
                    for place in current_places:
                        response += f"🏢 *{place['name']}*\n"
                        if 'area' in place:
                            response += f"📍 Area: {place['area']}\n"
                        if 'description' in place:
                            response += f"ℹ️ {place['description']}\n"
                        if 'opening_hours' in place:
                            response += f"🕒 {place['opening_hours']}\n"
                        if 'contact' in place:
                            contact = place['contact']
                            if 'phone' in contact:
                                response += f"📞 {contact['phone']}\n"
                            if 'website' in contact:
                                response += f"🌐 {contact['website']}\n"
                        response += "\n"
                    
                    # Navigation buttons
                    keyboard = []
                    nav_row = []
                    
                    if page > 1:
                        nav_row.append(InlineKeyboardButton(
                            "◀️ Previous",
                            callback_data=f"cat_{category.lower()}_{page-1}"
                        ))
                    
                    if page < total_pages:
                        nav_row.append(InlineKeyboardButton(
                            "Next ▶️",
                            callback_data=f"cat_{category.lower()}_{page+1}"
                        ))
                    
                    if nav_row:
                        keyboard.append(nav_row)
                    
                    keyboard.extend([
                        [InlineKeyboardButton("📋 Back to Categories", callback_data="nav_categories")],
                        [InlineKeyboardButton("🔙 Main Menu", callback_data="menu_back")]
                    ])
                    
                    await query.message.edit_text(
                        response,
                        reply_markup=InlineKeyboardMarkup(keyboard),
                        parse_mode='Markdown'
                    )
                    return
                
            # If no places found or error occurred
            keyboard = [[InlineKeyboardButton("🔙 Back to Categories", callback_data="nav_categories")]]
            await query.message.edit_text(
                f"No places found in category: {category}",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
            
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