import json
import requests
import time
import os
import sys
from typing import Dict, List
import logging

# Add parent directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from config import SUPPORTED_CATEGORIES

logger = logging.getLogger(__name__)


class OSMDataFetcher:
    """Fetch data from OpenStreetMap using Overpass API"""

    # Overpass API endpoint
    OVERPASS_API = "https://overpass-api.de/api/interpreter"

    # Addis Ababa bounding box coordinates
    ADDIS_BBOX = "8.9,38.7,9.1,38.9"  # (south,west,north,east)

    # OSM tag mappings for each category
    CATEGORY_TAGS = {
        "Hotels": ["tourism=hotel", "tourism=guest_house"],
        "Restaurants": ["amenity=restaurant"],
        "Cafes": ["amenity=cafe"],
        "Shopping": ["shop=mall", "shop=supermarket", "shop=department_store"],
        "Entertainment": ["leisure=park", "amenity=cinema", "amenity=theatre"],
        "Education": ["amenity=university", "amenity=school", "amenity=college"],
        "Healthcare": ["amenity=hospital", "amenity=clinic"],
        "Banks": ["amenity=bank", "amenity=atm"],
        "Sports": ["leisure=sports_centre", "leisure=stadium"],
        "Cultural": ["tourism=museum", "historic=monument", "amenity=place_of_worship"],
    }

    @staticmethod
    def build_overpass_query(category: str) -> str:
        """Build Overpass QL query for a specific category"""
        tags = OSMDataFetcher.CATEGORY_TAGS.get(category, [])
        if not tags:
            return ""

        # Build query for each tag in the category
        queries = []
        for tag in tags:
            key, value = tag.split("=")
            queries.append(
                f'node["{key}"="{value}"]({OSMDataFetcher.ADDIS_BBOX});'
                f'way["{key}"="{value}"]({OSMDataFetcher.ADDIS_BBOX});'
                f'relation["{key}"="{value}"]({OSMDataFetcher.ADDIS_BBOX});'
            )

        # Combine all queries
        full_query = f"""
        [out:json][timeout:25];
        (
            {" ".join(queries)}
        );
        out body;
        >;
        out skel qt;
        """
        return full_query

    @staticmethod
    def fetch_category_data(category: str) -> List[Dict]:
        """Fetch OSM data for a specific category"""
        try:
            query = OSMDataFetcher.build_overpass_query(category)
            if not query:
                logger.error(f"No query built for category: {category}")
                return []

            # Make request to Overpass API
            response = requests.post(OSMDataFetcher.OVERPASS_API, data=query)
            response.raise_for_status()
            data = response.json()

            # Process and format the results
            locations = []
            for element in data.get("elements", []):
                if element.get("type") == "node":  # Only process nodes for simplicity
                    location = {
                        "name": element.get("tags", {}).get("name:en")
                        or element.get("tags", {}).get("name"),
                        "coordinates": {
                            "latitude": element.get("lat"),
                            "longitude": element.get("lon"),
                        },
                        "category": category,
                        "description": element.get("tags", {}).get("description", ""),
                        "opening_hours": element.get("tags", {}).get(
                            "opening_hours", ""
                        ),
                        "contact": {
                            "phone": element.get("tags", {}).get("phone", ""),
                            "email": element.get("tags", {}).get("email", ""),
                        },
                    }

                    # Only add locations with names
                    if location["name"]:
                        locations.append(location)

            return locations

        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching data for {category}: {str(e)}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error processing {category}: {str(e)}")
            return []

    @staticmethod
    def fetch_all_categories() -> Dict[str, List[Dict]]:
        """Fetch data for all supported categories"""
        all_locations = []

        for category in SUPPORTED_CATEGORIES:
            logger.info(f"Fetching data for category: {category}")
            try:
                # Add delay to avoid hitting API rate limits
                time.sleep(2)
                locations = OSMDataFetcher.fetch_category_data(category)
                all_locations.extend(locations)
                logger.info(f"Found {len(locations)} locations for {category}")
            except Exception as e:
                logger.error(f"Error processing category {category}: {str(e)}")

        return all_locations

    @staticmethod
    def save_to_json(locations: List[Dict], filename: str = "data/locations.json"):
        """Save fetched locations to JSON file"""
        try:
            # Ensure data directory exists
            os.makedirs(os.path.dirname(filename), exist_ok=True)

            # Save data to JSON file
            with open(filename, "w", encoding="utf-8") as f:
                json.dump({"locations": locations}, f, ensure_ascii=False, indent=2)

            logger.info(f"Successfully saved {len(locations)} locations to {filename}")

        except Exception as e:
            logger.error(f"Error saving locations to JSON: {str(e)}")


def update_locations_data():
    """Main function to update locations data"""
    try:
        logger.info("Starting location data update from OpenStreetMap")

        # Fetch all locations
        locations = OSMDataFetcher.fetch_all_categories()

        if locations:
            # Save to JSON file
            OSMDataFetcher.save_to_json(locations)
            logger.info("Location data update completed successfully")
            return True
        else:
            logger.error("No locations fetched")
            return False

    except Exception as e:
        logger.error(f"Error updating locations data: {str(e)}")
        return False


if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    # Update locations data
    update_locations_data()
