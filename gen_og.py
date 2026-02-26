from PIL import Image, ImageDraw, ImageFont
import os

W, H = 1200, 630
img = Image.new('RGB', (W, H), '#080c14')
draw = ImageDraw.Draw(img)

# Background gradient effect (dark blue strips)
for y in range(H):
    r = int(8 + (y/H)*4)
    g = int(12 + (y/H)*6)
    b = int(20 + (y/H)*12)
    draw.line([(0, y), (W, y)], fill=(r, g, b))

# Border
draw.rectangle([0, 0, W-1, H-1], outline='#1a2535', width=2)

# Accent line at top
draw.rectangle([0, 0, W, 4], fill='#00d4ff')

# Title
try:
    title_font = ImageFont.truetype("C:/Windows/Fonts/consola.ttf", 56)
    sub_font = ImageFont.truetype("C:/Windows/Fonts/consola.ttf", 24)
    desc_font = ImageFont.truetype("C:/Windows/Fonts/segoeui.ttf", 22)
except:
    title_font = ImageFont.load_default()
    sub_font = title_font
    desc_font = title_font

# Logo triangle
pts = [(80, 340), (120, 260), (160, 340)]
draw.polygon(pts, outline='#00d4ff', width=3)
draw.ellipse([110, 320, 130, 340], fill='#00ff88')

# Title text
draw.text((190, 260), "ALPHA - OMEGA", fill='#e2e8f0', font=title_font)
draw.text((190, 330), "Council of Experts Trading System", fill='#4a6a7a', font=sub_font)

# Features
y_start = 420
features = [
    ("SwingTrader AI v4.3", "#00ff88"),
    ("5-Pillar Conviction Scoring", "#00d4ff"),
    ("Real-Time Market Data", "#fbbf24"),
    ("Multi-Agent Analysis", "#a78bfa"),
]
x = 80
for text, color in features:
    draw.rounded_rectangle([x, y_start, x+250, y_start+36], radius=4, fill='#0d1a2a', outline=color)
    draw.text((x+12, y_start+6), text, fill=color, font=desc_font)
    x += 270

# System online badge
draw.ellipse([1050, 30, 1060, 40], fill='#00ff88')
draw.text((1068, 26), "LIVE", fill='#00ff88', font=sub_font)

out = os.path.join("C:\\Users\\asus\\Alpha-Omega-System\\frontend\\public", "og-image.png")
img.save(out, "PNG")
print(f"Saved: {out}")
