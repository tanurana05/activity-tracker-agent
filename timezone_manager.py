import time
import threading

class TimeZoneManager:
    def __init__(self):
        self.current_timezone = self.get_current_timezone()

    def get_current_timezone(self):
        # This gets the current system time zone
        return time.tzname[0]  # This may return something like 'GMT' or 'UTC'

    def check_time_zone_change(self):
        while True:
            new_timezone = self.get_current_timezone()
            if new_timezone != self.current_timezone:
                print(f"Time zone changed from {self.current_timezone} to {new_timezone}")
                self.current_timezone = new_timezone
                # Here, you could add logic to update timestamps in logs if necessary
            time.sleep(60)  # Check every minute

