    # wa = browser.pages[0]
    # page = browser.new_page()
    # page.set_default_timeout(10000)  # Set global timeout to 3 seconds
    # page.goto(f"https://www.seek.com.au/job/{job_id}")

    # apply_btn_locator = page.locator('//a[@data-automation="job-detail-apply"]')
    # apply_btn_locator.wait_for(state="visible")
    # apply_btn_text = apply_btn_locator.inner_text().strip().lower()
    # print(f"Button text detected: {apply_btn_text}")

    # if "quick apply" in apply_btn_text:
    #     print("Quick Apply detected. Proceeding...")

    #     job_type_locator = page.locator('span[data-automation="job-detail-classifications"]')
    #     job_type_locator.wait_for(state='visible')
    #     job_type = job_type_locator.inner_text().strip().lower()
    #     print(f"Job type: {job_type}")

    #     job_details_locator = page.locator('div[data-automation="jobAdDetails"]')
    #     raw_html = job_details_locator.inner_html()
    #     cover_letter = gen_cover_letter(raw_html)
    #     resume_pdf_path = generate_resume(job_title, advertiser, raw_html, browser)
    #     if "error" in resume_pdf_path.lower():
    #         print("Resume wasn't generated")
    #         print(resume_pdf_path)

    #     print("Quick Applying...")

    #     with page.context.expect_page() as new_page_info:
    #         apply_btn_locator.click()
    #     new_page = new_page_info.value
    #     new_page.wait_for_load_state()

    #     if new_page.url.startswith("https://www.seek.com.au/"):
    #         print(new_page.url)
    #         try:
                
    #             dropdown = new_page.locator("//select[@id=':r3:']")
    #             dropdown.wait_for(state="attached", timeout=5000)
    #             try:
    #                 dropdown.select_option(index=1, timeout=5000) 
    #                 delete_btn = new_page.locator("//button[@id='deleteResume']")
    #                 delete_btn.wait_for(state="visible", timeout=5000)
    #                 delete_btn.click()
    #                 delete_cfmbtn = new_page.locator("//button[@data-testid='delete-confirmation']")
    #                 delete_cfmbtn.wait_for(state="visible", timeout=5000)
    #                 delete_cfmbtn.click()
    #             except Exception as e:
    #                 print(f"Error: {e}. No resume options found to delete.")


    #             resume_upload_radio = new_page.locator('//input[@data-testid="resume-method-upload"]')
    #             resume_upload_radio.wait_for(state="visible", timeout=5000)
    #             resume_upload_radio.click()

    #             resume_upload_btn = new_page.locator("//button[@id='resume-file-:r2:']")
    #             resume_upload_btn.wait_for(state="visible", timeout=5000)

    #             directory = "C:/Users/abrah/Downloads/mycv"
    #             file_path = os.path.abspath(os.path.join(directory, f"{resume_pdf_path}"))
    #             print(f"PDF path: {file_path}")
                

    #             file_input = new_page.locator("//div[@data-testid='resumeFileInput']/input[@id='resume-fileFile']")
    #             file_input.wait_for(state="attached", timeout=5000)
    #             file_input.set_input_files(file_path)


    #             cover_letter_radio = new_page.locator('//input[@type="radio" and @data-testid="coverLetter-method-change"]')
    #             cover_letter_radio.wait_for(state="attached")
    #             cover_letter_radio.click()

    #             cover_letter_textarea = new_page.locator('//textarea[@data-testid="coverLetterTextInput"]')
    #             cover_letter_textarea.wait_for(state="visible")
    #             cover_letter_textarea.fill(cover_letter)

    #             cont_btn_locator = new_page.locator('//button[@data-testid="continue-button"]')
    #             cont_btn_locator.wait_for(state="visible", timeout=3000)
    #             cont_btn_locator.click()
    #             print("Cover Letter Generated!")
    #             print("\n")

    #             try:
    #                 cont_btn_locator.wait_for(state="visible", timeout=3000)
    #                 cont_btn_locator.click()

    #                 cont_btn_locator.wait_for(state="visible", timeout=3000)
    #                 cont_btn_locator.click()
    #             except Exception as e:
    #                 print(f"Error: {e}. Cannot continue further, may require manual input.")

    #             page.bring_to_front()

    #             if new_page.url.endswith("profile"):
    #                 cont_btn_locator.wait_for(state="visible", timeout=3000)
    #                 cont_btn_locator.click()

    #         except Exception as e:
    #             print(f"Error: {e}. Skipping the page.")
    #             import traceback
    #             traceback.print_exc()
    #     else:
    #         print("The page URL does not match, skipping...")
    # else:
    #     print("No Quick Apply option, skipping...")