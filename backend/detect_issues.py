import gspread
from oauth2client.service_account import ServiceAccountCredentials

def connect_sheet():
    scope = ["https://spreadsheets.google.com/feeds",
             "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
    client = gspread.authorize(creds)
    sheet = client.open("MMU_Student_Feedback").sheet1
    return sheet

def detect_issue_type(text, specific_area):
    text_lower = text.lower() if text else ''
    area_lower = specific_area.lower() if specific_area else ''

    # Step 1: Area-based detection FIRST (most reliable)
    if 'food court' in area_lower or 'canteen' in area_lower or 'cafe' in area_lower:
        return 'Food/Canteen'
    if 'hostel wi-fi' in area_lower or 'hostel wifi' in area_lower:
        return 'WiFi/Internet'
    if 'hostel' in area_lower:
        return 'Hostel'
    if 'campus security' in area_lower or 'parking' in area_lower:
        return 'Security/Parking'
    if 'fist labs' in area_lower or 'labs' in area_lower:
        return 'Facilities/Equipment'
    if 'library' in area_lower:
        return 'Library'
    if 'mmu portal' in area_lower or 'portal' in area_lower:
        return 'System/Portal'
    if 'moodle' in area_lower:
        return 'System/Portal'
    if 'sport' in area_lower or 'gym' in area_lower:
        return 'Facilities/Equipment'
    if 'lecturer' in area_lower or 'feedback' in area_lower:
        return 'Lecturer/Teaching'
    if 'finance' in area_lower or 'exam' in area_lower or 'international' in area_lower:
        return 'Administrative'
    if 'clc' in area_lower or 'clic' in area_lower:
        return 'Facilities/Equipment'

    # Step 2: Text keyword detection (only if area doesn't match)
    if any(word in text_lower for word in ['wifi', 'wi-fi', 'internet', 'connection', 'network', 'disconnect', 'lag']):
        return 'WiFi/Internet'
    if any(word in text_lower for word in ['dirty', 'clean', 'hygiene', 'smell', 'mess', 'toilet', 'rubbish']):
        return 'Cleanliness'
    if any(word in text_lower for word in ['lecturer', 'teacher', 'teaching', 'lecture', 'subject', 'course', 'marks', 'grade']):
        return 'Lecturer/Teaching'
    if any(word in text_lower for word in ['broken', 'equipment', 'computer', 'pc', 'printer', 'projector', 'aircond', 'fan', 'chair']):
        return 'Facilities/Equipment'
    if any(word in text_lower for word in ['security', 'theft', 'stolen', 'guard', 'cctv']):
        return 'Security'
    if any(word in text_lower for word in ['food', 'canteen', 'cafe', 'hungry', 'eat', 'meal', 'drink']):
        return 'Food/Canteen'
    if any(word in text_lower for word in ['parking', 'park', 'car', 'vehicle', 'motorcycle']):
        return 'Parking'
    if any(word in text_lower for word in ['portal', 'system', 'website', 'online', 'moodle', 'register', 'login']):
        return 'System/Portal'
    if any(word in text_lower for word in ['admin', 'office', 'staff', 'process', 'document', 'form', 'queue', 'wait']):
        return 'Administrative'

    return 'General'

def run():
    print("🔄 Connecting to Google Sheets...")
    sheet = connect_sheet()
    rows = sheet.get_all_records()

    print(f"📊 Found {len(rows)} rows to process...")

    for i, row in enumerate(rows):
        row_num = i + 2
        feedback_text = str(row.get('Feedback_Text', ''))
        specific_area = str(row.get('Specific_Area', ''))
        issue_type = detect_issue_type(feedback_text, specific_area)
        sheet.update_cell(row_num, 13, issue_type)
        print(f"✅ Row {row_num}: {specific_area} → {issue_type}")

    print("\n🎉 All rows updated with Issue_Type!")

if __name__ == '__main__':
    run()