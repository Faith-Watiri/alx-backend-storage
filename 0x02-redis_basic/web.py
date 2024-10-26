import requests
import redis
from functools import wraps

# Initialize Redis connection
redis_client = redis.Redis()


def cache_page(expiration=10):
    """
    Decorator to cache the result of get_page function.

    Args:
        expiration (int): The cache expiration time in seconds.

    Returns:
        function: A wrapper function that caches the result of the decorated function.
    """
    
    def decorator(func):
        @wraps(func)
        def wrapper(url):
            """
            Wrapper function to cache and fetch the URL content.

            Args:
                url (str): The URL to fetch.

            Returns:
                str: The HTML content of the URL, either from cache or directly fetched.
            """
            # Create a Redis key for the cache and count
            cache_key = f"cache:{url}"
            count_key = f"count:{url}"

            # Increment the count of accesses
            redis_client.incr(count_key)

            # Check if the page is already cached in Redis
            cached_page = redis_client.get(cache_key)
            if cached_page:
                return cached_page.decode('utf-8')

            # If not cached, fetch the page and store it in Redis
            result = func(url)

            # Cache the result and set an expiration time
            redis_client.setex(cache_key, expiration, result)
            return result
        return wrapper
    return decorator


@cache_page(expiration=10)
def get_page(url: str) -> str:
    """
    Fetches the HTML content of a given URL and returns it.

    Args:
        url (str): The URL to fetch the HTML content from.

    Returns:
        str: The HTML content of the URL.
    """
    response = requests.get(url)
    return response.text
