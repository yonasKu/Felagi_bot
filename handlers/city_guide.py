import json
import os
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes, CommandHandler, CallbackQueryHandler
from utils import setup_logger
from typing import Dict, Any, List
from dataclasses import dataclass

logger = setup_logger("city_guide_handler")


@dataclass
class GuideData:
    """Data class for city guide information"""

    attractions: List[Dict[str, Any]]
    subcities: Dict[str, Dict[str, Any]]
    transport_info: Dict[str, List[Dict[str, Any]]]
    safety_tips: Dict[str, Any]
    useful_phrases: Dict[str, List[Dict[str, str]]]

    @classmethod
    def load_guide_data(cls) -> "GuideData":
        """Load guide data from JSON file"""
        try:
            file_path = os.path.join("data", "city_guide.json")
            with open(file_path, "r", encoding="utf-8") as file:
                data = json.load(file)
                return cls(**data)
        except Exception as e:
            logger.error(f"Error loading guide data: {str(e)}")
            raise


class CityGuideHandler:
    """Handler for city guide functionality"""

    def __init__(self):
        try:
            self.guide_data = GuideData.load_guide_data()
        except Exception as e:
            logger.error(f"Failed to load guide data: {str(e)}")
            self.guide_data = None

    async def show_attractions(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE, page: int = 1
    ):
        """Show attractions with pagination"""
        try:
            query = update.callback_query
            await query.answer()  # Acknowledge the callback query

            items_per_page = 3
            attractions = self.guide_data.attractions
            total_pages = (len(attractions) + items_per_page - 1) // items_per_page
            start_idx = (page - 1) * items_per_page
            end_idx = start_idx + items_per_page
            current_attractions = attractions[start_idx:end_idx]

            message = (
                f"🏛 *Top Attractions in Addis Ababa*\nPage {page} of {total_pages}\n\n"
            )

            for attraction in current_attractions:
                message += (
                    f"{attraction['emoji']} *{attraction['name']}*\n"
                    f"📝 {attraction['description']}\n"
                )
                if "opening_hours" in attraction:
                    message += f"🕒 {attraction['opening_hours']}\n"
                if "entry_fee" in attraction:
                    message += f"💰 Entry: {attraction['entry_fee']}\n"
                if "highlights" in attraction:
                    message += "\n✨ Highlights:\n"
                    for highlight in attraction["highlights"]:
                        message += f"• {highlight}\n"
                if "tips" in attraction:
                    message += "\n💡 Tips:\n"
                    for tip in attraction["tips"]:
                        message += f"• {tip}\n"
                message += "\n"

            keyboard = []
            nav_row = []

            if page > 1:
                nav_row.append(
                    InlineKeyboardButton(
                        "◀️ Previous", callback_data=f"guide_attractions_{page - 1}"
                    )
                )
            if page < total_pages:
                nav_row.append(
                    InlineKeyboardButton(
                        "Next ▶️", callback_data=f"guide_attractions_{page + 1}"
                    )
                )

            if nav_row:
                keyboard.append(nav_row)
            keyboard.append(
                [InlineKeyboardButton("🔙 Back to Guide", callback_data="show_guide")]
            )

            await query.message.edit_text(
                message,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode="Markdown",
            )

        except Exception as e:
            logger.error(f"Error showing attractions: {str(e)}")
            await self._handle_error(update, "Could not show attractions")

    async def show_subcities(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show subcities information"""
        try:
            query = update.callback_query
            await query.answer()  # Acknowledge the callback query

            message = "🏙 *Addis Ababa Subcities*\n\n"

            for name, info in self.guide_data.subcities.items():
                message += (
                    f"*{name}*\n"
                    f"📝 {info['description']}\n"
                    f"📍 Main areas: {info['main_areas']}\n"
                )
                if "highlights" in info:
                    message += "\n✨ Highlights:\n"
                    for highlight in info["highlights"]:
                        message += f"• {highlight}\n"
                if "transportation" in info:
                    message += "\n🚗 Transportation:\n"
                    for transport in info["transportation"]:
                        message += f"• {transport}\n"
                message += "\n"

            keyboard = [
                [InlineKeyboardButton("🔙 Back to Guide", callback_data="show_guide")]
            ]

            await query.message.edit_text(
                message,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode="Markdown",
            )

        except Exception as e:
            logger.error(f"Error showing subcities: {str(e)}")
            await self._handle_error(update, "Could not show subcities")

    async def show_transport(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show transportation information"""
        try:
            query = update.callback_query
            await query.answer()  # Acknowledge the callback query

            transport_info = self.guide_data.transport_info
            message = "🚇 *Transportation Guide*\n\n"

            # Public Transport
            message += "*Public Transport:*\n"
            for transport in transport_info.get("public_transport", []):
                message += f"🚍 *{transport['type']}*\n📝 {transport['description']}\n"
                if "operating_hours" in transport:
                    message += f"🕒 Operating Hours: {transport['operating_hours']}\n"
                if "fare_range" in transport:
                    message += f"💰 Fare Range: {transport['fare_range']}\n"
                if "routes" in transport:
                    message += "\n🛤 Routes:\n"
                    for route in transport["routes"]:
                        message += f"• {route}\n"
                if "tips" in transport:
                    message += "\n💡 Tips:\n"
                    for tip in transport["tips"]:
                        message += f"• {tip}\n"
                message += "\n"

            # Taxis
            message += "*Taxis:*\n"
            for taxi in transport_info.get("taxis", []):
                message += f"🚖 *{taxi['type']}*\n📝 {taxi['description']}\n"
                if "fare_range" in taxi:
                    message += f"💰 Fare Range: {taxi['fare_range']}\n"
                if "available_apps" in taxi:
                    message += "\n📱 Available Apps:\n"
                    for app in taxi["available_apps"]:
                        message += f"• {app}\n"
                if "tips" in taxi:
                    message += "\n💡 Tips:\n"
                    for tip in taxi["tips"]:
                        message += f"• {tip}\n"
                message += "\n"

            keyboard = [
                [InlineKeyboardButton("🔙 Back to Guide", callback_data="show_guide")]
            ]

            await query.message.edit_text(
                message,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode="Markdown",
            )

        except KeyError as e:
            logger.error(f"Error showing transport info: Missing key {str(e)}")
            await self._handle_error(update, f"Missing transport information: {str(e)}")
        except Exception as e:
            logger.error(f"Error showing transport info: {str(e)}")
            await self._handle_error(update, "Could not show transport information")

    async def show_safety(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show safety tips"""
        try:
            query = update.callback_query
            await query.answer()  # Acknowledge the callback query

            safety = self.guide_data.safety_tips
            message = "🛡 *Safety Tips for Addis Ababa*\n\n"

            message += "*General Safety:*\n"
            for tip in safety["general_safety"]:
                message += f"• {tip}\n"

            message += "\n*Health Safety:*\n"
            for tip in safety["health_safety"]:
                message += f"• {tip}\n"

            message += "\n*📞 Emergency Numbers:*\n"
            for service, number in safety["emergency_numbers"].items():
                message += f"• {service}: `{number}`\n"

            keyboard = [
                [InlineKeyboardButton("🔙 Back to Guide", callback_data="show_guide")]
            ]

            await query.message.edit_text(
                message,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode="Markdown",
            )

        except Exception as e:
            logger.error(f"Error showing safety tips: {str(e)}")
            await self._handle_error(update, "Could not show safety tips")

    async def show_phrases(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show useful phrases"""
        try:
            query = update.callback_query
            await query.answer()  # Acknowledge the callback query

            phrases = self.guide_data.useful_phrases["Amharic"]
            message = "💬 *Useful Amharic Phrases*\n\n"

            for phrase in phrases:
                message += (
                    f"*{phrase['phrase']}*\n"
                    f"🗣 Pronunciation: _{phrase['pronunciation']}_\n"
                    f"🔤 Meaning: {phrase['meaning']}\n\n"
                )

            keyboard = [
                [InlineKeyboardButton("🔙 Back to Guide", callback_data="show_guide")]
            ]

            await query.message.edit_text(
                message,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode="Markdown",
            )

        except Exception as e:
            logger.error(f"Error showing phrases: {str(e)}")
            await self._handle_error(update, "Could not show useful phrases")

    @staticmethod
    async def show_guide(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show city guide main menu"""
        try:
            # First acknowledge the callback query if it exists
            if update.callback_query:
                await update.callback_query.answer()

            keyboard = [
                [
                    InlineKeyboardButton(
                        "🏛 Top Attractions", callback_data="guide_attractions_1"
                    )
                ],
                [
                    InlineKeyboardButton(
                        "🏙 Explore Subcities", callback_data="guide_subcities"
                    )
                ],
                [
                    InlineKeyboardButton(
                        "🚇 Transportation Guide", callback_data="guide_transport"
                    )
                ],
                [InlineKeyboardButton("🛡 Safety & Tips", callback_data="guide_safety")],
                [
                    InlineKeyboardButton(
                        "💬 Useful Phrases", callback_data="guide_phrases"
                    )
                ],
                [
                    InlineKeyboardButton(
                        "🔙 Back to Main Menu", callback_data="menu_back"
                    )
                ],
            ]

            message = (
                "🌟 *Welcome to Addis Ababa City Guide*\n\n"
                "Discover Ethiopia's capital city:\n"
                "• Historical attractions and landmarks\n"
                "• Different areas of the city\n"
                "• Getting around\n"
                "• Essential tips and phrases\n\n"
                "Select a category to explore:"
            )

            markup = InlineKeyboardMarkup(keyboard)

            if update.callback_query:
                await update.callback_query.message.edit_text(
                    text=message, reply_markup=markup, parse_mode="Markdown"
                )
            else:
                await update.message.reply_text(
                    text=message, reply_markup=markup, parse_mode="Markdown"
                )

        except Exception as e:
            logger.error(f"Error showing city guide: {str(e)}", exc_info=True)
            await CityGuideHandler._handle_error(update, "Could not show city guide")

    @staticmethod
    async def _handle_error(update: Update, message: str):
        """Handle errors in city guide"""
        keyboard = [
            [InlineKeyboardButton("🔙 Back to Guide", callback_data="show_guide")]
        ]
        if update.callback_query:
            await update.callback_query.message.edit_text(
                f"⚠️ {message}", reply_markup=InlineKeyboardMarkup(keyboard)
            )
        else:
            await update.message.reply_text(
                f"⚠️ {message}", reply_markup=InlineKeyboardMarkup(keyboard)
            )

    @staticmethod
    def get_handlers():
        """Return the handlers for this functionality"""
        try:
            guide_handler = CityGuideHandler()
            return [
                CommandHandler("guide", guide_handler.show_guide),
                CallbackQueryHandler(
                    guide_handler.show_guide, pattern="^(nav_guide|show_guide)$"
                ),
                CallbackQueryHandler(
                    lambda u, c: guide_handler.show_attractions(
                        u, c, int(u.callback_query.data.split("_")[2])
                    ),
                    pattern="^guide_attractions_\d+$",
                ),
                CallbackQueryHandler(
                    guide_handler.show_subcities, pattern="^guide_subcities$"
                ),
                CallbackQueryHandler(
                    guide_handler.show_transport, pattern="^guide_transport$"
                ),
                CallbackQueryHandler(
                    guide_handler.show_safety, pattern="^guide_safety$"
                ),
                CallbackQueryHandler(
                    guide_handler.show_phrases, pattern="^guide_phrases$"
                ),
            ]
        except Exception as e:
            logger.error(f"Error setting up guide handlers: {str(e)}", exc_info=True)
            return []
