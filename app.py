from flask import Flask, request, send_file
from PIL import Image, ImageDraw, ImageFont
import io

app = Flask(__name__)

@app.route('/api/screen')
def render_terminal():
    # 1. Grab live game parameters out of the JanitorAI URL
    state = request.args.get('state', 'MAIN').upper()
    temp = request.args.get('temp', '285')
    power = request.args.get('power', '100')
    press = request.args.get('press', '15.5')
    status = request.args.get('status', 'green').lower()

    # 2. Create a clean, retro 600x350 dark-slate canvas
    canvas = Image.new('RGB', (600, 350), color='#0d1117')
    draw = ImageDraw.Draw(canvas)
    
    # Load standard text font styling
    font = ImageFont.load_default()

    # 3. Draw the Outer Industrial Terminal Frame
    draw.rectangle([10, 10, 590, 340], outline='#30363d', width=3)
    draw.line([10, 50, 590, 50], fill='#30363d', width=2)

    # 4. Handle the Global Status Indicator Block (Green, Yellow, Red)
    status_colors = {'green': '#4af626', 'yellow': '#ffeb3b', 'red': '#f44336'}
    active_color = status_colors.get(status, '#4af626')
    
    # Draw the illuminated status alert lens at the top right
    draw.text((20, 20), f"[NEK-CONTROL MONITOR v5.0 // {state}]", fill='#ffffff', font=font)
    draw.rectangle([480, 18, 575, 42], fill=active_color)
    draw.text((495, 23), f"SYS: {status.upper()}", fill='#000000', font=font)

    # 5. Populate Data Readouts Depending on the Active Panel View
    if state == "MAIN":
        draw.text((40, 90),  f"CORE THERMAL POWER :  {power}%", fill='#c9d1d9', font=font)
        draw.text((40, 130), f"CORE COOLANT TEMP  :  {temp} C", fill='#ffffff' if status == 'green' else active_color, font=font)
        draw.text((40, 170), f"PRIMARY PRESSURE   :  {press} MPa", fill='#c9d1d9', font=font)
        draw.text((40, 210), f"TURBINE VELOCITY   :  1500 RPM", fill='#c9d1d9', font=font)
        
        # Bottom Prompt Area
        draw.line([10, 270, 590, 270], fill='#30363d', width=2)
        draw.text((20, 290), "> MAIN CONSOLE ACTIVE. AWAITING PINPAD SELECTION...", fill='#8b949e', font=font)

    elif state == "REACTIVITY":
        draw.text((40, 90),  "[SUB-SYSTEM: REACTIVITY CONTROL BENCH]", fill='#ffeb3b', font=font)
        draw.text((40, 140), f"CONTROL ROD DEPTH  : 110 STEPS", fill='#c9d1d9', font=font)
        draw.text((40, 180), f"FLUX AXIAL BALANCE : 0.01 NOMINAL", fill='#c9d1d9', font=font)
        draw.text((20, 290), "> KEYS: [1] WITHDRAW, [2] INSERT, [B] BACK", fill='#8b949e', font=font)

    elif state == "COOLING":
        draw.text((40, 90),  "[SUB-SYSTEM: PRIMARY COOLING RACK]", fill='#2196f3', font=font)
        draw.text((40, 140), f"FEEDWATER PUMP 1   : ON (50% THROTTLE)", fill='#c9d1d9', font=font)
        draw.text((40, 180), f"CORE CORE VOIDING  : 0.00% SUBCOOLED", fill='#c9d1d9', font=font)
        draw.text((20, 290), "> KEYS: [1] PUMP UP, [2] PUMP DOWN, [B] BACK", fill='#8b949e', font=font)

    # 6. Stream the PNG image back to the user's chat window
    img_io = io.BytesIO()
    canvas.save(img_io, 'PNG')
    img_io.seek(0)
    return send_file(img_io, mimetype='image/png')
      
