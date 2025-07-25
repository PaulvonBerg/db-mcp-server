# rate_limiter.py
"""
Simple in-memory rate limiter for the MCP server
"""

import time
import asyncio
from collections import defaultdict, deque
from typing import Dict, Tuple
from fastapi import HTTPException

class RateLimiter:
    """Simple sliding window rate limiter"""
    
    def __init__(self, requests_per_minute: int = 60, requests_per_hour: int = 1000):
        self.requests_per_minute = requests_per_minute
        self.requests_per_hour = requests_per_hour
        self.minute_windows: Dict[str, deque] = defaultdict(deque)
        self.hour_windows: Dict[str, deque] = defaultdict(deque)
        self._lock = asyncio.Lock()
    
    async def is_allowed(self, client_id: str) -> bool:
        """Check if client is allowed to make a request"""
        async with self._lock:
            now = time.time()
            
            # Clean old entries and check minute limit
            minute_window = self.minute_windows[client_id]
            while minute_window and minute_window[0] < now - 60:
                minute_window.popleft()
            
            if len(minute_window) >= self.requests_per_minute:
                return False
            
            # Clean old entries and check hour limit
            hour_window = self.hour_windows[client_id]
            while hour_window and hour_window[0] < now - 3600:
                hour_window.popleft()
            
            if len(hour_window) >= self.requests_per_hour:
                return False
            
            # Add current request
            minute_window.append(now)
            hour_window.append(now)
            
            return True
    
    async def get_retry_after(self, client_id: str) -> int:
        """Get retry-after time in seconds"""
        async with self._lock:
            now = time.time()
            
            # Check minute window
            minute_window = self.minute_windows[client_id]
            if len(minute_window) >= self.requests_per_minute and minute_window:
                oldest_in_minute = minute_window[0]
                return max(1, int(oldest_in_minute + 60 - now))
            
            # Check hour window
            hour_window = self.hour_windows[client_id]
            if len(hour_window) >= self.requests_per_hour and hour_window:
                oldest_in_hour = hour_window[0]
                return max(60, int(oldest_in_hour + 3600 - now))
            
            return 0

# Global rate limiter instance
rate_limiter = RateLimiter()

def get_client_id(request) -> str:
    """Extract client identifier from request"""
    # Use X-Forwarded-For header if available (for load balancers)
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        # Take the first IP in the chain
        client_ip = forwarded_for.split(",")[0].strip()
    else:
        client_ip = request.client.host if request.client else "unknown"
    
    # Include user agent for additional fingerprinting
    user_agent = request.headers.get("User-Agent", "")[:50]  # Limit length
    
    return f"{client_ip}:{hash(user_agent) % 10000}"

async def check_rate_limit(request):
    """Middleware function to check rate limits"""
    client_id = get_client_id(request)
    
    if not await rate_limiter.is_allowed(client_id):
        retry_after = await rate_limiter.get_retry_after(client_id)
        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded",
            headers={"Retry-After": str(retry_after)}
        )