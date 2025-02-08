from telegram import Update
from telegram.ext import ContextTypes, CommandHandler, MessageHandler, filters
from utils import (
    setup_logger,
    show_main_menu,
    handle_error
)

logger = setup_logger('menu_handler')

class MenuHandler:
    """Handler for main menu interactions"""

    @staticmethod
    async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle the /start command and main menu"""
        try:
            user = update.effective_user
            logger.info(f"New conversation started by User {user.id} ({user.username or 'No username'})")
            await show_main_menu(update, context)
            
        except Exception as e:
            logger.error(f"Error in start handler: {str(e)}", exc_info=True)
            await handle_error(update, "Failed to show main menu")

    @staticmethod
    def get_handlers():
        """Return the handlers for this functionality"""
        return [
            CommandHandler('start', MenuHandler.start),
            MessageHandler(
                filters.Regex("^🔙 Back to Main Menu$"),
                MenuHandler.start
            )
        ] 