# Import from dev_config for backward compatibility
try:
    from dev_config import LIGHT_LOADING_TIME, HEAVY_LOADING_TIME, BUFFER_TIME
except ImportError:
    # Fallback values if dev_config is not available
    LIGHT_LOADING_TIME = 1.5
    HEAVY_LOADING_TIME = 2
    BUFFER_TIME = 0.1