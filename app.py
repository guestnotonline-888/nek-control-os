@app.route('/')
def home():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>NEK-CONTROL SYSTEM v4.8 // Project Preview</title>
        <style>
            body { 
                background-color: #050b14; 
                color: #e0e1dd; 
                font-family: 'Courier New', monospace; 
                padding: 30px;
                display: flex;
                justify-content: center;
            }
            .terminal-box { 
                border: 3px solid #415a77; 
                padding: 25px; 
                max-width: 650px; 
                background-color: #0d1b2a; 
                box-shadow: 0 0 20px rgba(65, 90, 119, 0.4);
                border-radius: 4px;
            }
            h1 { 
                color: #00ff00; 
                font-size: 20px; 
                margin-top: 0;
                border-bottom: 2px solid #415a77;
                padding-bottom: 10px;
                text-shadow: 0 0 5px rgba(0, 255, 0, 0.5);
            }
            .meta { color: #8ecae6; font-size: 13px; }
            .highlight { color: #ffb703; }
            .preview-img { 
                width: 100%; 
                border: 2px solid #415a77; 
                margin-top: 15px;
                margin-bottom: 15px;
            }
            .footer {
                font-size: 12px;
                color: #64dfdf;
                border-top: 1px dashed #415a77;
                padding-top: 10px;
                margin-top: 20px;
            }
        </style>
    </head>
    <body>
        <div class="terminal-box">
            <h1>☢️ NEK-CONTROL SYSTEM v4.8 // CORE GRAPHICS ENGINE</h1>
            <p class="meta">STATUS: ONLINE // ENVIRONMENT: LIVE PRODUCTION</p>
            
            <p>Welcome to the development preview interface. This cloud engine dynamically draws real-time CRT instrumentation metrics for text-based tactical simulations.</p>
            
            <p>⚡ <span class="highlight">Current Live Telemetry Render:</span></p>
            
            <!-- This automatically pulls your live canvas generator right onto the page -->
            <img class="preview-img" src="/api/screen/PREVIEW/285/100/15.5/green.png" alt="Terminal UI">
            
            <p>The backend script parses live simulation variables (UI State, Core Temperature, Reactor Power, and Pressure) and converts them into an instant visual display board.</p>
            
            <div class="footer">
                >> Project Status: In Active Deployment // Built for External Bot Integrations.
            </div>
        </div>
    </body>
    </html>
    '''
    
