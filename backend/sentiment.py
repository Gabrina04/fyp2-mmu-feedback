import gspread
from oauth2client.service_account import ServiceAccountCredentials
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from collections import defaultdict

def connect_sheet():
    scope = ["https://spreadsheets.google.com/feeds",
             "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
    client = gspread.authorize(creds)
    sheet = client.open("MMU_Student_Feedback").sheet1
    return sheet

def classify_sentiment(text):
    analyzer = SentimentIntensityAnalyzer()
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

def calculate_FSI(rating, sentiment_score):
    try:
        r = float(rating)
        s = float(sentiment_score)
        return round(r * s, 4)
    except (ValueError, TypeError):
        return 0

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
        if n == 0:
            continue
        S = round(sum(data['sentiment_scores']) / n, 4)
        FSI = round(sum(data['fsi_scores']) / n, 4)
        avg_rating = round(sum(data['ratings']) / n, 2)

        print(f"\n📌 Service Category: {category}")
        print(f"   Total Responses  : {n}")
        print(f"   Average Rating   : {avg_rating} / 5")
        print(f"   S (Avg Sentiment): {S}  ← Formula: Σw / n")
        print(f"   FSI (Final Score): {FSI}  ← Formula: Σ(R×S) / n")
        print(f"   Positive: {data['positive']} | Neutral: {data['neutral']} | Negative: {data['negative']}")

def run_sentiment_analysis():
    print("🔄 Connecting to Google Sheets...")
    sheet = connect_sheet()
    rows = sheet.get_all_records()

    if not rows:
        print("⚠️ No data found in sheet.")
        return

    print(f"📊 Processing ALL {len(rows)} responses (force reprocess)...")

    for i, row in enumerate(rows):
        row_num = i + 2

        feedback_text = str(row.get('Feedback_Text', '')).strip()
        rating = row.get('Rating', 0)

        if not feedback_text:
            print(f"⚠️ Row {row_num}: Empty feedback, skipping.")
            continue

        label, score = classify_sentiment(feedback_text)
        fsi = calculate_FSI(rating, score)

        sheet.update_cell(row_num, 10, label)
        sheet.update_cell(row_num, 11, score)
        sheet.update_cell(row_num, 12, fsi)

        print(f"✅ Row {row_num}: '{feedback_text[:40]}' → {label} (score: {score}, FSI: {fsi})")

    print("\n🎉 All rows processed!")
    updated_rows = sheet.get_all_records()
    calculate_category_summary(updated_rows)

if __name__ == '__main__':
    run_sentiment_analysis()