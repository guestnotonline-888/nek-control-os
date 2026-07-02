from flask import Flask, render_file, request, send_file
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont

app = Flask(__name__)

# 1. LIVE INTERACTIVE CRT TERMINAL (Root Dashboard)
@app.route('/')
def home():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>NEK-Control-OS Terminal</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body {
                background-color: #020503;
                color: #00ff33;
                font-family: 'Courier New', monospace;
                display: flex;
                justify-content: center;
                align-items: center;
                min-height: 100vh;
                margin: 0;
                padding: 12px;
                box-sizing: border-box;
            }
            .monitor {
                width: 100%;
                max-width: 480px;
                background-color: #040d06;
                border: 3px solid #143518;
                border-radius: 12px;
                padding: 18px;
                box-shadow: 0 0 30px rgba(0, 255, 51, 0.15);
                position: relative;
                overflow: hidden;
            }
            .monitor::after {
                content: " ";
                display: block;
                position: absolute;
                top: 0; left: 0; bottom: 0; right: 0;
                background: linear-gradient(rgba(18, 16, 16, 0) 50%, rgba(0, 0, 0, 0.25) 50%);
                background-size: 100% 4px;
                z-index: 5;
                pointer-events: none;
            }
            .header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                border-bottom: 2px solid #00ff33;
                padding-bottom: 8px;
                margin-bottom: 18px;
                font-size: 12px;
                font-weight: bold;
            }
            .status-led {
                width: 12px;
                height: 12px;
                background-color: #00ff33;
                border-radius: 50%;
                box-shadow: 0 0 8px #00ff33;
                display: inline-block;
            }
            .title {
                font-size: 15px;
                font-weight: bold;
                margin-bottom: 20px;
                text-shadow: 0 0 4px #00ff33;
            }
            .gauge-set {
                margin-bottom: 16px;
            }
            .gauge-info {
                display: flex;
                justify-content: space-between;
                font-size: 13px;
                margin-bottom: 5px;
            }
            .meter-frame {
                border: 1px solid #00ff33;
                background: #010402;
                height: 22px;
            }
            .meter-blocks {
                background: repeating-linear-gradient(90deg, #00ff33, #00ff33 10px, transparent 10px, transparent 14px);
                height: 100%;
                width: 50%;
                transition: width 0.3s ease-in-out;
            }
            .summary-deck {
                display: flex;
                justify-content: space-around;
                border-top: 1px solid #143518;
                margin-top: 22px;
                padding-top: 14px;
                text-align: center;
                font-size: 13px;
            }
            .nav-pill {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-top: 18px;
            }
            .btn-nav {
                background: #0a1c0d;
                border: 1px solid #00ff33;
                color: #00ff33;
                padding: 6px 14px;
                cursor: pointer;
                font-family: inherit;
                font-weight: bold;
            }
            .btn-nav:active { background: #00ff33; color: #040d06; }
            .pill-label {
                background: #112e16;
                padding: 6px 15px;
                flex-grow: 1;
                text-align: center;
                margin: 0 8px;
                font-size: 13px;
                font-weight: bold;
            }
            .btn-grid {
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 10px;
                margin-top: 15px;
            }
            .control-btn {
                background: #040d06;
                border: 1px solid #00ff33;
                color: #00ff33;
                padding: 12px;
                font-family: inherit;
                cursor: pointer;
                font-size: 12px;
                font-weight: bold;
            }
            .control-btn:active { background: #00ff33; color: #040d06; }
        </style>
    </head>
    <body>

    <div class="monitor">
        <div class="header">
            <span>TERMINAL v4.2 // SYS_SYSTEM_STATUS:</span>
            <span class="status-led" id="ledStatus"></span>
        </div>

        <div class="title" id="panelTitle">> MAIN_DASHBOARD_OVERVIEW</div>

        <div class="gauge-set">
            <div class="gauge-info"><span>CORE TEMPERATURE:</span><span id="txtTemp">285 K</span></div>
            <div class="meter-frame"><div class="meter-blocks" id="barTemp" style="width: 25%;"></div></div>
        </div>

        <div class="gauge-set">
            <div class="gauge-info"><span>REACTOR POWER:</span><span id="txtPower">100%</span></div>
            <div class="meter-frame"><div class="meter-blocks" id="barPower" style="width: 66%;"></div></div>
        </div>

        <div class="gauge-set">
            <div class="gauge-info"><span>PRIMARY PRESSURE:</span><span id="txtPress">15.5 MPa</span></div>
            <div class="meter-frame"><div class="meter-blocks" id="barPress" style="width: 50%;"></div></div>
        </div>

        <div class="summary-deck">
            <div>
                <div style="color: #00aa22; font-size: 11px; margin-bottom: 2px;">Core Temp</div>
                <span id="deckTemp">285 K</span>
            </div>
            <div>
                <div style="color: #00aa22; font-size: 11px; margin-bottom: 2px;">Status</div>
                <span id="deckStatus" style="color: #00ff33;">GREEN</span>
            </div>
        </div>

        <div class="nav-pill">
            <button class="btn-nav" onclick="changePanel(-1)">&lt;</button>
            <div class="pill-label" id="panelLabel">Main Dashboard</div>
            <button class="btn-nav" onclick="changePanel(1)">&gt;</button>
        </div>

        <div class="btn-grid">
            <button class="control-btn" onclick="adjustRods()">Adjust Rods (+ Temp)</button>
            <button class="control-btn" onclick="throttlePumps()">Throttle Pumps (- Press)</button>
            <button class="control-btn" onclick="triggerScram()" style="color: #ff3333; border-color: #ff3333;">EMERGENCY SCRAM</button>
            <button class="control-btn" onclick="resetSystem()">Reset System</button>
        </div>
    </div>

    <script>
        // System parameter states
        let temp = 285;
        let power = 100;
        let press = 15.5;
        let activeTab = 0;
        
        const tabs = ["Main Dashboard", "Electrical Matrix", "Cooling Auxiliary"];

        function refreshUI() {
            // Keep parameters properly bounded
            if (temp < 100) temp = 100;
            if (power < 0) power = 0;
            if (press < 0) press = 0;

            let status = "GREEN";
            let color = "#00ff33";

            if (temp >= 1000 || press >= 25) {
                status = "RED";
                color = "#ff3333";
            } else if (temp >= 450 || press >= 19) {
                status = "YELLOW";
                color = "#ffff33";
            }

            // Text nodes
            document.getElementById("txtTemp").innerText = temp + " K";
            document.getElementById("deckTemp").innerText = temp + " K";
            document.getElementById("txtPower").innerText = power + "%";
            document.getElementById("txtPress").innerText = press.toFixed(1) + " MPa";
            document.getElementById("deckStatus").innerText = status;
            document.getElementById("deckStatus").style.color = color;
            
            // LED alert node
            document.getElementById("ledStatus").style.backgroundColor = color;
            document.getElementById("ledStatus").style.boxShadow = "0 0 8px " + color;

            // Bar mappings
            document.getElementById("barTemp").style.width = Math.min(((temp - 100) / 1300) * 100, 100) + "%";
            document.getElementById("barPower").style.width = Math.min(power, 100) + "%";
            document.getElementById("barPress").style.width = Math.min((press / 30) * 100, 100) + "%";
        }

        function changePanel(dir) {
            activeTab = (activeTab + dir + tabs.length) % tabs.length;
            document.getElementById("panelLabel").innerText = tabs[activeTab];
            document.getElementById("panelTitle").innerText = "> " + tabs[activeTab].toUpperCase().replace(" ", "_") + "_OVERVIEW";
        }

        function adjustRods() {
            temp += 150;
            power = Math.min(150, power + 15);
            press += 2.2;
            refreshUI();
        }

        function throttlePumps() {
            press = Math.max(2, press - 3.5);
            temp = Math.min(1400, temp + 80);
            refreshUI();
        }

        function triggerScram() {
            power = 0;
            temp = 120;
            press = 4.0;
            refreshUI();
        }

        function resetSystem() {
            temp = 285;
            power = 100;
            press = 15.5;
            refreshUI();
        }

        refreshUI();
    </script>
    </body>
    </html>
    '''

# 2. COMPREHENSIVE BOT IMAGE GENERATOR ENDPOINT
# Merges all parsed URL variations (?temp=X or /api/screen/MAIN/285/...) into the green CRT design
@app.route('/api/screen', defaults={'state': 'MAIN', 'temp': '285', 'power': '100', 'press': '15.5', 'status': 'green'})
@app.route('/api/screen/<state>/<temp>/<power>/<press>/<status>.png')
@app.route('/<state>_<temp>_<power>_<press>_<status>.png')
def draw_screen(state, temp, power, press, status):
    # Support both explicit URL paths and query parameters gracefully
    state_param = request.args.get('state', state).upper()
    temp_param = request.args.get('temp', temp)
    power_param = request.args.get('power', power)
    press_param = request.args.get('press', press)
    status_param = request.args.get('status', status).upper()

    # Create solid display base matching terminal color space
    canvas = Image.new('RGB', (500, 340), color='#040d06')
    raw = ImageDraw.Draw(canvas)
    
    # Outer Monitor Border lines
    raw.rectangle([10, 10, 490, 330], outline='#143518', width=3)
    raw.line([10, 45, 490, 45], fill='#00ff33', width=2)

    font = ImageFont.load_default()
    
    # Header Status Layout
    raw.text((20, 20), f"TERMINAL v4.2 // SYS_STATUS:", fill='#00ff33', font=font)
    alert_color = (0, 255, 51) if status_param == "GREEN" else ((255, 255, 51) if status_param == "YELLOW" else (255, 51, 51))
    raw.ellipse([460, 20, 474, 34], fill=alert_color)

    # Core Panel System Text
    raw.text((20, 65), f"> {state_param}_DASHBOARD_OVERVIEW", fill='#00ff33', font=font)
    
    # Render Metrics with matching drawn graphic blocks
    metrics = [
        ("CORE TEMPERATURE:", f"{temp_param} K", float(temp_param.replace('K','').strip()) / 1500),
        ("REACTOR POWER:", f"{power_param}%", float(power_param.replace('%','').strip()) / 150),
        ("PRIMARY PRESSURE:", f"{press_param} MPa", float(press_param.replace('MPa','').strip()) / 30)
    ]
    
    y_cursor = 100
    for label, val_str, pct in metrics:
        raw.text((20, y_cursor), f"{label} {val_str}", fill='#00ff33', font=font)
        # Draw background track
        raw.rectangle([20, y_cursor + 18, 470, y_cursor + 32], outline='#00ff33', fill='#010402')
        
        # Fill chunks incrementally to replicate retro segments
        fill_width = int(min(max(pct, 0), 1) * 440)
        for step in range(0, fill_width, 14):
            if step + 10 <= fill_width:
                raw.rectangle([21 + step, y_cursor + 20, 21 + step + 10, y_cursor + 30], fill='#00ff33')
        y_cursor += 55

    # Bottom Footer Card
    raw.line([10, 280, 490, 280], fill='#143518', width=1)
    raw.text((30, 298), f"Core Temp: {temp_param} K", fill='#00ff33', font=font)
    raw.text((320, 298), f"Status: {status_param}", fill=alert_color, font=font)

    img_io = BytesIO()
    canvas.save(img_io, 'PNG')
    img_io.seek(0)
    return send_file(img_io, mimetype='image/png')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
                              
