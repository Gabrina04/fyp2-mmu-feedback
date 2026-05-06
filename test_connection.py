import gspread
from oauth2client.service_account import ServiceAccountCredentials

scope = ["https://spreadsheets.google.com/feeds", 
         "https://www.googleapis.com/auth/drive"]

creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client = gspread.authorize(creds)

sheet = client.open("MMU_Student_Feedback").sheet1

sheet.append_row([
    "2026-05-05 10:00:00",
    "TEST001",
    "FIST",
    "Undergraduate",
    "Academic Support",
    5,
    "The lecturers are very helpful and supportive",
    "Overall great experience",
    "",
    "",
    ""
])

print("✅ Connection successful! Check your Google Sheet.")