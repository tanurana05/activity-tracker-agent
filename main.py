import os
import json
import threading
import time
import socket
from botocore.exceptions import NoCredentialsError, ClientError  # Handle AWS errors
from activity_tracker import ActivityTracker
from screenshot_manager import ScreenshotManager
from timezone_manager import TimeZoneManager
from tray_icon import run_tray_icon
from data_uploader import DataUploader  # Import the DataUploader class

def load_config(config_file):
    """Loads configuration from the JSON file."""
    with open(config_file, 'r') as f:
        return json.load(f)

def initialize_config(config_file):
    """Initializes default configuration if not present."""
    if not os.path.exists(config_file):
        default_config = {
            "capture_screenshots": True,
            "capture_blurred": False,
            "screenshot_interval": 60
        }
        with open(config_file, 'w') as f:
            json.dump(default_config, f, indent=4)

def is_internet_available():
    """Checks if the internet is available."""
    try:
        # Attempt to connect to a public DNS server
        socket.create_connection(("8.8.8.8", 53))
        return True
    except OSError:
        return False

def upload_data_files(data_uploader):
    """Uploads data files using DataUploader."""
    if data_uploader.cloud_upload:  # Check if cloud upload is enabled
        log_file = os.path.join(data_uploader.base_directory, 'activity_tracker_log.txt')
        screenshot_directory = os.path.join(data_uploader.base_directory, 'screenshots')

        # Upload log file
        if os.path.exists(log_file):
            try:
                data_uploader.upload_file(log_file, 'activity_tracker_log.txt')  # Specify destination name
            except (NoCredentialsError, ClientError) as e:
                print(f"Error uploading log file: {e}. This might be due to firewall restrictions.")
            except Exception as e:
                print(f"Error uploading log file: {e}")
        else:
            print(f"Log file not found: {log_file}")

        # Upload screenshots
        for screenshot_file in os.listdir(screenshot_directory):
            if screenshot_file.endswith('.png'):  # Assuming screenshots are in PNG format
                full_screenshot_path = os.path.join(screenshot_directory, screenshot_file)
                if os.path.exists(full_screenshot_path):
                    try:
                        data_uploader.upload_file(full_screenshot_path, f"screenshots/{screenshot_file}")  # Specify destination name
                    except (NoCredentialsError, ClientError) as e:
                        print(f"Error uploading screenshot file: {e}. This might be due to firewall restrictions.")
                    except Exception as e:
                        print(f"Error uploading screenshot file: {e}")
                else:
                    print(f"Screenshot file not found: {full_screenshot_path}")


def check_single_instance():
    """Ensures that only one instance of the application can run at a time."""
    lock_file = "app.lock"
    if os.path.exists(lock_file):
        print("Another instance is already running.")
        exit(1)
    else:
        with open(lock_file, 'w') as f:
            f.write(str(os.getpid()))  # Store the PID in the lock file

def remove_lock():
    """Removes the lock file upon exit."""
    if os.path.exists("app.lock"):
        os.remove("app.lock")

def handle_uploads(data_uploader):
    """Handles upload attempts, queuing them if there is no internet connection."""
    while True:
        if is_internet_available():
            print("Internet connection restored. Attempting to upload data files...")
            upload_data_files(data_uploader)
            break
        else:
            print("No internet connection. Queuing uploads...")
            time.sleep(5)  # Wait before retrying


def main():
    # Check for a single instance
    check_single_instance()

    # Set the base directory to data_to_upload
    data_directory = os.path.join(os.getcwd(), 'data_to_upload')
    screenshot_directory = os.path.join(data_directory, 'screenshots')
    config_file = os.path.join(os.getcwd(), 'config.json')

    # Create the data directory if it doesn't exist
    os.makedirs(data_directory, exist_ok=True)
    os.makedirs(screenshot_directory, exist_ok=True)  # Create screenshot directory

    # Initialize default configuration if not available
    initialize_config(config_file)

    # Load the configuration
    config = load_config(config_file)

    # Initialize TimeZone Manager
    tz_manager = TimeZoneManager()
    tz_manager_thread = threading.Thread(target=tz_manager.check_time_zone_change)
    tz_manager_thread.daemon = True
    tz_manager_thread.start()

    # Initialize and start the activity tracker
    log_file = os.path.join(data_directory, 'activity_tracker_log.txt')
    activity_tracker = ActivityTracker(log_file=log_file, tz_manager=tz_manager)
    activity_tracker_thread = threading.Thread(target=activity_tracker.start_tracking)
    activity_tracker_thread.daemon = True
    activity_tracker_thread.start()

    # Initialize and start the screenshot manager
    screenshot_manager = ScreenshotManager(
        base_directory=screenshot_directory,
        activity_tracker=activity_tracker,
        config_file=config_file
    )
    screenshot_thread = threading.Thread(target=screenshot_manager.start_capturing)
    screenshot_thread.daemon = True
    screenshot_thread.start()

    # Start the tray icon in a separate thread
    tray_thread = threading.Thread(target=run_tray_icon, args=(screenshot_manager, config_file, activity_tracker))
    tray_thread.start()

    # Initialize DataUploader
    cloud_upload = False  # Set to True if you want to upload files to cloud
    BUCKET_NAME = 'your-s3-bucket-name'
    AWS_ACCESS_KEY_ID = 'your-access-key-id'
    AWS_SECRET_ACCESS_KEY = 'your-secret-access-key'

    data_uploader = DataUploader(
        base_directory=data_directory,
        cloud_upload=cloud_upload,
        bucket_name=BUCKET_NAME,
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY
    )

    # Handle data uploads in a separate thread
    upload_thread = threading.Thread(target=handle_uploads, args=(data_uploader,))
    upload_thread.start()

    # Keep the main thread alive and monitor for shutdown
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Shutting down...")
    finally:
        activity_tracker.stop_tracking()  # Stop activity tracking
        screenshot_manager.stop_capturing()  # Stop screenshot capturing           
        remove_lock()  # Remove the lock file
        

if __name__ == "__main__":
    main()
