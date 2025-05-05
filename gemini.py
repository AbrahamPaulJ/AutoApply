import google.generativeai as genai
from datetime import datetime
import json
import subprocess
import os
import re

# ========== GLOBAL CONFIG ==========
API_KEY = "AIzaSyDKeLDQgsIO2esEx_eN7bhl9NCjP04bI_U"
CL_RESUME_FILE = "clres.txt"
RESUME_FILE = "resume.txt"
NAME = "Abraham Paul Jaison"
ADDRESS = "184 Walkerville Terrace, Walkerville SA 5081"
PHONE = "0489209259"
EMAIL = "abrahampauljaison2@gmail.com"
PROJECT_DIR = os.path.abspath(os.path.dirname(__file__))
JSONCV_DIR = os.path.join(PROJECT_DIR, 'jsoncv')
RESUME_OUT_DIR = os.path.join(PROJECT_DIR, 'mycv')
DATA_FILENAME = os.path.join(JSONCV_DIR, 'cv.json')

# ========== INIT SETUP ==========
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel("gemini-2.0-flash")




# ========== GLOBAL COVER LETTER PROMPT ==========
def generate_cl_prompt(raw_html: str) -> str:
    date = datetime.now().strftime("%d %B %Y").lstrip("0")
    try:
        with open(CL_RESUME_FILE, 'r') as file:
            json_resume = file.read()
    except FileNotFoundError:
        return "Resume file not found."
    
    return f'''
Read the job description from the raw html below:
{raw_html}

I want you to generate a cover letter for {NAME} who is applying for this role. Do not mention the company names of my previous experience, do not mention work experiences that are not relevant to the job. My resume in json format:
{json_resume}

NOTE: Please DO NOT include any placeholders or any other hints that your response is AI generated; you can omit or guess the missing details as required. The current date is {date}. Here is a template you can follow:

{NAME}
{ADDRESS}
{PHONE}
{EMAIL}

{date}

Hiring Manager
[replace with company name]

Dear Hiring Manager,

I am writing to express my keen interest in the [] position at [store/company name], as advertised on Seek. [Insert sentences based on job description and how my experience will contribute to the company]

Thank you for considering my application. I have attached my resume for your review and welcome the opportunity to discuss my qualifications further in an interview.

Sincerely,

{NAME}
    '''

# ========== COVER LETTER FUNCTION ==========
def gen_cover_letter(raw_html: str) -> str:
    prompt = generate_cl_prompt(raw_html)
    response = model.generate_content(prompt)
    return response.text if response.text else "Error. NRFG"

# ========== GLOBAL RESUME PROMPT ==========
def generate_resume_prompt(job_title: str, advertiser_name: str, raw_html: str) -> str:
    # Use global RESUME_FILE
    try:
        with open(RESUME_FILE, 'r', encoding='utf-8') as file:
            json_resume = file.read()
    except FileNotFoundError:
        return "Error: Resume file not found."

    return f'''{json_resume}\nThis is my resume in JSON format, and I want you to modify it to fit the job description. You only need to include my work that is most relevant to the job (try to include AHS Hospitality whenever possible).  
You may change the summary, work, soft skills, and technical skills sections to include keywords relevant to the job description.
You only need to include my work experience that is most relevant to the job. For administration jobs please include my IT work experience. You can omit "certificates" if it is not at all relevant to the job. 
Your reply must have only the json output.
The job description is:\n {raw_html}
'''

# ========== RESUME FUNCTION ==========
def generate_resume(job_title, advertiser_name, raw_html, browser):
    # Define base directories
    jsoncv_dir = JSONCV_DIR
    out_dir = RESUME_OUT_DIR
    data_filename = DATA_FILENAME

    prompt = generate_resume_prompt(job_title, advertiser_name, raw_html)

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


# ========== ASYNC RESUME FUNCTION ==========
def agen_cover_letter(job_id, job_title, advertiser_name, raw_html):
    prompt = generate_cl_prompt(raw_html)
    response = model.generate_content(prompt)
    response_text = response.text if response.text else "Error. NRFG"

    out_dir = "mycl"
    os.makedirs(out_dir, exist_ok=True)

    filename = f"{job_title[:10]}_{advertiser_name[:10]}_{job_id}.txt"
    filename = re.sub(r'[\\/*?:"<>| ]', '_', filename)
    txt_file_path = os.path.join(out_dir, filename)

    with open(txt_file_path, "w", encoding="utf-8") as f:
        f.write(response_text)

    return response_text, txt_file_path

# ========== ASYNC COVER LETTER FUNCTION ==========
async def agenerate_resume(job_id, job_title, advertiser_name, raw_html, browser):
    # Generate prompt using global function
    prompt = generate_resume_prompt(job_title, advertiser_name, raw_html)

    response = model.generate_content(prompt)

    if not response or not response.text:
        return "Error generating resume - 500"

    try:
        cleaned_text = response.text.replace('```', '').replace('json', '').strip()
        resume_json = json.loads(cleaned_text)
    except json.JSONDecodeError as e:
        return f"Error decoding JSON: {str(e)}"
    except Exception as e:
        return f"Error cleaning Gemini response: {str(e)}"

    try:
        os.makedirs(os.path.dirname(DATA_FILENAME), exist_ok=True)
        with open(DATA_FILENAME, 'w', encoding='utf-8') as json_file:
            json.dump(resume_json, json_file, indent=4)
        print("Resume saved successfully.")
    except Exception as e:
        return f"Error writing to JSON file: {str(e)}"

    env = os.environ.copy()
    env["DATA_FILENAME"] = DATA_FILENAME
    env["OUT_DIR"] = RESUME_OUT_DIR

    try:
        subprocess.run(
            ['npm', 'run', 'build'],
            cwd=JSONCV_DIR,
            check=True,
            shell=True,
            env=env
        )
        print("Build completed successfully.")
    except subprocess.CalledProcessError as e:
        return f"Error during build: {e}"

    try:
        html_file_path = os.path.join(RESUME_OUT_DIR, 'index.html')
        filename = f"{job_title[:10]}_{advertiser_name[:10]}_{job_id}.pdf"
        filename = re.sub(r'[\\/*?:"<>| ]', '_', filename)
        pdf_file_path = os.path.join(RESUME_OUT_DIR, filename)

        page = await browser.new_page()
        await page.goto(f'file:///{html_file_path}', wait_until='load')
        await page.pdf(path=pdf_file_path)

        print(f"PDF generated successfully at {pdf_file_path}")
        return filename
    except Exception as e:
        return f"Error converting HTML to PDF: {str(e)}"


def is_admin_job(raw_html: str) -> bool:

    prompt = f"""
You are a helpful assistant that classifies job listings.

The following HTML contains a job description:
{raw_html}

Does this job involve administrative, office support, receptionist, bookkeeping or clerical responsibilities?
Reply with only True or False.
"""
    
    try:
        genai.configure(api_key="AIzaSyDKeLDQgsIO2esEx_eN7bhl9NCjP04bI_U")
        model = genai.GenerativeModel("gemini-2.0-flash")
        response = model.generate_content(prompt)
        answer = response.text.strip()
        return answer.lower() == "true"
    except Exception as e:
        print(f"[Gemini Error] {e}")
        return False  # Default to False on failure
    

    
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