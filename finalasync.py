from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from pyngrok import ngrok
from playwright.async_api import async_playwright
import asyncio
import os
import re
import urllib.parse
import threading
from gemini import gen_summary, is_suitable, agen_cover_letter, agenerate_resume


playwright = None
browser = None
public_url = ngrok.connect(5000).public_url  # Start ngrok tunnel and get public URL
print(f"App is accessible at {public_url}")  # Print the public URL

# FastAPI App Setup
app = FastAPI()

async def init_browser():
    global playwright, browser
    
    if browser is None or not hasattr(browser, "new_context"):
        print("Initializing browser...")
        playwright = await async_playwright().start()
        browser = await playwright.chromium.launch_persistent_context(
            user_data_dir="C:\\Users\\abrah\\OneDrive\\Desktop\\Projects\\Automator\\chrome_profile",
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

        wa = browser.pages[0]
        await wa.goto("https://web.whatsapp.com/")
        abraham = wa.locator("//span[@title='abraham_paul_jaison']")
        await abraham.wait_for(state="visible")
        await abraham.click()
        
        message_input = wa.locator("//div[@aria-label='Type a message']//p")
        await message_input.wait_for(state="visible")

        page = await browser.new_page()
        page.set_default_timeout(10000)
        page.set_default_navigation_timeout(30000)


@app.get("/generate_clcv_request", response_class=HTMLResponse)
async def generate_clcv_request(request: Request, title: str, advertiser: str, job_id: str):
    return f"""
    <html>
        <head>
            <title>Generate resume and cover letter.</title>
        </head>
        <body>
            <h2>Generate for: {title} at {advertiser}</h2>
            <form action="/generate_clcv" method="get">
                <input type="hidden" name="title" value="{title}">
                <input type="hidden" name="advertiser" value="{advertiser}">
                <input type="hidden" name="job_id" value="{job_id}">
                <button type="submit">Generate</button>
            </form>
        </body>
    </html>
    """

@app.get("/generate_clcv")
async def generate_clcv(title: str, advertiser: str, job_id: str):
    global browser
    await init_browser()

    try:
        print(f"Applying for job: {title} at {advertiser}")
        wa = browser.pages[0]
        await wa.bring_to_front()

        apage = await browser.new_page()
        apage.set_default_timeout(10000)

        target_url = f"https://www.seek.com.au/job/{job_id}"
        print(f"Navigating to: {target_url}")
        await apage.goto(target_url, wait_until='domcontentloaded')

        apply_btn_locator = apage.locator('//a[@data-automation="job-detail-apply"]')
        await apply_btn_locator.wait_for(state="visible")
        apply_btn_text = (await apply_btn_locator.inner_text()).strip().lower()
        print(f"Button text detected: {apply_btn_text}")

        job_type_locator = apage.locator('span[data-automation="job-detail-classifications"]')
        await job_type_locator.wait_for(state='visible')
        job_type = (await job_type_locator.inner_text()).strip().lower()
        print(f"Job type: {job_type}")

        job_details_locator = apage.locator('div[data-automation="jobAdDetails"]')
        raw_html = await job_details_locator.inner_html()

        cover_letter, cover_letter_path = agen_cover_letter(title, advertiser, raw_html, raw_html)
        resume_pdf_path = await agenerate_resume(job_id, title, advertiser, raw_html, browser)
        if "error" in resume_pdf_path.lower():
            print("Resume wasn't generated")
            print(resume_pdf_path)

        directory = "C:/Users/abrah/Downloads/mycv"
        file_path = os.path.abspath(os.path.join(directory, f"{resume_pdf_path}"))
        cl_file_path = os.path.abspath(os.path.join(directory, f"{cover_letter_path}"))
        print(f"PDF path: {file_path}")
        print(f"CL path: {cover_letter_path}")

        await wa.bring_to_front()
        up_btn_locator = wa.locator("//button[@title='Attach']")
        await up_btn_locator.wait_for(state='visible')
        await up_btn_locator.click()
        file_input = wa.locator("//li[@tabindex='0']//input[@type='file' and @accept='*']")
        await file_input.wait_for(state='attached')


        await file_input.set_input_files(file_path)
        send_button = wa.locator("//span[@data-icon='send']").nth(0)
        await send_button.wait_for(state='visible')
        await send_button.click()
        message_input = wa.locator("//div[@aria-label='Type a message']//p")
        await message_input.wait_for(state="visible")
        await message_input.fill(cover_letter) 
        await send_button.wait_for(state="visible")
        await send_button.click()
        await apply_btn_locator.click()
        await apage.wait_for_load_state("load")  # Wait for redirect to complete
        print(f"Redirected to: {apage.url}")
        try:
            dropdown = apage.locator("//select[@id=':r3:']")
            await dropdown.wait_for(state="attached", timeout=5000)
            try:
                await dropdown.select_option(index=1)
                delete_btn = apage.locator("//button[@id='deleteResume']")
                await delete_btn.wait_for(state="visible")
                await delete_btn.click()
                delete_cfmbtn = apage.locator("//button[@data-testid='delete-confirmation']")
                await delete_cfmbtn.wait_for(state="visible")
                await delete_cfmbtn.click()
            except Exception as e:
                print(f"Resume deletion skipped: {e}")

            resume_upload_radio = apage.locator('//input[@data-testid="resume-method-upload"]')
            await resume_upload_radio.wait_for(state="visible")
            await resume_upload_radio.click()

            resume_upload_btn = apage.locator("//button[@id='resume-file-:r2:']")
            await resume_upload_btn.wait_for(state="visible")

            directory = "C:/Users/abrah/Downloads/mycv"
            file_path = os.path.abspath(os.path.join(directory, f"{resume_pdf_path}"))
            print(f"PDF path: {file_path}")

            file_input = apage.locator("//div[@data-testid='resumeFileInput']/input[@id='resume-fileFile']")
            await file_input.wait_for(state="attached")
            await file_input.set_input_files(file_path)

            cover_letter_radio = apage.locator('//input[@type="radio" and @data-testid="coverLetter-method-upload"]')
            await cover_letter_radio.wait_for(state="attached")

            await cover_letter_radio.click()
            cover_letter_upload_btn = apage.locator("//button[@id='coverLetter-file-:r5:']")
            await cover_letter_upload_btn.wait_for(state="visible")

            directory = "C:/Users/abrah/Downloads/mycl"
            file_path = os.path.abspath(os.path.join(directory, f"{cover_letter_path}"))
            print(f"PDF path: {file_path}")

            cl_file_input = apage.locator("//div[@data-testid='coverLetterFileInput']/input[@id='coverLetter-fileFile']")
            await cl_file_input.wait_for(state="attached")
            await cl_file_input.set_input_files(cl_file_path)

            # cover_letter_textarea = apage.locator('//textarea[@data-testid="coverLetterTextInput"]')
            # await cover_letter_textarea.wait_for(state="visible")
            # await cover_letter_textarea.fill(cover_letter)

            cont_btn_locator = apage.locator('//button[@data-testid="continue-button"]')
            await cont_btn_locator.wait_for(state="visible", timeout=3000)
            await cont_btn_locator.click()
            print("Cover Letter Generated! \n")

            try:
                await cont_btn_locator.wait_for(state="visible", timeout=3000)
                await cont_btn_locator.click()
                await cont_btn_locator.wait_for(state="visible", timeout=3000)
                await cont_btn_locator.click()
            except Exception as e:
                print(f"Error continuing further: {e}")

            if apage.url.endswith("profile"):
                await cont_btn_locator.wait_for(state="visible", timeout=3000)
                await cont_btn_locator.click()

        except Exception as e:
            print(f"Error filling application form: {e}")
            import traceback
            traceback.print_exc()

        return {"message": f"Application completed."}
    except Exception as e:
        print(f"⚠️ Error: {type(e).__name__} - {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
    
async def process_job_listings(public_url):
    global browser

    wa = browser.pages[0]
    await wa.goto("https://web.whatsapp.com/")
    abraham = wa.locator("//span[@title='abraham_paul_jaison']")
    await abraham.wait_for(state="visible")
    await abraham.click()
    
    message_input = wa.locator("//div[@aria-label='Type a message']//p")
    await message_input.wait_for(state="visible")

    page = await browser.new_page()
    page.set_default_timeout(10000)
    page.set_default_navigation_timeout(30000)

    AA = "https://www.seek.com.au/jobs/in-All-Adelaide-SA?classification=6251%2C1200%2C1204%2C6163%2C1209%2C1212%2C6281%2C6092%2C6008%2C6043%2C6362%2C1223%2C1225&daterange=3&sortmode=ListedDate&subclassification=6226%2C6229%2C6143%2C6166%2C6168%2C6169%2C6171%2C6172%2C6095%2C6093%2C6097%2C6099%2C6101%2C6104%2C6105%2C6103%2C6106%2C6109%2C6108&worktype=243%2C245"
    await page.goto(AA)

    while True:  # Loop to go through all pages of job listings

        job_cards = page.locator('[id^="jobcard-"]').filter(
            has=page.locator('span[data-automation="jobListingDate"]', has_text=re.compile(r'\d{1,2}m'))
        )
        job_count = await job_cards.count()
        print(f"Found {job_count} job card(s) posted.")

        for i in range(0, 1):
            job = job_cards.nth(i) 
            job_id = await job.get_attribute('data-job-id')
            print(job_id)
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

                if "quick apply" in apply_btn_text:
                    print("Quick Apply detected. Proceeding...")

                    # Advertiser Name
                    advertiser_name_locator = page.locator('span[data-automation="advertiser-name"]')
                    await advertiser_name_locator.wait_for(state='visible')
                    advertiser_name = await advertiser_name_locator.inner_text()
                    print(f"Advertiser name: {advertiser_name}")

                    # Job Type
                    job_type_locator = page.locator('span[data-automation="job-detail-classifications"]')
                    await job_type_locator.wait_for(state='visible')
                    job_type = await job_type_locator.inner_text()
                    print(f"Job type: {job_type}")

                    # Job Location
                    job_location_locator = page.locator('span[data-automation="job-detail-location"]')
                    await job_location_locator.wait_for(state='visible')
                    job_location = await job_location_locator.inner_text()
                    print(f"Job location: {job_location}")

                    # Work Type
                    job_work_type_locator = page.locator('span[data-automation="job-detail-work-type"]')
                    await job_work_type_locator.wait_for(state='visible')
                    job_work_type = await job_work_type_locator.inner_text()
                    print(f"Work type: {job_work_type}")

                    job_details_locator = page.locator('div[data-automation="jobAdDetails"]')
                    raw_html = await job_details_locator.inner_html()

                    await message_input.fill(f"{job_title} @ {advertiser_name}") 
                    send_icon = wa.locator("//span[@data-icon='send']")
                    await send_icon.wait_for(state="visible")
                    await send_icon.click()

                    summary = gen_summary(job_title,advertiser_name,job_type,job_location,job_work_type,raw_html)
                    suitable = is_suitable(job_title,advertiser_name,job_type,job_location,job_work_type,raw_html)

                    if suitable:
                        print(f"{job_title} @ {advertiser_name} is a match.")
                        
                        # Generate the summary for the job application
                        summary = gen_summary(job_title, advertiser_name, job_type, job_location, job_work_type, raw_html)
                        await message_input.fill(summary)
                        await send_icon.click()
                        
                        params = {
                            'job_id': job_id,
                            'title': job_title,
                            'advertiser': advertiser_name
                        }
                        encoded_params = urllib.parse.urlencode(params)
                        apply_url = f"{public_url}/generate_clcv_request?{encoded_params}"

                        # Print or use this URL wherever you need
                        print(f"Apply via URL: {apply_url}")


                        await message_input.fill(f"Apply Now: {apply_url}")
                        await send_icon.click()
                        print(f"Sent URL to Whatsapp: {apply_url}")      
                    else:
                        await message_input.fill(f"{job_title} @ {advertiser_name} was not a match.") 
                        await send_icon.click() 
                        print(f"{job_title} @ {advertiser_name} is not a match.")   

            except Exception as e:
                print(f"Error: {e}. Skipping the page.")
                import traceback
                traceback.print_exc()

        await page.wait_for_timeout(2000)
        await browser.close()
        break

        # Check if the "Next" button exists
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


async def start_job_processing():
    # Start Playwright job processing
    await init_browser()
    await process_job_listings(public_url)

if __name__ == '__main__':
    from fastapi import FastAPI
    import uvicorn

    # Start Playwright job processing in a background thread
    threading.Thread(target=asyncio.run, args=(start_job_processing(),)).start()

    # Run FastAPI server
    uvicorn.run(app, host="0.0.0.0", port=5000)
    
