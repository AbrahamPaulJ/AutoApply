import asyncio
import os
from playwright.async_api import async_playwright
from tenacity import retry, stop_after_attempt, wait_fixed
from gemini import agen_cover_letter, agenerate_resume, get_question_actions
from pathlib import Path

# Configuration
user = 'abraham_paul_jaison'

USER_DATA_DIR  = os.path.abspath(os.path.join("Users", user, "chrome_profile"))
EXTENSION_PATH = r"C:\Users\abrah\OneDrive\Desktop\Projects\cover_letter_extension"
DEFAULT_TIMEOUT = 5000
NAVIGATION_TIMEOUT = 30000
SHORT_TIMEOUT = 3000

# Ensure directories exist
if not os.path.exists(USER_DATA_DIR):
    os.makedirs(USER_DATA_DIR)

@retry(stop=stop_after_attempt(3), wait=wait_fixed(1))
async def click_element(locator, timeout=DEFAULT_TIMEOUT):
    """Click an element after ensuring it's visible."""
    await locator.wait_for(state="visible", timeout=timeout)
    await locator.click()

async def init_browser():
    """Initialize Playwright browser with persistent context."""
    print("Initializing browser...")
    playwright = await async_playwright().start()
    browser = await playwright.chromium.launch_persistent_context(
        user_data_dir=str(USER_DATA_DIR),
        headless=False,
        no_viewport=True
    )
    return playwright, browser

async def process_job_listings(playwright, browser):
    """Process job listings and apply to suitable jobs."""
    page = await browser.new_page()
    page.set_default_timeout(DEFAULT_TIMEOUT)
    page.set_default_navigation_timeout(NAVIGATION_TIMEOUT)

    # Load job search URL
# Read job search URL from file
    file_path = os.path.join("Users", user, "filter.txt")
    with open(file_path, "r") as f:
        job_url = f.read().strip()
    await page.goto(job_url)

    while True:
        # Locate job cards
        job_cards = page.locator('[id^="jobcard-"]')
        job_count = await job_cards.count()
        print(f"Found {job_count} job card(s) posted.")

        for i in range(1, job_count+1):
            job = job_cards.nth(i)
            job_id = await job.get_attribute('data-job-id')

            try:
                # Navigate to job details
                await click_element(job.locator('a[data-automation="jobTitle"]'))
                job_title = await page.locator('//h1[@data-automation="job-detail-title"]/a').inner_text()
                print(f"\n------------------------------------------------------------------------------------")
                print(f"Retail Job found: {job_title}")

                # Check for Quick Apply
                apply_btn = page.locator('//a[@data-automation="job-detail-apply"]')
                await apply_btn.wait_for(state="visible")
                apply_btn_text = (await apply_btn.inner_text()).strip().lower()
                print(f"Button text detected: {apply_btn_text}")

                if "quick apply" not in apply_btn_text:
                    print("No Quick Apply option, skipping...")
                    continue

                # Extract job details
                details = {
                    "advertiser_name": await page.locator('span[data-automation="advertiser-name"]').inner_text(),
                    "job_type": await page.locator('span[data-automation="job-detail-classifications"]').inner_text(),
                    "job_location": await page.locator('span[data-automation="job-detail-location"]').inner_text(),
                    "job_work_type": await page.locator('span[data-automation="job-detail-work-type"]').inner_text(),
                    "raw_html": await page.locator('div[data-automation="jobAdDetails"]').inner_html(),
                }
                print(f"Advertiser: {details['advertiser_name']}, Location: {details['job_location']}")

                # Generate resume and cover letter
                resume_extra, cl_extra = "", ""
                resume_pdf_path = await agenerate_resume(
                    user, job_id, job_title, details['advertiser_name'], details['raw_html'], resume_extra, browser
                )
                if "error" in resume_pdf_path.lower():
                    print(f"Resume generation failed: {resume_pdf_path}")
                    continue

                cover_letter, _ = agen_cover_letter(
                    user, job_title, details['advertiser_name'], details['raw_html'], details['raw_html'], cl_extra
                )

                # Start Quick Apply
                print("Quick Applying...")
                async with page.context.expect_page() as new_page_info:
                    await click_element(apply_btn)
                new_page = await new_page_info.value
                await new_page.wait_for_load_state("load")

                if not new_page.url.startswith("https://www.seek.com.au/"):
                    print(f"Unexpected URL: {new_page.url}, skipping...")
                    await new_page.close()
                    continue

                # Handle resume upload
                try:
                    # Delete existing resume if present
                    dropdown = new_page.locator("//select[@data-testid='select-input']")
                    if await dropdown.is_visible(timeout=SHORT_TIMEOUT):
                        await dropdown.select_option(index=1)
                        delete_btn = new_page.locator("//button[@id='deleteResume']")
                        if await delete_btn.is_visible(timeout=SHORT_TIMEOUT):
                            await click_element(delete_btn)
                            await click_element(new_page.locator("//button[@data-testid='delete-confirmation']"))

                    # Upload new resume
                    await click_element(new_page.locator('//input[@data-testid="resume-method-upload"]'))
                    directory = os.path.join("Users", user, "mycv")

                    resume_path = Path(os.path.abspath(os.path.join(directory, f"{resume_pdf_path}")))
                    if not resume_path.exists():
                        print(f"Resume not found at {resume_path}")
                        continue
                    await new_page.locator("//div[@data-testid='resumeFileInput']/input[@id='resume-fileFile']").set_input_files(str(resume_path))

                    # Upload cover letter
                    await click_element(new_page.locator('//input[@type="radio" and @data-testid="coverLetter-method-change"]'))
                    await new_page.locator('//textarea[@data-testid="coverLetterTextInput"]').fill(cover_letter)
                    print("Cover Letter Generated!")

                    # Navigate application steps
                    cont_btn = new_page.locator('//button[@data-testid="continue-button"]')
                    await click_element(cont_btn)

                    # Handle Q&A or Career History
                    if await new_page.locator("h3", has_text="Career history").is_visible(timeout=SHORT_TIMEOUT):
                        print("Bypassed Q&A, on Career History page...")
                    else:
                        form = new_page.locator("form").first
                        if await form.is_visible(timeout=SHORT_TIMEOUT):
                            actions = get_question_actions(user, await form.inner_html())
                            print(f"Actions:\n{actions}")
                            for act in actions:
                                answer_text = act.get('chosen_option', act.get('value'))
                                print(f"Answering: {act['question']} --> {answer_text}")
                                locator = new_page.locator(act["xpath"])
                                await locator.wait_for(state="visible", timeout=DEFAULT_TIMEOUT)
                                if act["action"] == "select_option":
                                    await locator.select_option(index=act["index"])
                                elif act["action"] == "fill":
                                    await locator.fill(act["value"])
                                elif act["action"] == "check":
                                    if not await locator.is_checked():
                                        await locator.check()
                                elif act["action"] == "choose_radio":
                                    await locator.click()

                    # Final steps
                    await click_element(cont_btn)
                    if await new_page.locator("h3", has_text="Documents included").is_visible(timeout=SHORT_TIMEOUT):
                        print("Detected docs_included header")
                        privacy_checkbox = new_page.locator('//input[@type="checkbox" and contains(@id, "privacyPolicy")]')
                        if await privacy_checkbox.is_visible(timeout=SHORT_TIMEOUT) and not await privacy_checkbox.is_checked():
                            await privacy_checkbox.check()
                            print("Privacy policy checkbox checked.")
                        await click_element(new_page.locator('//button[@data-testid="review-submit-application"]'))
                        print(f"Applied successfully: {new_page.url}")
                    else:
                        print("Debugging: Could not reach submission page.")

                    await new_page.close()

                except Exception as e:
                    print(f"Error during application for job {job_id}: {e}")
                    await new_page.close()

            except Exception as e:
                print(f"Error processing job {job_id}: {e}")
                continue

        # Pagination
        try:
            next_button = page.locator("//span[contains(text(),'Next')]").first
            if not await next_button.is_enabled(timeout=SHORT_TIMEOUT):
                print("No more pages available. Exiting loop.")
                break
            await click_element(next_button)
            print("Navigating to next page...")
            await page.wait_for_load_state("domcontentloaded")
            await page.wait_for_timeout(2000)  # Reduced from 5000ms for faster navigation
        except Exception:
            print("No more pages available. Exiting loop.")
            break

    await browser.close()
    await playwright.stop()

async def start_job_processing():
    """Start the job processing workflow."""
    playwright, browser = await init_browser()
    try:
        await process_job_listings(playwright, browser)
    finally:
        await browser.close()
        await playwright.stop()

if __name__ == "__main__":
    asyncio.run(start_job_processing())