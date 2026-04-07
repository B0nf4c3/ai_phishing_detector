import requests
import time
import random

API_URL = "http://127.0.0.1:5000/predict"
AGENT_ID = "sh3rl0ck"

sample_urls = [
    "https://google.com",
    "https://keraekken-loagginnusa.godaddysites.com/",
    "https://wikipedia.org/wiki/Main_Page",
    "http://instagramtick-git-master-behhruzs-projects.vercel.app/",
    "https://github.com/trending",
    "http://bt-101274.weeblysite.com/",
    "https://microsoft.com",
    "http://bafybeicsc2iofzskpmb56uzh72jirndpnmcs42vb34rlewvt5hgzmqweqa.ipfs.dweb.link/",
    "https://apple.com/support",
    "http://186237glade-fcbe.bardoglet.workers.dev/",
    "https://stackoverflow.com",
    "http://molina-c2f.pages.dev/",
    "https://amazon.com/your-account",
    "http://secure-login-verify-account.com/paypal/home.php",
    "http://192.168.1.105/login/index.html"
]

def run_simulation():
    print(f"--- SOC SIMULATOR START [Agent: {AGENT_ID}] ---")
    random.shuffle(sample_urls)

    for i, url in enumerate(sample_urls, 1):
        try:
            payload = {
                "input": url,
                "user": AGENT_ID
            }
            response = requests.post(API_URL, json=payload)
            
            if response.status_code == 200:
                data = response.json()
                print(f"[{i}/15] {url[:40]}... -> {data['prediction']}")
            else:
                print(f"[{i}/15] API Error: {response.status_code}")
        except Exception as e:
            print(f"[{i}/15] Connection Error: {e}")
            break
            
        time.sleep(random.uniform(1.0, 2.5))

    print("--- SIMULATION COMPLETE ---")

if __name__ == "__main__":
    run_simulation()