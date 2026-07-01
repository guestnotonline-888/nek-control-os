from flask import Flask, send_file
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont

app = Flask(__name__)

@app.route('/')
def home():
    return "<h2>NEK-CONTROL SYSTEM: Graphics Engine Online!</h2>"

# Disguised Route: Looks like a single image file to bypass chat firewalls
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
    
