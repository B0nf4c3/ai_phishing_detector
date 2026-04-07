import pandas as pd
import numpy as np
import math
import re
import os
import joblib
from urllib.parse import urlparse
from collections import Counter
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score

def calculate_entropy(s):
    """Calculates Shannon Entropy of the URL string."""
    p, l = Counter(s), float(len(s))
    return -sum(count/l * math.log2(count/l) for count in p.values())

def extract_url_features(url):
    """Manual extraction to ensure alignment between training and app logic."""
    url = str(url)
    parsed = urlparse(url)
    netloc = parsed.netloc if parsed.netloc else url.split('/')[0]
    path = parsed.path
    
    url_length = len(url)
    number_of_digits = sum(c.isdigit() for c in url)
    
    # 17 Features as per the new dataset specification
    features = {
        'url_length': url_length,
        'has_ip_address': 1 if re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', netloc) else 0,
        'dot_count': url.count('.'),
        'https_flag': 1 if url.startswith('https') else 0,
        'url_entropy': calculate_entropy(url),
        'token_count': len([t for t in re.split(r'[/._\-?=&]', url) if t]),
        'subdomain_count': netloc.count('.') - 1 if netloc.count('.') > 1 else 0,
        'query_param_count': len(parsed.query.split('&')) if parsed.query else 0,
        'tld_length': len(netloc.split('.')[-1]) if '.' in netloc else 0,
        'path_length': len(path),
        'has_hyphen_in_domain': 1 if '-' in netloc else 0,
        'number_of_digits': number_of_digits,
        'tld_popularity': 1 if any(tld in netloc for tld in ['com', 'org', 'net', 'edu', 'gov']) else 0,
        'suspicious_file_extension': 1 if any(url.endswith(ext) for ext in ['.exe', '.zip', '.bat', '.sh']) else 0,
        'domain_name_length': len(netloc.split('.')[-2]) if netloc.count('.') >= 1 else len(netloc),
        'percentage_numeric_chars': (number_of_digits / url_length * 100) if url_length > 0 else 0
    }
    return features

# --- Execution ---
print("Loading new dataset...")

df = pd.read_csv('../data/url_features_extracted1.csv') # I downloaded the dataset from LegitPhish Dataset


df = df.dropna(subset=['ClassLabel'])
# Fill any missing feature values with 0
df = df.fillna(0)

# Target labels: 1 = Legitimate, 0 = Phishing
X = df.drop(['URL', 'ClassLabel'], axis=1)
y = df['ClassLabel'].astype(int)

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

print(f"Training updated model on {len(y_train)} samples...")
model = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
model.fit(X_train, y_train)

# Evaluation
y_pred = model.predict(X_test)
print(f"Forensic Accuracy: {accuracy_score(y_test, y_pred):.4f}")
print("\nClassification Report (1=Legit, 0=Phish):")
print(classification_report(y_test, y_pred))



os.makedirs('../model', exist_ok=True)


joblib.dump(model, '../model/phishing_detector_model.pkl')
joblib.dump(list(X.columns), '../model/feature_names.pkl')
print("Model and Feature Names saved successfully.")