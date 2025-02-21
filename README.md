# Felagi Bot 🏢

A Telegram bot designed to help users discover and navigate places in Addis Ababa, Ethiopia. The bot provides information about various locations, transport hubs, and points of interest throughout the city.

## Features 🌟

### 1. Find Nearby Places 🔍
- Share your location to find places near you
- Get distance calculations and estimated travel times
- View detailed information about each location

### 2. Category Browse 📋
Explore places by categories including:
- Hotels 🏨
- Restaurants 🍽
- Cafes ☕
- Shopping 🛍
- Entertainment 🎭
- Education 🎓
- Healthcare 🏥
- Banks 🏦
- Sports 🏃‍♂️
- Cultural 🏛

### 3. Transport Hubs 🚉
Find transportation facilities:
- Taxi Stands 🚖
- Transit Hubs 🚉
- Bus Terminals 🚌
- Train Stations 🚂
- Airport Terminals ✈️

## Technical Details 🔧

### Data Sources
- OpenStreetMap (OSM) data through Overpass API
- Custom JSON data files for transport hubs
- Real-time location-based calculations

### Key Components
1. **OSM Fetcher**
   - Fetches location data from OpenStreetMap
   - Updates local database periodically
   - Handles different location categories

2. **Handlers**
   - Menu Handler: Main menu navigation
   - Categories Handler: Category-based browsing
   - FindMe Handler: Location-based search
   - Transport Hubs Handler: Transport facility lookup
   - Info Handler: Help and information
   - City Guide Handler: City exploration features

3. **Utils**
   - Distance calculations using geopy
   - Error handling
   - Logging system
   - Message formatting

### Dependencies
- python-telegram-bot
- geopy (for precise distance calculations)
- requests (for API calls)
- python-dotenv (for environment variables)

## Commands 📝

- `/start` - Launch the bot
- `/findme` - Find nearby places
- `/categories` - Browse by category
- `/transporthubs` - Find transport hubs
- `/info` - Show help information

## Features in Detail 🔎

### Location Search
- Precise distance calculations using geodesic formulas
- Walking and driving time estimates
- Sorted results by proximity

### Transport Hub Information
- Operating hours
- Available services
- Descriptions
- Distance and travel time estimates

### Category Navigation
- Paginated results
- Detailed place information
- Easy navigation between categories

## Setup and Configuration ⚙️

1. Environment Variables:
   ```
   TOKEN=your_telegram_bot_token
   ```

2. Data Files:
   - `locations.json`: Main locations database
   - `transport_hubs.json`: Transport facilities data
   - `city_guide.json`: City guide information

## Error Handling 🛠

- Comprehensive error logging
- User-friendly error messages
- Graceful fallbacks for missing data
- Connection error handling

## Future Improvements 🚀

- Real-time traffic data integration
- Public transport schedules
- More detailed place information
- User reviews and ratings
- Multiple language support
- Favorite locations saving

## Contributing 🤝

Contributions are welcome! Please feel free to submit pull requests or open issues for improvements.
