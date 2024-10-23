import requests
import redis
from functools import wraps
import time

# Initialize Redis connection
redis_client = redis.Redis()

def cache_page(expiration=10):
    """Decorator to cache the result of get_page function."""
    def decorator(func):
        @wraps(func)
        def wrapper(url):
            # Create a Redis key for the cache and count
            cache_key = f"cache:{url}"
            count_key = f"count:{url}"

            # Check if the page is already cached in Redis
            cached_page = redis_client.get(cache_key)
            if cached_page:
                # Increment the count of accesses
                redis_client.incr(count_key)
                return cached_page.decode('utf-8')

            # If not cached, fetch the page and store it in Redis
            result = func(url)

            # Cache the result and set an expiration time
            redis_client.setex(cache_key, expiration, result)
            # Increment the access count
            redis_client.incr(count_key)
            return result
        return wrapper
    return decorator

@cache_page(expiration=10)
def get_page(url: str) -> str:
    """Fetches the HTML content of a given URL and returns it."""
    response = requests.get(url)
    return response.text


# Testing
if __name__ == "__main__":
    url = "http://slowwly.robertomurray.co.uk/delay/3000/url/http://www.google.com"
    
    print("First request (should take time):")
    print(get_page(url))
    
    time.sleep(5)  # Sleep for 5 seconds (within cache time)
    
    print("Second request (should be cached):")
    print(get_page(url))

    time.sleep(10)  # Sleep for 10 seconds (cache expiration)
    
    print("Third request (cache expired, should fetch again):")
    print(get_page(url))

