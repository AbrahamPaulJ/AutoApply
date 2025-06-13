from playwright.sync_api import sync_playwright
from playwright_stealth import stealth_sync
import os
import sys
import shutil

user = "Aaron"

if len(sys.argv) > 1:
    user = sys.argv[1]

# Base user folder
user_base_dir = os.path.abspath(f".\\Users\\{user}")
# Create profile directory
user_data_dir = os.path.join(user_base_dir, "chrome_profile")
os.makedirs(user_data_dir, exist_ok=True)
# Create other necessary folders
mycv_dir = os.path.join(user_base_dir, "mycv")
mycl_dir = os.path.join(user_base_dir, "mycl")
os.makedirs(mycv_dir, exist_ok=True)
os.makedirs(mycl_dir, exist_ok=True)

# Reference base directory (template source)
template_user_dir = os.path.abspath(".\\Users\\John_Doe")

# List of required files to copy
required_files = [
    "info.yaml",
    "job_ids.txt",
    "resume.txt"
]

for filename in required_files:
    dest_path = os.path.join(user_base_dir, filename)
    src_path = os.path.join(template_user_dir, filename)
    if not os.path.exists(dest_path):
        shutil.copyfile(src_path, dest_path)

print(f"Setup complete for user: {user}. Proceed to login to Seek.")

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
    browser.pages[0].close()
    page.goto("https://login.seek.com/")
    input("Press Enter after logging in...")

    print("Logged in successfully!")
    input("Press Enter to close the browser...")

    # Close the browser after actions
    browser.close()

# try:
#     if os.path.exists(backup_dir):
#         shutil.rmtree(backup_dir)  # Remove old backup
#     shutil.copytree(user_data_dir, backup_dir)
#     print(f"Copied user data from '{user_data_dir}' to '{backup_dir}'.")
# except Exception as e:
#     print(f"Error copying profile: {e}")
