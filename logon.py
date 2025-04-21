from playwright.sync_api import sync_playwright
import os
import json

# Define the user data directory path for WebKit
user_data_dir = "C:\\Users\\abrah\\OneDrive\\Desktop\\Projects\\Automator\\chrome_profile_serve"

# Create the directory if it doesn't exist
if not os.path.exists(user_data_dir):
    os.makedirs(user_data_dir)

with sync_playwright() as p:
    # Launch WebKit with persistent context
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

    # Open the second page (WhatsApp Web)
    page2 = browser.new_page()
    page2.goto("https://web.whatsapp.com/")

    # Wait for manual login
    input("Log in manually and then press Enter to continue...")

    print("Logged in successfully!")

    # Keep the browser open for further automation
    input("Press Enter to close the browser...")

    # Close the browser after actions
    browser.close()

