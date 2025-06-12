from utils import generate_cl_prompt, generate_resume_prompt, get_user_field
from dotenv import load_dotenv
import google.generativeai as genai
import json
import subprocess
import os
import re

# ========== GLOBAL CONFIG ==========
load_dotenv()  # loads .env file
API_KEY = os.getenv("GOOGLE_API_KEY")
#print(API_KEY)

CL_RESUME_FILE = "clres.txt"
RESUME_FILE = "resume.txt"
PROJECT_DIR = os.path.abspath(os.path.dirname(__file__))
JSONCV_DIR = os.path.join(PROJECT_DIR, 'jsoncv')
RESUME_OUT_DIR = os.path.join(PROJECT_DIR, 'mycv')
DATA_FILENAME = os.path.join(JSONCV_DIR, 'cv.json')

# ========== INIT SETUP ==========
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel("gemini-2.0-flash")

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
    
    response = model.generate_content(prompt)

    return response.text if response.text else "Error. No response from Gemini"

# ========== ASYNC COVER LETTER FUNCTION ==========
def gen_cover_letter(user, job_id, job_title, advertiser_name, raw_html, cl_extra=""):
    prompt = generate_cl_prompt(user, raw_html)

    # Append additional notes if provided
    if cl_extra.strip():
        prompt += f"\n\nImportant Notes: {cl_extra.strip()}"
    response = model.generate_content(prompt)
    response_text = response.text if response.text else "Error. NRFG"

    out_dir = os.path.join("Users", user, "mycl")
    os.makedirs(out_dir, exist_ok=True)

    filename = f"{job_title[:10]}_{advertiser_name[:10]}_{job_id}.txt"
    filename = re.sub(r'[\\/*?:"<>| ]', '_', filename)
    txt_file_path = os.path.join(out_dir, filename)

    with open(txt_file_path, "w", encoding="utf-8") as f:
        f.write(response_text)

    return response_text, txt_file_path

# ========== ASYNC RESUME FUNCTION ==========
async def agenerate_resume(user, job_id, job_title, advertiser_name, raw_html, resume_extra, browser):
    # Generate the base prompt
    prompt = generate_resume_prompt(user, job_title, raw_html)

    # Append important notes if provided 
    if resume_extra.strip():
        prompt += f"\n\nImportant Notes: {resume_extra.strip()}"

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
        USER_DIR = os.path.join(PROJECT_DIR, 'Users', user, "mycv") 
        os.makedirs(os.path.dirname(DATA_FILENAME), exist_ok=True)
        with open(DATA_FILENAME, 'w', encoding='utf-8') as json_file:
            json.dump(resume_json, json_file, indent=4)
        print("Resume json saved successfully.")
    except Exception as e:
        return f"Error writing to JSON file: {str(e)}"

    env = os.environ.copy()
    env["DATA_FILENAME"] = DATA_FILENAME
    env["OUT_DIR"] = USER_DIR

    print(f"usf:{USER_DIR}")
    print(DATA_FILENAME)

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
        html_file_path = os.path.join(USER_DIR, 'index.html')
        filename = f"{job_title[:10]}_{advertiser_name[:10]}_{job_id}.pdf"
        filename = re.sub(r'[\\/*?:"<>| ]', '_', filename)
        pdf_file_path = os.path.join(USER_DIR, filename)

        page = await browser.new_page()
        await page.goto(f'file:///{html_file_path}', wait_until='load')
        await page.pdf(path=pdf_file_path)

        print(f"PDF generated successfully at {pdf_file_path}")
        return filename
    except Exception as e:
        return f"Error converting HTML to PDF: {str(e)}"
    
# ========== JOB SUITABILITY CHECKER  ==========
def is_suitable(user, name, adv, jtype, loc, wtype, desc):
    try:
        resume_txt_path = os.path.join("Users", user, RESUME_FILE)
        with open(resume_txt_path, 'r', encoding='utf-8') as file:
            json_resume = file.read()
    except FileNotFoundError:
        return {
            "suitable": False,
            "reason": "Error: Resume file not found.",
            "confidence": 0
        }
    
    additional_info = get_user_field(user, "additional_info") 

    prompt_template = get_user_field(user, "suitable_prompt")
    if prompt_template is None:
        return {
            "suitable": False,
            "reason": "Error: suitable_prompt field not found.",
            "confidence": 0
        }

    prompt = prompt_template.format(
        json_resume=json_resume,
        additional_info=additional_info,
        name=name,
        adv=adv,
        jtype=jtype,
        loc=loc,
        wtype=wtype,
        desc=desc
    )

    response = model.generate_content(prompt)

    try:
        raw_text = response.text.strip()
        cleaned = re.sub(r"^```(?:json)?\s*|\s*```$", "", raw_text.strip(), flags=re.IGNORECASE)
        result = json.loads(cleaned)

        result["suitable"] = result.get("suitable", False) and result.get("confidence", 0) >= 50
    except Exception as e:
        result = {
            "suitable": False,
            "reason": f"Error parsing response: {str(e)}. Response was: {response.text}",
            "confidence": 0
        }
    return result

# ========== ANSWER QUESTIONS ==========
def get_question_actions(user: str, html: str):
    try:
        resume_txt_path = os.path.join("Users", user, RESUME_FILE)
        with open(resume_txt_path, 'r', encoding='utf-8') as file:
            json_resume = file.read()
    except FileNotFoundError:
        return "Error: Resume file not found."
    
    additional_info = get_user_field(user, "additional_info") 

    prompt = f"""{json_resume}
    This is my resume in JSON format.

    Extract form questions from the following HTML, but ONLY if they are:
    <select>, <textarea>, <input type="checkbox">, or <input type="radio"> elements and have NOT been answered. 

    For each matched element, respond strictly with a JSON array where each entry follows this schema:

    {{
    "question_type": "select" | "textarea" | "checkbox" | "radio",
    "question": "<The visible label or question text>",
    "xpath": "<A unique, absolute XPath for the input element, ideally using unique attributes like id, name, or label text nearby. Avoid using only tag nesting like /div/div/div.>",
    "options": ["<option1>", "<option2>", ...],                       // only for select, checkbox
    "selected_options": ["<option1>", ...],                           // only for checkbox
    "chosen_label": "<the label of the selected option>",             
    "chosen_option": "<value attribute of the selected option>",      // only for radio
    "fill_value":"<short answer depending on the question>"           // only for textarea
    }}

    For clarity and consistency, here are separate JSON examples for each `question_type`. Please use the same xpath structure in the examples:

    [
    // SELECT
    {{
        "question_type": "select",
        "question": "What is your current employment status?",
        "xpath": "//select/parent::div/parent::div/parent::div/div/span[contains(., "What is your current employement status")][1]",
        "options": ["Employed", "Unemployed", "Student", "Other"],
        "chosen_label": "Student",
    }},

    // RADIO 
    {{
        "question_type": "radio",
        "question": "Are you legally allowed to work in Australia?",
        "xpath": "//input[@type='radio' and @id=':r1f:']",
        "chosen_label": "Yes",
        "chosen_option": "<value attribute of the selected radio button>"  // MUST be input value attribute
    }},

    // CHECKBOX (FIELDSET)
    {{
        "question_type": "checkbox",
        "question": "Which shifts are you available for?",
        "xpath": "//span[normalize-space()='<question>']/ancestor::div[2]//label[.//span[normalize-space()='<selected_option>']]/parent::div/parent::div/parent::div/parent::div/div/input",
        "options": ["Morning", "Afternoon", "Night"],
        "selected_options": ["Morning", "Afternoon"]              //These contain the selected option, DO NOT OMIT
    }},

    // TEXTAREA
    {{
        "question_type": "textarea",
        "question": "Tell us briefly why you are suitable for this role.",
        "xpath": "//textarea[@aria-describedby=':r21:']",
        "fill_value": "I am reliable, have retail experience, and am available on weekends."  // Text answer
    }}
    ]

    Rules:
    - You MUST ANSWER the questions by filling or choosing, make decision from the info you have.
    - The XPath **must uniquely identify the input element**. Prefer XPaths with attributes like:
        - `//select[@name='xyz']`
        - `//input[@type='radio'][@value='abc']`
        - or using associated label text via `label[normalize-space(text())='...']/following::select[1]`
    - DO NOT GENERATE SHALLOW OR ABSOLUTE XPaths like `/div/div/div/select`. THIS IS VERY IMPORTANT. Ensure the XPath works even if the surrounding div structure changes.
    - ONLY answer questions if in addition to the form, that are also present in //div[@id='errorPanel'].
    - Return only the fields applicable to the question type.
    - Always use valid JSON.
    - Avoid Markdown or code block wrappers like ```json.
    - Always choose "Less than 1 year" for experience related questions if available, even if I have no experience.
    -You MUST answer based on the info I provided, if vague you have to guess. For example:
        - If the question is "Are you an Australian or New Zealand Citizen?", answer "No".
        - If it's a Yes/No question and my context clearly answers it, infer the correct option (e.g., "student visa" means NOT a citizen).

    Apart from my resume, here is additional context about me:\n
    {additional_info}\n


    HTML form:
    {html}
    """

    response = model.generate_content(prompt)
    response_text = response.text or "Error: No response from Gemini."

    response_text = re.sub(r"^```(?:json)?\s*|\s*```$\n*", "", response_text.strip(), flags=re.IGNORECASE).strip()
    
    print(response_text)

    try:
        questions = json.loads(response_text)
    except json.JSONDecodeError:
        print("❌ JSON Decode Error on response:")
        print(response_text)
        return []

    actions = []
    for q in questions:
        qtype = q.get("question_type")
        if qtype == "select":
            chosen_label = q.get("chosen_label")
            if not chosen_label:
                print(f"⚠️ Missing chosen_label for select: {q}")
                continue

            actions.append({
                "xpath": q["xpath"],
                "action": "select_option",
                "question": q["question"],
                "chosen_label": chosen_label
            })

        elif qtype == "textarea":
            fill_value = q.get("fill_value") 
            actions.append({
                "xpath": q["xpath"],
                "action": "fill",
                "value": fill_value,
                "chosen_label": fill_value,
                "question": q["question"]
            })

        elif qtype == "checkbox":
            selected_options = q.get("selected_options", [])
            question = q.get("question", [])
            # Validate inputs
            if not selected_options:
                print(f"⚠️ Missing selected_options for checkbox: {q}")
                continue

            for selected_option in selected_options:
                # Use label-based XPath for checkboxes
                xpath = f'//span[normalize-space()="{question}"]/ancestor::div[2]//label[.//span[normalize-space()="{selected_option}"]]/parent::div/parent::div/parent::div/parent::div/div/input'



                actions.append({
                    "xpath": xpath,
                    "action": "check",
                    "question": q["question"],
                    "chosen_label": selected_option
                })
            
        elif q['question_type'] == 'radio':
            chosen_label = q.get("chosen_label")
            chosen_option = q.get("chosen_option")
            if not chosen_option:
                print(f"❌ Skipping due to lazy Gemini response; chosen_option is blank: {q}")
                continue
            actions.append({
                'xpath': q['xpath'],
                'action': 'choose_radio',
                'value': chosen_option,
                'question': q['question'],
                "chosen_label": chosen_label
            })

    return actions