from flask import Flask, request, jsonify
from flask_cors import CORS
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import json
import os
import re
import nltk
from collections import defaultdict

app = Flask(__name__)
CORS(app)

# Download nltk names corpus if not already downloaded
try:
    nltk.data.find('corpora/names')
except LookupError:
    nltk.download('names')

from nltk.corpus import names as nltk_names
ALL_NAMES = set(w.lower() for w in nltk_names.words())

def connect_sheet():
    scope = ["https://spreadsheets.google.com/feeds",
             "https://www.googleapis.com/auth/drive"]
    creds_json = os.environ.get('GOOGLE_CREDENTIALS')
    if creds_json:
        creds_dict = json.loads(creds_json)
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    else:
        creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
    client = gspread.authorize(creds)
    sheet = client.open("MMU_Student_Feedback").sheet1
    return sheet

def censor_names(text):
    if not text:
        return text

    # Step 1: Title-based censoring (Dr, Prof, Mr, etc.)
    titles = [
        'Dr', 'Dr.', 'Prof', 'Prof.', 'Professor',
        'Mr', 'Mr.', 'Mrs', 'Mrs.', 'Ms', 'Ms.',
        'Sir', 'Madam', 'Mdm', 'Mdm.'
    ]
    censored = text
    for title in titles:
        pattern = rf'\b{re.escape(title)}\.?\s+[A-Z][a-zA-Z]+(\s+[A-Z][a-zA-Z]+)*'
        censored = re.sub(pattern, f'{title} [Name Redacted]', censored)

    # Step 2: NLTK name detection for capitalized words
    words = censored.split()
    result = []
    for word in words:
        clean_word = re.sub(r'[^a-zA-Z]', '', word)
        if (clean_word and
            clean_word[0].isupper() and
            clean_word.lower() in ALL_NAMES and
            len(clean_word) > 2):
            result.append('[Name Redacted]')
        else:
            result.append(word)

    return ' '.join(result)

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
    except:
        return 0

@app.route('/submit', methods=['POST'])
def submit_feedback():
    try:
        data = request.json
        sheet = connect_sheet()
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Censor all names before saving
        feedback_text = censor_names(data.get('feedback_text', ''))
        additional_comments = censor_names(data.get('additional_comments', ''))

        rating = int(data.get('rating', 0))
        label, score = classify_sentiment(feedback_text)
        fsi = calculate_FSI(rating, score)

        sheet.append_row([
            timestamp,
            data.get('student_id', ''),
            data.get('faculty', ''),
            data.get('level', ''),
            data.get('service_category', ''),
            data.get('specific_area', ''),
            rating,
            feedback_text,
            additional_comments,
            label,
            score,
            fsi
        ])
        return jsonify({"status": "success", "message": "Feedback submitted!"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/dashboard', methods=['GET'])
def get_dashboard():
    try:
        sheet = connect_sheet()
        rows = sheet.get_all_records()

        if not rows:
            return jsonify({"status": "error", "message": "No data found"}), 404

        total = len(rows)
        positive = sum(1 for r in rows if r.get('Sentiment_Label') == 'Positive')
        negative = sum(1 for r in rows if r.get('Sentiment_Label') == 'Negative')
        neutral = sum(1 for r in rows if r.get('Sentiment_Label') == 'Neutral')

        positive_pct = round((positive / total) * 100, 1) if total > 0 else 0
        negative_pct = round((negative / total) * 100, 1) if total > 0 else 0

        fsi_values = []
        for r in rows:
            try:
                fsi_values.append(float(r.get('FSI', 0)))
            except:
                continue
        overall_fsi = round(sum(fsi_values) / len(fsi_values), 4) if fsi_values else 0

        category_data = defaultdict(lambda: {
            'positive': 0, 'neutral': 0, 'negative': 0,
            'fsi_scores': [], 'total': 0
        })

        for r in rows:
            cat = r.get('Service_Category', 'Unknown')
            label = r.get('Sentiment_Label', '')
            try:
                fsi = float(r.get('FSI', 0))
            except:
                fsi = 0
            category_data[cat]['total'] += 1
            category_data[cat]['fsi_scores'].append(fsi)
            if label == 'Positive':
                category_data[cat]['positive'] += 1
            elif label == 'Negative':
                category_data[cat]['negative'] += 1
            else:
                category_data[cat]['neutral'] += 1

        area_data = defaultdict(lambda: {
            'positive': 0, 'neutral': 0, 'negative': 0,
            'fsi_scores': [], 'total': 0
        })

        for r in rows:
            area = r.get('Specific_Area', 'Unknown')
            label = r.get('Sentiment_Label', '')
            try:
                fsi = float(r.get('FSI', 0))
            except:
                fsi = 0
            area_data[area]['total'] += 1
            area_data[area]['fsi_scores'].append(fsi)
            if label == 'Positive':
                area_data[area]['positive'] += 1
            elif label == 'Negative':
                area_data[area]['negative'] += 1
            else:
                area_data[area]['neutral'] += 1

        categories = {}
        for cat, d in category_data.items():
            n = len(d['fsi_scores'])
            categories[cat] = {
                'positive': d['positive'],
                'neutral': d['neutral'],
                'negative': d['negative'],
                'total': d['total'],
                'fsi': round(sum(d['fsi_scores']) / n, 4) if n > 0 else 0
            }

        areas = {}
        for area, d in area_data.items():
            n = len(d['fsi_scores'])
            areas[area] = {
                'positive': d['positive'],
                'neutral': d['neutral'],
                'negative': d['negative'],
                'total': d['total'],
                'fsi': round(sum(d['fsi_scores']) / n, 4) if n > 0 else 0
            }

        return jsonify({
            "status": "success",
            "total": total,
            "positive": positive,
            "negative": negative,
            "neutral": neutral,
            "positive_pct": positive_pct,
            "negative_pct": negative_pct,
            "overall_fsi": overall_fsi,
            "categories": categories,
            "areas": areas
        })

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)