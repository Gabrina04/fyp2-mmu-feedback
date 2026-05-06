import gspread
from oauth2client.service_account import ServiceAccountCredentials
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from collections import defaultdict

# Connect to Google Sheets
def connect_sheet():
    scope = ["https://spreadsheets.google.com/feeds",
             "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
    client = gspread.authorize(creds)
    sheet = client.open("MMU_Student_Feedback").sheet1
    return sheet

# Classify sentiment
def classify_sentiment(text):
    analyzer = SentimentIntensityAnalyzer()

    # Custom Malaysian English words
    analyzer.lexicon.update({
        'syok': 2.0,
        'oklah': 0.5,
        'bagus': 2.0,
        'teruk': -2.0,
        'cincai': -1.5,
        'best': 1.5,
        'terima kasih': 1.5,
        'susah': -1.0,
        'lambat': -1.0,
        'cepat': 1.0
    })

    score = analyzer.polarity_scores(text)['compound']

    if score >= 0.05:
        label = 'Positive'
    elif score <= -0.05:
        label = 'Negative'
    else:
        label = 'Neutral'

    return label, round(score, 4)

# Calculate FSI per row
def calculate_FSI(rating, sentiment_score):
    try:
        r = float(rating)
        s = float(sentiment_score)
        fsi = round(r * s, 4)
        return fsi
    except:
        return 0

# Calculate S and FSI per category
def calculate_category_summary(rows):
    # Group by service category
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
        except:
            continue

    print("\n" + "="*60)
    print("📊 CATEGORY SUMMARY REPORT")
    print("="*60)

    for category, data in category_data.items():
        n = data['total']
        if n == 0:
            continue

        # Formula 1: S = Σw / n
        S = round(sum(data['sentiment_scores']) / n, 4)

        # Formula 2: FSI = Σ(R × S) / n
        FSI = round(sum(data['fsi_scores']) / n, 4)

        # Average rating
        avg_rating = round(sum(data['ratings']) / n, 2)

        print(f"\n📌 Service Category: {category}")
        print(f"   Total Responses  : {n}")
        print(f"   Average Rating   : {avg_rating} / 5")
        print(f"   S (Avg Sentiment): {S}  ← Formula: Σw / n")
        print(f"   FSI              : {FSI}  ← Formula: Σ(R×S) / n")
        print(f"   Positive         : {data['positive']} responses")
        print(f"   Neutral          : {data['neutral']} responses")
        print(f"   Negative         : {data['negative']} responses")

    print("\n" + "="*60)
    print("✅ Summary complete!")
    print("="*60)

# Main function
def run_sentiment_analysis():
    print("🔄 Connecting to Google Sheets...")
    sheet = connect_sheet()
    rows = sheet.get_all_records()

    if not rows:
        print("⚠️ No data found in sheet.")
        return

    print(f"📊 Found {len(rows)} responses. Processing...")

    for i, row in enumerate(rows):
        row_num = i + 2

        # Skip if already processed
        if row.get('Sentiment_Label') and row.get('Sentiment_Score'):
            continue

        feedback_text = str(row.get('Feedback_Text', ''))
        rating = row.get('Rating', 0)

        if not feedback_text:
            continue

        label, score = classify_sentiment(feedback_text)
        fsi = calculate_FSI(rating, score)

        # Write back to Google Sheet
        sheet.update_cell(row_num, 9, label)
        sheet.update_cell(row_num, 10, score)
        sheet.update_cell(row_num, 11, fsi)

        print(f"✅ Row {row_num}: '{feedback_text[:40]}' → {label} (score: {score}, FSI: {fsi})")

    # Refresh rows after processing
    rows = sheet.get_all_records()

    # Calculate and print category summary
    calculate_category_summary(rows)

if __name__ == '__main__':
    run_sentiment_analysis()