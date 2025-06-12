# AutoApply

Real time scraping and auto-applying to **"Quick Apply"** job listings on [seek.com.au](https://www.seek.com.au). 

---

### 🚀 Features
- Scrapes desired job listings from Seek every few minutes.
- Use your desired filters for the jobs. Gemini API matches your details to the job listing to decide whether to complete the application.
- If suitable, Gemini API generates a custom resume, cover letter, answers recruiter questions and applies for the job. 
- The suitability and application status is sent via Telegram to the user in real time. 

---

### 🛠 Requirements
- Python
- Node.js (version 18 or higher)
- Playwright with Chromium
- A `chrome_profile` folder
  *(Must be logged into Seek)*
- A Gemini API Key. Get one for free at https://aistudio.google.com/app/apikey
- Optional: A Telegram number to receive application updates in real time

---

### ⚙️ Installation

```bash
git clone https://github.com/AbrahamPaulJ/AutoApply.git
cd AutoApply
git submodule update --init --recursive
```

- Install `requirements.txt` from the root folder via pip
- Go to the `jsoncv` folder and install the dependencies by running: `npm install`

---

### ▶️ Run
- Run `scraper.bat` to start scraping in real time.  

