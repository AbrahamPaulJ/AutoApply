import google.generativeai as genai
from datetime import datetime
import json
import subprocess
import os
import re

def gen_cover_letter(raw_html: str) -> str:

    date = datetime.now().strftime("%d %B %Y").lstrip("0")  
    resume = "clres.txt"
    
    # Read the resume template
    with open(resume, 'r') as file:
        json_resume = file.read()
    

    prompt = f'''Read the job description from the raw html below:\n {raw_html}\n I want you to generate a cover letter for Abraham Paul Jaison who is
    applying for this role. Do not mention the company names of my previous experience. My resume in json format:\n {json_resume}\n NOTE: Please DO NOT include any placeholders or any other hints that your response is AI generated;
    you can omit or guess the missing details as required. The current date is {date} .Here is a template you can follow:
    
    Abraham Paul Jaison
    184 Walkerville Terrace, Walkerville SA 5081
    0489209259
    abrahampauljaison2@gmail.com

    [insert current date here]

    Hiring Manager
    [replace with company name]

    Dear Hiring Manager,

    I am writing to express my keen interest in the [] position at [store/company name], as advertised on Seek. [Insert sentences based on job description and how my experience will contribute to the company]

    Thank you for considering my application. I have attached my resume for your review and welcome the opportunity to discuss my qualifications further in an interview.

    Sincerely,

    Abraham Paul Jaison
    '''

    genai.configure(api_key="AIzaSyDKeLDQgsIO2esEx_eN7bhl9NCjP04bI_U")
    model = genai.GenerativeModel("gemini-2.0-flash")
    response = model.generate_content(prompt)

    return response.text if response.text else "Error. NRFG"


def generate_resume(job_title, advertiser_name, raw_html, browser):
    # Define base directories
    project_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    jsoncv_dir = os.path.join(project_dir, 'jsoncv')
    resume_txt_path = os.path.join(project_dir, 'resume.txt')
    out_dir = os.path.join(project_dir, 'mycv')
    data_filename = os.path.join(jsoncv_dir, 'cv.json')
    

    # Read the resume template
    with open(resume_txt_path, 'r', encoding='utf-8') as file:
        json_resume = file.read()

    prompt = f'''{json_resume}\n This is my resume in JSON format, and I want you to modify it to fit the job description. You only need to include my work that is most relevant to the job.
    You may change the summary, work, soft skills, and technical skills sections to include keywords relevant to the job description.
    You only need to include my work experience that is most relevant to the job. You can omit "certificates" if it is not at all relevant to the job. 
    Your reply must have only the json output.
    The job description is:\n {raw_html}
    '''

    model = genai.GenerativeModel("gemini-2.0-flash")
    response = model.generate_content(prompt)

    if not response or not response.text:
        return "Error generating resume - 500"

    try:
        cleaned_text = response.text.replace('```', '').replace('json', '').strip()

        try:
            resume_json = json.loads(cleaned_text)
        except json.JSONDecodeError as e:
            return f"Error decoding JSON: {str(e)}"

        with open(data_filename, 'w', encoding='utf-8') as json_file:
            json.dump(resume_json, json_file, indent=4)
        print("Resume saved successfully.")
    except Exception as e:
        return f"Error writing to JSON file: {str(e)}"

    # Run the build process
    env = os.environ.copy()
    env["DATA_FILENAME"] = data_filename
    env["OUT_DIR"] = out_dir

    try:
        subprocess.run(
            ['npm', 'run', 'build'],
            cwd=jsoncv_dir,
            check=True,
            shell=True,
            env=env
        )
        print("Build completed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error during build: {e}")
        return f"Error during build: {e}"

    # Convert to PDF using Playwright
    try:
        html_file_path = os.path.join(out_dir, 'index.html')
        filename = f"{job_title[:10]}_{advertiser_name[:10]}.pdf"
        filename = re.sub(r'[\\/*?:"<>| ]', '_', filename)  # Sanitize filename
        pdf_file_path = os.path.join(out_dir, filename)

        res_page = browser.new_page()
        res_page.goto(f'file:///{html_file_path}')
        res_page.pdf(path=pdf_file_path)
        res_page.goto(f'file:///{pdf_file_path}')

        print(f"PDF generated successfully at {pdf_file_path}")
        return pdf_file_path
    except Exception as e:
        return f"Error converting HTML to PDF: {str(e)}"

def gen_summary(name,adv,jtype,loc,wtype,desc) -> str:
   
    prompt = f'''Summarize this job:\n 
    Name: {name}\n
    Advertised by: {adv}\n
    Job type: {jtype}\n
    Location: {loc}\n
    Work Type: {wtype}\n
    Job Description(raw HTML): {desc}\n

    In the summary please list all requirements for working, for example: drivers license, barista experience etc.
    The summary must be in neat text format, do not write anything else other than the summary in your reply.'''
    
    genai.configure(api_key="AIzaSyDKeLDQgsIO2esEx_eN7bhl9NCjP04bI_U")
    model = genai.GenerativeModel("gemini-2.0-flash")
    response = model.generate_content(prompt)

    return response.text if response.text else "Error. No response from Gemini"

def is_suitable(name,adv,jtype,loc,wtype,desc) -> bool:
   
    prompt = f'''Summarize this job:\n 
    Name: {name}\n
    Advertised by: {adv}\n
    Job type: {jtype}\n
    Location: {loc}\n
    Work Type: {wtype}\n
    Job Description(raw HTML): {desc}\n

    I need you to read the job description and tell me if I am suitable for this job. Answer in only one word with "yes" or "no".
    Answer "no" if any of these conditions are met, else answer "yes":
    - The job is mainly related to driving.
    - A working with children check (WWCC) is mandatory.
    - A forklift license is mandatory.
    - It is a job as a chef requiring certifications in commercial cookery.

    '''
    genai.configure(api_key="AIzaSyDKeLDQgsIO2esEx_eN7bhl9NCjP04bI_U")
    model = genai.GenerativeModel("gemini-2.0-flash")
    response = model.generate_content(prompt)
    answer = response.text.strip().lower() if response.text else ""
    print(f"is_suitable: {answer}")
    return not ("no" in answer)


async def agenerate_resume(job_id, job_title, advertiser_name, raw_html, browser):
    # Define base paths
    project_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    jsoncv_dir = os.path.join(project_dir, 'jsoncv')
    resume_txt_path = os.path.join(project_dir, 'resume.txt')
    data_filename = os.path.join(jsoncv_dir, 'mycv', 'cv.json')
    out_dir = os.path.join(project_dir, 'mycv')

    # Read resume template
    try:
        with open(resume_txt_path, 'r', encoding='utf-8') as file:
            json_resume = file.read()
    except Exception as e:
        return f"Error reading resume template: {str(e)}"

    # Prompt to Gemini
    prompt = f'''{json_resume}\n This is my resume in JSON format, and I want you to modify it to fit the job description. You only need to include my work that is most relevant to the job.
    You may change the summary, work, soft skills, and technical skills sections to include keywords relevant to the job description.
    You only need to include my work experience that is most relevant to the job. You can omit "certificates" if it is not at all relevant to the job. 
    Your reply must have only the json output.
    The job description is:\n {raw_html}
    '''

    model = genai.GenerativeModel("gemini-2.0-flash")
    response = model.generate_content(prompt)

    if not response or not response.text:
        return "Error generating resume - 500"

    # Parse Gemini's response
    try:
        cleaned_text = response.text.replace('```', '').replace('json', '').strip()

        try:
            resume_json = json.loads(cleaned_text)
        except json.JSONDecodeError as e:
            return f"Error decoding JSON: {str(e)}"

        os.makedirs(os.path.dirname(data_filename), exist_ok=True)
        with open(data_filename, 'w', encoding='utf-8') as json_file:
            json.dump(resume_json, json_file, indent=4)
        print("Resume saved successfully.")
    except Exception as e:
        return f"Error writing to JSON file: {str(e)}"

    # Run npm build
    env = os.environ.copy()
    env["DATA_FILENAME"] = data_filename
    env["OUT_DIR"] = out_dir

    try:
        subprocess.run(
            ['npm', 'run', 'build'],
            cwd=jsoncv_dir,
            check=True,
            shell=True,
            env=env
        )
        print("Build completed successfully.")
    except subprocess.CalledProcessError as e:
        return f"Error during build: {e}"

    # Convert HTML to PDF using Playwright (async)
    try:
        html_file_path = os.path.join(out_dir, 'index.html')
        filename = f"{job_title[:10]}_{advertiser_name[:10]}_{job_id}.pdf"
        filename = re.sub(r'[\\/*?:"<>| ]', '_', filename)  # Clean filename
        pdf_file_path = os.path.join(out_dir, filename)

        page = await browser.new_page()
        await page.goto(f'file:///{html_file_path}', wait_until='load')
        await page.pdf(path=pdf_file_path)

        print(f"PDF generated successfully at {pdf_file_path}")
        return filename
    except Exception as e:
        return f"Error converting HTML to PDF: {str(e)}"
    

def agen_cover_letter(job_id, job_title, advertiser_name, raw_html):

    date = datetime.now().strftime("%d %B %Y").lstrip("0")  
    resume = "clres.txt"
    
    # Read the resume template
    with open(resume, 'r') as file:
        json_resume = file.read()
    

    prompt = f'''Read the job description from the raw html below:\n {raw_html}\n I want you to generate a cover letter for Abraham Paul Jaison who is
    applying for this role. Do not mention the company names of my previous experience. My resume in json format:\n {json_resume}\n NOTE: Please DO NOT include any placeholders or any other hints that your response is AI generated;
    you can omit or guess the missing details as required. The current date is {date} .Here is a template you can follow:
    
    Abraham Paul Jaison
    184 Walkerville Terrace, Walkerville SA 5081
    0489209259
    abrahampauljaison2@gmail.com

    [insert current date here]

    Hiring Manager
    [replace with company name]

    Dear Hiring Manager,

    I am writing to express my keen interest in the [] position at [store/company name], as advertised on Seek. [Insert sentences based on job description and how my experience will contribute to the company]

    Thank you for considering my application. I have attached my resume for your review and welcome the opportunity to discuss my qualifications further in an interview.

    Sincerely,

    Abraham Paul Jaison
    '''

    genai.configure(api_key="AIzaSyDKeLDQgsIO2esEx_eN7bhl9NCjP04bI_U")
    model = genai.GenerativeModel("gemini-2.0-flash")
    response = model.generate_content(prompt)

    response_text = response.text if response.text else "Error. NRFG"

    out_dir = r"mycl" 
    os.makedirs(out_dir, exist_ok=True)  # ensure the folder exists

    filename = f"{job_title[:10]}_{advertiser_name[:10]}_{job_id}.txt"
    filename = filename.replace(" ", "_")
    filename = re.sub(r'[\\/*?:"<>|]', '_', filename)
    txt_file_path = os.path.join(out_dir, filename)

    # Write to file
    with open(txt_file_path, "w", encoding="utf-8") as f:
        f.write(response_text)

    return response_text, txt_file_path

