from utils import get_user_field
from playwright.async_api import async_playwright
import asyncio
import os
import re
import sys
import requests
from gemini import gen_summary, is_suitable, agen_cover_letter, agenerate_resume, get_question_actions

from utils import clear_job_ids

# Default mode
#clear_job_ids()
pagination = False
looprange = 5
timeframe = re.compile(r'(5|[1-5]\d|60)m')  # 5–60 mins
ui_mode = 1

if ui_mode:
    pagination = True
    timeframe = re.compile(r'.*')

user = 'abraham'
CHAT_ID = get_user_field(user, "chat_id")

if len(sys.argv) > 1:
    looprange = int(sys.argv[1])
if len(sys.argv) > 2:
    timeframe_pattern = sys.argv[2]
if len(sys.argv) > 3:
    user = sys.argv[3]

# Telegram Bot Configuration
BOT_TOKEN = '7565937945:AAGEoHuAhoiNU-MAEXHQc6bF_8lr14_LgzA'

# Function to send message via Telegram API
def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        'chat_id': CHAT_ID,
        'text': message
    }
    response = requests.post(url, data=payload)
    if response.status_code != 200:
        print(f"Failed to send Telegram message: {response.text}")

playwright = None
browser = None
with open("ngrok_url.txt", "r") as f:
    public_url = f.read().strip()
print(f"App is accessible at {public_url}")  # Print the public URL

async def init_browser():
    global playwright, browser
    
    if browser is None or not hasattr(browser, "new_context"):
        print("Initializing browser...")
        playwright = await async_playwright().start()
        
        user_data_dir = os.path.abspath(os.path.join("Users", user, "chrome_profile"))
        browser = await playwright.chromium.launch_persistent_context(
            user_data_dir= user_data_dir,
            headless=False,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--no-sandbox',
                '--disable-web-security',
                '--disable-infobars',
                "--start-maximized",
            ],
            no_viewport=True
        )

async def process_job_listings(public_url):
    global browser

    page = await browser.new_page()
    await browser.pages[0].close()
    page.set_default_timeout(3000)
    page.set_default_navigation_timeout(5000)

    
    file_path = os.path.join("Users", user, "filter.txt")
    with open(file_path, "r") as f:
        AA = f.read().strip()
    await page.goto(AA)

    while True:  # Loop to go through all pages of job listings
        
        job_cards = page.locator('[id^="jobcard-"]').filter(
            has=page.locator('span[data-automation="jobListingDate"]', has_text=timeframe)
        )
        job_count = await job_cards.count()
        print(f"Found {job_count} job card(s) posted.")
         

        for i in range(0,  job_count if pagination else looprange):
            job = job_cards.nth(i)
            job_id = await job.get_attribute('data-job-id')
            job_link_locator = job.locator('a[data-automation="jobTitle"]')
            try:
                await job_link_locator.wait_for(state="visible")
                await job_link_locator.click()

                h1_locator = page.locator('//h1[@data-automation="job-detail-title"]/a')
                await h1_locator.wait_for(state="visible")
                job_title = await h1_locator.inner_text()
                print("\n------------------------------------------------------------------------------------")
                print(f"Retail Job found: {job_title}")

                apply_btn_locator = page.locator('//a[@data-automation="job-detail-apply"]')
                await apply_btn_locator.wait_for(state="visible")
                apply_btn_text = (await apply_btn_locator.inner_text()).strip().lower()
                print(f"Button text detected: {apply_btn_text}")

                if "apply" in apply_btn_text.lower() and "quick apply" not in apply_btn_text.lower():

                    print("Manual Apply detected. Proceeding...")

                    advertiser_name_locator = page.locator('span[data-automation="advertiser-name"]')
                    await advertiser_name_locator.wait_for(state='visible')
                    advertiser_name = await advertiser_name_locator.inner_text()
                    print(f"Advertiser name: {advertiser_name}")

                    job_type_locator = page.locator('span[data-automation="job-detail-classifications"]')
                    await job_type_locator.wait_for(state='visible')
                    job_type = await job_type_locator.inner_text()
                    print(f"Job type: {job_type}")

                    job_location_locator = page.locator('span[data-automation="job-detail-location"]')
                    await job_location_locator.wait_for(state='visible')
                    job_location = await job_location_locator.inner_text()
                    print(f"Job location: {job_location}")

                    job_work_type_locator = page.locator('span[data-automation="job-detail-work-type"]')
                    await job_work_type_locator.wait_for(state='visible')
                    job_work_type = await job_work_type_locator.inner_text()
                    print(f"Work type: {job_work_type}")

                    job_details_locator = page.locator('div[data-automation="jobAdDetails"]')
                    raw_html = await job_details_locator.inner_html()

                    async with page.context.expect_page() as new_page_info:
                        await apply_btn_locator.click()
                    new_page = await new_page_info.value
                    await new_page.wait_for_load_state("domcontentloaded")
                    await new_page.bring_to_front()

                    # Wait until the URL is no longer a Seek URL (i.e., external site)
                    try:
                        await new_page.wait_for_function("() => !window.location.href.includes('seek.com.au')", timeout=10000)
                        job_url = new_page.url
                        import json

                        manual_links_file = os.path.join("Users", user, "manual_links.json")

                        # Build the dictionary
                        manual_entry = {
                            "job_title": job_title,
                            "advertiser": advertiser_name,
                            "job_type": job_type,
                            "location": job_location,
                            "work_type": job_work_type,
                            "summary": raw_html,
                            "url": job_url
                        }

                        # Load existing entries (if any), append the new one, and write back
                        try:
                            if os.path.exists(manual_links_file):
                                with open(manual_links_file, "r") as f:
                                    existing_data = json.load(f)
                            else:
                                existing_data = []
                        except Exception as e:
                            print(f"⚠️ Failed to load existing manual_links.json: {e}")
                            existing_data = []

                        existing_data.append(manual_entry)

                        with open(manual_links_file, "w") as f:
                            json.dump(existing_data, f, indent=2)

                        print(f"✅ Saved job to manual_links.json: {job_title}")
                    except:
                        print("Timed out waiting for redirection to non-Seek site.")


            except Exception as e:
                print(f"Error: {e}. Skipping the page.")
                import traceback
                traceback.print_exc()


        if pagination:
            try:
                next_button = page.locator("//span[contains(text(),'Next')]").first
                await next_button.wait_for(state="visible", timeout=3000)
                await next_button.click()
                print("Navigating to next page...")
                await page.wait_for_load_state("domcontentloaded")  # Wait for the new page to load
                await page.wait_for_timeout(5000)
            except Exception:
                print("No more pages available. Exiting loop.")
                break

    await page.wait_for_timeout(2000)
    await browser.close()


async def start_job_processing():
    await init_browser()
    await process_job_listings(public_url)

asyncio.run(start_job_processing())


