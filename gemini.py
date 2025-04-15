import google.generativeai as genai
from datetime import datetime
import json
import subprocess
import os
import re

def gen_cover_letter(raw_html: str) -> str:

    date = datetime.now().strftime("%d %B %Y").lstrip("0")  
    resume = r"C:\Users\abrah\OneDrive\Desktop\Projects\Automator\clres.txt"
    
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
    # Define the resume file path
    resume = r"C:\Users\abrah\OneDrive\Desktop\Projects\cover_letter_extension\resume.txt"
    
    # Read the resume template
    with open(resume, 'r') as file:
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

    # Save the generated resume JSON to the DATA_FILENAME location
    data_filename = r'C:\Users\abrah\Downloads\mycv\cv.json'
    try:
        cleaned_text = response.text.replace('```', '').replace('json', '').strip()

        try:
            resume_json = json.loads(cleaned_text)
        except json.JSONDecodeError as e:
            return f"Error decoding JSON: {str(e)}"

        # Now save the parsed JSON to the file
        with open(data_filename, 'w', encoding='utf-8') as json_file:
            json.dump(resume_json, json_file, indent=4)
        print("Resume saved successfully.")
    except Exception as e:
        return f"Error writing to JSON file: {str(e)}"

    # Run the build process with npm
    out_dir = r"C:\Users\abrah\Downloads\mycv"
    env = os.environ.copy()
    env["DATA_FILENAME"] = data_filename
    env["OUT_DIR"] = out_dir

    try:
        subprocess.run(
            ['npm', 'run', 'build'], 
            cwd=r'C:\Users\abrah\OneDrive\Desktop\Projects\cover_letter_extension\jsoncv', 
            check=True, 
            shell=True, 
            env=env
        )
        print("Build completed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error during build: {e}")
        return f"Error during build: {e}"

    # Convert the generated HTML to PDF using Playwright (Reuse the page)
    try:
        html_file_path = os.path.join(out_dir, 'index.html')
        filename = f"{job_title[:10]}_{advertiser_name[:10]}.pdf"
        filename = filename.replace(" ", "_")
        filename = re.sub(r'[\\/*?:"<>|]', '_', filename)

        # Ensure the filename is safe (remove spaces or special characters if needed)
        

        # Construct the full file path
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



# def answer_xpath(q: str, qtype: str) -> str:
#     user_info = {
#         "name": "Abraham Paul Jaison",
#         "address": "184 Walkerville Terrace, Walkerville SA 5081",
#         "phone": "0489209259",
#         "email": "abrahampauljaison2@gmail.com",
#         "gender": "male",
#         "Resident/ VISA status": "Student VISA subclass 500 with limited work right, Indian ethnicity",
#         "retail_experience": "6 months"
#     }

#     prompt = f'''My info is {user_info}\n I want you to generate an xpath to answer a question which is of type {qtype}. The question is:\n{q}\n . Depending on the answer,
#       generate an xpath for submitting the answer.
#       For radio buttons, generate as: //span[text() = 'Please make a selection']/ancestor::div[4]//input[@xpath="insert positional index here"]
#      Generate only the xpath in your answer, no other lines are allowed.
#       '''

#     genai.configure(api_key="AIzaSyDKeLDQgsIO2esEx_eN7bhl9NCjP04bI_U")
#     model = genai.GenerativeModel("gemini-2.0-flash")
#     response = model.generate_content(prompt)

#     return response.text if response.text else "Error. NRFG"


# q = '''Do you have experience using point of sale (POS) software?
# Yes
# No
# Please make a selection'''

# print(answer_xpath(q, "radio button"))


# raw_html = '''<div class="gepq850 _1iptfqa0"><p><strong>About the Role</strong></p>
# <p>Join the Jay Jays crew as an <strong>Assistant Store Manager</strong> and help steer the ship at our&nbsp;<strong>Harbourtown&nbsp;</strong>store! You’ll support the Store Manager to drive sales, hit KPIs, and ensure your team is always delivering awesome customer service. If you’re passionate about streetwear and inspiring others, this is your chance to step up and shine.</p>
# <p>This is a <strong>30 Hour Part Time</strong> role requiring availability for weekends, late-night trading hours, and public holidays.</p>
# <p><strong>A Day in the Life</strong></p>
# <ul>
# <li>Assist the Store Manager in achieving sales goals and providing an epic customer experience.</li>
# <li>Coach your team to be the best they can be, offering guidance and feedback.</li>
# <li>Help with day-to-day operations like stock management and keeping the store looking fresh.</li>
# <li>Collaborate with the Store Manager to create a positive and inclusive environment for your team.</li>
# <li>Assist with visual merchandising to make sure the store is always on point.</li>
# </ul>
# <p><strong>What You’ll Bring</strong></p>
# <ul>
# <li>Previous experience in retail, with leadership or supervisory experience.</li>
# <li>A love for streetwear and a passion for delivering top-notch customer service.</li>
# <li>A proactive attitude to drive sales and team performance.</li>
# <li>Strong organisational skills and the ability to juggle multiple tasks.</li>
# <li>Experience with visual merchandising is a bonus.</li>
# </ul>
# <p><strong>What We Offer</strong></p>
# <ul>
# <li>Competitive hourly rate with penalty rates for evenings, weekends, and public holiday shifts.</li>
# <li>50% off Jay Jays products so you can rock the latest styles.</li>
# <li>Training workshops and internal programs to help you grow and develop.</li>
# <li>Exclusive perks via the Just Us Portal, such as Gym membership discounts.</li>
# <li>A structured 3-month training program to help you settle in.</li>
# <li>Flexible rosters that help you keep a great work/life balance.</li>
# <li>Employee Assistance Program for your well-being and mental health.</li>
# </ul>
# <p><strong>About Jay Jays</strong></p>
# <p>Jay Jays – a place where we’re all about freedom of expression and about being whoever you want to be! <strong>Nail it. Rock it. Love it. Own It.</strong> As part of a well established and successful retail group with four other dynamic brands, Jay Jays offers clear development paths, leadership workshops, and upskilling opportunities in a people-first culture!</p>
# <p><strong>HOW TO APPLY </strong></p>
# <p><strong>This exciting and challenging opportunity awaits for a driven individual to take the next step in their career with Jay Jays – a place where we’re all about “freedom of expression” and about being whoever you want to be! Nail it. Rock it. Love it. Own It. </strong></p>
# <p><strong>Click the “Apply for this Job” button today!</strong></p>
# <p>&nbsp;</p>
# <div><strong><em>Our team members and customers have the right to a safe working and shopping environment.&nbsp;</em></strong></div>
# <div><strong><em>Where you visit a store or meet with one of our teams for a job interview, please treat everyone with respect.&nbsp;&nbsp;Verbal Aggression, Sexual Harassment and Physical Abuse will not be tolerated.</em></strong></div></div>'''
# print(gen_cover_letter(raw_html))



