# auth_server.py
# 
# PLACEHOLDER: Authentication Server Implementation
# This file is reserved for future OAuth 2.1 authentication implementation
# Currently not used - the MCP server runs without authentication
#
from fastapi import APIRouter

# import time
# from starlette.responses import HTMLResponse
#
# # This is a placeholder for the auth server.
# # If Auth is desired at a later point in time, you can implement OAuth 2.1 endpoints here.
# _users_db = {
#     "user_id_1": {"username": "testuser"},
# }
# _clients_db = {
#     "client_id_1": {
#         "client_id": "",
#         "client_secret": "",
#         "redirect_uris": ["http://localhost:8000/callback"],
#         "scope": "profile",
#         "response_type": "code",
#         "grant_type": "authorization_code",
#         "token_endpoint_auth_method": "client_secret_basic",
#     }
# }
# _tokens_db = {}
#
# def _get_user(username):
#     for user_id, user in _users_db.items():
#         if user["username"] == username:
#             return {"user_id": user_id, **user}
#     return None

def init_auth_server():
    """Initialize a simplified auth router for demo purposes."""
    router = APIRouter()

    @router.get("/auth/status")
    async def auth_status():
        return {"status": "Auth server placeholder - OAuth2 implementation disabled for now"}

    return router
