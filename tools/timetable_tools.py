# tools/timetable_tools.py
"""
Timetable-related MCP tools for Deutsche Bahn API
"""

import logging
import xmltodict
from typing import List, Dict, Any

from models import TimetableStationSearchResponse, Timetable
from utils import tool_error_handler, fetch_from_db_api
from config import BASE_URL_TIMETABLES

# Import MCP instance from shared module
from server_instance import mcp

# --- Timetables API Tools ---


@mcp.tool()
@tool_error_handler  
async def get_planned_timetable(eva_number: str, date: str, hour: str) -> Dict[str, Any]:
    """
    Get the planned timetable for a specific station, date, and hour. Returns scheduled train departures and arrivals without real-time changes.

    This tool provides the baseline scheduled service for a station during a specific hour. Perfect for planning journeys in advance or understanding the regular service pattern. Use this with real-time tools to see current vs. planned service.

    Args:
        eva_number: Station EVA number (get from get_station_by_name)
        date: Date in YYMMDD format (e.g., "250723" for July 23, 2025)  
        hour: Hour in HH format, 24-hour clock (e.g., "14" for 2 PM)

    Returns:
        Dictionary containing planned timetable data:
        - station: Station name
        - eva: EVA number
        - stops: List of planned train stops with:
          - Trip information (train number, category)
          - Planned times and platforms
          - Route information (origin/destination)
          - Service type and operator

    Examples:
        - get_planned_timetable("8000105", "250723", "14") → Frankfurt 2-3 PM planned service
        - get_planned_timetable("8011160", "250724", "08") → Berlin Hbf 8-9 AM planned service
        - get_planned_timetable("8000261", "250725", "18") → München 6-7 PM planned service

    Notes:
        - Shows only planned/scheduled data, no delays or cancellations
        - Each hour slice includes trains arriving/departing in that hour
        - Use get_recent_timetable_changes() for real-time information
        - Date format is 2-digit year + 2-digit month + 2-digit day
    """
    url = f"{BASE_URL_TIMETABLES}/plan/{eva_number}/{date}/{hour}"
    response = await fetch_from_db_api(url, accept_xml=True)
    
    # Handle cases where XML parsing returns None or empty response
    if not response:
        return {}
    
    return response.get("timetable", {})

@mcp.tool()
@tool_error_handler
async def get_recent_timetable_changes(eva_number: str) -> Dict[str, Any]:
    """
    Get recent timetable changes (last 2 minutes) for a station. Returns only the most recent delays, cancellations, and platform changes.

    This tool provides immediate updates about service disruptions that occurred in the last 2 minutes. Essential for real-time travel decisions and current station status. Use this for the most up-to-date information about ongoing travel disruptions.

    Args:
        eva_number: Station EVA number (get from get_station_by_name)

    Returns:
        Dictionary with recent changes including:
        - station: Station name
        - eva: EVA number  
        - stops: List of recently changed train stops with:
          - Updated departure/arrival times
          - Platform changes
          - Cancellation status
          - Delay information
          - Trip details (train number, route)

    Examples:
        - get_recent_timetable_changes("8000105") → Frankfurt recent disruptions
        - get_recent_timetable_changes("8011160") → Berlin Hbf last 2 min changes
        - get_recent_timetable_changes("8000261") → München immediate updates

    Notes:
        - Only shows changes from the last 2 minutes
        - Updated every 30 seconds
        - Empty result means no recent changes
        - Use get_full_timetable_changes() for complete disruption overview
        - Critical for passengers currently at the station
    """
    url = f"{BASE_URL_TIMETABLES}/rchg/{eva_number}"
    response = await fetch_from_db_api(url, accept_xml=True)
    
    # Handle cases where XML parsing returns None or empty response
    if not response:
        return {}
    
    return response.get("timetable", {})

@mcp.tool()
@tool_error_handler
async def get_full_timetable_changes(eva_number: str) -> Dict[str, Any]:
    """
    Get all known timetable changes for a station. Returns complete disruption information from now until indefinitely into the future.

    This tool provides a comprehensive view of all known service disruptions affecting a station. Perfect for journey planning and understanding the overall service situation. Changes are removed once trains depart.

    Args:
        eva_number: Station EVA number (get from get_station_by_name)

    Returns:
        Dictionary with all known changes including:
        - station: Station name
        - eva: EVA number
        - stops: Complete list of affected train stops with:
          - All current and future delays
          - Platform changes
          - Cancellations
          - Route modifications
          - Service disruption details

    Examples:
        - get_full_timetable_changes("8000105") → All Frankfurt disruptions
        - get_full_timetable_changes("8011160") → Complete Berlin Hbf status
        - get_full_timetable_changes("8000261") → All München service issues

    Notes:
        - Shows all changes from now into the future
        - Updated every 30 seconds
        - More comprehensive than recent changes
        - Use for complete disruption analysis
        - Changes removed after trains depart
        - May include planned track work and temporary service changes
    """
    url = f"{BASE_URL_TIMETABLES}/fchg/{eva_number}"
    response = await fetch_from_db_api(url, accept_xml=True)
    
    # Handle cases where XML parsing returns None or empty response
    if not response:
        return {}
    
    return response.get("timetable", {})