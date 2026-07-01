from flask import Flask, request, send_file
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont

app = Flask(__name__)

# 1. Main Home Route (Prevents the 404 error on your main link)
@app.route('/')
def home():
    return "<h2>NEK-CONTROL SYSTEM: Graphics Engine is Online!</h2><p>Use /api/screen to load the terminal display.</p>"

# 2. Dynamic Image Generator Route
@app.route('/api/screen')
def draw_screen():
    # Fetch parameters from the chat link
    state = request.args.get('state', 'MAIN')
    temp = request.args.get('temp', '285')
    power = request.args.get('power', '100')
    press = request.args.get('press', '15.5')
    status = request.args.get('status', 'green')

    # Create a clean, retro 600x350 dark-slate canvas
    canvas = Image.new('RGB', (600, 350), color='#0d1b2a')
    raw = ImageDraw.Draw(canvas)

    # Draw retro terminal frame lines
    raw.rectangle([15, 15, 585, 335], outline='#415a77', width=3)
    raw.line([15, 65, 585, 65], fill='#415a77', width=2)

    # Fallback to default engine font
    font = ImageFont.load_default()

    # Draw text values onto the display panel
    raw.text((35, 30), f"SYSTEM CONTROL OPERATING SYSTEM // STATE: {state}", fill='#e0e1dd', font=font)
    raw.text((40, 95), f"CORE TEMPERATURE:   {temp} K", fill='#e0e1dd', font=font)
    raw.text((40, 135), f"REACTOR POWER:      {power} %", fill='#e0e1dd', font=font)
    raw.text((40, 175), f"PRIMARY PRESSURE:   {press} MPa", fill='#e0e1dd', font=font)
    raw.text((40, 215), f"GLOBAL STATUS:      {status.upper()}", fill='#e0e1dd', font=font)

    # Map status indicator colors
    color_map = {'green': '#00ff00', 'yellow': '#ffff00', 'red': '#ff0000'}
    indicator_color = color_map.get(status.lower(), '#ffffff')
    raw.rectangle([40, 255, 120, 295], fill=indicator_color)

    # Output image bytes directly to browser
    img_io = BytesIO()
    canvas.save(img_io, 'PNG')
    img_io.seek(0)
    return send_file(img_io, mimetype='image/png')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
    
