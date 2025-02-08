from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes, CommandHandler, MessageHandler, CallbackQueryHandler, filters
from utils.location_utils import LocationService
from utils.logger import setup_logger

logger = setup_logger('city_guide_handler')

class CityGuideHandler:
    """Unified handler for city guide functionality"""

    @staticmethod
    async def show_guide(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show city guide options"""
        try:
            user = update.effective_user
            logger.info(f"Showing city guide to User {user.id}")

            keyboard = [
                [InlineKeyboardButton("🏛 Subcities", callback_data="guide_subcities")],
                [InlineKeyboardButton("📍 Key Areas", callback_data="guide_areas")],
                [InlineKeyboardButton("🚗 Transportation", callback_data="guide_transport")],
                [InlineKeyboardButton("📅 Events", callback_data="guide_events")],
                [InlineKeyboardButton("🔙 Back to Main Menu", callback_data="nav_back")]
            ]

            message = (
                "🏢 *Addis Ababa City Guide*\n\n"
                "Explore different aspects of the city:\n"
                "• Subcities and their features\n"
                "• Key areas and landmarks\n"
                "• Transportation options\n"
                "• Current events and activities"
            )

            if update.callback_query:
                await update.callback_query.message.edit_text(
                    message,
                    reply_markup=InlineKeyboardMarkup(keyboard),
                    parse_mode='Markdown'
                )
            else:
                await update.message.reply_text(
                    message,
                    reply_markup=InlineKeyboardMarkup(keyboard),
                    parse_mode='Markdown'
                )

        except Exception as e:
            logger.error(f"Error showing city guide: {str(e)}", exc_info=True)

    @staticmethod
    async def handle_guide_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle guide option selection"""
        try:
            query = update.callback_query
            user = update.effective_user

            guide_type = query.data.replace("guide_", "")
            logger.info(f"User {user.id} selected guide: {guide_type}")

            if guide_type == "subcities":
                await CityGuideHandler._show_subcities(query)
            elif guide_type == "areas":
                await CityGuideHandler._show_areas(query)
            elif guide_type == "transport":
                await CityGuideHandler._show_transport(query)
            elif guide_type == "events":
                await CityGuideHandler._show_events(query)

        except Exception as e:
            logger.error(f"Error handling guide selection: {str(e)}", exc_info=True)

    @staticmethod
    async def _show_subcities(query):
        """Show subcities information"""
        subcities_info = LocationService.get_subcities_info()
        response = "🏛 *Addis Ababa Subcities*\n\n"
        
        for subcity, info in subcities_info.items():
            response += f"*{subcity}*\n"
            response += f"📍 Main areas: {info.get('main_areas', 'N/A')}\n"
            response += f"ℹ️ {info.get('description', 'No description available')}\n\n"
        
        keyboard = [[InlineKeyboardButton("◀️ Back to City Guide", callback_data="show_guide")]]
        
        await query.message.edit_text(
            response,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )

# Create handlers
guide_handler = CommandHandler("guide", CityGuideHandler.show_guide)
guide_callback_handler = CallbackQueryHandler(
    CityGuideHandler.handle_guide_selection,
    pattern="^guide_"
) 