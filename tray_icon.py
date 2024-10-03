import os
import pystray
from PIL import Image, ImageDraw
from pystray import MenuItem, Menu
import json
from tkinter import simpledialog, Tk  # Import Tkinter for dialog

def remove_lock():
    """Removes the lock file upon exit."""
    if os.path.exists("app.lock"):
        os.remove("app.lock")

def load_config(config_file):
    """Loads configuration from the specified JSON file."""
    with open(config_file, 'r') as f:
        return json.load(f)

def update_config(config_file, key, value):
    """Updates a specific key in the configuration file."""
    config = load_config(config_file)
    config[key] = value
    with open(config_file, 'w') as f:
        json.dump(config, f, indent=4)

def create_image(width, height, color1, color2):
    """Creates an icon for the tray."""
    image = Image.new('RGB', (width, height), color1)
    dc = ImageDraw.Draw(image)
    dc.rectangle((width // 2, 0, width, height // 2), fill=color2)
    dc.rectangle((0, height // 2, width // 2, height), fill=color2)
    return image

def run_tray_icon(screenshot_manager, config_file, activity_tracker):
    """Runs the tray icon with options to manage screenshot settings."""

    # Function to toggle screenshot capturing
    def toggle_screenshots(icon, item):
        new_value = not screenshot_manager.capture_screenshots
        update_config(config_file, 'capture_screenshots', new_value)
        screenshot_manager.capture_screenshots = new_value
        update_menu(icon)  # Refresh menu

    # Function to toggle blur option
    def toggle_blur(icon, item):
        new_value = not screenshot_manager.capture_blurred
        update_config(config_file, 'capture_blurred', new_value)
        screenshot_manager.capture_blurred = new_value
        update_menu(icon)  # Refresh menu

    # Function to set screenshot interval
    def set_screenshot_interval(icon, item):
        # Create a simple dialog to get user input
        root = Tk()
        root.withdraw()  # Hide the root window
        user_input = simpledialog.askinteger("Set Screenshot Interval",
                                              "Enter screenshot interval in seconds:",
                                              minvalue=1)  # Min value of 1 second

        if user_input is not None:
            screenshot_manager.set_screenshot_interval(user_input)  # Update the interval
            update_menu(icon)  # Refresh menu

    # Function to handle quit
    def on_quit(icon, item):
        print("Tray icon clicked, exiting...")
        activity_tracker.stop_tracking()  # Stop activity tracking
        screenshot_manager.stop_capturing()  # Stop screenshot capturing
        remove_lock()  # Remove the lock file
        print("Shutdown complete.")
        icon.stop()  # Stops the tray icon loop
        os._exit(0)  # Forces the application to exit

    def update_menu(icon):
        """Updates the tray menu with the current states."""
        icon.menu = Menu(
            MenuItem(
                f"Capture Screenshots: {screenshot_manager.capture_screenshots}",
                toggle_screenshots,
                checked=lambda item: screenshot_manager.capture_screenshots
            ),
            MenuItem(
                f"Blur Screenshots: {screenshot_manager.capture_blurred}",
                toggle_blur,
                checked=lambda item: screenshot_manager.capture_blurred
            ),
            MenuItem(
                "Set Screenshot Interval",
                set_screenshot_interval  # New menu item for setting interval
            ),
            MenuItem("Quit", on_quit)
        )

    # Create an image for the tray icon
    icon_image = create_image(64, 64, 'black', 'white')

    # Create and run the tray icon
    icon = pystray.Icon("activity_tracker_icon", icon_image)
    update_menu(icon)  # Set initial menu
    print("User's activity is being tracked...")
    icon.run()
