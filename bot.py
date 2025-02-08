import logging
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
)
from config import TOKEN
from handlers.menu import MenuHandler
from handlers.findme import FindMeHandler
from handlers.categories import CategoriesHandler
from handlers.info import InfoHandler
from utils import setup_logger, handle_error, show_main_menu

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


async def handle_callback(update: Update, context):
    """Handle callback queries"""
    try:
        query = update.callback_query
        logger.info(f"Button clicked: {query.data}")

        # Handle different button clicks
        if query.data == "nav_categories":
            await CategoriesHandler.show_categories(update, context)
        elif query.data == "nav_info":
            await InfoHandler.show_info(update, context)
        elif query.data == "menu_back":
            await show_main_menu(update, context)
        elif query.data.startswith("cat_"):
            await CategoriesHandler.handle_category_selection(update, context)
        # Remove or comment out the nav_findme handling here since it's handled by ConversationHandler
        # elif query.data == "nav_findme":
        #     await FindMeHandler.start_findme(update, context)

        # Always acknowledge the button click
        await query.answer()

    except Exception as e:
        logger.error(f"Error handling button click: {str(e)}")
        await handle_error(update, "Could not process your selection")


def main():
    """Start the bot"""
    try:
        logger.info("Starting bot...")
        app = Application.builder().token(TOKEN).build()

        # Add handlers in specific order
        # 1. Conversation handler for FindMe (must be first to catch nav_findme callbacks)
        app.add_handler(FindMeHandler.get_handler())

        # 2. Callback query handler (for other button clicks)
        app.add_handler(CallbackQueryHandler(handle_callback))

        # 3. Command handlers
        for handler in MenuHandler.get_handlers():
            app.add_handler(handler)

        for handler in CategoriesHandler.get_handlers():
            app.add_handler(handler)

        for handler in InfoHandler.get_handlers():
            app.add_handler(handler)

        # 4. General message handler (lowest priority)
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

        # Add error handler
        app.add_error_handler(handle_error)

        logger.info("Bot handlers registered successfully")
        app.run_polling(allowed_updates=Update.ALL_TYPES)

    except Exception as e:
        logger.error(f"Error starting bot: {str(e)}", exc_info=True)


if __name__ == "__main__":
    main()
