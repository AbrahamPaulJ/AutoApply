from playwright.sync_api import sync_playwright
import os
import shutil

user = "static"

# Define the user data directories
user_data_dir = f"C:\\Users\\abrah\\OneDrive\\Desktop\\Projects\\Automator\\Users\\{user}\\chrome_profile"
backup_dir = f"C:\\Users\\abrah\\OneDrive\\Desktop\\Projects\\Automator\\Users\\{user}\\chrome_profile_serve"

# Create the directory if it doesn't exist
if not os.path.exists(user_data_dir):
    os.makedirs(user_data_dir)

with sync_playwright() as p:
    # Launch Chromiums
    browser = p.chromium.launch_persistent_context(
        user_data_dir=user_data_dir,
        headless=False,
        no_viewport=True,
        args=[
            '--disable-blink-features=AutomationControlled',
            '--no-sandbox',
            '--disable-web-security',
            '--disable-infobars',
            "--start-maximized",
        ],
    )

    # Open the first page (Seek login)
    page = browser.new_page()
    page.goto("https://login.seek.com/")

    # Wait for manual login
    input("Log in manually and then press Enter to continue...")

    print("Logged in successfully!")

    # Keep the browser open for further automation
    input("Press Enter to close the browser...")

    # Close the browser after actions
    browser.close()

try:
    if os.path.exists(backup_dir):
        shutil.rmtree(backup_dir)  # Remove old backup
    shutil.copytree(user_data_dir, backup_dir)
    print(f"Copied user data from '{user_data_dir}' to '{backup_dir}'.")
except Exception as e:
    print(f"Error copying profile: {e}")

