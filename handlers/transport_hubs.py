import json
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes, CommandHandler, CallbackQueryHandler
from utils import setup_logger, handle_error

logger = setup_logger("transport_hubs_handler")


class TransportHubsHandler:
    """Handler for transport hubs functionality"""

    @staticmethod
    def load_hubs_data():
        """Load transport hubs data from JSON file"""
        try:
            with open("data/transport_hubs.json", "r", encoding="utf-8") as f:
                data = json.load(f)["hubs"]
                logger.debug(f"Loaded hubs data: {data}")
                return data
        except Exception as e:
            logger.error(f"Error loading transport hubs data: {str(e)}")
            return []

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
                [InlineKeyboardButton(name, callback_data=f"hub_category_{data}")]
                for name, data in categories.items()
            ]
            
            keyboard.append([InlineKeyboardButton("🔙 Back to Main Menu", callback_data="menu_back")])

            message = "🚏 *Select a Transport Hub Category:*"
            if update.callback_query:
                await update.callback_query.message.edit_text(
                    message,
                    reply_markup=InlineKeyboardMarkup(keyboard),
                    parse_mode="Markdown",
                )
                await update.callback_query.answer()
            else:
                await update.message.reply_text(
                    message,
                    reply_markup=InlineKeyboardMarkup(keyboard),
                    parse_mode="Markdown",
                )

        except Exception as e:
            logger.error(f"Error showing transport hub categories: {str(e)}")
            await handle_error(update, context, "Could not show transport hub categories")

    async def show_hubs(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show transport hubs based on selected category with pagination"""
        try:
            query = update.callback_query
            await query.answer()

            logger.debug(f"Full callback query data: {query.data}")

            parts = query.data[len("hub_category_"):].split("_")
            if len(parts) >= 2 and parts[-1].isdigit():
                full_category = "_".join(parts[:-1])
                page = int(parts[-1])
            else:
                full_category = "_".join(parts)
                page = 1

            logger.debug(f"Extracted full category: {full_category}")

            hubs = self.load_hubs_data()

            if full_category != "all_hubs":
                filtered_hubs = [hub for hub in hubs if hub["category"] == full_category]
                logger.debug(f"Filtered hubs for {full_category}: {filtered_hubs}")
            else:
                filtered_hubs = hubs

            items_per_page = 4
            start_index = (page - 1) * items_per_page
            end_index = start_index + items_per_page
            current_hubs = filtered_hubs[start_index:end_index]

            if not current_hubs:
                message = "No transport hubs found for this category."
            else:
                message = f"🚏 *Transport Hubs - {full_category.replace('_', ' ').title()}*\n\n"
                for hub in current_hubs:
                    message += (
                        f"🏢 *{hub['name']}*\n"
                        f"📝 {hub['description']}\n"
                        f"🕒 Operating Hours: {hub['operating_hours']}\n"
                        f"🚍 Services: {', '.join(hub['services'])}\n\n"
                    )

            keyboard = [
                [InlineKeyboardButton("🔙 Back to Categories", callback_data="nav_transporthubs")]
            ]
            
            if end_index < len(filtered_hubs):
                keyboard.append([
                    InlineKeyboardButton(
                        "Show More",
                        callback_data=f"hub_category_{full_category}_{page + 1}",
                    )
                ])
            
            keyboard.append([InlineKeyboardButton("🔙 Back to Main Menu", callback_data="menu_back")])

            await query.message.edit_text(
                message,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode="Markdown",
            )

        except Exception as e:
            logger.error(f"Error showing transport hubs: {str(e)}")
            await handle_error(update, context, "Could not show transport hubs")

    @staticmethod
    def get_handlers():
        """Return the handlers for this functionality"""
        handler = TransportHubsHandler()
        return [
            CommandHandler("transporthubs", handler.show_categories),
            CallbackQueryHandler(handler.show_categories, pattern="^nav_transporthubs$"),
            CallbackQueryHandler(handler.show_hubs, pattern="^hub_category_"),
        ]
