"""
PRISM Rate Limiter.
Uses slowapi to prevent webhook flooding and dashboard API abuse.
"""

from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
