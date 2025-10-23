from datetime import datetime, timezone, timedelta
import diskcache as dc
import time

cache = dc.Cache('./cache')
# cache.set('temp_key', 'temp_value', expire=60)

def timeToISO(local_dt):
    utc_dt = local_dt.astimezone(timezone.utc)
    
    return utc_dt.isoformat().replace('+00:00', 'Z')


def timeFromISO(isodate):
    dt = datetime.fromisoformat(isodate.replace('Z', '+00:00'))
    local_dt = dt.astimezone()
    return(local_dt)

class TimestampedCache(dc.Cache):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._timestamp_suffix = '__timestamp__'
    
    def set(self, key, value, *args, **kwargs):
        """Set a value and store its timestamp."""
        # Store the actual value
        result = super().set(key, value, *args, **kwargs)
        # Store the timestamp with a special key
        if result:
            timestamp_key = f"{key}{self._timestamp_suffix}"
            super().set(timestamp_key, time.time(), *args, **kwargs)
        return result
    
    def get(self, key, default=None, *args, **kwargs):
        """Get a value without the timestamp."""
        return super().get(key, default, *args, **kwargs)
    
    def get_timestamp(self, key):
        """Retrieve the timestamp of when the value was last set."""
        timestamp_key = f"{key}{self._timestamp_suffix}"
        return super().get(timestamp_key)
    
    def delete(self, key, *args, **kwargs):
        timestamp_key = f"{key}{self._timestamp_suffix}"
        super().delete(timestamp_key)

        return super().delete(key, *args, **kwargs)
