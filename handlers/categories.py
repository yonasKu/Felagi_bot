from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    ContextTypes,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
)
from utils import (
    setup_logger,
    get_nearby_places,
    show_results,
    handle_error,
    CATEGORY_EMOJIS,
    get_category_emoji,
    debug_log,
    format_distance,
)
from config import SUPPORTED_CATEGORIES, LOCATIONS_FILE
import json
from typing import List, Dict, Any
from dataclasses import dataclass
from datetime import datetime

logger = setup_logger("categories_handler")

@dataclass
class Place:
    """Data class for place information"""
    name: str
    category: str
    coordinates: Dict[str, float]
    description: str = ""
    opening_hours: str = ""
    contact: Dict[str, str] = None
    distance: float = None
    last_updated: str = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Place':
        """Create Place instance from dictionary"""
        return cls(
            name=data.get('name', ''),
            category=data.get('category', ''),
            coordinates=data.get('coordinates', {}),
            description=data.get('description', ''),
            opening_hours=data.get('opening_hours', ''),
            contact=data.get('contact', {}),
            last_updated=datetime.now().isoformat()
        )

    def format_message(self) -> str:
        """Format place information for display"""
        emoji = get_category_emoji(self.category)
        message = f"{emoji} *{self.name}*\n"

        if self.coordinates:
            message += f"📌 Location: {self.coordinates.get('latitude')}, {self.coordinates.get('longitude')}\n"

        if self.distance is not None:
            message += f"📏 Distance: {format_distance(self.distance)}\n"

        if self.description:
            message += f"ℹ️ {self.description}\n"

        if self.opening_hours:
            message += f"🕒 {self.opening_hours}\n"

        if self.contact:
            if self.contact.get('phone'):
                phones = self.contact['phone'].split(',')
                for phone in phones:
                    message += f"📞 {phone.strip()}\n"
            if self.contact.get('email'):
                message += f"📧 {self.contact['email']}\n"
            if self.contact.get('website'):
                message += f"🌐 {self.contact['website']}\n"

        return message


class CategoryManager:
    """Manager for category-related operations"""
    
    def __init__(self):
        self.places: List[Place] = self._load_places()

    def _load_places(self) -> List[Place]:
        """Load places from JSON file"""
        try:
            with open(LOCATIONS_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return [Place.from_dict(place) for place in data.get('locations', [])]
        except Exception as e:
            logger.error(f"Error loading places: {str(e)}")
            return []

    def get_places_by_category(self, category: str) -> List[Place]:
        """Get places filtered by category"""
        return [place for place in self.places if place.category.lower() == category.lower()]

    def get_categories_count(self) -> Dict[str, int]:
        """Get count of places in each category"""
        counts = {}
        for place in self.places:
            counts[place.category] = counts.get(place.category, 0) + 1
        return counts


class CategoriesHandler:
    """Handler for categories functionality"""
    
    def __init__(self):
        self.category_manager = CategoryManager()

    @staticmethod
    async def show_categories(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show available categories"""
        try:
            user = update.effective_user
            logger.info(f"Showing categories to User {user.id}")
            
            # Initialize category manager
            category_manager = CategoryManager()
            category_counts = category_manager.get_categories_count()
            
            # Create category buttons - 2 per row
            keyboard = []
            for i in range(0, len(SUPPORTED_CATEGORIES), 2):
                row = []
                for category in SUPPORTED_CATEGORIES[i:i+2]:
                    emoji = get_category_emoji(category)
                    count = category_counts.get(category, 0)
                    row.append(InlineKeyboardButton(
                        f"{emoji} {category} ({count})",
                        callback_data=f"cat_{category.lower()}_1"
                    ))
                keyboard.append(row)
            
            # Add back button
            keyboard.append([InlineKeyboardButton("🔙 Back to Main Menu", callback_data="menu_back")])
            
            message = (
                "🏢 *Categories*\n\n"
                "Browse places by category:\n"
                f"Total categories: {len(SUPPORTED_CATEGORIES)}\n"
                f"Total places: {sum(category_counts.values())}\n\n"
                "Select a category to view places:"
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
            logger.error(f"Error showing categories: {str(e)}", exc_info=True)
            await handle_error(update, "Could not show categories")

    @staticmethod
    async def handle_category_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle category selection and show places"""
        try:
            query = update.callback_query
            await query.answer()
            
            # Parse callback data: cat_category_page
            _, category, page = query.data.split("_")
            page = int(page)
            
            logger.info(f"Selected category: {category}, Page: {page}")
            
            # Get places for category
            category_manager = CategoryManager()
            places = category_manager.get_places_by_category(category)
            
            if not places:
                await query.message.edit_text(
                    f"No places found in category: {category.title()}",
                    reply_markup=InlineKeyboardMarkup([[
                        InlineKeyboardButton("🔙 Back to Categories", callback_data="nav_categories")
                    ]]),
                    parse_mode='Markdown'
                )
                return
            
            # Calculate pagination
            items_per_page = 5
            total_pages = (len(places) + items_per_page - 1) // items_per_page
            start_idx = (page - 1) * items_per_page
            end_idx = start_idx + items_per_page
            current_places = places[start_idx:end_idx]
            
            # Format message
            emoji = get_category_emoji(category.title())
            message = (
                f"{emoji} *{category.title()}*\n"
                f"Page {page} of {total_pages}\n"
                f"Total places: {len(places)}\n\n"
            )
            
            # Add place information
            for place in current_places:
                message += place.format_message() + "\n"
            
            # Create navigation buttons
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
            
            keyboard.append([InlineKeyboardButton(
                "🔙 Back to Categories",
                callback_data="nav_categories"
            )])
            
            await query.message.edit_text(
                message,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode='Markdown'
            )
            
        except Exception as e:
            logger.error(f"Error handling category selection: {str(e)}", exc_info=True)
            await handle_error(update, "Could not show category places")

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
            ),
        ]
