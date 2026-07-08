import hashlib
import os
from functools import wraps
from typing import Callable

SALT = os.getenv("WIKI_APP_SALT", "WIKI_default_local_salt_123")

HashFunction = Callable[..., str]

def with_salt(salt: str) -> Callable[[HashFunction], HashFunction]:
    def decorator(func: HashFunction) -> HashFunction:
        @wraps(func) 
        def wrapper(data: str, *args, **kwargs) -> str:
            salted_data = f"{data}{salt}"
            result = func(salted_data, *args, **kwargs)
            return result
        return wrapper
    return decorator

@with_salt(SALT)
def hash_sha256(data: str) -> str:
    return hashlib.sha256(data.encode()).hexdigest()