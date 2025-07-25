# server_instance.py
"""
MCP server instance - shared across modules
"""

from mcp.server.fastmcp import FastMCP

# Create the MCP server instance
mcp = FastMCP(
    "deutschebahn_mcp_server",
    instructions="A server providing tools to access Deutsche Bahn (DB) and related mobility APIs for train schedules, station information, and parking.",
)