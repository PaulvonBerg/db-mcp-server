# mcp_server.py
"""
Deutsche Bahn MCP Server - Main server setup and configuration
"""

import logging
import sys
from fastapi import Depends, Request
from mcp import McpError
from mcp.server.fastmcp import FastMCP
from authlib.oauth2.rfc6750 import BearerTokenValidator

from config import (
    DB_API_KEY, DB_API_SECRET, BASE_URL_TIMETABLES, BASE_URL_STADA,
    BASE_URL_PARKING, BASE_URL_FASTA,
)

# --- Logging Setup ---
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s",
    stream=sys.stderr,
)

# --- Authentication & Authorization ---
class MyTokenValidator(BearerTokenValidator):
    def authenticate_token(self, token_string):
        # This is a simplified validator. In a real-world application, you would
        # decode a JWT here and validate its claims (e.g., signature, expiry).
        return {"token": token_string, "scope": "profile"}

# OAuth2 protection disabled for now
# require_oauth = ResourceProtector()
# require_oauth.register_token_validator(MyTokenValidator())

# Import the MCP server instance
from server_instance import mcp

# Import and register all modules after MCP server is initialized
def register_modules():
    """Register all tools, resources, and prompts after server initialization"""
    # Import tools
    from tools import station_tools, timetable_tools, parking_tools, facility_tools
    
    # Import resources and register them
    from resources import travel_resources
    
    # Import prompts
    from prompts import travel_prompts

# Register all modules
register_modules()