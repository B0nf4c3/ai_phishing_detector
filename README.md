# Cerberus-AI: Forensic Phishing Detection Framework
Cerberus-AI is an end-to-end cybersecurity solution that leverages machine learning to detect phishing threats in real-time. Unlike standard URL filters, Cerberus-AI focuses on **Forensic Accountability**, ensuring that every security event is attributed to a specific investigator (Agent) to maintain a non-repudiable audit trail.

## Core Features
### 1. ML-Driven Threat Detection
Uses a Random Forest classifier trained on thousands of legitimate and phishing URLs. It performs real-time feature extraction on 15+ data points, including:

* **URL Entropy:** Detecting randomized "gibberish" characters.
* **Structural Anomalies:** Counting dots, hyphens, and suspicious TLDs.
* **Identity Integrity:** Evaluating domain length and HTTPS status.

### 2. Proactive Interception (Chrome Extension)
The extension monitors navigation and intercepts requests at the `onCommitted` stage. If the backend classifies a site as **PHISHING**, the user is immediately redirected to a "Blocked" safety page, preventing credential theft before the page even renders.

  
### 3. Agent Accountability (Objective 5)
Every session begins with an **Agent Initialization**. Investigators must provide an Agent ID (e.g., `Sh3rl0ck`), which is then tagged to every automatic scan and manual forensic inquiry.


### 4. SOC Dashboard & Forensic Reporting
A Flask-powered Security Operations Center (SOC) dashboard provides:
* **Live Telemetry:** Real-time feed of all intercepted URLs.
* **Forensic Logs:** A central CSV-based audit trail.
* **Automated Reporting:** One-click PDF generation for professional incident reporting.

  
## Tech Stack
* **Backend:** Python, Flask, Pandas, Scikit-Learn
* **Frontend:** JavaScript (ES6), HTML5, CSS3 (Cyberpunk/Dark Theme)
* **Browser API:** Chrome Extension Manifest V3
* **Forensics:** FPDF for automated report generation

## Project Structure
```sh
├── extension/          # Chrome Extension source code
│   ├── popup.html      # Agent Login and Status UI
│   ├── popup.js        # Extension logic & API communication
│   └── manifest.json   # Extension configuration
├── server/             # Flask Backend
│   ├── app.py          # ML Inference and Logging Engine
│   └── templates/      # SOC Dashboard UI
├── model/              # Trained ML models (.pkl)
├── logs/               # CSV Audit Trails & PDF Reports
└── simulator/          # Python script for SOC stress-testing
  
```

## Installation & Setup

1. **Clone the Repository:**

```bash
   git clone https://github.com/b0nf4c3/ai_phishing_detector.git
```


2. **Create a python virtual Environment and  Install Dependencies:**
   
```bash
   # Create the environment
   python3 -m venv venv
   
   # Activate the Env
   source /venv/bin/activate
   
   # install the Dependences
   pip install -r requirements.txt
```

  
3. **Start the Forensic Engine:**
   
```bash
   python server/app.py
```

  
4. **Load the Extension:**  
   * Open Chrome and go to `chrome://extensions/`  
   * Enable **Developer Mode**.  
   * Click **Load unpacked** and select the `extension/` folder.  
![alt text](/images/image.png)
##  Usage
1. Open the extension and "Log In" with your **Agent ID**.  
For example `test`  
![alt text](/images/image-1.png)
2. Browse the web; Cerberus will automatically intercept threats.  
 Test a legit site   like `https://microsoft.com`  
 ![alt text](/images/image-2.png)  
 Then Enter a malicious site  
![alt text](/images/image-3.png)

3. Access `http://127.0.0.1:5000` to view the **Live Activity Logs** and download forensic reports.  
![alt text](/images/image-4.png)
