# AutoApply

Real time scraping of **"Quick Apply"** job listings on [seek.com.au](https://www.seek.com.au).

---

### 🚀 Features
- Scrapes desired job listings from Seek every 2 minutes.
- Uses Gemini API to generate a custom resume and cover letter and sends them via WhatsApp Web (along with the link for the job).
- You can then manually apply via the link (redirects to Seek mobile app). 

---

### 🛠 Requirements
- Python & Node.js
- Playwright with Chromium
- Two `chrome_profile` folders  
  *(Both must be logged into Seek and WhatsApp Web)*
- A Gemini API Key. Get one for free at https://aistudio.google.com/app/apikey
