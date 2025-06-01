# AutoApply

Real time scraping and auto-applying to **"Quick Apply"** job listings on [seek.com.au](https://www.seek.com.au). 

---

### 🚀 Features
- Scrapes desired job listings from Seek every 2 minutes.
- Use your desired filters for the jobs. Gemini API matches your details to the job listing to decide whether to complete the application.
- If suitable, Gemini API generates a custom resume and cover letter and applies for the job. 
- The suitability and application status is sent via Telegram to the user in real time. 

---

### 🛠 Requirements
- Python
- Node.js (version 18 or higher)
- Playwright with Chromium
- Two `chrome_profile` folders  
  *(Both must be logged into Seek)*
- ngrok auth Key. Get one for free at https://ngrok.com/docs/api/resources/api-keys/
- A Gemini API Key. Get one for free at https://aistudio.google.com/app/apikey
- A Telegram number to receive the applications in real time.

---

### ⚙️ Installation
- Install `requirements.txt` from the root folder via pip  
- Go to the `jsoncv` folder and install the dependencies by running: `npm install`

---

### ▶️ Run
- Run `scraper_server.bat` to start scraping in real time.  
**or**  
- Run `asyncscrape.py` in UI mode to mass apply all listings from the last 3 days.
