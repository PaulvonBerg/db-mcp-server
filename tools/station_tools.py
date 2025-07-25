# tools/station_tools.py
"""
Station-related MCP tools for Deutsche Bahn API
"""

import logging
from typing import List

from models import StaDaStation, StationByPosition
from utils import (
    tool_error_handler, fetch_from_db_api, haversine_distance,
    validate_station_name, validate_coordinates, validate_positive_number
)
from config import BASE_URL_STADA

# Import MCP instance from shared module
from server_instance import mcp

# --- General Tools ---

@mcp.tool()
async def ping() -> dict:
    """
    Simple ping tool to verify server responsiveness.
    Returns empty object as per MCP specification.
    """
    return {}

# --- Station Data Tools ---

@mcp.tool()
@tool_error_handler
async def get_station_by_name(name: str, limit: int = 10) -> List[StaDaStation]:
    """
    Search for German railway stations by name or partial name. Returns comprehensive station master data including contact information, services, and facilities.

    This tool searches the official Deutsche Bahn station database (StaDa) and supports flexible search patterns. Perfect for finding stations when you know the approximate name or want to explore stations in a specific area.

    Args:
        name: Station name or partial name to search for (e.g., "Berlin", "Frankfurt", "München")
        limit: Maximum number of results to return (default: 10, max: 50)

    Returns:
        List of matching stations with complete details including:
        - Official station name and location
        - Station category (1-7 scale, 1 = major hub)
        - Contact information and addresses
        - Available services (DB Lounge, Travel Center, etc.)
        - Accessibility features and barrier-free information
        - EVA numbers for timetable integration

    Examples:
        - get_station_by_name("Berlin") → Returns all Berlin stations
        - get_station_by_name("Frankfurt Hbf") → Returns Frankfurt main station
        - get_station_by_name("München", 5) → Returns top 5 Munich area stations
    """
    # Validate inputs with fallbacks
    try:
        name = validate_station_name(name)
    except ValueError as e:
        # Log validation error but use basic sanitization
        logging.warning(f"Station name validation failed: {e}")
        name = str(name).strip()[:1000] if name else ""
        if not name:
            raise ValueError("Station name cannot be empty")
    
    try:
        limit = int(validate_positive_number(limit, "limit", maximum=50))
    except ValueError:
        limit = max(1, min(int(limit) if isinstance(limit, (int, float)) else 10, 50))
    
    # First try with searchstring parameter
    logging.info(f"Searching stations using API searchstring parameter: {name}")
    url = f"{BASE_URL_STADA}/stations"
    try:
        response = await fetch_from_db_api(url, params={"searchstring": name})
        stations = response.get("result", [])
    except Exception as e:
        # Fallback: get all stations and filter client-side
        logging.warning(f"Searchstring failed ({e}), falling back to client-side filtering")
        response = await fetch_from_db_api(url, params={"limit": 5500})
        all_stations = response.get("result", [])
        
        # Filter by name client-side
        name_lower = name.lower()
        stations = [
            station for station in all_stations
            if name_lower in station.get("name", "").lower()
        ]
    
    # Sort by relevance (exact matches first, then by name)
    name_lower = name.lower()
    stations.sort(key=lambda s: (
        not s.get("name", "").lower().startswith(name_lower),
        s.get("name", "")
    ))

    # Limit results
    limited_stations = stations[:min(limit, 50)]
    
    # Convert to Pydantic models
    return [StaDaStation(**station) for station in limited_stations]

@mcp.tool()
@tool_error_handler
async def get_stations_by_position(latitude: float, longitude: float, radius: float = 2.0, limit: int = 10) -> List[StationByPosition]:
    """
    Find German railway stations near a geographic location within a specified radius. Returns stations with distance calculations and basic information.

    This tool helps travelers find the closest railway stations to any location in Germany. Perfect for finding stations near hotels, airports, tourist attractions, or your current position.

    Args:
        latitude: Geographic latitude in decimal degrees (e.g., 52.5200 for Berlin)
        longitude: Geographic longitude in decimal degrees (e.g., 13.4050 for Berlin)
        radius: Search radius in kilometers (default: 2.0, max: 50.0)
        limit: Maximum number of stations to return (default: 10, max: 25)

    Returns:
        List of nearby stations sorted by distance, including:
        - Station name and location details
        - Distance from search coordinates
        - Geographic coordinates of the station
        - EVA number for further API calls
        - Basic station information

    Examples:
        - get_stations_by_position(52.5200, 13.4050) → Stations near Berlin center
        - get_stations_by_position(50.1109, 8.6821, 5.0) → Stations within 5km of Frankfurt
        - get_stations_by_position(48.1351, 11.5820, 1.0, 5) → 5 closest stations to Munich center

    Notes:
        - Coordinates should be in WGS84 format (standard GPS coordinates)
        - Results are sorted by straight-line distance
        - Use get_station_by_name() for detailed station information
    """
    # Validate inputs with fallbacks
    try:
        latitude, longitude = validate_coordinates(latitude, longitude)
    except ValueError as e:
        # Log validation error but do basic checks
        logging.warning(f"Coordinate validation failed: {e}")
        if not (-90 <= latitude <= 90) or not (-180 <= longitude <= 180):
            raise ValueError("Invalid coordinates: latitude must be between -90 and 90, longitude between -180 and 180")
    
    try:
        radius = validate_positive_number(radius, "radius", maximum=50.0)
    except ValueError:
        radius = max(0.1, min(float(radius) if isinstance(radius, (int, float)) else 2.0, 50.0))
    
    try:
        limit = int(validate_positive_number(limit, "limit", maximum=25))
    except ValueError:
        limit = max(1, min(int(limit) if isinstance(limit, (int, float)) else 10, 25))

    # Note: StaDa API doesn't have a byCoords endpoint, so we'll get stations by region
    # and filter by distance client-side. We determine the likely federal state(s)
    # based on coordinates to get more relevant stations.
    
    # Map coordinate ranges to German federal states for smarter filtering
    def get_likely_federal_states(lat, lon):
        """Determine likely federal states based on coordinates"""
        # Approximate coordinate ranges for German federal states
        state_coords = {
            "baden-wuerttemberg": (47.5, 49.8, 7.5, 10.5),  # SW Germany
            "bayern": (47.3, 50.6, 8.9, 13.8),              # Bavaria (SE)
            "berlin": (52.3, 52.7, 13.1, 13.8),             # Berlin
            "brandenburg": (51.4, 53.6, 11.3, 14.8),        # Around Berlin
            "bremen": (53.0, 53.6, 8.5, 8.9),               # Bremen city
            "hamburg": (53.4, 53.7, 9.7, 10.3),             # Hamburg city
            "hessen": (49.4, 51.7, 7.8, 10.2),              # Central Germany
            "mecklenburg-vorpommern": (53.1, 54.7, 10.6, 14.4), # NE coast
            "niedersachsen": (51.3, 53.9, 6.7, 11.6),       # NW Germany
            "nordrhein-westfalen": (50.3, 52.5, 5.9, 9.5),  # W Germany
            "rheinland-pfalz": (49.1, 50.9, 6.1, 8.5),      # SW Germany
            "saarland": (49.1, 49.6, 6.4, 7.4),             # Small SW state
            "sachsen": (50.2, 51.7, 11.9, 15.0),            # E Germany
            "sachsen-anhalt": (51.0, 53.0, 10.6, 13.2),     # Central E
            "schleswig-holstein": (53.4, 55.1, 8.0, 11.3),  # N Germany
            "thueringen": (50.2, 51.6, 9.9, 12.7)           # Central Germany
        }
        
        likely_states = []
        for state, (min_lat, max_lat, min_lon, max_lon) in state_coords.items():
            # Check if coordinates are within or near the state bounds (with buffer)
            buffer = 0.5  # degrees buffer for border areas
            if (min_lat - buffer <= lat <= max_lat + buffer and 
                min_lon - buffer <= lon <= max_lon + buffer):
                likely_states.append(state)
        
        return likely_states
    
    # Get likely states for the search coordinates
    likely_states = get_likely_federal_states(latitude, longitude)
    
    all_stations = []
    
    if likely_states:
        # Fetch stations from likely federal states
        for state in likely_states[:3]:  # Limit to 3 states to avoid too many requests
            url = f"{BASE_URL_STADA}/stations"
            params = {"federalstate": state, "limit": 1000}
            try:
                response = await fetch_from_db_api(url, params=params)
                stations = response.get("result", [])
                all_stations.extend(stations)
            except Exception as e:
                logging.warning(f"Failed to fetch stations for {state}: {e}")
                continue
    
    # Fallback: if no likely states found or all requests failed, get general stations
    if not all_stations:
        url = f"{BASE_URL_STADA}/stations"
        params = {"limit": 2000}  # Increase limit for fallback
        response = await fetch_from_db_api(url, params=params)
        all_stations = response.get("result", [])
    
    # Filter stations by coordinates and calculate distances
    stations_with_distance = []
    for station in all_stations:
        # Get coordinates from evaNumbers array
        eva_numbers = station.get("evaNumbers", [])
        if not eva_numbers:
            continue
            
        # Use the main EVA number's coordinates
        main_eva = next((eva for eva in eva_numbers if eva.get("isMain", False)), eva_numbers[0] if eva_numbers else None)
        if not main_eva:
            continue
            
        coords = main_eva.get("geographicCoordinates", {})
        if not coords or coords.get("type") != "Point":
            continue
            
        # Coordinates are [longitude, latitude] in GeoJSON
        coord_array = coords.get("coordinates", [])
        if len(coord_array) < 2:
            continue
            
        station_lon, station_lat = coord_array[0], coord_array[1]
        
        if station_lat and station_lon:
            distance = haversine_distance(latitude, longitude, station_lat, station_lon)
            
            # Only include stations within the radius
            if distance <= radius:
                # Create simplified station object for StationByPosition model
                simple_station = {
                    "name": station.get("name", ""),
                    "id": str(station.get("number", "")),
                    "lat": station_lat,
                    "lon": station_lon,
                    "distance_km": round(distance, 2)
                }
                stations_with_distance.append(simple_station)
    
    # Sort by distance and limit results
    stations_with_distance.sort(key=lambda s: s.get("distance_km", float('inf')))
    limited_stations = stations_with_distance[:limit]
    
    return [StationByPosition(**station) for station in limited_stations]