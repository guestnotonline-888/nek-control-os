from flask import Flask, request, send_file
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont

app = Flask(__name__)

# 1. LIVE INTERACTIVE RETRO CRT INTERFACE
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
                background-color: #010402;
                color: #00ff33;
                font-family: 'Courier New', monospace;
                display: flex;
                justify-content: center;
                align-items: center;
                min-height: 100vh;
                margin: 0;
                padding: 15px;
                box-sizing: border-box;
            }
            .monitor {
                width: 100%;
                max-width: 460px;
                background-color: #030a04;
                border: 3px solid #0d2b12;
                border-radius: 10px;
                padding: 20px;
                box-shadow: 0 0 25px rgba(0, 255, 51, 0.12);
                position: relative;
            }
            /* CRT Scanline Effect Overlay */
            .monitor::after {
                content: " ";
                display: block;
                position: absolute;
                top: 0; left: 0; bottom: 0; right: 0;
                background: linear-gradient(rgba(18, 16, 16, 0) 50%, rgba(0, 0, 0, 0.2) 50%);
                background-size: 100% 4px;
                z-index: 10;
                pointer-events: none;
            }
            .header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                border-bottom: 2px solid #00ff33;
                padding-bottom: 6px;
                margin-bottom: 20px;
                font-size: 11px;
                font-weight: bold;
            }
            .status-led {
                width: 11px;
                height: 11px;
                background-color: #00ff33;
                border-radius: 50%;
                box-shadow: 0 0 8px #00ff33;
            }
            .title {
                font-size: 14px;
                font-weight: bold;
                margin-bottom: 22px;
                text-shadow: 0 0 3px #00ff33;
            }
            .gauge-block {
                margin-bottom: 18px;
            }
            .gauge-labels {
                display: flex;
                justify-content: space-between;
                font-size: 12px;
                margin-bottom: 6px;
            }
            .meter-container {
                border: 1px solid #00ff33;
                background: #000000;
                height: 24px;
                padding: 2px;
                box-sizing: border-box;
            }
            .meter-fill {
                background: repeating-linear-gradient(90deg, #00ff33, #00ff33 11px, transparent 11px, transparent 14px);
                height: 100%;
                width: 50%;
                transition: width 0.25s ease-in-out;
            }
            .summary-deck {
                display: flex;
                justify-content: space-around;
                border-top: 1px solid #0d2b12;
                margin-top: 25px;
                padding-top: 15px;
                text-align: center;
                font-size: 12px;
            }
            .nav-bench {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-top: 20px;
            }
            .btn-nav {
                background: #051407;
                border: 1px solid #00ff33;
                color: #00ff33;
                padding: 6px 12px;
                cursor: pointer;
                font-family: inherit;
                font-weight: bold;
            }
            .btn-nav:active { background: #00ff33; color: #030a04; }
            .bench-label {
                background: #09210d;
                padding: 6px;
                flex-grow: 1;
                text-align: center;
                margin: 0 10px;
                font-size: 12px;
                font-weight: bold;
            }
            .control-grid {
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 12px;
                margin-top: 18px;
            }
            .action-btn {
                background: #030a04;
                border: 1px solid #00ff33;
                color: #00ff33;
                padding: 12px;
                font-family: inherit;
                cursor: pointer;
                font-size: 11px;
                font-weight: bold;
            }
            .action-btn:active { background: #00ff33; color: #030a04; }
        </style>
    </head>
    <body>

    <div class="monitor">
        <div class="header">
            <span>TERMINAL v4.2 // SYS_STATUS:</span>
            <div class="status-led" id="ledAlert"></div>
        </div>

        <div class="title" id="panelTitle">> MAIN_DASHBOARD_OVERVIEW</div>

        <div class="gauge-block">
            <div class="gauge-labels"><span>CORE TEMPERATURE:</span><span id="valTemp">285 K</span></div>
            <div class="meter-container"><div class="meter-fill" id="barTemp" style="width: 25%;"></div></div>
        </div>

        <div class="gauge-block">
            <div class="gauge-labels"><span>REACTOR POWER:</span><span id="valPower">100%</span></div>
            <div class="meter-container"><div class="meter-fill" id="barPower" style="width: 66%;"></div></div>
        </div>

        <div class="gauge-block">
            <div class="gauge-labels"><span>PRIMARY PRESSURE:</span><span id="valPress">15.5 MPa</span></div>
            <div class="meter-container"><div class="meter-fill" id="barPress" style="width: 50%;"></div></div>
        </div>

        <div class="summary-deck">
            <div>
                <div style="color: #00a120; font-size: 11px; margin-bottom: 3px;">Core Temp</div>
                <span id="deckTemp">285 K</span>
            </div>
            <div>
                <div style="color: #00a120; font-size: 11px; margin-bottom: 3px;">Status</div>
                <span id="deckStatus" style="color: #00ff33;">GREEN</span>
            </div>
        </div>

        <div class="nav-bench">
            <button class="btn-nav" onclick="slidePanel(-1)">&lt;</button>
            <div class="bench-label" id="panelLabel">Main Dashboard</div>
            <button class="btn-nav" onclick="slidePanel(1)">&gt;</button>
        </div>

        <div class="control-grid">
            <button class="action-btn" onclick="addRods()">Adjust Rods (+ Temp)</button>
            <button class="action-btn" onclick="coolPumps()">Throttle Pumps (- Press)</button>
            <button class="action-btn" onclick="scram()" style="color: #ff3333; border-color: #ff3333;">EMERGENCY SCRAM</button>
            <button class="action-btn" onclick="clearSystem()">Reset System</button>
        </div>
    </div>

    <script>
        let currentTemp = 285;
        let currentPower = 100;
        let currentPress = 15.5;
        let activeIndex = 0;
        
        const benches = ["Main Dashboard", "Electrical Matrix", "Cooling Auxiliary"];

        function updateScreen() {
            if (currentTemp < 100) currentTemp = 100;
            if (currentPower < 0) currentPower = 0;
            if (currentPress < 0) currentPress = 0;

            let condition = "GREEN";
            let colorHex = "#00ff33";

            if (currentTemp >= 1000 || currentPress >= 25) {
                condition = "RED";
                colorHex = "#ff3333";
            } else if (currentTemp >= 450 || currentPress >= 19) {
                condition = "YELLOW";
                colorHex = "#ffff33";
            }

            document.getElementById("valTemp").innerText = currentTemp + " K";
            document.getElementById("deckTemp").innerText = currentTemp + " K";
            document.getElementById("valPower").innerText = currentPower + "%";
            document.getElementById("valPress").innerText = currentPress.toFixed(1) + " MPa";
            document.getElementById("deckStatus").innerText = condition;
            document.getElementById("deckStatus").style.color = colorHex;
            
            document.getElementById("ledAlert").style.backgroundColor = colorHex;
            document.getElementById("ledAlert").style.boxShadow = "0 0 8px " + colorHex;

            document.getElementById("barTemp").style.width = Math.min(((currentTemp - 100) / 1300) * 100, 100) + "%";
            document.getElementById("barPower").style.width = Math.min(currentPower, 100) + "%";
            document.getElementById("barPress").style.width = Math.min((currentPress / 30) * 100, 100) + "%";
        }

        function slidePanel(offset) {
            activeIndex = (activeIndex + offset + benches.length) % benches.length;
            document.getElementById("panelLabel").innerText = benches[activeIndex];
            document.getElementById("panelTitle").innerText = "> " + benches[activeIndex].toUpperCase().replace(" ", "_") + "_OVERVIEW";
        }

        function addRods() {
            currentTemp += 150;
            currentPower = Math.min(150, currentPower + 10);
            currentPress += 2.5;
            updateScreen();
        }

        function coolPumps() {
            currentPress = Math.max(1, currentPress - 3.0);
            currentTemp = Math.min(1500, currentTemp + 75);
            updateScreen();
        }

        function scram() {
            currentPower = 0;
            currentTemp = 110;
            currentPress = 3.5;
            updateScreen();
        }

        function clearSystem() {
            currentTemp = 285;
            currentPower = 100;
            currentPress = 15.5;
            updateScreen();
        }

        updateScreen();
    </script>
    </body>
    </html>
    '''

# 2. DYNAMIC BOT GRAPHICS ENGINE (Generates terminal screens dynamically)
@app.route('/api/screen', defaults={'state': 'MAIN', 'temp': '285', 'power': '100', 'press': '15.5', 'status': 'green'})
@app.route('/api/screen/<state>/<temp>/<power>/<press>/<status>.png')
@app.route('/<state>_<temp>_<power>_<press>_<status>.png')
def generate_render(state, temp, power, press, status):
    # Safe query parameters extraction fallback
    s_val = request.args.get('state', state).upper()
    t_val = request.args.get('temp', temp)
    p_val = request.args.get('power', power)
    pr_val = request.args.get('press', press)
    st_val = request.args.get('status', status).upper()

    # Generate Image Canvas
    img = Image.new('RGB', (480, 330), color='#030a04')
    draw = ImageDraw.Draw(img)
    
    # Render Retro Accents
    draw.rectangle([10, 10, 470, 320], outline='#0d2b12', width=2)
    draw.line([10, 42, 470, 42], fill='#00ff33', width=2)

    font = ImageFont.load_default()
    
    # Top Status Lights
    draw.text((20, 18), "TERMINAL v4.2 // SYS_STATUS:", fill='#00ff33', font=font)
    led_color = (0, 255, 51) if st_val == "GREEN" else ((255, 255, 51) if st_val == "YELLOW" else (255, 51, 51))
    draw.ellipse([445, 18, 457, 30], fill=led_color)

    # Header Panel Tracker
    draw.text((20, 60), f"> {s_val}_DASHBOARD_OVERVIEW", fill='#00ff33', font=font)
    
    # Calculations for Core progress block allocations
    try:
        t_pct = float(t_val.replace('K','').strip()) / 1500
        p_pct = float(p_val.replace('%','').strip()) / 100
        pr_pct = float(pr_val.replace('MPa','').strip()) / 30
    except:
        t_pct, p_pct, pr_pct = 0.25, 0.66, 0.50

    elements = [
        ("CORE TEMPERATURE:", f"{t_val} K", t_pct),
        ("REACTOR POWER:", f"{p_val}%", p_pct),
        ("PRIMARY PRESSURE:", f"{pr_val} MPa", pr_pct)
    ]
    
    y = 95
    for text_lbl, value_lbl, percent in elements:
        draw.text((20, y), f"{text_lbl} {value_lbl}", fill='#00ff33', font=font)
        draw.rectangle([20, y + 16, 450, y + 30], outline='#00ff33', fill='#000000')
        
        # Build segment blocks
        px_width = int(min(max(percent, 0), 1) * 426)
        for block in range(0, px_width, 14):
            if block + 10 <= px_width:
                draw.rectangle([22 + block, y + 18, 22 + block + 10, y + 28], fill='#00ff33')
        y += 55

    # Bottom Display Card Block
    draw.line([10, 275, 470, 275], fill='#0d2b12', width=1)
    draw.text((25, 292), f"Core Temp: {t_val} K", fill='#00ff33', font=font)
    draw.text((320, 292), f"Status: {st_val}", fill=led_color, font=font)

    byte_arr = BytesIO()
    img.save(byte_arr, 'PNG')
    byte_arr.seek(0)
    return send_file(byte_arr, mimetype='image/png')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
    
