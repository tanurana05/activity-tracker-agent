import time
from dateutil import tz
from datetime import datetime
from pynput import mouse, keyboard

class ActivityTracker:
    def __init__(self, log_file, tz_manager):
        self.mouse_activity = False
        self.keyboard_activity = False
        self.last_activity_time = time.time()
        self.log_file = log_file
        self.scripted_activity = False
        self.running = True
        self.mouse_listener = None
        self.keyboard_listener = None
        self.tz_manager = tz_manager
        self.time_diffs = []

    def log_activity(self, activity_type):
        """Logs activity to the log file with a timestamp."""
        try:
            # Use dateutil's tz library to handle various timezone formats
            local_tz = tz.gettz(self.tz_manager.current_timezone)  # Will work for "India Standard Time"
            timestamp = datetime.now(local_tz).strftime('%Y-%m-%d %H:%M:%S')
            
            with open(self.log_file, 'a') as log:
                log.write(f"{timestamp} - {activity_type}\n")
            print(f"Activity logged: {timestamp} - {activity_type}")
        except Exception as e:
            print(f"Error logging activity: {e}")

    def detect_scripted_activity(self):
        """Detects if scripted activity is occurring based on time differences and patterns."""
        current_time = time.time()
        time_diff = current_time - self.last_activity_time
        self.time_diffs.append(time_diff)
        
        # Keep a sliding window of recent time differences
        if len(self.time_diffs) > 10:  # Adjust the window size as needed
            self.time_diffs.pop(0)

        # Check for consistently small time differences
        if all(diff < 0.015 for diff in self.time_diffs):  # Detect fast repeated actions
            self.scripted_activity = True
            self.log_activity("Scripted activity detected!")
        else:
            self.scripted_activity = False  # Reset if no scripted activity detected

        self.last_activity_time = current_time

    def on_mouse_move(self, x, y):
        """Handles mouse movement events."""
        self.mouse_activity = True
        self.detect_scripted_activity()
        self.log_activity("Mouse Moved")

    def on_click(self, x, y, button, pressed):
        """Handles mouse click events."""
        self.mouse_activity = True
        self.detect_scripted_activity()
        self.log_activity("Mouse Clicked")

    def on_scroll(self, x, y, dx, dy):
        """Handles mouse scroll events."""
        self.mouse_activity = True
        self.detect_scripted_activity()
        self.log_activity("Mouse Scrolled")

    def on_key_press(self, key):
        """Handles key press events."""
        self.keyboard_activity = True
        self.detect_scripted_activity()
        try:
            self.log_activity(f"Key Pressed: {key.char}")
        except AttributeError:
            self.log_activity(f"Special Key Pressed: {key}")

    def start_tracking(self):
        """Starts tracking mouse and keyboard activities."""
        self.mouse_listener = mouse.Listener(
            on_move=self.on_mouse_move,
            on_click=self.on_click,
            on_scroll=self.on_scroll
        )
        self.keyboard_listener = keyboard.Listener(on_press=self.on_key_press)

        self.mouse_listener.start()
        self.keyboard_listener.start()

        # Keep the tracking alive until explicitly stopped
        while self.running:
            time.sleep(0.1)  # Reduce CPU usage while waiting

    def stop_tracking(self):
        """Stops tracking mouse and keyboard activities."""
        self.running = False
        if self.mouse_listener:
            self.mouse_listener.stop()
        if self.keyboard_listener:
            self.keyboard_listener.stop()
        
