from playwright.sync_api import sync_playwright
import os

# Define the user data directory path
user_data_dir = "C:\\Users\\abrah\\OneDrive\\Desktop\\Projects\\Automator\\chrome_profile"

# Create the directory if it doesn't exist
if not os.path.exists(user_data_dir):
    os.makedirs(user_data_dir)
with sync_playwright() as p:
    # Launch browser with persistent context (user data directory)
    browser = p.chromium.launch_persistent_context(
        user_data_dir=user_data_dir,
        headless=False,  # Set to False so you can interact with the browser
            args=[
            '--disable-blink-features=AutomationControlled',
            '--no-sandbox',
            '--disable-web-security',
            '--disable-infobars',
            "--start-maximized",
        ],
        no_viewport=True
    )
    # Open a new page
    page = browser.new_page()

    # Navigate to Google login page
    page.goto("https://login.seek.com/")

    # Keep the browser open so you can manually log in
    input("Log in manually and then press Enter to continue...")

    # After logging in, continue the script
    print("Logged in successfully!")

    # Save cookies to file
    cookies = page.context.cookies()
    import json
    with open("cookies.json", "w") as f:
        json.dump(cookies, f)
    print("Cookies saved.")

    # Keep the browser open for further automation
    input("Press Enter to close the browser...")

    # Close the browser after actions
    browser.close()
