# main.py
import uvicorn
import contextlib
import logging
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from mcp_server import mcp
from auth_server import init_auth_server
from rate_limiter import check_rate_limit
from config import CLOUD_RUN_URL, CUSTOM_DOMAIN

# The documentation shows that when mounting an MCP app, its session manager
# must be run within the parent application's lifespan.
@contextlib.asynccontextmanager
async def lifespan(app: FastAPI):
    async with mcp.session_manager.run():
        yield

# Create a standard FastAPI application
app = FastAPI(
    title="Deutsche Bahn MCP Server",
    description="A server that wraps public DB APIs as an MCP server.",
    version="1.0.0",
    lifespan=lifespan
)

# Add security middleware
allowed_hosts = [
    "localhost", 
    "127.0.0.1"
]

# Add custom domain if configured
if CUSTOM_DOMAIN:
    allowed_hosts.append(CUSTOM_DOMAIN)

# Add Cloud Run URL if configured (for load balancer routing)
if CLOUD_RUN_URL:
    # Extract hostname from URL
    from urllib.parse import urlparse
    cloud_run_hostname = urlparse(CLOUD_RUN_URL).netloc
    if cloud_run_hostname:
        allowed_hosts.append(cloud_run_hostname)

app.add_middleware(
    TrustedHostMiddleware, 
    allowed_hosts=allowed_hosts
)

# Add CORS middleware - production security settings
# Add CORS origins
cors_origins = [
    "https://claude.ai",
    "http://localhost:*",
    "http://127.0.0.1:*"
]

# Add custom domain origins if configured  
if CUSTOM_DOMAIN:
    cors_origins.extend([
        f"https://{CUSTOM_DOMAIN}",
        f"https://*.{CUSTOM_DOMAIN.split('.', 1)[-1] if '.' in CUSTOM_DOMAIN else CUSTOM_DOMAIN}"
    ])

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS", "HEAD"],
    allow_headers=[
        "Content-Type", 
        "Accept", 
        "X-Session-Id", 
        "Authorization",
        "X-Requested-With",
        "Origin"
    ],
    max_age=3600,
)

# Add rate limiting and security headers middleware
@app.middleware("http")
async def security_middleware(request: Request, call_next):
    # Re-enable rate limiting with reasonable limits
    if request.url.path.startswith("/mcp"):
        try:
            await check_rate_limit(request)
        except Exception as e:
            # Log rate limit errors but don't break the request
            logging.warning(f"Rate limit check failed: {e}")
            pass
    
    response = await call_next(request)
    
    # Security headers
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY" 
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
    
    # Prevent caching of sensitive responses
    if request.url.path.startswith("/mcp"):
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
    
    return response

# Add health check endpoint before mounting MCP server
@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "Deutsche Bahn MCP Server"}

# Initialize the OAuth 2.1 Authorization Server and get its router
auth_router = init_auth_server()
app.include_router(auth_router)

# Mount the streamable HTTP MCP server at root so /mcp endpoint is available
app.mount("/", mcp.streamable_http_app())

if __name__ == "__main__":
    # This block is for local development.
    uvicorn.run(app, host="0.0.0.0", port=8080)