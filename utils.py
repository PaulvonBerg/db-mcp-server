# utils.py
"""
Shared utilities for the Deutsche Bahn MCP Server
"""

import logging
import httpx
import math
import time
import functools
import re
from typing import Any, Dict, List, Tuple

from mcp import McpError
from config import DB_API_KEY, DB_API_SECRET, BASE_URL_STADA

# --- Security & Validation ---
MAX_CACHE_SIZE = 10000  # Maximum cached items
MAX_STRING_LENGTH = 1000  # Maximum string parameter length
ALLOWED_STATION_NAME_CHARS = re.compile(r'^[a-zA-Z0-9äöüÄÖÜß\s\-\(\)\./]+$')

def validate_station_name(name: str) -> str:
    """Validate and sanitize station name input"""
    if not name or len(name.strip()) == 0:
        raise ValueError("Station name cannot be empty")
    
    name = name.strip()
    if len(name) > MAX_STRING_LENGTH:
        raise ValueError(f"Station name too long (max {MAX_STRING_LENGTH} characters)")
    
    if not ALLOWED_STATION_NAME_CHARS.match(name):
        raise ValueError("Station name contains invalid characters")
    
    return name

def validate_coordinates(latitude: float, longitude: float) -> Tuple[float, float]:
    """Validate geographic coordinates"""
    if not isinstance(latitude, (int, float)) or not isinstance(longitude, (int, float)):
        raise ValueError("Coordinates must be numeric")
    
    if not (-90 <= latitude <= 90):
        raise ValueError("Latitude must be between -90 and 90 degrees")
    
    if not (-180 <= longitude <= 180):
        raise ValueError("Longitude must be between -180 and 180 degrees")
    
    return float(latitude), float(longitude)

def validate_positive_number(value: Any, name: str, maximum: float = None) -> float:
    """Validate positive numeric input"""
    if not isinstance(value, (int, float)):
        raise ValueError(f"{name} must be a number")
    
    if value <= 0:
        raise ValueError(f"{name} must be positive")
    
    if maximum and value > maximum:
        raise ValueError(f"{name} cannot exceed {maximum}")
    
    return float(value)

# --- Caching for StaDa Stations ---
_stada_stations_cache = {"data": None, "timestamp": 0, "size": 0}
CACHE_DURATION = 3600  # Cache for 1 hour

# --- Helper Functions ---
def get_db_api_headers() -> dict:
    if not DB_API_KEY or not DB_API_SECRET:
        raise Exception("API credentials are not configured on the server.")
    return {"DB-Client-Id": DB_API_KEY, "DB-Api-Key": DB_API_SECRET}

async def fetch_from_db_api(url: str, params: dict = None, json_body: dict = None, accept_xml: bool = False) -> Any:
    headers = get_db_api_headers()
    headers["accept"] = "application/xml" if accept_xml else "application/json"
    headers["User-Agent"] = "Deutsche-Bahn-MCP-Server/1.0"
    
    if json_body:
        headers["Content-Type"] = "application/json"

    # Configure timeouts and limits for security
    timeout_config = httpx.Timeout(
        connect=5.0,    # 5 seconds to establish connection
        read=15.0,      # 15 seconds to read response
        write=10.0,     # 10 seconds to write request
        pool=30.0       # 30 seconds total
    )
    
    limits = httpx.Limits(
        max_keepalive_connections=5,
        max_connections=10,
        keepalive_expiry=30.0
    )

    async with httpx.AsyncClient(timeout=timeout_config, limits=limits) as client:
        if json_body:
            response = await client.post(url, headers=headers, json=json_body)
        else:
            response = await client.get(url, headers=headers, params=params)
        
        response.raise_for_status()
        
        if accept_xml:
            import xmltodict
            try:
                parsed = xmltodict.parse(response.text)
                return parsed if parsed is not None else {}
            except Exception as e:
                logging.error(f"Failed to parse XML response: {e}")
                logging.debug(f"XML content: {response.text[:500]}...")
                return {}
        else:
            return response.json()

def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate the great circle distance between two points on earth in km"""
    # Convert decimal degrees to radians
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    # Haversine formula
    dlon, dlat = lon2 - lon1, lat2 - lat1
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    return 2 * math.asin(math.sqrt(a)) * 6371

# --- Error Handling ---
def tool_error_handler(func):
    """
    Decorator to handle tool-specific errors and convert them to JSON-RPC errors.
    """
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except httpx.HTTPStatusError as e:
            # Log full error details for debugging (server-side only)
            logging.error(f"DB API Error: {e.response.status_code} - {e.response.text}", exc_info=True)
            # Return sanitized error message to client
            if e.response.status_code == 404:
                msg = "Requested resource not found"
            elif e.response.status_code == 429:
                msg = "Rate limit exceeded, please try again later"
            elif e.response.status_code >= 500:
                msg = "External service temporarily unavailable"
            else:
                msg = f"External API error (HTTP {e.response.status_code})"
            raise McpError(msg) from e
        except ValueError as e:
            msg = f"Invalid parameter: {e}"
            logging.warning(msg)
            raise McpError(msg) from e
        except Exception as e:
            msg = f"An unexpected server error occurred: {type(e).__name__} - {e}"
            logging.error(msg, exc_info=True)
            raise McpError(msg) from e
    return wrapper