from flask import Flask, request, send_file
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont

app = Flask(__name__)

# 1. RETRO CRT WEB INTERFACE WITH REACTIVE DATA BENCHES
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
                padding: 6px 14px;
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

        <div id="gaugesContainer"></div>

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
        // Centralized core simulator variables shared across layout pages
        let state = {
            temp: 285,
            power: 100,
            press: 15.5,
            battery: 100,
            turbine: 1500,
            throttle: 50
        };
        
        let activeIndex = 0;

        function getPanelStructure() {
            return {
                0: {
                    title: "MAIN_DASHBOARD_OVERVIEW",
                    label: "Main Dashboard",
                    metrics: [
                        { name: "CORE TEMPERATURE", val: state.temp, unit: " K", max: 1500 },
                        { name: "REACTOR POWER", val: state.power, unit: "%", max: 100 },
                        { name: "PRIMARY PRESSURE", val: state.press, unit: " MPa", max: 30 }
                    ]
                },
                1: {
                    title: "ELECTRICAL_MATRIX_OVERVIEW",
                    label: "Electrical Matrix",
                    metrics: [
                        { name: "STORAGE BATTERY", val: state.battery, unit: "%", max: 100 },
                        { name: "TURBINE SPEED", val: state.turbine, unit: " RPM", max: 10000 }
                    ]
                },
                2: {
                    title: "COOLING_AUXILIARY_OVERVIEW",
                    label: "Cooling Auxiliary",
                    metrics: [
                        { name: "CORE TEMPERATURE", val: state.temp, unit: " K", max: 1500 },
                        { name: "STORAGE BATTERY", val: state.battery, unit: "%", max: 100 },
                        { name: "TURBINE SPEED", val: state.turbine, unit: " RPM", max: 10000 },
                        { name: "PUMP THROTTLE", val: state.throttle, unit: "%", max: 100 }
                    ]
                }
            };
        }

        function renderPanel() {
            const currentPanel = getPanelStructure()[activeIndex];
            document.getElementById("panelLabel").innerText = currentPanel.label;
            document.getElementById("panelTitle").innerText = "> " + currentPanel.title;
            
            let htmlStr = "";
            currentPanel.metrics.forEach(m => {
                let pct = (m.val / m.max) * 100;
                pct = Math.min(Math.max(pct, 0), 100);
                
                htmlStr += `
                <div class="gauge-block">
                    <div class="gauge-labels">
                        <span>${m.name}:</span>
                        <span>${m.val.toFixed(m.unit.includes('MPa') ? 1 : 0)}${m.unit}</span>
                    </div>
                    <div class="meter-container">
                        <div class="meter-fill" style="width: ${pct}%;"></div>
                    </div>
                </div>
                `;
            });
            document.getElementById("gaugesContainer").innerHTML = htmlStr;
            
            // Global Safety Alerts Checks
            document.getElementById("deckTemp").innerText = Math.round(state.temp) + " K";
            let alertCondition = "GREEN";
            let alertColor = "#00ff33";
            
            if (state.temp >= 1200 || state.press >= 26) {
                alertCondition = "RED";
                alertColor = "#ff3333";
            } else if (state.temp >= 450 || state.press >= 20) {
                alertCondition = "YELLOW";
                alertColor = "#ffff33";
            }
            
            document.getElementById("deckStatus").innerText = alertCondition;
            document.getElementById("deckStatus").style.color = alertColor;
            document.getElementById("ledAlert").style.backgroundColor = alertColor;
            document.getElementById("ledAlert").style.boxShadow = "0 0 8px " + alertColor;
        }

        function slidePanel(offset) {
            activeIndex = (activeIndex + offset + 3) % 3;
            renderPanel();
        }

        function addRods() {
            state.temp = Math.min(1500, state.temp + 150);
            state.power = Math.min(130, state.power + 10);
            state.press = Math.min(30, state.press + 2.5);
            state.turbine = Math.min(10000, state.turbine + 1650);
            state.battery = Math.max(0, state.battery - 15);
            renderPanel();
        }

        function coolPumps() {
            state.press = Math.max(1, state.press - 3.5);
            state.throttle = Math.min(100, state.throttle + 15);
            state.temp = Math.min(1500, state.temp + 60);
            state.turbine = Math.min(10000, state.turbine + 400);
            renderPanel();
        }

        function scram() {
            state.power = 0;
            state.temp = 110;
            state.press = 3.2;
            state.turbine = 0;
            state.throttle = 100;
            renderPanel();
        }

        function clearSystem() {
            state.temp = 285;
            state.power = 100;
            state.press = 15.5;
            state.battery = 100;
            state.turbine = 1500;
            state.throttle = 50;
            renderPanel();
        }

        renderPanel();
    </script>
    </body>
    </html>
    '''

# 2. BOT IMAGING API (Parses all standard path parameters and query strings smoothly)
@app.route('/api/screen', defaults={'state': 'MAIN', 'temp': '285', 'power': '100', 'press': '15.5', 'status': 'green'})
@app.route('/api/screen/<state>/<temp>/<power>/<press>/<status>.png')
@app.route('/<state>_<temp>_<power>_<press>_<status>.png')
def generate_render(state, temp, power, press, status):
    s_val = request.args.get('state', state).upper()
    t_val = request.args.get('temp', temp)
    p_val = request.args.get('power', power)
    pr_val = request.args.get('press', press)
    st_val = request.args.get('status', status).upper()

    img = Image.new('RGB', (480, 330), color='#030a04')
    draw = ImageDraw.Draw(img)
    
    draw.rectangle([10, 10, 470, 320], outline='#0d2b12', width=2)
    draw.line([10, 42, 470, 42], fill='#00ff33', width=2)

    font = ImageFont.load_default()
    
    draw.text((20, 18), "TERMINAL v4.2 // SYS_STATUS:", fill='#00ff33', font=font)
    led_color = (0, 255, 51) if st_val in ["GREEN", "OK"] else ((255, 255, 51) if st_val == "YELLOW" else (255, 51, 51))
    draw.ellipse([445, 18, 457, 30], fill=led_color)

    draw.text((20, 60), f"> {s_val}_DASHBOARD_OVERVIEW", fill='#00ff33', font=font)
    
    # Auto-adjust labels if target is explicitly cooling systems or main systems
    if "COOLING" in s_val or "ELECTRICAL" in s_val:
        elements = [
            ("CORE TEMPERATURE:", f"{t_val} K", 0.3),
            ("STORAGE BATTERY:", f"{p_val if '%' in p_val else '100%'}", 0.8),
            ("TURBINE SPEED:", f"{press if 'RPM' in str(press) else '1500 RPM'}", 0.2),
            ("PUMP THROTTLE:", "50%", 0.5)
        ]
    else:
        try:
            t_pct = float(t_val.replace('K','').strip()) / 1500
            p_pct = float(p_val.replace('%','').strip()) / 100
            pr_pct = float(pr_val.replace('MPa','').strip()) / 30
        except:
            t_pct, p_pct, pr_pct = 0.25, 1.0, 0.5
            
        elements = [
            ("CORE TEMPERATURE:", f"{t_val if 'K' in t_val else t_val + ' K'}", t_pct),
            ("REACTOR POWER:", f"{p_val if '%' in p_val else p_val + '%'}", p_pct),
            ("PRIMARY PRESSURE:", f"{pr_val if 'MPa' in pr_val else pr_val + ' MPa'}", pr_pct)
        ]
        
    y = 95
    for text_lbl, value_lbl, percent in elements:
        draw.text((20, y), f"{text_lbl} {value_lbl}", fill='#00ff33', font=font)
        draw.rectangle([20, y + 16, 450, y + 30], outline='#00ff33', fill='#000000')
        
        px_width = int(min(max(percent, 0), 1) * 426)
        for block in range(0, px_width, 14):
            if block + 10 <= px_width:
                draw.rectangle([22 + block, y + 18, 22 + block + 10, y + 28], fill='#00ff33')
        y += 50 if len(elements) == 4 else 55

    draw.line([10, 275, 470, 275], fill='#0d2b12', width=1)
    draw.text((25, 292), f"Core Temp: {t_val if 'K' in t_val else t_val + ' K'}", fill='#00ff33', font=font)
    draw.text((320, 292), f"Status: {st_val}", fill=led_color, font=font)

    byte_arr = BytesIO()
    img.save(byte_arr, 'PNG')
    byte_arr.seek(0)
    return send_file(byte_arr, mimetype='image/png')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
            
