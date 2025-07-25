# tools/parking_tools.py
"""
Parking-related MCP tools for Deutsche Bahn API
"""

import logging
from typing import List, Dict, Any

from models import ParkingFacility, ParkingSearchResponse
from utils import tool_error_handler, fetch_from_db_api
from config import BASE_URL_PARKING

# Import MCP instance from shared module
from server_instance import mcp

# --- Parking API Tools ---

@mcp.tool()
@tool_error_handler
async def get_parking_by_station(stop_place_id: str) -> List[ParkingFacility]:
    """
    Find all parking facilities available at or near a specific train station. Returns comprehensive parking information including capacity, pricing, and real-time availability.

    This tool helps travelers find parking options at German train stations for Park & Ride travel. Essential for planning car-to-train journeys and understanding parking availability before arrival.

    Args:
        stop_place_id: Station identifier - accepts multiple formats:
                      - EVA Number: 7-digit code (e.g., "8000105" for Frankfurt)
                      - StadaID: Integer as string (e.g., "1866" for Frankfurt)  
                      - RIL 100: 1-6 letter code (e.g., "FF" for Frankfurt)
                      - GlobalID: DHID format (e.g., "de:11000:900003201")

    Returns:
        List of parking facilities with detailed information:
        - Facility name and exact location details
        - Total capacity and available spaces by type
        - Pricing information (hourly/daily/monthly rates)
        - Parking types (garage, surface lot, disabled spaces)
        - Opening hours and access restrictions
        - Real-time occupancy status and prognosis support
        - Booking and payment options

    Examples:
        - get_parking_by_station("8000105") → Frankfurt: 4 facilities, 479 total spaces
        - get_parking_by_station("FF") → Frankfurt using RIL100: same results
        - get_parking_by_station("8011160") → Berlin: 1 facility, 860 spaces
        - get_parking_by_station("BLS") → Berlin using RIL100: same results
        - get_parking_by_station("8000261") → München: 1 facility, 242 spaces

    Notes:
        - All identifier formats work equally well - use what you have available
        - EVA numbers can be obtained from get_station_by_name()
        - Real-time availability updates every few minutes
        - Some facilities support advance booking via get_parking_prognoses()
        - Disabled parking spaces are separately tracked in capacity information
        - Major stations typically have multiple parking options with different pricing
    """
    url = f"{BASE_URL_PARKING}/parking-facilities"
    params = {"stopPlaceId": stop_place_id}
    
    response = await fetch_from_db_api(url, params=params)
    facilities = response.get("_embedded", [])
    
    return [ParkingFacility(**facility) for facility in facilities]

@mcp.tool()
@tool_error_handler
async def search_parking_facilities(station_name: str, with_passenger_relevance: bool = True) -> List[ParkingFacility]:
    """
    Search for parking facilities at German railway stations by station name using the official DB Bahnpark API.

    This function uses the real DB Bahnpark API endpoint with the stationName parameter. It searches for parking facilities associated with specific train stations across Germany.

    Args:
        station_name: Name of the train station (e.g., "Frankfurt", "Berlin Hauptbahnhof", "München Hbf")
        with_passenger_relevance: Only include parking spaces relevant for train passengers (default: True)

    Returns:
        List of parking facilities at the specified station:
        - Facility name, address, and location details
        - Pricing information and tariffs
        - Capacity and availability data
        - Access restrictions and opening hours
        - Equipment like charging stations

    Examples:
        - search_parking_facilities("Frankfurt") → Parking at Frankfurt stations
        - search_parking_facilities("Berlin Hauptbahnhof") → Berlin Hbf parking
        - search_parking_facilities("München", False) → Munich parking including non-passenger spaces

    Notes:
        - Uses the official DB Bahnpark API stationName parameter
        - Station names should match DB naming conventions (try "Hauptbahnhof" or "Hbf" suffixes)
        - Setting with_passenger_relevance=False includes all parking (e.g., supermarket spaces)
        - Returns empty list if no parking facilities found for the station name
        - For station ID-based search, use get_parking_by_station() instead
    """
    url = f"{BASE_URL_PARKING}/parking-facilities"
    params = {
        "stationName": station_name,
        "withPassengerRelevance": with_passenger_relevance
    }
    
    response = await fetch_from_db_api(url, params=params)
    facilities = response.get("_embedded", [])
    
    return [ParkingFacility(**facility) for facility in facilities]

@mcp.tool()
@tool_error_handler
async def get_parking_prognoses(facility_id: str, datetime: str) -> List[Dict[str, Any]]:
    """
    Get parking availability forecasts for a specific facility up to 2 hours in advance. Returns predicted occupancy levels and availability trends.

    This tool provides valuable parking predictions that help travelers plan their Park & Ride journeys more effectively. Perfect for avoiding overcrowded facilities and ensuring parking availability.

    Args:
        facility_id: Unique parking facility identifier from get_parking_by_station().id field
        datetime: Target time in ISO 8601 format (e.g., "2025-07-24T14:30:00")

    Returns:
        List of prognosis data including:
        - Predicted availability levels and occupancy rates
        - Confidence levels for predictions  
        - Facility capacity and current status
        - Quality indicators for forecast accuracy

    Examples:
        - get_parking_prognoses("100081", "2025-07-24T08:00:00") → Frankfurt facility morning forecast
        - get_parking_prognoses("103143", "2025-07-24T18:30:00") → Berlin facility evening forecast  
        - get_parking_prognoses("100006", "2025-07-24T12:00:00") → Aschaffenburg midday prediction

    Notes:
        - Use facility IDs from get_parking_by_station() results (e.g., facility.id)
        - Only facilities with hasPrognosis=True support forecasting
        - Predictions based on historical patterns and current trends
        - Forecasts typically available up to 2 hours in advance
        - Check closer to travel time for best accuracy
        - Not all facilities provide prognosis data - check hasPrognosis field first
    """
    url = f"{BASE_URL_PARKING}/parking-facilities/{facility_id}/prognoses"
    params = {"datetime": datetime}
    
    response = await fetch_from_db_api(url, params=params)
    
    # Return the prognoses array directly from _embedded field
    return response.get("_embedded", [])