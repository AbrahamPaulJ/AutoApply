from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from pyngrok import ngrok
from playwright.async_api import async_playwright
import os
from gemini import  agen_cover_letter, agenerate_resume


playwright = None
browser = None

with open("job_ids.txt", "w") as f:
    f.truncate(0)
print("Cleared job_ids.txt")

public_url = ngrok.connect(5000).public_url  # Start ngrok tunnel and get public URL
with open("ngrok_url.txt", "w") as f:
    f.write(public_url)
print(f"App is accessible at {public_url}")  # Print the public URL

# FastAPI App Setup
app = FastAPI()

async def init_browser():
    global playwright, browser
    
    if browser is None or not hasattr(browser, "new_context"):
        print("Initializing browser...")
        playwright = await async_playwright().start()
        user_data_dir = os.path.abspath("chrome_profile_serve")
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

        wa = browser.pages[0]
        await wa.goto("https://web.whatsapp.com/")
        abraham = wa.locator("//span[@title='abraham_paul_jaison']")
        await abraham.wait_for(state="visible")
        await abraham.click()
        
        message_input = wa.locator("//div[@aria-label='Type a message']//p")
        await message_input.wait_for(state="visible")

@app.get("/generate_clcv_request", response_class=HTMLResponse)
async def generate_clcv_request(request: Request, title: str, advertiser: str, job_id: str):
    return f"""
    <html>
        <head>
            <title>Generate resume and cover letter</title>
        </head>
        <body>
            <h2>{title} @ {advertiser}</h2>
            <form action="/generate_clcv" method="get">
                <input type="hidden" name="title" value="{title}">
                <input type="hidden" name="advertiser" value="{advertiser}">
                <input type="hidden" name="job_id" value="{job_id}">
                <button type="submit" style="padding: 20px 40px; font-size: 24px; background-color: #4CAF50; color: white; border: none; border-radius: 8px; cursor: pointer;">
                    Generate
                </button>
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

        directory = "mycv"
        file_path = os.path.abspath(os.path.join(directory, f"{resume_pdf_path}"))
        cl_file_path = os.path.abspath(os.path.join(directory, f"{cover_letter_path}"))
        print(f"PDF path: {file_path}")
        print(f"CL path: {cover_letter_path}")

        await wa.bring_to_front()
        up_btn_locator = wa.locator("//button[@title='Attach']")
        await up_btn_locator.wait_for(state='visible')
        await up_btn_locator.click()
        file_input = wa.locator("input[type='file'][accept='*']").nth(0)
        await file_input.wait_for(state='attached')


        await file_input.set_input_files(file_path)
        send_button = wa.locator("//span[@data-icon='send']").nth(0)
        await send_button.wait_for(state='visible')
        await send_button.click()
        message_input = wa.locator("//div[@aria-label='Type a message']//p")
        await message_input.wait_for(state="visible")
        await message_input.fill(cover_letter) 
        await send_button.wait_for(state='visible')
        await send_button.click()
        await message_input.fill(f"Apply here: \n {target_url}") 
        await send_button.wait_for(state='visible')
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

            directory = "mycv"
            file_path = os.path.abspath(os.path.join(directory, f"{resume_pdf_path}"))
            print(f"PDF path: {file_path}")

            resume_upload_radio = apage.locator('//input[@data-testid="resume-method-upload"]')
            await resume_upload_radio.wait_for(state="visible")
            await resume_upload_radio.click()

            resume_upload_btn = apage.locator("//button[@id='resume-file-:r2:']")
            await resume_upload_btn.wait_for(state="visible")

            file_input = apage.locator("//div[@data-testid='resumeFileInput']/input[@id='resume-fileFile']")
            await file_input.wait_for(state="attached")
            await file_input.set_input_files(file_path)

            directory = "mycl"
            file_path = os.path.abspath(os.path.join(directory, f"{cover_letter_path}"))
            print(f"CL path: {file_path}")

            cover_letter_radio = apage.locator('//input[@type="radio" and @data-testid="coverLetter-method-upload"]')
            await cover_letter_radio.wait_for(state="attached")

            await cover_letter_radio.click()
            cover_letter_upload_btn = apage.locator("//button[@id='coverLetter-file-:r5:']")
            await cover_letter_upload_btn.wait_for(state="visible")

            # cl_file_input = apage.locator("//div[@data-testid='coverLetterFileInput']/input[@id='coverLetter-fileFile']")
            # await cl_file_input.wait_for(state="attached")
            # await cl_file_input.set_input_files(cl_file_path)

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
    finally:
        await browser.close()
    

if __name__ == '__main__':
    from fastapi import FastAPI
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)
    