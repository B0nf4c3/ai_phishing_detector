let lastAnalyzedUrls = {};

chrome.webNavigation.onCommitted.addListener((details) => {
    if (details.frameId !== 0) return;

    chrome.storage.local.get(['signedIn', 'agentName'], (res) => {
        const targetUrl = details.url;
        if (!targetUrl.startsWith('http')) return;

        if (lastAnalyzedUrls[details.tabId] === targetUrl) return;
        lastAnalyzedUrls[details.tabId] = targetUrl;

        console.log("Cerberus: Early Intercept ->", targetUrl);

        fetch("http://127.0.0.1:5000/predict", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ 
                url: targetUrl,
                user: res.agentName || "Anonymous"
            })
        })
        .then(res => res.json())
        .then(data => {
            if (data.prediction === "PHISHING") {
                console.error("THREAT CONFIRMED. Executing Hard Block.");
                
                chrome.tabs.sendMessage(details.tabId, {
                    action: "EXECUTE_BLOCK",
                    score: data.confidence,
                    url: targetUrl
                }).catch(err => console.log("Content script not ready yet, retrying..."));
            } else {
                chrome.tabs.sendMessage(details.tabId, { action: "SAFE_ORIGIN" })
                .catch(err => {});
            }
        })
        .catch(err => {
            console.error("Forensic Engine Offline:", err);
            delete lastAnalyzedUrls[details.tabId];
        });
    });
}, { url: [{ urlPrefix: 'http' }] });

chrome.tabs.onRemoved.addListener(tabId => delete lastAnalyzedUrls[tabId]);