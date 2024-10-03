# Activity Tracker Desktop Agent

A Python-based desktop agent that captures user activity, including screenshots, mouse movements, and keyboard inputs. The application allows users to configure screenshot intervals, enable/disable screenshot capturing, and blur screenshots. It also uploads logs and screenshots to cloud storage if configured.

****Features
Screenshot Capture: Automatically captures screenshots at user-defined intervals.
Activity Tracking: Monitors user keyboard and mouse activity.
Configurable Options: Users can enable/disable screenshot capturing, apply blur effects, and set screenshot intervals through a system tray icon.
Cloud Upload: Uploads activity logs and screenshots to cloud storage (Amazon S3 or similar) when internet connectivity is available.
Automatic Configuration: The application automatically generates a configuration file (config.json) if it does not exist.
User-Friendly Interface: A system tray icon allows users to configure settings easily.

****Installation
Prerequisites -
Ensure you have Python 3.7 or higher installed. You will also need the following dependencies:

Pillow
pynput
pystray
boto3 (for AWS S3)

You can install the required packages using pip:
pip install Pillow pynput pystray boto3

****Setting Up the Application
1.Clone the Repository: Clone the repository to your local machine.
git clone https://github.com/yourusername/your-repo.git
cd your-repo

2.Run the Application: You can run the executable directly by running main.exe located in 'dist'. Otherwise, you can run the application using:
python main.py
Once the application is running, it will minimize to the system tray.

****Using the System Tray Icon
Right-click on the tray icon to access configuration options.
Capture Screenshots: Toggle this option to enable or disable screenshot capturing.
Blur Screenshots: Enable this option to save blurred versions of the captured screenshots.
Set Screenshot Interval: Select the interval (in seconds) at which screenshots should be captured.


