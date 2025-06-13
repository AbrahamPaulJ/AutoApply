import os
import yaml
from datetime import datetime

CL_RESUME_FILE = "clres.txt"
RESUME_FILE = "resume.txt"

def get_user_field(user: str, field: str):
    info_path = os.path.join("Users", user, "info.yaml")
    try:
        with open(info_path, 'r', encoding="utf-8") as file:
            user_data = yaml.safe_load(file)

        if user_data and field in user_data:
            return user_data[field]
        else:
            raise KeyError(f"{field} not found for user {user}")

    except FileNotFoundError:
        print(f"Info file not found for user: {user}")
        return None

# ========== GLOBAL COVER LETTER PROMPT ==========
def generate_cl_prompt(user: str, raw_html: str) -> str:
    date = datetime.now().strftime("%d %B %Y").lstrip("0")
    name = get_user_field(user, "name")
    email = get_user_field(user, "email")
    address = get_user_field(user, "name")
    phone = get_user_field(user, "email")
    
    try:
        clres_txt_path = os.path.join("Users", user, CL_RESUME_FILE)

        with open(clres_txt_path, 'r', encoding='utf-8') as file:
            json_resume = file.read().strip()
    except FileNotFoundError:
        return "Error: Resume file not found."
    
    try:
        clres_prompt = get_user_field(user, "cover_letter_prompt") 
    except:
        return "Error: Cover letter prompt field not found."

    return clres_prompt.format(
        name=name,
        email=email,
        address=address,
        phone=phone,
        json_resume=json_resume,
        date=date,
        raw_html=raw_html
    )

# ========== GLOBAL RESUME PROMPT ==========
def generate_resume_prompt(user: str, job_title: str, raw_html: str) -> str:
    # Use global RESUME_FILE
    try:
        resume_txt_path = os.path.join("Users", user, RESUME_FILE) 
        with open(resume_txt_path, 'r', encoding='utf-8') as file:
            json_resume = file.read()
    except FileNotFoundError:
        return "Error: Resume file not found."
    try:
        resume_prompt = get_user_field(user, "resume_prompt") 
    except:
        return "Error: Resume prompt field not found."
    
    final_prompt = resume_prompt.format(
        json_resume=json_resume,
        job_title=job_title,
        raw_html=raw_html
)
    return final_prompt

def clear_job_ids(base_dir="Users", file_to_clear="job_ids.txt"):
    """
    Clears the content of the given file in all subdirectories of the base directory.

    Parameters:
    - base_dir (str): The path to the base directory containing user folders.
    - file_to_clear (str): The filename to truncate within each user folder.
    """
    if not os.path.exists(base_dir):
        print(f"Base directory not found: {base_dir}")
        return

    for user_folder in os.listdir(base_dir):
        user_path = os.path.join(base_dir, user_folder)
        if os.path.isdir(user_path):
            job_ids_path = os.path.join(user_path, file_to_clear)
            if os.path.exists(job_ids_path):
                with open(job_ids_path, "w") as f:
                    f.truncate(0)
                print(f"Cleared: {job_ids_path}")
            else:
                print(f"Not found: {job_ids_path}")

