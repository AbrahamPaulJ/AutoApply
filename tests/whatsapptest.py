
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from pyngrok import ngrok
from playwright.async_api import async_playwright
import asyncio
import platform
import os
import re
import urllib.parse
import threading
from gemini import gen_summary, is_suitable, gen_cover_letter, agenerate_resume

playwright = None
browser = None

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

async def apply_job():
    await init_browser()
    wa = browser.pages[0]
    await wa.bring_to_front()

    await wa.bring_to_front()
    up_btn_locator = wa.locator("//button[@title='Attach']")
    await up_btn_locator.wait_for(state='visible')
    await up_btn_locator.click()
    # document_btn_locator = wa.locator("(//li[@role='button'])[1]")
    # await document_btn_locator.wait_for(state='visible')
    # await document_btn_locator.click()

    file_input = wa.locator("//li[@tabindex='0']//input[@type='file' and @accept='*']")
    await file_input.wait_for(state='attached')
    await file_input.set_input_files(r"C:\Users\abrah\Downloads\mycv\Sales_Show_Flair_Curt.pdf")

    send_button = wa.locator("//span[@data-icon='send']")
    await send_button.wait_for(state='visible')
    await send_button.click()

    await asyncio.sleep(10)



if __name__ == '__main__':
    asyncio.run(apply_job())