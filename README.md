# AutoApply

Real time scraping of **"Quick Apply"** job listings on [seek.com.au](https://www.seek.com.au).

---

### 🚀 Features
- Scrapes desired job listings from Seek every 2 minutes.
- Uses Gemini API to generate a custom resume and cover letter and sends them via WhatsApp Web (along with the link for the job).
- You can then manually apply via the link (redirects to Seek mobile app). 

---

### 🛠 Requirements
- Python
- Node.js (version 18 or higher)
- Playwright with Chromium
- Two `chrome_profile` folders  
  *(Both must be logged into Seek and WhatsApp Web)*
- ngrok auth Key. Get one for free at https://ngrok.com/docs/api/resources/api-keys/
- A Gemini API Key. Get one for free at https://aistudio.google.com/app/apikey
- A Whatsapp number to receive the job listings in real time.

---

### ⚙️ Installation
- Install `requirements.txt` from the root folder via pip  
- Go to the `jsoncv` folder and install the dependencies by running: `npm install`

---

### ▶️ Run
- Run scraper_server.bat to start scraping in real time.
**or**  
- Run automate.py to mass apply all listings in the last 1-3 days.

