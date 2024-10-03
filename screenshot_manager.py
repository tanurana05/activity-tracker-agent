import os
import time
import json
from datetime import datetime
from PIL import ImageGrab, Image, ImageFilter
from data_uploader import DataUploader

# Function to read configuration from a JSON file
def read_config(config_file):
    with open(config_file, 'r') as f:
        config = json.load(f)
    return config

class ScreenshotManager:
    def __init__(self, base_directory, activity_tracker, config_file):
        self.base_directory = base_directory
        self.data_uploader = DataUploader(self.base_directory)
        self.screenshot_interval = 60  # Default interval
        self.activity_tracker = activity_tracker
        self.capture_screenshots = True
        self.capture_blurred = False
        self.config_file = config_file
        self.running = True

        if not os.path.exists(self.base_directory):
            os.makedirs(self.base_directory)

        # Load initial configuration
        self.load_config()

    def load_config(self):
        """Loads configuration settings from the JSON file."""
        config = read_config(self.config_file)
        self.capture_screenshots = config.get('capture_screenshots', True)
        self.capture_blurred = config.get('capture_blurred', False)
        self.screenshot_interval = config.get('screenshot_interval', 60)

    def save_config(self):
        """Saves the current configuration settings to the JSON file."""
        config = {
            'capture_screenshots': self.capture_screenshots,
            'capture_blurred': self.capture_blurred,
            'screenshot_interval': self.screenshot_interval
        }
        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=4)

    def blur_image(self, image_path):
        """Blurs the image and saves it."""
        img = Image.open(image_path)
        blurred_img = img.filter(ImageFilter.GaussianBlur(10))
        blurred_img.save(image_path)
        print(f"Blurred image saved: {image_path}")

    def capture_screenshot(self):
        """Captures a screenshot based on the current configuration."""
        self.load_config()  # Load updated config settings before each screenshot
        if not self.capture_screenshots:
            print("Screenshot capture is disabled in the config.")
            return

        timestamp = datetime.now().strftime('%Y%m%d-%H')
        screenshot_dir = os.path.join(self.base_directory, timestamp)
        if not os.path.exists(screenshot_dir):
            os.makedirs(screenshot_dir)

        screenshot_file = f"screenshot_{datetime.now().strftime('%Y%m%d-%H%M%S')}.png"
        screenshot_path = os.path.join(screenshot_dir, screenshot_file)

        if time.time() - self.activity_tracker.last_activity_time <= self.screenshot_interval:
            try:
                # Capture the screenshot using Pillow's ImageGrab on Windows
                screenshot = ImageGrab.grab()
                screenshot.save(screenshot_path)
                print(f"Screenshot saved at {screenshot_path}")

                if self.capture_blurred:
                    self.blur_image(screenshot_path)
            except Exception as e:
                print(f"Failed to capture screenshot: {e}")
        else:
            print("No activity detected, skipping screenshot.")

    def start_capturing(self):
        """Starts the screenshot capturing process and polls for configuration updates."""
        while self.running:  # Check if the capturing is still running
            self.capture_screenshot()  # Capture screenshots at the configured interval
            time.sleep(self.screenshot_interval)

    def set_screenshot_interval(self, interval):
        """Allows manual setting of screenshot interval and saves the new interval to config."""
        self.screenshot_interval = interval
        self.save_config()  # Save the updated interval to the config file
        print(f"Screenshot interval updated to: {interval} seconds")

    def stop_capturing(self):
        """Stops the screenshot capturing process."""
        self.running = False
