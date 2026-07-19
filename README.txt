SENTIMENT-DRIVEN FRAMEWORK FOR ENHANCING STUDENT SATISFACTION AND UNIVERSITY SERVICES
Gabrina Janice Theseira
================================================================================

1. LIVE DEMO LINKS
--------------------------------------------------------------------------------
Frontend (GitHub Pages): https://gabrina04.github.io/fyp2-mmu-feedback/frontend/login.html
Backend API (Render): https://fyp2-mmu-feedback.onrender.com
Dashboard (Power BI): https://app.powerbi.com/view?r=eyJrIjoiYzc2YzRkMjYtNTZkNC00MzI3LTk3Y2MtODJkYmNjNTMxOGM0IiwidCI6IjdlMGI1ZmNmLTEyYzQtNGVmZi05NmI2LTQ2NjRmMjVkYzdkYSIsImMiOjEwfQ%3D%3D 

Demo admin login:
  Username / ID: admin
  Password: admin123

Note: The backend is hosted on Render's free tier, which sleeps after 15
minutes of inactivity. Please allow up to 60 seconds for the server to
wake up on the first request of a session.

2. SOURCE CODE REPOSITORY
--------------------------------------------------------------------------------
Full version-controlled source code: https://github.com/Gabrina04/fyp2-mmu-feedback

3. TOOLS REQUIRED (with versions and download links)
--------------------------------------------------------------------------------
- Python 3.10 or later          https://www.python.org/downloads/
- pip (bundled with Python)
- Git                            https://git-scm.com/downloads
- A modern web browser (Chrome/Edge/Firefox) to run the frontend HTML files
- A Google Cloud Platform account with a Service Account + Sheets API
  enabled, to generate your own credentials.json for local testing
  https://console.cloud.google.com/
- (Optional, dashboard viewing only) Power BI Desktop
  https://www.microsoft.com/en-us/power-platform/products/power-bi/desktop

4. PYTHON LIBRARIES USED (backend, app.py)
--------------------------------------------------------------------------------
Install all of these with:
  pip install -r requirements.txt

requirements.txt should contain (adjust versions to match what you actually
pinned in your project):
  Flask
  flask-cors
  gspread
  google-auth
  oauth2client
  vaderSentiment
  gunicorn        (only needed if you replicate the Render production server)

5. SETUP INSTRUCTIONS (running the backend locally)
--------------------------------------------------------------------------------
Step 1: Clone the repository
  git clone https://github.com/Gabrina04/fyp2-mmu-feedback.git
  cd fyp2-mmu-feedback

Step 2: Create and activate a virtual environment (recommended)
  python -m venv venv
  venv\Scripts\activate        (Windows)
  source venv/bin/activate     (macOS/Linux)

Step 3: Install dependencies
  pip install -r requirements.txt

Step 4: Set up Google Sheets access
  - Create a Google Cloud service account and download its JSON key.
  - Share your target Google Sheet with the service account's email address.
  - Save the key file as credentials.json in the project's backend folder
    (used automatically for local development), OR
  - Set it as an environment variable named GOOGLE_CREDENTIALS (used in
    the Render production deployment instead of a file).

Step 5: Set up Firebase Authentication
  - Create a Firebase project and enable Email/Password authentication.
  - Copy your Firebase config keys into the frontend's firebase-config.js
    (or equivalent config file in the /frontend folder).

Step 6: Run the Flask backend
  python app.py
  The backend will start on http://localhost:5000 (or the port set in app.py).

Step 7: Run the frontend
  - Open /frontend/login.html directly in a browser, OR serve it locally:
    python -m http.server 8000
    then visit http://localhost:8000/frontend/login.html
  - Make sure the API base URL in the frontend JS files points to your
    local backend (http://localhost:5000) instead of the Render URL when
    testing locally.

6. DATA / DATASET NOTE
--------------------------------------------------------------------------------
This project does not use a static pre-collected dataset. Feedback data is
captured live through the web form and written directly to a Google Sheet
(MMU_Student_Feedback), which serves as the system's data store. A sample
CSV of the 37 test responses used for prototype validation (see Chapter 5,
Testing) is included in the repository under /data/sample_feedback.csv for
reference.

7. CONTACT
--------------------------------------------------------------------------------
Gabrina Janice Theseira
Faculty of Information Science & Technology, Multimedia University