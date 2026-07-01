from flask import Flask, send_file
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont

app = Flask(__name__)

# 1. Fully Interactive Web Terminal App Dashboard
@app.route('/')
def home():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Control Room Terminal v4.2</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body {
                background-color: #030708;
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
                max-width: 500px;
                background-color: #050f08;
                border: 4px solid #1a3a20;
                border-radius: 8px;
                padding: 20px;
                box-shadow: 0 0 25px rgba(0, 255, 51, 0.15);
                position: relative;
                overflow: hidden;
            }
            /* CRT Scanline overlay effect */
            .monitor::after {
                content: " ";
                display: block;
                position: absolute;
                top: 0; left: 0; bottom: 0; right: 0;
                background: linear-gradient(rgba(18, 16, 16, 0) 50%, rgba(0, 0, 0, 0.25) 50%), linear-gradient(90deg, rgba(255, 0, 0, 0.06), rgba(0, 255, 0, 0.02), rgba(0, 0, 255, 0.06));
                z-index: 2;
                background-size: 100% 4px, 6px 100%;
                pointer-events: none;
            }
            .header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                border-bottom: 2px solid #00ff33;
                padding-bottom: 8px;
                margin-bottom: 15px;
                font-size: 12px;
                font-weight: bold;
            }
            .status-dot {
                width: 12px;
                height: 12px;
                background-color: #00ff33;
                border-radius: 50%;
                display: inline-block;
                box-shadow: 0 0 8px #00ff33;
            }
            .title {
                font-size: 18px;
                font-weight: bold;
                margin: 15px 0;
                text-shadow: 0 0 4px #00ff33;
            }
            .metric-group {
                margin-bottom: 14px;
            }
            .metric-txt {
                display: flex;
                justify-content: space-between;
                font-size: 14px;
                margin-bottom: 4px;
            }
            .bar-bg {
                background: #020804;
                border: 1px solid #00ff33;
                height: 20px;
                position: relative;
            }
            .bar-fill {
                background: repeating-linear-gradient(90deg, #00ff33, #00ff33 8px, transparent 8px, transparent 12px);
                height: 100%;
                width: 50%;
                transition: width 0.3s ease;
            }
            .summary-box {
                display: flex;
                justify-content: space-around;
                border-top: 1px solid #1a3a20;
                margin-top: 20px;
                padding-top: 15px;
                text-align: center;
                font-size: 14px;
            }
            .nav-row {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-top: 20px;
            }
            .btn-nav {
                background: #102514;
                border: 1px solid #00ff33;
                color: #00ff33;
                padding: 6px 14px;
                cursor: pointer;
                font-family: inherit;
                font-weight: bold;
            }
            .btn-nav:active { background: #00ff33; color: #050f08; }
            .panel-name {
                background: #15301b;
                padding: 6px 20px;
                flex-grow: 1;
                text-align: center;
                margin: 0 10px;
                font-size: 13px;
                font-weight: bold;
            }
            .controls-grid {
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 10px;
                margin-top: 15px;
            }
            .btn-action {
                background: #050f08;
                border: 1px solid #00ff33;
                color: #00ff33;
                padding: 10px;
                font-family: inherit;
                cursor: pointer;
                font-size: 12px;
            }
            .btn-action:hover { background: #102514; }
            .btn-action:active { background: #00ff33; color: #050f08; }
        </style>
    </head>
    <body>

    <div class="monitor">
        <div class="header">
            <span>TERMINAL v4.2 // SYS_SYSTEM_STATUS:</span>
            <span class="status-dot" id="statusDot"></span>
        </div>

        <div class="title" id="panelTitle">> MAIN_DASHBOARD_OVERVIEW</div>

        <!-- Dynamic Control Gauges Component -->
        <div id="gaugeContainer">
            <div class="metric-group">
                <div class="metric-txt"><span>CORE TEMPERATURE:</span><span id="txtTemp">285 K</span></div>
                <div class="bar-bg"><div class="bar-fill" id="barTemp" style="width: 25%;"></div></div>
            </div>

            <div class="metric-group">
                <div class="metric-txt"><span>STORAGE BATTERY:</span><span id="txtBattery">100%</span></div>
                <div class="bar-bg"><div class="bar-fill" id="barBattery" style="width: 100%;"></div></div>
            </div>

            <div class="metric-group">
                <div class="metric-txt"><span>TURBINE SPEED:</span><span id="txtTurbine">1500 RPM</span></div>
                <div class="bar-bg"><div class="bar-fill" id="barTurbine" style="width: 60%;"></div></div>
            </div>

            <div class="metric-group">
                <div class="metric-txt"><span>PUMP THROTTLE:</span><span id="txtPump">50%</span></div>
                <div class="bar-bg"><div class="bar-fill" id="barPump" style="width: 50%;"></div></div>
            </div>
        </div>

        <div class="summary-box">
            <div>
                <div style="color: #888; font-size: 11px; margin-bottom:4px;">Core Temp</div>
                <span id="subTemp">285 K</span>
            </div>
            <div>
                <div style="color: #888; font-size: 11px; margin-bottom:4px;">Status</div>
                <span id="subStatus" style="color: #00ff33;">GREEN</span>
            </div>
        </div>

        <!-- Clickable Navigation Row -->
        <div class="nav-row">
            <button class="btn-nav" onclick="cyclePanel(-1)">&lt;</button>
            <div class="panel-name" id="currentTabLabel">Main Dashboard</div>
            <button class="btn-nav" onclick="cyclePanel(1)">&gt;</button>
        </div>

        <!-- Clickable Interactive System Adjustments -->
        <div class="controls-grid">
            <button class="btn-action" onclick="adjustCore(25)">Adjust Rods (+ Temp)</button>
            <button class="btn-action" onclick="throttlePumps(10)">Throttle Pumps (+ Speed)</button>
            <button class="btn-action" onclick="triggerScram()" style="color: #ff3333; border-color: #ff3333;">EMERGENCY SCRAM</button>
            <button class="btn-action" onclick="resetSystem()">Reset System</button>
        </div>
    </div>

    <script>
        // Reactive App Simulation States
        let coreTemp = 285;
        let battery = 100;
        let turbine = 1500;
        let pumpThrottle = 50;
        let globalStatus = "GREEN";
        
        let activeTab = 0;
        const tabs = ["Main Dashboard", "Electrical Matrix", "Cooling Auxiliary"];

        function updateUI() {
            // Limits variables
            if(coreTemp < 0) coreTemp = 0;
            if(turbine < 0) turbine = 0;

            // Compute safety states based on heat thresholds
            if (coreTemp >= 450) {
                globalStatus = "RED";
                document.getElementById('subStatus').style.color = '#ff3333';
                document.getElementById('statusDot').style.backgroundColor = '#ff3333';
                document.getElementById('statusDot').style.boxShadow = '0 0 8px #ff3333';
            } else if (coreTemp >= 360) {
                globalStatus = "YELLOW";
                document.getElementById('subStatus').style.color = '#ffff33';
                document.getElementById('statusDot').style.backgroundColor = '#ffff33';
                document.getElementById('statusDot').style.boxShadow = '0 0 8px #ffff33';
            } else {
                globalStatus = "GREEN";
                document.getElementById('subStatus').style.color = '#00ff33';
                document.getElementById('statusDot').style.backgroundColor = '#00ff33';
                document.getElementById('statusDot').style.boxShadow = '0 0 8px #00ff33';
            }

            // Update Text Nodes
            document.getElementById('txtTemp').innerText = coreTemp + " K";
            document.getElementById('subTemp').innerText = coreTemp + " K";
            document.getElementById('txtBattery').innerText = battery + "%";
            document.getElementById('txtTurbine').innerText = turbine + " RPM";
            document.getElementById('txtPump').innerText = pumpThrottle + "%";
            document.getElementById('subStatus').innerText = globalStatus;

            // Map variables cleanly to graphical segment bar fills
            document.getElementById('barTemp').style.width = Math.min((coreTemp / 600) * 100, 100) + "%";
            document.getElementById('barBattery').style.width = battery + "%";
            document.getElementById('barTurbine').style.width = Math.min((turbine / 2500) * 100, 100) + "%";
            document.getElementById('barPump').style.width = pumpThrottle + "%";
        }

        function cyclePanel(direction) {
            activeTab = (activeTab + direction + tabs.length) % tabs.length;
            document.getElementById('currentTabLabel').innerText = tabs[activeTab];
            document.getElementById('panelTitle').innerText = "> " + tabs[activeTab].toUpperCase().replace(" ", "_") + "_OVERVIEW";
        }

        function adjustCore(amount) {
            coreTemp += amount;
            battery = Math.max(0, battery - 5);
            updateUI();
        }

        function throttlePumps(amount) {
            pumpThrottle = Math.min(100, pumpThrottle + 5);
            turbine += 150;
            coreTemp = Math.max(100, coreTemp - 15);
            updateUI();
        }

        function triggerScram() {
            coreTemp = 120;
            turbine = 0;
            pumpThrottle = 100;
            battery = 45;
            updateUI();
        }

        function resetSystem() {
            coreTemp = 285;
            battery = 100;
            turbine = 1500;
            pumpThrottle = 50;
            updateUI();
        }
    </script>
    </body>
    </html>
    '''

# 2. Keep image engine route safe and completely intact behind the scenes
@app.route('/<state>_<temp>_<power>_<press>_<status>.png')
def draw_screen(state, temp, power, press, status):
    canvas = Image.new('RGB', (600, 350), color='#0d1b2a')
    raw = ImageDraw.Draw(canvas)
    raw.rectangle([15, 15, 585, 335], outline='#415a77', width=3)
    raw.line([15, 65, 585, 65], fill='#415a77', width=2)

    font = ImageFont.load_default()
    raw.text((35, 30), f"SYSTEM CONTROL OPERATING SYSTEM // STATE: {state.upper()}", fill='#e0e1dd', font=font)
    raw.text((40, 95), f"CORE TEMPERATURE:   {temp} K", fill='#e0e1dd', font=font)
    raw.text((40, 135), f"REACTOR POWER:      {power} %", fill='#e0e1dd', font=font)
    raw.text((40, 175), f"PRIMARY PRESSURE:   {press} MPa", fill='#e0e1dd', font=font)
    raw.text((40, 215), f"GLOBAL STATUS:      {status.upper()}", fill='#e0e1dd', font=font)

    color_map = {'green': '#00ff00', 'yellow': '#ffff00', 'red': '#ff0000'}
    raw.rectangle([40, 255, 120, 295], fill=color_map.get(status.lower(), '#ffffff'))

    img_io = BytesIO()
    canvas.save(img_io, 'PNG')
    img_io.seek(0)
    return send_file(img_io, mimetype='image/png')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
    
