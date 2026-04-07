document.addEventListener('DOMContentLoaded', function() {
    const statusText = document.getElementById('status-text');
    const loginSection = document.getElementById('login-section');
    const scannerSection = document.getElementById('scanner-section');
    const agentNameSpan = document.getElementById('agent-display-name');
    const usernameInput = document.getElementById('username-input');
    const loginBtn = document.getElementById('login-btn');
    const rescanBtn = document.getElementById('rescan-btn');

    chrome.storage.local.get(['agentName'], function(data) {
        if (data.agentName) {
            showScanner(data.agentName);
        } else {
            showLogin();
        }
    });

    loginBtn.addEventListener('click', function() {
        const name = usernameInput.value.trim();
        if (name) {
            chrome.storage.local.set({ agentName: name, signedIn: true }, function() {
                showScanner(name);
            });
        }
    });

    function showScanner(name) {
        loginSection.style.display = 'none';
        scannerSection.style.display = 'block';
        agentNameSpan.textContent = name;
        checkCurrentTab(name);
    }

    function showLogin() {
        loginSection.style.display = 'block';
        scannerSection.style.display = 'none';
    }

    function checkCurrentTab(agentName) {
        chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
            let activeTab = tabs[0];
            if (activeTab && activeTab.url.startsWith('http')) {
                statusText.textContent = "SCANNING...";
                statusText.className = "safe";

                fetch("http://127.0.0.1:5000/predict", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ 
                        url: activeTab.url,
                        user: agentName 
                    })
                })
                .then(response => response.json())
                .then(data => {
                    if (data.prediction === "PHISHING") {
                        statusText.textContent = "DANGER: PHISHING";
                        statusText.className = "danger";
                    } else {
                        statusText.textContent = "SECURE: LEGITIMATE";
                        statusText.className = "safe";
                    }
                })
                .catch(err => {
                    statusText.textContent = "OFFLINE";
                    statusText.className = "danger";
                });
            }
        });
    }

    rescanBtn.addEventListener('click', function() {
        chrome.storage.local.get(['agentName'], function(data) {
            checkCurrentTab(data.agentName || "Anonymous");
        });
    });
});