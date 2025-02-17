import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
    ContextTypes,
)
from config import TOKEN
from handlers.menu import MenuHandler
from handlers.findme import FindMeHandler
from handlers.categories import CategoriesHandler
from handlers.info import InfoHandler
from utils import setup_logger, handle_error, show_main_menu
from handlers.city_guide import CityGuideHandler
from handlers.transport_hubs import TransportHubsHandler

# Set up logger
logger = setup_logger("bot")


async def handle_message(update: Update, context):
    """Handle all non-command messages"""
    try:
        user = update.effective_user
        message = update.message.text if update.message else "No message"
        logger.info(f"Received message from User {user.id}: {message}")
    except Exception as e:
        logger.error(f"Error in message handler: {str(e)}", exc_info=True)


async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle callback queries"""
    try:
        query = update.callback_query
        logger.info(f"Button clicked: {query.data}")

        # Create guide handler instance
        guide_handler = CityGuideHandler()

        # Always acknowledge the callback query first
        await query.answer()

        if query.data == "nav_categories":
            await CategoriesHandler.show_categories(update, context)
        elif query.data == "nav_info":
            await InfoHandler.show_info(update, context)
        elif query.data in ["nav_guide", "show_guide"]:
            await guide_handler.show_guide(update, context)
        elif query.data == "guide_transport":
            await guide_handler.show_transport(update, context)
        elif query.data == "guide_phrases":
            await guide_handler.show_phrases(update, context)
        elif query.data == "guide_safety":
            await guide_handler.show_safety(update, context)
        elif query.data == "guide_subcities":
            await guide_handler.show_subcities(update, context)
        elif query.data.startswith("guide_attractions_"):
            page = int(query.data.split("_")[2])
            await guide_handler.show_attractions(update, context, page)
        elif query.data == "menu_back":
            await show_main_menu(update, context)
        elif query.data.startswith("cat_"):
            await CategoriesHandler.handle_category_selection(update, context)

    except Exception as e:
        logger.error(f"Error handling button click: {str(e)}", exc_info=True)
        await handle_error(update, context, "Could not process your selection")


async def handle_error(
    update: Update, context: ContextTypes.DEFAULT_TYPE, error_message: str
):
    """Handle errors and show appropriate messages to user"""
    logger = setup_logger("error_handler")
    logger.error(f"Error: {error_message}")

    try:
        keyboard = [
            [InlineKeyboardButton("🔙 Back to Main Menu", callback_data="menu_back")]
        ]

        if update.callback_query:
            await update.callback_query.message.edit_text(
                f"Sorry, an error occurred: {error_message}",
                reply_markup=InlineKeyboardMarkup(keyboard),
            )
            await update.callback_query.answer()
        else:
            await update.effective_message.reply_text(
                f"Sorry, an error occurred: {error_message}",
                reply_markup=InlineKeyboardMarkup(keyboard),
            )
    except Exception as e:
        logger.error(f"Error in error handler: {str(e)}", exc_info=True)


def main():
    """Start the bot"""
    try:
        logger.info("Starting bot...")
        app = Application.builder().token(TOKEN).build()

        # Add handlers in specific order
        # 1. City Guide handlers
        for handler in CityGuideHandler.get_handlers():
            app.add_handler(handler)

        # 2. Transport Hubs handler
        for handler in TransportHubsHandler.get_handlers():
            app.add_handler(handler)

        # 3. Conversation handler for FindMe
        app.add_handler(FindMeHandler.get_handler())

        # 4. General callback query handler (for other button clicks)
        app.add_handler(CallbackQueryHandler(handle_callback))

        # 5. Command handlers
        for handler in MenuHandler.get_handlers():
            app.add_handler(handler)

        for handler in CategoriesHandler.get_handlers():
            app.add_handler(handler)

        for handler in InfoHandler.get_handlers():
            app.add_handler(handler)

        # 6. General message handler (lowest priority)
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

        # Add error handler
        app.add_error_handler(handle_error)

        logger.info("Bot handlers registered successfully")
        app.run_polling(allowed_updates=Update.ALL_TYPES)

    except Exception as e:
        logger.error(f"Error starting bot: {str(e)}", exc_info=True)


if __name__ == "__main__":
    main()
