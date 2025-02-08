from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes, CommandHandler, MessageHandler, filters
from utils import setup_logger, handle_error

logger = setup_logger('info_handler')

class InfoHandler:
    """Handler for help and about information"""

 
    @staticmethod
    async def show_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show help and about information"""
        try:
            user = update.effective_user
            logger.info(f"Info accessed by User {user.id}")

            info_text = (
                "🤖 *How to use Addis Places Bot*\n\n"
                "*Commands:*\n"
                "/start - Start the bot\n"
                "/findme - Find nearby places\n"
                "/categories - Browse by category\n"
                "/info - Show this help message\n\n"
                "*Features:*\n"
                "• Click '🔍 Find Nearby Places' to discover places near you\n"
                "• Use '📋 Categories' to browse places by type\n"
                "• Share your location to find nearby places\n"
                "• Get distances and directions\n\n"
                "Version: 1.0.0"
            )

            keyboard = [[InlineKeyboardButton("🔙 Back to Main Menu", callback_data="menu_back")]]
            
            if update.callback_query:
                await update.callback_query.message.edit_text(
                    info_text,
                    reply_markup=InlineKeyboardMarkup(keyboard),
                    parse_mode='Markdown'
                )
                await update.callback_query.answer()
            else:
                await update.message.reply_text(
                    info_text,
                    reply_markup=InlineKeyboardMarkup(keyboard),
                    parse_mode='Markdown'
                )

        except Exception as e:
            logger.error(f"Error in info handler: {str(e)}", exc_info=True)
            await handle_error(update, "Failed to show info")

    @staticmethod
    def get_handlers():  # Changed method name to indicate multiple handlers
        """Return the handlers for this functionality"""
        return [
            CommandHandler('info', InfoHandler.show_info),
            MessageHandler(
                filters.Regex("^ℹ️ Info$"),
                InfoHandler.show_info
            )
        ]