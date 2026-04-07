(function() {
    // 1. INSTANT BLANK: Hide the page before it can render a single pixel
    const hideStyle = document.createElement('style');
    hideStyle.id = "sh3rl0ck-hide-logic";
    hideStyle.innerHTML = 'html { display: none !important; }';
    
    // Add the style to the root element immediately
    if (document.documentElement) {
        document.documentElement.appendChild(hideStyle);
    }

    // 2. LISTEN FOR THE VERDICT FROM BACKGROUND.JS
    chrome.runtime.onMessage.addListener((request) => {
        if (request.action === "EXECUTE_BLOCK") {
            // STOP loading and WIPE the page
            window.stop();
            document.documentElement.innerHTML = "";
            renderRedAlert(request.score, request.url);
        } else if (request.action === "SAFE_ORIGIN") {
            // UNHIDE: AI says it's legitimate
            const styleElement = document.getElementById("sh3rl0ck-hide-logic");
            if (styleElement) styleElement.remove();
        }
    });

    function renderRedAlert(score, targetUrl) {
        document.documentElement.style.display = "block";
        const alertPage = document.createElement("div");
        alertPage.id = "sh3rl0ck-red-alert";
        
        Object.assign(alertPage.style, {
            position: "fixed", top: "0", left: "0",
            width: "100vw", height: "100vh",
            backgroundColor: "#800000",
            backgroundImage: "radial-gradient(circle, #ff0000, #300000)",
            zIndex: "2147483647", display: "flex",
            alignItems: "center", justifyContent: "center",
            color: "white", fontFamily: "'Courier New', monospace",
            textAlign: "center"
        });

        alertPage.innerHTML = `
            <div style="border: 8px solid white; padding: 50px; background: rgba(0,0,0,0.9); box-shadow: 0 0 100px #000; max-width: 800px; border-radius: 20px;">
                <h1 style="font-size: 5rem; margin: 0; color: #ff3333; text-transform: uppercase;">SITE BLOCKED</h1>
                <h2 style="letter-spacing: 5px; margin-top: 10px;">CERBERUS AI ENGINE</h2>
                <hr style="border: 1px solid rgba(255,255,255,0.3); margin: 30px 0;">
                <p style="font-size: 1.5rem; line-height: 1.6;">
                    SH3RL0CK FORENSICS has intercepted a malicious connection.<br>
                    Target: <span style="background: white; color: black; padding: 2px 8px; font-weight: bold;">${new URL(targetUrl).hostname}</span>
                </p>
                <div style="margin: 30px 0; padding: 20px; border: 2px dashed #ff3333; background: rgba(255,0,0,0.1); font-size: 1.4rem;">
                    THREAT CONFIDENCE: ${score}%
                </div>
                <button id="back-to-safety" style="background: white; color: black; border: none; padding: 20px 50px; font-size: 1.5rem; font-weight: bold; cursor: pointer; border-radius: 5px;">BACK TO SAFETY</button>
            </div>`;

        document.documentElement.appendChild(alertPage);
        document.getElementById("back-to-safety").onclick = () => window.location.href = "https://www.google.com";
    }
})();