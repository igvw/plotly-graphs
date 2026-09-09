import pandas as pd
import os
import functools
import colorsys

def cache():
    """Decorator to cache function results as CSV files."""
    cache_dir='data/cache'
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Ensure cache directory exists
            os.makedirs(cache_dir, exist_ok=True)

            # Generate cache file path based on function arguments
            cache_filename = "_".join(
                [func.__name__] + 
                ["_".join(v) for _, v in kwargs.items()]
            ) + ".csv"
            print(cache_filename)
            cache_path = os.path.join(cache_dir, cache_filename)

            # If cached file exists, return cached DataFrame
            if os.path.exists(cache_path):
                print(f"Loading cached data from {cache_path}")
                return pd.read_csv(cache_path)

            # Run function normally and cache result
            result = func(*args, **kwargs)
            if isinstance(result, pd.DataFrame):
                result.to_csv(cache_path, index=False)
                print(f"Cached result at {cache_path}")
            return result
        return wrapper
    return decorator

with open('data/dictionaries/ordbok.csv') as f:
    ordbok = {
        line.split(';')[0]: line.split(';')[1].strip()
        for line in f.readlines()
    }

def translate(key, language='no'):
    assert language in ['en', 'no']
    if language == 'no':
        translation_dict = ordbok
    elif language == 'en':
        return key
    if isinstance(key, list):
        for k in key:
            assert k in translation_dict, key
        return [translation_dict[k] for k in key]
    elif isinstance(key, str):
        assert key in ordbok, key
        return translation_dict[key]
    
def eng2no(key):
    translate(language='no')

def hsv_to_hex(h, s=0.7, v=0.7):
    """Convert HSV values to HEX."""
    if h < 0:
        h += 1
    rgb = colorsys.hsv_to_rgb(h, s, v)  # Normalize H to [0,1]
    return f"#{int(rgb[0] * 255):02x}{int(rgb[1] * 255):02x}{int(rgb[2] * 255):02x}"