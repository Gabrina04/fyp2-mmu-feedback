from flask import Flask, request, jsonify
from flask_cors import CORS
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import json
import os

app = Flask(__name__)
CORS(app)

def connect_sheet():
    scope = ["https://spreadsheets.google.com/feeds",
             "https://www.googleapis.com/auth/drive"]
    
    # Try environment variable first (for Render)
    creds_json = os.environ.get('GOOGLE_CREDENTIALS')
    if creds_json:
        creds_dict = json.loads(creds_json)
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    else:
        # Fall back to local credentials.json (for local development)
        creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
    
    client = gspread.authorize(creds)
    sheet = client.open("MMU_Student_Feedback").sheet1
    return sheet

def classify_sentiment(text):
    analyzer = SentimentIntensityAnalyzer()
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

def calculate_FSI(rating, sentiment_score):
    try:
        r = float(rating)
        s = float(sentiment_score)
        fsi = round(r * s, 4)
        return fsi
    except:
        return 0

@app.route('/submit', methods=['POST'])
def submit_feedback():
    try:
        data = request.json
        sheet = connect_sheet()

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        feedback_text = data.get('feedback_text', '')
        rating = int(data.get('rating', 0))

        label, score = classify_sentiment(feedback_text)
        fsi = calculate_FSI(rating, score)

        sheet.append_row([
            timestamp,
            data.get('student_id', ''),
            data.get('faculty', ''),
            data.get('level', ''),
            data.get('service_category', ''),
            rating,
            feedback_text,
            data.get('additional_comments', ''),
            label,
            score,
            fsi
        ])

        return jsonify({"status": "success", "message": "Feedback submitted!"})

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)