import gspread
from oauth2client.service_account import ServiceAccountCredentials
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from collections import defaultdict

# 1. Connect to Google Sheets
def connect_sheet():
    scope = ["https://spreadsheets.google.com/feeds",
             "https://www.googleapis.com/auth/drive"]
    # Ensure credentials.json is in your backend folder
    creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
    client = gspread.authorize(creds)
    sheet = client.open("MMU_Student_Feedback").sheet1
    return sheet

# 2. Classify sentiment with Malaysian context
def classify_sentiment(text):
    analyzer = SentimentIntensityAnalyzer()

    # Custom lexicon for MMU/Malaysian student context
    analyzer.lexicon.update({
        'syok': 2.0, 'oklah': 0.5, 'bagus': 2.0, 'teruk': -2.0,
        'cincai': -1.5, 'best': 1.5, 'terima kasih': 1.5,
        'susah': -1.0, 'lambat': -1.0, 'cepat': 1.0
    })

    score = analyzer.polarity_scores(text)['compound']

    if score >= 0.05:
        label = 'Positive'
    elif score <= -0.05:
        label = 'Negative'
    else:
        label = 'Neutral'

    return label, round(score, 4)

# 3. Formula: FSI = Rating * Sentiment Score
def calculate_FSI(rating, sentiment_score):
    try:
        r = float(rating)
        s = float(sentiment_score)
        fsi = round(r * s, 4)
        return fsi
    except (ValueError, TypeError):
        return 0

# 4. Generate the BIA Summary Report
def calculate_category_summary(rows):
    category_data = defaultdict(lambda: {
        'sentiment_scores': [],
        'fsi_scores': [],
        'ratings': [],
        'positive': 0,
        'neutral': 0,
        'negative': 0,
        'total': 0
    })

    for row in rows:
        # get_all_records() uses Header Names from Row 1
        category = row.get('Service_Category', 'Unknown')
        sentiment_score = row.get('Sentiment_Score', 0)
        fsi = row.get('FSI', 0)
        rating = row.get('Rating', 0)
        label = row.get('Sentiment_Label', '')

        try:
            category_data[category]['sentiment_scores'].append(float(sentiment_score))
            category_data[category]['fsi_scores'].append(float(fsi))
            category_data[category]['ratings'].append(float(rating))
            category_data[category]['total'] += 1

            if label == 'Positive':
                category_data[category]['positive'] += 1
            elif label == 'Negative':
                category_data[category]['negative'] += 1
            else:
                category_data[category]['neutral'] += 1
        except (ValueError, TypeError):
            continue

    print("\n" + "="*60)
    print("📊 CATEGORY SUMMARY REPORT (BIA ANALYSIS)")
    print("="*60)

    for category, data in category_data.items():
        n = data['total']
        if n == 0: continue

        # S = Σw / n
        S = round(sum(data['sentiment_scores']) / n, 4)
        # FSI = Σ(R × S) / n
        FSI = round(sum(data['fsi_scores']) / n, 4)
        avg_rating = round(sum(data['ratings']) / n, 2)

        print(f"\n📌 Service Category: {category}")
        print(f"   Total Responses  : {n}")
        print(f"   Average Rating   : {avg_rating} / 5")
        print(f"   S (Avg Sentiment): {S}")
        print(f"   FSI (Final Score): {FSI}")

# 5. Main Loop
def run_sentiment_analysis():
    print("🔄 Connecting to Google Sheets...")
    sheet = connect_sheet()
    rows = sheet.get_all_records()

    if not rows:
        print("⚠️ No data found in sheet.")
        return

    print(f"📊 Processing {len(rows)} responses...")

    for i, row in enumerate(rows):
        row_num = i + 2 # Google Sheets is 1-indexed, and Row 1 is Headers

        # Skip if already analyzed to save API quota
        if row.get('Sentiment_Label') and row.get('Sentiment_Score'):
            continue

        feedback_text = str(row.get('Feedback_Text', ''))
        rating = row.get('Rating', 0)

        if not feedback_text:
            continue

        label, score = classify_sentiment(feedback_text)
        fsi = calculate_FSI(rating, score)

        # UPDATED: Writing to Columns 10, 11, and 12
        # J=10 (Label), K=11 (Score), L=12 (FSI)
        sheet.update_cell(row_num, 10, label)
        sheet.update_cell(row_num, 11, score)
        sheet.update_cell(row_num, 12, fsi)

        print(f"✅ Row {row_num}: Feedback processed (FSI: {fsi})")

    # Final Summary
    updated_rows = sheet.get_all_records()
    calculate_category_summary(updated_rows)

if __name__ == '__main__':
    run_sentiment_analysis()