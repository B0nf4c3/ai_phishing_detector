import joblib, pandas as pd, os, re, csv, math
from datetime import datetime
from urllib.parse import urlparse
from collections import Counter
from flask import Flask, request, jsonify, render_template, send_file
from flask_cors import CORS
from fpdf import FPDF

# --- Configuration ---
MODEL_PATH = '../model/phishing_detector_model.pkl'
FEATURES_PATH = '../model/feature_names.pkl'
LOG_FILE_PATH = '../logs/soc_scan_logs.csv'

app = Flask(__name__, template_folder=os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'templates')))
CORS(app) 

def calculate_entropy(s):
    p, l = Counter(s), float(len(s))
    return -sum(count/l * math.log2(count/l) for count in p.values())

def extract_url_features(url):
    url = str(url)
    parsed = urlparse(url)
    netloc = parsed.netloc if parsed.netloc else url.split('/')[0]
    num_digits = sum(c.isdigit() for c in url)
    return {
        'url_length': len(url),
        'has_ip_address': 1 if re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', netloc) else 0,
        'dot_count': url.count('.'),
        'https_flag': 1 if url.startswith('https') else 0,
        'url_entropy': calculate_entropy(url),
        'token_count': len([t for t in re.split(r'[/._\-?=&]', url) if t]),
        'subdomain_count': netloc.count('.') - 1 if netloc.count('.') > 1 else 0,
        'query_param_count': len(parsed.query.split('&')) if parsed.query else 0,
        'tld_length': len(netloc.split('.')[-1]) if '.' in netloc else 0,
        'path_length': len(parsed.path),
        'has_hyphen_in_domain': 1 if '-' in netloc else 0,
        'number_of_digits': num_digits,
        'tld_popularity': 1 if any(t in netloc for t in ['com', 'org', 'net', 'edu', 'gov']) else 0,
        'suspicious_file_extension': 1 if any(url.endswith(ext) for ext in ['.exe', '.zip', '.bat']) else 0,
        'domain_name_length': len(netloc.split('.')[-2]) if netloc.count('.') >= 1 else len(netloc),
        'percentage_numeric_chars': (num_digits / len(url) * 100) if len(url) > 0 else 0
    }

def initialize_logs():
    try:
        os.makedirs('../logs', exist_ok=True)
        if not os.path.exists(LOG_FILE_PATH):
            with open(LOG_FILE_PATH, mode='w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(['Timestamp', 'User', 'URL', 'Prediction', 'Confidence'])
    except Exception as e:
        print(f"Error initializing logs: {e}")

initialize_logs()

try:
    clf = joblib.load(MODEL_PATH)
    FEATURE_NAMES = joblib.load(FEATURES_PATH)
except:
    clf, FEATURE_NAMES = None, []

@app.route('/')
def index(): 
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    if clf is None: return jsonify({"error": "Model offline"}), 500
    data = request.get_json()
    url = data.get('input') or data.get('url')
    user_id = data.get('user', 'Anonymous')

    if not url: return jsonify({"error": "No URL"}), 400

    try:
        feat_dict = extract_url_features(url)
        X_new = pd.DataFrame([feat_dict]).reindex(columns=FEATURE_NAMES, fill_value=0)
        prediction = clf.predict(X_new)[0]
        probs = clf.predict_proba(X_new)[0]
        confidence = probs[1] if prediction == 1 else probs[0]
        result = "LEGITIMATE" if prediction == 1 else "PHISHING"

        with open(LOG_FILE_PATH, mode='a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([datetime.now().strftime("%Y-%m-%d %H:%M:%S"), user_id, url, result, round(float(confidence), 4)])

        return jsonify({"prediction": result, "confidence": round(float(confidence) * 100, 2)})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/get_session_logs')
def get_session_logs():
    if os.path.exists(LOG_FILE_PATH):
        return jsonify(pd.read_csv(LOG_FILE_PATH).to_dict(orient='records'))
    return jsonify([])

@app.route('/download_csv')
def download_csv():
    return send_file(LOG_FILE_PATH, as_attachment=True) if os.path.exists(LOG_FILE_PATH) else ("No logs", 404)

@app.route('/download_pdf')
def download_pdf():
    if not os.path.exists(LOG_FILE_PATH): return "No logs", 404
    df = pd.read_csv(LOG_FILE_PATH)
    pdf = FPDF()
    pdf.add_page()
    pdf.set_fill_color(11, 14, 20)
    pdf.rect(0, 0, 210, 35, 'F')
    pdf.set_text_color(0, 255, 194)
    pdf.set_font("Arial", 'B', 18)
    pdf.cell(190, 15, "SOC FORENSIC THREAT REPORT", ln=True, align='C')
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Arial", size=10)
    pdf.ln(15)
    pdf.cell(100, 8, f"Report Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=True)
    pdf.cell(100, 8, f"Total Scans: {len(df)}", ln=True)
    pdf.ln(10)
    pdf.set_fill_color(220, 220, 220)
    pdf.set_font("Arial", 'B', 8)
    pdf.cell(35, 10, "Timestamp", 1, 0, 'C', True)
    pdf.cell(30, 10, "User", 1, 0, 'C', True)
    pdf.cell(85, 10, "Target URL", 1, 0, 'C', True)
    pdf.cell(40, 10, "Result", 1, 1, 'C', True)
    pdf.set_font("Arial", size=8)
    
    # Changed to iterate through ALL rows for a full forensic report
    for _, row in df.iterrows():
        pdf.cell(35, 10, str(row['Timestamp']), 1)
        pdf.cell(30, 10, str(row['User']), 1)
        pdf.cell(85, 10, str(row['URL'])[:45], 1)
        pdf.set_text_color(200, 0, 0) if str(row['Prediction']).strip() == 'PHISHING' else pdf.set_text_color(0, 128, 0)
        pdf.cell(40, 10, str(row['Prediction']), 1, 1, 'C')
        pdf.set_text_color(0, 0, 0)
        
    report_path = "../logs/forensic_report.pdf"
    pdf.output(report_path)
    return send_file(report_path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True, port=5000)