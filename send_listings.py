from playwright.sync_api import sync_playwright
import os
from gemini import gen_summary

# Define the user data directory path
user_data_dir = "C:\\Users\\abrah\\OneDrive\\Desktop\\Projects\\Automator\\chrome_profile"
extension_path = "C:\\Users\\abrah\\OneDrive\\Desktop\\Projects\\cover_letter_extension"

# Ensure the directory exists
if not os.path.exists(user_data_dir):
    os.makedirs(user_data_dir)

with sync_playwright() as p:
    browser = p.chromium.launch_persistent_context(
        user_data_dir=user_data_dir,
        headless=False, 
        args=[
            f'--load-extension={extension_path}',
            '--disable-blink-features=AutomationControlled',
            '--no-sandbox',
            '--disable-web-security',
            '--disable-infobars',
            f'--disable-extensions-except={extension_path}',
            "--start-maximized",
        ],
        no_viewport=True
    )
    wa = browser.pages[0]
    wa.goto("https://web.whatsapp.com/")
    abraham = wa.locator("//span[@title='abraham_paul_jaison']")
    abraham.wait_for(state="visible")
    abraham.click()
    message_input = wa.locator("//div[@aria-label='Type a message']//p")
    message_input.wait_for(state="visible")
    message_input.fill("testing") 


    page = browser.new_page()
    page.set_default_timeout(10000)  # Set global timeout to 3 seconds
    page.set_default_navigation_timeout(30000)


    page.goto("https://www.seek.com.au/jobs/in-All-Adelaide-SA?classification=6251%2C1200%2C1204%2C6163%2C1209%2C1212%2C6281%2C6092%2C6008%2C6043%2C6362%2C1223%2C1225&daterange=3&sortmode=ListedDate&subclassification=6226%2C6229%2C6143%2C6166%2C6168%2C6169%2C6171%2C6172%2C6095%2C6093%2C6097%2C6099%2C6101%2C6104%2C6105%2C6103%2C6106%2C6109%2C6108&worktype=243%2C245")

    while True:  # Loop to go through all pages of job listings

        job_cards = page.locator('[id^="jobcard-"]').filter(has=page.locator('span', has_text="Be an early applicant"))
        job_count = job_cards.count()
        print(f"Found {job_count} job cards with 'Be an early applicant'.")

        for i in range(1, job_count + 1):
            job = job_cards.nth(i) 

            job_link_locator = job.locator('div:nth-child(2) > a')
            try:
                job_link_locator.wait_for(state="visible")

                job_link_locator.click()

                h1_locator = page.locator('//h1[@data-automation="job-detail-title"]/a')
                h1_locator.wait_for(state="visible")
                job_title = h1_locator.inner_text()
                print("\n------------------------------------------------------------------------------------")
                print(f"Retail Job found: {job_title}")

                apply_btn_locator = page.locator('//a[@data-automation="job-detail-apply"]')
                apply_btn_locator.wait_for(state="visible")
                apply_btn_text = apply_btn_locator.inner_text().strip().lower()
                print(f"Button text detected: {apply_btn_text}")

                if "quick apply" in apply_btn_text:
                    print("Quick Apply detected. Proceeding...")

                    # Advertiser Name
                    advertiser_name_locator = page.locator('span[data-automation="advertiser-name"]')
                    advertiser_name_locator.wait_for(state='visible')
                    advertiser_name = advertiser_name_locator.inner_text().strip()
                    print(f"Advertiser name: {advertiser_name}")

                    # Job Type
                    job_type_locator = page.locator('span[data-automation="job-detail-classifications"]')
                    job_type_locator.wait_for(state='visible')
                    job_type = job_type_locator.inner_text().strip().lower()
                    print(f"Job type: {job_type}")

                    # Job Location
                    job_location_locator = page.locator('span[data-automation="job-detail-location"]')
                    job_location_locator.wait_for(state='visible')
                    job_location = job_location_locator.inner_text().strip()
                    print(f"Job location: {job_location}")

                    # Work Type
                    job_work_type_locator = page.locator('span[data-automation="job-detail-work-type"]')
                    job_work_type_locator.wait_for(state='visible')
                    job_work_type = job_work_type_locator.inner_text().strip()
                    print(f"Work type: {job_work_type}")

                    job_details_locator = page.locator('div[data-automation="jobAdDetails"]')
                    raw_html = job_details_locator.inner_html()

                    message_input.fill(f"{job_title} @ {advertiser_name}") 
                    send_icon = wa.locator("//span[@data-icon='send']")
                    send_icon.wait_for(state="visible")
                    send_icon.click() 

                    summary = gen_summary(job_title,advertiser_name,job_type,job_location,job_work_type,raw_html)
                    message_input.fill(summary) 
                    send_icon = wa.locator("//span[@data-icon='send']")
                    send_icon.wait_for(state="visible")
                    send_icon.click() 


            #         cover_letter = gen_cover_letter(raw_html)
            #         resume_pdf_path = generate_resume(raw_html, browser)
            #         print(resume_pdf_path)
            #         print("Quick Applying...")

            #         with page.context.expect_page() as new_page_info:
            #             apply_btn_locator.click()
            #         new_page = new_page_info.value
            #         new_page.wait_for_load_state()

            #         if new_page.url.startswith("https://www.seek.com.au/"):
            #             print(new_page.url)
            #             try:
                            

            #                 resume_upload_radio = new_page.locator('//input[@data-testid="resume-method-upload"]')
            #                 resume_upload_radio.wait_for(state="visible", timeout=5000)
            #                 resume_upload_radio.click()

            #                 resume_upload_btn = new_page.locator("//button[@id='resume-file-:r2:']")
            #                 resume_upload_btn.wait_for(state="visible", timeout=5000)
            #                 #resume_upload_btn.click()

            #                 # Set the file input field to the desired file path
            #                 file_input = new_page.locator("//input[@id='resume-fileFile']")
            #                 file_input.wait_for(state="attached", timeout=5000)
            #                 file_path = os.path.abspath("C:/Users/abrah/Downloads/mycv/resume.pdf")
            #                 file_input.set_input_files(file_path)

            #                 cover_letter_radio = new_page.locator('//input[@type="radio" and @data-testid="coverLetter-method-change"]')
            #                 cover_letter_radio.wait_for(state="attached")
            #                 cover_letter_radio.click()

            #                 cover_letter_textarea = new_page.locator('//textarea[@data-testid="coverLetterTextInput"]')
            #                 cover_letter_textarea.wait_for(state="visible")
            #                 cover_letter_textarea.fill(cover_letter)

            #                 cont_btn_locator = new_page.locator('//button[@data-testid="continue-button"]')
            #                 cont_btn_locator.wait_for(state="visible")
            #                 cont_btn_locator.click()
            #                 print("Cover Letter Generated!")
            #                 print("\n")

            #                 cont_btn_locator.wait_for(state="visible", timeout=3000)
            #                 cont_btn_locator.click()

            #                 cont_btn_locator.wait_for(state="visible", timeout=3000)
            #                 cont_btn_locator.click()

            #                 if new_page.url.endswith("profile"):
            #                     cont_btn_locator.wait_for(state="visible", timeout=3000)
            #                     cont_btn_locator.click()

            #             except Exception as e:
            #                 print(f"Error: {e}. Skipping the page.")
            #                 import traceback
            #                 traceback.print_exc()
            #         else:
            #             print("The page URL does not match, skipping...")
            #     else:
            #         print("No Quick Apply option, skipping...")
            except Exception as e:
                print(f"Error: {e}. Skipping the page.")
                import traceback
                traceback.print_exc()

        # Check if the "Next" button exists
        try:
            next_button = page.locator("//span[contains(text(),'Next')]").first
            next_button.wait_for(state="visible", timeout=3000)
            next_button.click()
            print("Navigating to next page...")
            page.wait_for_load_state("domcontentloaded")  # Wait for the new page to load
            page.wait_for_timeout(5000)
        except Exception:
            print("No more pages available. Exiting loop.")
            break

    input("Press Enter to close the browser...")
    browser.close()
