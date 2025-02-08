import os
from dotenv import load_dotenv
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import logging
from math import radians, sin, cos, sqrt, atan2

# Load environment variables
load_dotenv()
TOKEN = os.getenv("TOKEN")


locations = {
    "Bole": [
        {"name": "Bole Medhanialem Church", "coordinates": (9.02, 38.77)},
        {"name": "Bole International Hotel", "coordinates": (9.02, 38.77)},
        {"name": "Edna Mall", "coordinates": (9.02, 38.75)},
        {"name": "Friendship Mall", "coordinates": (9.02, 38.76)},
        {"name": "Bole Subcity Market", "coordinates": (9.03, 38.75)},
        {"name": "Bole Atlas", "coordinates": (9.02, 38.77)},
        {"name": "Addis Ababa Bole International Airport", "coordinates": (9.03, 38.8)},
        {"name": "Kenyatta Avenue", "coordinates": (9.03, 38.77)},
        {"name": "Zefmesh Grand Mall", "coordinates": (9.02, 38.76)},
        {"name": "Bole Dembel", "coordinates": (9.03, 38.75)}
    ],
    
    "Lideta and Megenagna": [
        {"name": "Meskel Square", "coordinates": (9.03, 38.75)},
        {"name": "Lideta Church", "coordinates": (9.02, 38.74)},
        {"name": "Addis Ababa Railway Station", "coordinates": (9.02, 38.74)},
        {"name": "Megenagna Roundabout", "coordinates": (9.03, 38.76)},
        {"name": "Old Airport", "coordinates": (9.03, 38.79)},
        {"name": "Sar Bet Kidane Meheret Church", "coordinates": (9.04, 38.76)},
        {"name": "Lideta Market", "coordinates": (9.02, 38.74)},
        {"name": "Tiglachin Memorial", "coordinates": (9.02, 38.74)},
        {"name": "Chamber of Commerce Building", "coordinates": (9.02, 38.75)},
        {"name": "Lideta Taxi Station", "coordinates": (9.02, 38.73)}
    ],
    
    "Piazza": [
        {"name": "St. George's Cathedral", "coordinates": (9.02, 38.75)},
        {"name": "National Museum of Ethiopia", "coordinates": (9.03, 38.74)},
        {"name": "Ethnological Museum", "coordinates": (9.03, 38.75)},
        {"name": "Addis Ababa University", "coordinates": (9.03, 38.75)},
        {"name": "Lion of Judah Monument", "coordinates": (9.03, 38.75)},
        {"name": "Commercial Bank of Ethiopia", "coordinates": (9.03, 38.74)},
        {"name": "Addis Ababa City Hall", "coordinates": (9.03, 38.74)},
        {"name": "Piazza Market", "coordinates": (9.03, 38.75)},
        {"name": "Fasika Church", "coordinates": (9.03, 38.75)},
        {"name": "Addis Ababa Post Office", "coordinates": (9.02, 38.73)}
    ],
    
    "Akaki Kaliti": [
        {"name": "Akaki Kaliti Subcity", "coordinates": (8.90, 38.79)},
        {"name": "Akaki Kaliti Market", "coordinates": (8.90, 38.78)},
        {"name": "Kaliti Park", "coordinates": (8.91, 38.79)},
        {"name": "Factory Area (Eastern Industrial Zone)", "coordinates": (8.89, 38.80)},
        {"name": "Akaki River", "coordinates": (8.89, 38.77)},
        {"name": "Akaki Kaliti Police Station", "coordinates": (8.91, 38.78)},
        {"name": "Addis Ababa Ceramic Factory", "coordinates": (8.90, 38.81)},
        {"name": "Dembel City Mall", "coordinates": (8.91, 38.79)},
        {"name": "Kaliti Clinic", "coordinates": (8.91, 38.78)},
        {"name": "Akaki Bole Road", "coordinates": (8.90, 38.77)}
    ],
    
    "Gullele": [
        {"name": "Gullele Botanical Garden", "coordinates": (9.03, 38.83)},
        {"name": "Entoto Park", "coordinates": (9.04, 38.83)},
        {"name": "Entoto Hill", "coordinates": (9.02, 38.83)},
        {"name": "Mount Entoto", "coordinates": (9.03, 38.84)},
        {"name": "Gullele Subcity Market", "coordinates": (9.03, 38.83)},
        {"name": "Addis Ababa Observatory", "coordinates": (9.03, 38.84)},
        {"name": "Entoto Palace", "coordinates": (9.03, 38.82)},
        {"name": "Entoto Natural Park", "coordinates": (9.03, 38.84)},
        {"name": "Addis Ababa Memorial Park", "coordinates": (9.03, 38.82)},
        {"name": "Gullele Community Hall", "coordinates": (9.03, 38.83)}
    ],
    
    "Kirkos": [
        {"name": "Kirkos Subcity", "coordinates": (9.03, 38.74)},
        {"name": "Tabor Church", "coordinates": (9.03, 38.75)},
        {"name": "Kirkos Market", "coordinates": (9.03, 38.73)},
        {"name": "Addis Ababa Stadium", "coordinates": (9.03, 38.75)},
        {"name": "Giant Pizza and Restaurant", "coordinates": (9.03, 38.74)},
        {"name": "Kirkos Taxi Station", "coordinates": (9.03, 38.74)},
        {"name": "National Bank of Ethiopia", "coordinates": (9.03, 38.74)},
        {"name": "Hotel Sheraton Addis", "coordinates": (9.03, 38.74)},
        {"name": "Fasil Plaza", "coordinates": (9.03, 38.74)},
        {"name": "Kirkos Main Street", "coordinates": (9.03, 38.74)}
    ],
    
    "Yeka": [
        {"name": "Yeka Subcity", "coordinates": (9.03, 38.84)},
        {"name": "Bole Bulbula", "coordinates": (9.03, 38.84)},
        {"name": "Yeka Orthodox Church", "coordinates": (9.03, 38.85)},
        {"name": "Yeka Town Center", "coordinates": (9.03, 38.83)},
        {"name": "Fitawrari Haile Selassie Avenue", "coordinates": (9.03, 38.85)},
        {"name": "Dembel City Center", "coordinates": (9.02, 38.84)},
        {"name": "Bole Hills", "coordinates": (9.02, 38.85)},
        {"name": "Yeka Park", "coordinates": (9.03, 38.84)},
        {"name": "Lalibela Restaurant", "coordinates": (9.03, 38.84)},
        {"name": "Yeka Subcity Hospital", "coordinates": (9.03, 38.84)}
    ],
    
    "Nifas Silk-Lafto": [
        {"name": "Nifas Silk-Lafto Subcity", "coordinates": (9.03, 38.75)},
        {"name": "Lafto Market", "coordinates": (9.02, 38.76)},
        {"name": "Hawassa Street", "coordinates": (9.03, 38.75)},
        {"name": "Megenagna", "coordinates": (9.03, 38.77)},
        {"name": "Nifas Silk Park", "coordinates": (9.03, 38.77)},
        {"name": "Kality Park", "coordinates": (9.03, 38.77)},
        {"name": "Lafto Church", "coordinates": (9.02, 38.77)},
        {"name": "Bole Subcity Shopping Center", "coordinates": (9.02, 38.76)},
        {"name": "Lafto Club", "coordinates": (9.02, 38.76)},
        {"name": "Nifas Silk-Lafto Stadium", "coordinates": (9.03, 38.76)}
    ],
    
    "Kolfe Keranio": [
        {"name": "Kolfe Keranio Subcity", "coordinates": (9.03, 38.75)},
        {"name": "Kolfe Market", "coordinates": (9.03, 38.75)},
        {"name": "Alem Gena", "coordinates": (9.03, 38.76)},
        {"name": "Kolfe Keranio Church", "coordinates": (9.03, 38.75)},
        {"name": "Kolfe Bus Station", "coordinates": (9.02, 38.75)},
        {"name": "Kolfe Commercial Center", "coordinates": (9.02, 38.75)},
        {"name": "Kolfe Street", "coordinates": (9.03, 38.75)},
        {"name": "Kolfe Transport Hub", "coordinates": (9.03, 38.76)},
        {"name": "Kolfe Park", "coordinates": (9.03, 38.75)},
        {"name": "Kolfe Police Station", "coordinates": (9.03, 38.75)}
    ]
}
# Set up logging
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)

# Function to calculate the distance using Haversine formula
def haversine(lat1, lon1, lat2, lon2):
    # Radius of the Earth in kilometers
    R = 6371.0

    # Convert latitude and longitude from degrees to radians
    lat1 = radians(lat1)
    lon1 = radians(lon1)
    lat2 = radians(lat2)
    lon2 = radians(lon2)

    # Differences in coordinates
    dlat = lat2 - lat1
    dlon = lon2 - lon1

    # Haversine formula
    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    # Distance in kilometers
    distance = R * c
    return distance

# Subcity centers with their coordinates
subcities = {
    'Bole': (9.0300, 38.7400),  # Example for Bole center (latitude, longitude)
    'Addis Ketema': (9.0273, 38.7461),
    'Akaki Kaliti': (8.8958, 38.7892),
    'Arada': (9.0292, 38.7461),
    'Gullele': (9.0373, 38.8350),
    'Kirkos': (9.0273, 38.7461),
    'Kolfe Keranio': (9.0273, 38.7461),
    'Lideta': (9.0273, 38.7461),
    'Nifas Silk-Lafto': (9.0273, 38.7461),
    'Yeka': (9.0373, 38.8350),
    'Lemi-Kura': (9.0273, 38.7461)
}

# Function to find the subcity based on user's coordinates
def find_subcity(user_lat, user_lon, radius_km=2):
    for subcity, (lat, lon) in subcities.items():
        # Calculate the distance to the subcity center
        distance = haversine(user_lat, user_lon, lat, lon)
        if distance <= radius_km:
            return subcity, distance
    return "No subcity found within the radius", None

# Start command handler
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Greet the user first
    await update.message.reply_text("Hi, how are you doing?")

    # Now, ask for location by sending the button
    button = KeyboardButton("Share Your Location", request_location=True)
    reply_markup = ReplyKeyboardMarkup([[button]], one_time_keyboard=True)

    # Send the location request with the button
    await update.message.reply_text(
        "Please share your location by clicking the button below.",
        reply_markup=reply_markup
    )

# Handle location sharing
async def handle_location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.location:
        location = update.message.location
        latitude = location.latitude
        longitude = location.longitude
        logging.info(f"User's location: Latitude={latitude}, Longitude={longitude}")

        # Find the subcity based on location
        subcity, distance = find_subcity(latitude, longitude)

        # Log subcity result
        logging.info(f"User's location: Latitude={latitude}, Longitude={longitude}, Subcity={subcity}")

        # If a subcity is found within the radius
        if subcity != "No subcity found within the radius":
            response = f"📍 Your location:\nLatitude: {latitude}\nLongitude: {longitude}\n\nYou are in the subcity: {subcity} (Distance: {distance:.2f} km)"
        else:
            response = f"📍 Your location:\nLatitude: {latitude}\nLongitude: {longitude}\n\nWe couldn't determine your subcity based on the given location."

        # Send the result back to the user
        await update.message.reply_text(response)
    else:
        await update.message.reply_text("❌ No location detected. Please try again.")

# Main function
if __name__ == "__main__":
    # Create the bot application
    app = Application.builder().token(TOKEN).build()

    # Add handlers
    app.add_handler(CommandHandler("start", start_command))  # Start command
    app.add_handler(MessageHandler(filters.LOCATION, handle_location))  # Handle location sharing

    # Start the bot
    print("Bot is running...")
    app.run_polling()
