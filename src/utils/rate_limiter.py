"""Rate limiting utilities using Token Bucket algorithm."""

import time
from dataclasses import dataclass, field
from threading import Lock
from typing import Optional


@dataclass
class RateLimiter:
    """
    Token Bucket rate limiter.
    
    Allows bursts up to max_tokens, then limits to tokens_per_second.
    """
    
    tokens_per_second: float
    max_tokens: int
    tokens: float = field(init=False)
    last_update: float = field(init=False)
    lock: Lock = field(default_factory=Lock, init=False)
    
    def __post_init__(self):
        self.tokens = float(self.max_tokens)
        self.last_update = time.time()
    
    def _add_tokens(self):
        """Add tokens based on time elapsed."""
        now = time.time()
        elapsed = now - self.last_update
        self.tokens = min(self.max_tokens, self.tokens + elapsed * self.tokens_per_second)
        self.last_update = now
    
    def acquire(self, tokens: int = 1, blocking: bool = True) -> bool:
        """
        Acquire tokens from the bucket.
        
        Args:
            tokens: Number of tokens to acquire
            blocking: If True, wait until tokens are available
            
        Returns:
            True if tokens were acquired, False otherwise
        """
        with self.lock:
            self._add_tokens()
            
            if self.tokens >= tokens:
                self.tokens -= tokens
                return True
            
            if not blocking:
                return False
            
            # Calculate wait time
            needed = tokens - self.tokens
            wait_time = needed / self.tokens_per_second
            
        # Wait outside the lock
        time.sleep(wait_time)
        
        with self.lock:
            self._add_tokens()
            self.tokens -= tokens
            return True
    
    def wait(self):
        """Wait for one token to become available."""
        self.acquire(1, blocking=True)


class MultiRateLimiter:
    """Manage multiple rate limiters for different APIs."""
    
    def __init__(self):
        self.limiters: dict[str, RateLimiter] = {}
    
    def add_limiter(self, name: str, tokens_per_second: float, max_tokens: int):
        """Add a new rate limiter."""
        self.limiters[name] = RateLimiter(
            tokens_per_second=tokens_per_second,
            max_tokens=max_tokens
        )
    
    def acquire(self, name: str, tokens: int = 1, blocking: bool = True) -> bool:
        """Acquire tokens from a named limiter."""
        if name not in self.limiters:
            return True  # No limiter = no limit
        return self.limiters[name].acquire(tokens, blocking)
    
    def wait(self, name: str):
        """Wait for one token from a named limiter."""
        if name in self.limiters:
            self.limiters[name].wait()


# Global rate limiter instance
rate_limiters = MultiRateLimiter()

# Configure default limiters
rate_limiters.add_limiter("youtube", tokens_per_second=1, max_tokens=5)  # 1/sec, burst of 5
rate_limiters.add_limiter("trends", tokens_per_second=0.5, max_tokens=3)  # 1 per 2 sec
rate_limiters.add_limiter("notion", tokens_per_second=3, max_tokens=3)  # 3/sec as per API
