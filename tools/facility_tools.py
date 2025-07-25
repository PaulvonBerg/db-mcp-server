# tools/facility_tools.py
"""
Facility and service-related MCP tools for Deutsche Bahn API
"""

import logging
from typing import List, Dict, Any

from models import SZentrale, SZentraleQuery, Facility, FacilityStationResponse
from utils import tool_error_handler, fetch_from_db_api
from config import BASE_URL_STADA, BASE_URL_FASTA

# Import MCP instance from shared module
from server_instance import mcp

# --- S-Zentralen Tools ---

@mcp.tool()
@tool_error_handler
async def get_szentralen_by_location(latitude: float, longitude: float, radius: int = 10000) -> List[SZentrale]:
    """
    Find S-Zentralen (DB mobility service centers) near a geographic location. Returns contact information and services for customer assistance centers.

    Uses smart regional filtering based on coordinates to determine relevant federal states, then filters S-Zentralen by cities in those regions.

    S-Zentralen are Deutsche Bahn's regional customer service centers that provide personalized travel assistance, mobility services, and support for travelers with special needs. Essential for accessibility planning and comprehensive travel support.

    Args:
        latitude: Geographic latitude in decimal degrees (e.g., 52.5200 for Berlin)
        longitude: Geographic longitude in decimal degrees (e.g., 13.4050 for Berlin)
        radius: Search radius in meters (default: 10000m = 10km, max: 50000m)

    Returns:
        List of S-Zentralen in the relevant geographic region:
        - Contact details (phone, email, address with city names)
        - Service center numbers and identifiers
        - Available phone and fax numbers
        - Address information and regional coverage

    Examples:
        - get_szentralen_by_location(52.5200, 13.4050) → Berlin/Brandenburg S-Zentralen
        - get_szentralen_by_location(50.1109, 8.6821) → Hessen S-Zentralen (Frankfurt area)
        - get_szentralen_by_location(48.1351, 11.5820) → Bayern S-Zentralen (Munich area)

    Notes:
        - Uses coordinate-to-federal-state mapping for regional filtering
        - Filters by major cities within relevant states
        - S-Zentralen provide 24/7 mobility assistance and accessibility support
        - Can arrange wheelchair assistance, platform support, etc.
        - Essential for travelers requiring special assistance
    """
    from utils import validate_coordinates
    
    # Validate inputs
    try:
        latitude, longitude = validate_coordinates(latitude, longitude)
    except ValueError as e:
        logging.warning(f"Coordinate validation failed: {e}")
        if not (-90 <= latitude <= 90) or not (-180 <= longitude <= 180):
            raise ValueError("Invalid coordinates: latitude must be between -90 and 90, longitude between -180 and 180")
    
    if radius > 50000:
        radius = 50000
    
    # Same coordinate-to-state mapping as stations
    def get_likely_federal_states(lat, lon):
        """Determine likely federal states based on coordinates"""
        state_coords = {
            "baden-wuerttemberg": (47.5, 49.8, 7.5, 10.5),
            "bayern": (47.3, 50.6, 8.9, 13.8),
            "berlin": (52.3, 52.7, 13.1, 13.8),
            "brandenburg": (51.4, 53.6, 11.3, 14.8),
            "bremen": (53.0, 53.6, 8.5, 8.9),
            "hamburg": (53.4, 53.7, 9.7, 10.3),
            "hessen": (49.4, 51.7, 7.8, 10.2),
            "mecklenburg-vorpommern": (53.1, 54.7, 10.6, 14.4),
            "niedersachsen": (51.3, 53.9, 6.7, 11.6),
            "nordrhein-westfalen": (50.3, 52.5, 5.9, 9.5),
            "rheinland-pfalz": (49.1, 50.9, 6.1, 8.5),
            "saarland": (49.1, 49.6, 6.4, 7.4),
            "sachsen": (50.2, 51.7, 11.9, 15.0),
            "sachsen-anhalt": (51.0, 53.0, 10.6, 13.2),
            "schleswig-holstein": (53.4, 55.1, 8.0, 11.3),
            "thueringen": (50.2, 51.6, 9.9, 12.7)
        }
        
        likely_states = []
        buffer = 0.5  # degrees buffer for border areas
        for state, (min_lat, max_lat, min_lon, max_lon) in state_coords.items():
            if (min_lat - buffer <= lat <= max_lat + buffer and 
                min_lon - buffer <= lon <= max_lon + buffer):
                likely_states.append(state)
        
        return likely_states
    
    # Map major cities to federal states for S-Zentralen filtering
    def get_relevant_cities_for_states(states):
        """Get major cities in the specified federal states"""
        state_cities = {
            "baden-wuerttemberg": ["stuttgart", "karlsruhe", "mannheim", "freiburg", "heidelberg"],
            "bayern": ["münchen", "nürnberg", "augsburg", "würzburg", "regensburg", "ingolstadt"],
            "berlin": ["berlin"],
            "brandenburg": ["potsdam", "cottbus", "brandenburg"],
            "bremen": ["bremen", "bremerhaven"],
            "hamburg": ["hamburg"],
            "hessen": ["frankfurt", "wiesbaden", "kassel", "darmstadt", "offenbach"],
            "mecklenburg-vorpommern": ["schwerin", "rostock", "neubrandenburg"],
            "niedersachsen": ["hannover", "braunschweig", "oldenburg", "osnabrück", "göttingen"],
            "nordrhein-westfalen": ["köln", "düsseldorf", "dortmund", "essen", "duisburg", "bochum"],
            "rheinland-pfalz": ["mainz", "ludwigshafen", "koblenz", "trier"],
            "saarland": ["saarbrücken"],
            "sachsen": ["dresden", "leipzig", "chemnitz"],
            "sachsen-anhalt": ["magdeburg", "halle"],
            "schleswig-holstein": ["kiel", "lübeck"],
            "thueringen": ["erfurt", "jena", "gera"]
        }
        
        relevant_cities = []
        for state in states:
            relevant_cities.extend(state_cities.get(state, []))
        return relevant_cities
    
    # Get likely states and their cities
    likely_states = get_likely_federal_states(latitude, longitude)
    relevant_cities = get_relevant_cities_for_states(likely_states)
    
    # Get all S-Zentralen
    url = f"{BASE_URL_STADA}/szentralen"
    response = await fetch_from_db_api(url, params={"limit": 200})  # Get all S-Zentralen
    all_szentralen = response.get("result", [])
    
    # Filter S-Zentralen by relevant cities
    filtered_szentralen = []
    if relevant_cities:
        for sz in all_szentralen:
            address = sz.get("address", {})
            city = address.get("city", "").lower() if address else ""
            
            # Check if S-Zentrale city matches any relevant city
            for relevant_city in relevant_cities:
                if relevant_city in city or city in relevant_city:
                    filtered_szentralen.append(sz)
                    break
    
    # If no regional filtering worked, return a reasonable subset
    if not filtered_szentralen:
        logging.info(f"No regional S-Zentralen found for coordinates {latitude}, {longitude}, returning general results")
        filtered_szentralen = all_szentralen[:10]  # Return first 10 as fallback
    
    return [SZentrale(**sz) for sz in filtered_szentralen]

@mcp.tool()
@tool_error_handler
async def search_szentralen(limit: int = 50, offset: int = 0) -> List[SZentrale]:
    """
    Get all S-Zentralen (DB mobility service centers) with pagination support. Returns comprehensive list of customer service centers across Germany.

    S-Zentralen provide personalized travel assistance, mobility services, and accessibility support. This tool retrieves all available service centers that can help with travel planning, accessibility arrangements, and customer support.

    Args:
        limit: Maximum number of S-Zentralen to return (default: 50, max: 10000)
        offset: Number of results to skip for pagination (default: 0)

    Returns:
        List of S-Zentralen with complete information:
        - Contact details (phone, email, address)
        - Service center numbers and identifiers
        - Location and accessibility information
        - Available services and support options

    Examples:
        - search_szentralen() → First 50 S-Zentralen nationwide
        - search_szentralen(limit=10) → First 10 service centers only
        - search_szentralen(limit=25, offset=50) → Results 51-75 for pagination

    Notes:
        - Use get_szentralen_by_location() to find centers near specific coordinates
        - All S-Zentralen provide mobility assistance and accessibility support
        - Contact information includes both public and internal phone/fax numbers
        - Essential for travelers requiring special assistance or personalized support
        - Results are not filtered by location - use location-based search for geographic filtering
    """
    url = f"{BASE_URL_STADA}/szentralen"
    params = {"limit": min(limit, 10000), "offset": offset}
    
    response = await fetch_from_db_api(url, params=params)
    szentralen = response.get("result", [])
    
    return [SZentrale(**sz) for sz in szentralen]

# --- Facility Status (FaSta) Tools ---

@mcp.tool()
@tool_error_handler
async def find_facilities(station_number: int, type: str = None, state: str = None, equipment_number: int = None) -> List[Facility]:
    """
    Find facilities (elevators, escalators) at a specific German railway station with optional filtering by type and operational status.

    This tool is essential for accessibility planning and real-time facility status checking. Perfect for travelers who need to ensure elevator availability or check accessibility infrastructure before travel.

    Args:
        station_number: Station number (use StadaID format, same as parking functions)
        type: Facility type filter - "ELEVATOR" or "ESCALATOR" (optional)
        state: Operational state filter - "ACTIVE", "INACTIVE", or "UNKNOWN" (optional)  
        equipment_number: Specific equipment number for individual facility lookup (optional)

    Returns:
        List of facilities with detailed information:
        - Facility type (ELEVATOR/ESCALATOR) and descriptive location
        - Current operational status (ACTIVE/INACTIVE/UNKNOWN)
        - Equipment number for specific identification
        - Geographic coordinates (geocoordX/geocoordY in WGS84)
        - Station number and operator information
        - State explanation for detailed status information

    Examples:
        - find_facilities(1071) → All facilities at Berlin Hauptbahnhof (64 total)
        - find_facilities(1071, "ELEVATOR") → Berlin elevators only (12 elevators)
        - find_facilities(1071, "ELEVATOR", "ACTIVE") → Working Berlin elevators (9 active)
        - find_facilities(1866, "ESCALATOR") → Frankfurt escalators (44 escalators)

    Notes:
        - Use same station numbers as parking functions (StadaID format)
        - Berlin Hbf has 64 facilities: 12 elevators, 52 escalators
        - Frankfurt Hbf has 48 facilities: 4 elevators, 44 escalators
        - Real-time status updates show current operational state
        - Critical for wheelchair users and travelers with mobility aids
        - INACTIVE facilities may be temporarily or permanently out of service
    """
    url = f"{BASE_URL_FASTA}/facilities"
    params = {"stationnumber": station_number}
    
    if type:
        params["type"] = type
    if state:
        params["state"] = state  
    if equipment_number:
        params["equipmentnumber"] = equipment_number
    
    response = await fetch_from_db_api(url, params=params)
    
    # FaSta API returns facilities directly as a list
    if isinstance(response, list):
        facilities = response
    else:
        # Fallback: check if response has facilities key or is empty dict
        facilities = response.get("facilities", []) if response else []
    
    return [Facility(**facility) for facility in facilities]

@mcp.tool()
@tool_error_handler
async def get_facilities_by_station(station_number: int) -> FacilityStationResponse:
    """
    Get comprehensive facility information for a specific station including all accessibility infrastructure.

    This tool provides a complete overview of a station's accessibility features and facility status. Perfect for comprehensive accessibility assessment and travel planning for travelers with special needs.

    Args:
        station_number: Station number (use StadaID format, same as find_facilities and parking functions)

    Returns:
        Complete facility information including:
        - Station details and location information
        - All elevators with current status and descriptions
        - Escalator availability and operational status
        - Accessibility infrastructure overview
        - Platform access information
        - Service facility locations and equipment numbers

    Examples:
        - get_facilities_by_station(1071) → Berlin Hauptbahnhof: 64 total facilities
        - get_facilities_by_station(1866) → Frankfurt Hauptbahnhof: 48 total facilities
        - get_facilities_by_station(4859) → München Hauptbahnhof: complete facility overview

    Notes:
        - Use same station numbers as find_facilities() and parking functions (StadaID format)
        - Provides most comprehensive facility view for a station
        - Shows both active and inactive equipment with detailed status
        - Essential for accessibility planning and comprehensive assessment
        - Includes equipment numbers for specific facility identification
        - May include construction schedules and maintenance information
        - Berlin Hbf typically shows 64 facilities, Frankfurt Hbf shows 48 facilities
    """
    url = f"{BASE_URL_FASTA}/stations/{station_number}"
    
    response = await fetch_from_db_api(url)
    
    return FacilityStationResponse(**response)