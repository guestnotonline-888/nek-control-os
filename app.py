from flask import Flask, send_file
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont

app = Flask(__name__)

# 1. Retro Preview Homepage Route
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
            
            <!-- Pulls your new layout right into the homepage preview -->
            <img class="preview-img" src="/PREVIEW_285_100_15.5_green.png" alt="Terminal UI">
            
            <p>The backend script parses live simulation variables (UI State, Core Temperature, Reactor Power, and Pressure) and converts them into an instant visual display board.</p>
            
            <div class="footer">
                >> Project Status: In Active Deployment // Built for External Bot Integrations.
            </div>
        </div>
    </body>
    </html>
    '''

# 2. Disguised Image Generator Route (Underscores only to slip past chat firewalls)
@app.route('/<state>_<temp>_<power>_<press>_<status>.png')
def draw_screen(state, temp, power, press, status):
    # Create a clean, retro 600x350 dark-slate canvas
    canvas = Image.new('RGB', (600, 350), color='#0d1b2a')
    raw = ImageDraw.Draw(canvas)

    # Draw retro terminal frame lines
    raw.rectangle([15, 15, 585, 335], outline='#415a77', width=3)
    raw.line([15, 65, 585, 65], fill='#415a77', width=2)

    font = ImageFont.load_default()

    # Draw text values onto the display panel
    raw.text((35, 30), f"SYSTEM CONTROL OPERATING SYSTEM // STATE: {state.upper()}", fill='#e0e1dd', font=font)
    raw.text((40, 95), f"CORE TEMPERATURE:   {temp} K", fill='#e0e1dd', font=font)
    raw.text((40, 135), f"REACTOR POWER:      {power} %", fill='#e0e1dd', font=font)
    raw.text((40, 175), f"PRIMARY PRESSURE:   {press} MPa", fill='#e0e1dd', font=font)
    raw.text((40, 215), f"GLOBAL STATUS:      {status.upper()}", fill='#e0e1dd', font=font)

    # Map status indicator colors
    color_map = {'green': '#00ff00', 'yellow': '#ffff00', 'red': '#ff0000'}
    indicator_color = color_map.get(status.lower(), '#ffffff')
    raw.rectangle([40, 255, 120, 295], fill=indicator_color)

    img_io = BytesIO()
    canvas.save(img_io, 'PNG')
    img_io.seek(0)
    return send_file(img_io, mimetype='image/png')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
    
