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
submit = True
#clear_job_ids()
pagination = False
looprange = 5
timeframe = re.compile(r'(5|[1-5]\d|60)m')  # 5–60 mins
ui_mode = 0

user = 'abraham'

if len(sys.argv) > 1:
    ui_mode = int(sys.argv[1])
if len(sys.argv) > 2:
    looprange = sys.argv[2]
if len(sys.argv) > 3:
    user = sys.argv[3]


if ui_mode:
    pagination = True
    timeframe = re.compile(r'.*')

# Telegram Bot Configuration
CHAT_ID = get_user_field(user, "chat_id")
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
#print(f"App is accessible at {public_url}")  # Print the public URL

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
    page.set_default_timeout(5000)
    page.set_default_navigation_timeout(10000)

    file_path = os.path.join("Users", user, "filter.txt")
    with open(file_path, "r") as f:
        AA = f.read().strip()
    await page.goto(AA)
    page.set_default_navigation_timeout(5000)

    while True:  # Loop to go through all pages of job listings
        
        job_cards = page.locator('[id^="jobcard-"]').filter(
            has=page.locator('span[data-automation="jobListingDate"]', has_text=timeframe)
        )
        job_count = await job_cards.count()
        print(f"Found {job_count} job card(s) posted.")
         
        PROCESSED_JOBS_FILE = os.path.join("Users", user, "job_ids.txt")
        if os.path.exists(PROCESSED_JOBS_FILE):
            with open(PROCESSED_JOBS_FILE, "r") as f:
                processed_ids = set(line.strip() for line in f)
        else:
            processed_ids = set()

        for i in range(0,  job_count if pagination else looprange):
            job = job_cards.nth(i)
            job_id = await job.get_attribute('data-job-id')
            if job_id not in processed_ids:
                job_link_locator = job.locator('a[data-automation="jobTitle"]')
                try:
                    await job_link_locator.wait_for(state="visible")
                    await job_link_locator.click()

                    h1_locator = page.locator('//h1[@data-automation="job-detail-title"]/a')
                    await h1_locator.wait_for(state="visible")
                    job_title = await h1_locator.inner_text()
                    print("\n------------------------------------------------------------------------------------")
                    print(f"Retail Job found: {job_title}")

                    apply_btn_locator = page.locator('//a[@data-automation="job-detail-apply"]').first
                    await apply_btn_locator.wait_for(state="visible")
                    apply_btn_text = (await apply_btn_locator.inner_text()).strip().lower()
                    print(f"Button text detected: {apply_btn_text}")

                    if "quick apply" in apply_btn_text:
                        print("Quick Apply detected. Proceeding...")

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

                        # Generate summary and suitability report
                        summary = gen_summary(job_title, advertiser_name, job_type, job_location, job_work_type, raw_html)
                        suitable_json = is_suitable(user, job_title, advertiser_name, job_type, job_location, job_work_type, raw_html)
                        suitable_raw = suitable_json.get("suitable", False)

                        # Normalize it to boolean
                        if isinstance(suitable_raw, str):
                            suitable_bool = suitable_raw.strip().lower() == "true"
                        else:
                            suitable_bool = bool(suitable_raw)

                        status_line = "✅ Suitable" if suitable_bool else "❌ Not Suitable"
                        reason_text = suitable_json.get("reason", "No reason provided.")
                        reason_line = f"Reason: {reason_text}"

                        suitable_report = f"{status_line}\n\n{reason_line}".strip()

                        # Send summary and suitability report on Telegram
                        combined_message = f"{job_title} @ {advertiser_name} ({job_id})\n\n{summary}"
                        send_telegram_message(combined_message)
                        send_telegram_message(suitable_report)
                        #import urllib.parse
                        # params = {
                        #     'job_id': job_id,
                        #     'title': job_title,
                        #     'advertiser': advertiser_name,
                        #     'suitable': suitable_bool
                        # }
                        # encoded_params = urllib.parse.urlencode(params)
                        # apply_url = f"{public_url}/generate_clcv_request?{encoded_params}"

                        if suitable_bool:
                            # Suitable: proceed with quick apply
                            print("Quick applying...")

                            resume_extra,cl_extra = "", ""
                            resume_pdf_path = await agenerate_resume(user, job_id, job_title, advertiser_name, raw_html,resume_extra, browser)
                            
                            directory = os.path.join("Users", user, "mycv")
                            file_path = os.path.abspath(os.path.join(directory, f"{resume_pdf_path}"))
                            print(f"PDF path: {file_path}")
                            assert os.path.exists(file_path), f"File not found at {file_path}"

                            async with page.context.expect_page() as new_page_info:
                                await apply_btn_locator.click()
                            new_page = await new_page_info.value
                            await new_page.wait_for_load_state("load")

                            if new_page.url.startswith("https://www.seek.com.au/"):
                                target_url = f"https://www.seek.com.au/job/{job_id}"  
                                print(new_page.url)
                                submit_btn_locator = new_page.locator('//button[@data-testid="review-submit-application"]') 
                                try:
                                    
                                    dropdown = new_page.locator("//select[@data-testid='select-input']")
                                    await dropdown.wait_for(state="attached", timeout=5000)
                                    try:
                                        await dropdown.select_option(index=1, timeout=5000)

                                        delete_btn = new_page.locator("//button[@id='deleteResume']")
                                        await delete_btn.wait_for(state="visible", timeout=5000)
                                        await delete_btn.click()

                                        delete_cfmbtn = new_page.locator("//button[@data-testid='delete-confirmation']")
                                        await delete_cfmbtn.wait_for(state="visible", timeout=5000)
                                        await delete_cfmbtn.click()
                                    except Exception as e:
                                        print(f"Error deleting resume options: {e}")

                                    resume_upload_radio = new_page.locator('//input[@data-testid="resume-method-upload"]')
                                    await resume_upload_radio.wait_for(state="visible", timeout=5000)
                                    await resume_upload_radio.click()

                                    resume_upload_btn = new_page.locator("//button[@id='resume-file-:ra:']")
                                    await resume_upload_btn.wait_for(state="visible", timeout=5000)

                                    print("Locating resume file input...")
                                    file_input = new_page.locator("//div[@data-testid='resumeFileInput']/input[@id='resume-fileFile']")
                                    await file_input.wait_for(state="attached", timeout=5000)
                                    print("Resume file input attached.")
                                    await file_input.set_input_files(file_path)
                                    print(f"Resume uploaded from: {file_path}")

                                    print("Generating cover letter...")
                                    cover_letter, _ = agen_cover_letter(user, job_title, advertiser_name, raw_html, raw_html, cl_extra)
                                    print("Cover letter generated.")

                                    print("Locating cover letter radio button...")
                                    cover_letter_radio = new_page.locator('//input[@type="radio" and @data-testid="coverLetter-method-change"]')
                                    await cover_letter_radio.wait_for(state="attached")
                                    print("Cover letter radio button found.")
                                    await cover_letter_radio.click()
                                    print("Cover letter radio button clicked.")

                                    print("Locating cover letter textarea...")
                                    cover_letter_textarea = new_page.locator('//textarea[@data-testid="coverLetterTextInput"]')
                                    await cover_letter_textarea.wait_for(state="visible")
                                    print("Cover letter textarea is visible.")
                                    await cover_letter_textarea.fill(cover_letter)
                                    print("Cover letter filled.")

                                    print("Locating Continue button...")
                                    cont_btn_locator = new_page.locator('//button[@data-testid="continue-button"]')
                                    await cont_btn_locator.wait_for(state="visible", timeout=3000)
                                    print("Continue button is visible.")
                                    await cont_btn_locator.click()
                                    print("Clicked Continue button. Proceeding to Q&A page...\n")

                                    try:
                                        await cont_btn_locator.wait_for(state="visible", timeout=3000)
                                        await cont_btn_locator.click()
                                        

                                        career_history = new_page.locator("//h3[text()='Career history']")

                                        if await career_history.is_visible(timeout=5000):
                                            print("Bypassed Q&A, proceeding to Career History page...!\n")  
                                        else:
                                            try:
                                                form_locator = new_page.locator("form") 
                                                await form_locator.first.wait_for(state="visible", timeout=3000)
                                                form_html = await form_locator.first.inner_html()
                                                actions = get_question_actions(user, form_html)
                                                print(f"Actions:\n{actions}")
                                                messages = []

                                                for i, act in enumerate(actions):
                                                    try:
                                                        msg = f"\nAnswering ({i+1}/{len(actions)}): {act['question']} --> {act.get('chosen_label', act.get('value'))}"
                                                        print(msg)
                                                        messages.append(msg)

                                                        locator = new_page.locator(f"xpath={act['xpath']}").first
                                                        print(f"Waiting for element: {act['xpath']}")
                                                        await locator.wait_for(state="visible", timeout=5000)

                                                        if act["action"] == "select_option":
                                                            await locator.select_option(label=act["chosen_label"])
                                                        elif act["action"] == "fill":
                                                            await locator.fill(act["value"])
                                                        elif act["action"] == "check":
                                                            if not await locator.is_checked():
                                                                await locator.check()
                                                        elif act["action"] == "choose_radio":
                                                            await locator.click()

                                                        print(f"✔️ Successfully answered: {act['question']}")
                                                        
                                                    except Exception as e:
                                                        import traceback
                                                        error_msg = f"❌ Error with question: '{act['question']}' | XPath: {act['xpath']} | Error: {str(e)}"
                                                        print(error_msg)
                                                        traceback.print_exc()
                                                        msg.append(f"❌ Failed to answer: {act['question']}")


                                                # After all actions
                                                full_message = "\n".join(messages)
                                                print(full_message)
                                                send_telegram_message(full_message)
                                            except Exception as e:
                                                        import traceback
                                                        error_msg = f"Error: {str(e)}"
                                                        print(error_msg)
                                                        traceback.print_exc()
                                                        messages.append(error_msg)

                                        try: 
                                            await cont_btn_locator.wait_for(state="visible", timeout=3000)
                                            await cont_btn_locator.click()
                                        except:
                                            print("Submit page.")

                                        # if await career_history.is_visible(timeout=5000):
                                        #     print("Bypassed Q&A, proceeding to Career History page...!\n") 
                                        # else:
                                        #     print("Career history h3 not visible.") 

                                    except Exception as e:
                                        print(f"Error continuing application steps: {e}")

                                    await cont_btn_locator.wait_for(state="visible", timeout=3000)
                                    await cont_btn_locator.click()

                                    # docs_included = new_page.locator("h3", has_text="Documents included")

                                    # if await docs_included.is_visible(timeout=5000):
                                    #     print("detected docs_included header")
                                    try:
                                        privacy_checkbox = new_page.locator('//input[@type="checkbox" and contains(@id, "privacyPolicy")]')
                                        print("checking pcbox")
                                        await privacy_checkbox.wait_for(state="visible", timeout=3000)
                                        if not await privacy_checkbox.is_checked(timeout=1000):
                                            await privacy_checkbox.check()
                                            print("Privacy policy checkbox checked.")  
                                    except Exception as e:
                                                    error_msg = f"Error: {str(e)}"
                                                    print(error_msg)
                                                    import traceback
                                                    traceback.print_exc()
                                                    messages.append(error_msg)

                                    try:
                                        if submit:
                                            await submit_btn_locator.wait_for(state="visible", timeout=3000)
                                            await submit_btn_locator.click()
                                            send_telegram_message(f"Applied successfully: {target_url}")
                                        else:
                                            print("Submitting is disabled.")
                                    except Exception as e:
                                        print(f"Error clicking submit button: {e}")
                                        send_telegram_message(f"⚠️ Application incomplete: Unanswered questions.")


                                except Exception as e:
                                    print(f"Error during quick apply/ submit page detected (?): {e}")
                                    try:
                                        if submit:
                                            await submit_btn_locator.wait_for(state="visible", timeout=3000)
                                            await submit_btn_locator.click()
                                            send_telegram_message(f"Applied successfully: {target_url}")
                                        else:
                                            print("Submitting is disabled.")

                                    except Exception as e:
                                        print(f"Error clicking submit button: {e}")
                                        send_telegram_message(f"⚠️ Application incomplete: Unanswered questions.")
 


                                finally:
                                    await page.bring_to_front()

                        else:
                            # Not suitable: send apply URL message only
                            print("Not suitable.")

                except Exception as e:
                    print(f"Error: {e}. Skipping the page.")
                    import traceback
                    traceback.print_exc()
                
                finally:
                    with open(PROCESSED_JOBS_FILE, "a") as f:
                        f.write(f"{job_id}\n")
                    processed_ids.add(job_id)



            else:
                print(f"Job ID {job_id} is already processed.")

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


