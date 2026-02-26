from PIL import Image, ImageDraw, ImageFont
import os

W, H = 1200, 630
img = Image.new('RGB', (W, H), '#080c14')
draw = ImageDraw.Draw(img)

# Background gradient
for y in range(H):
    r = int(8 + (y/H)*5)
    g = int(12 + (y/H)*8)
    b = int(20 + (y/H)*16)
    draw.line([(0, y), (W, y)], fill=(r, g, b))

# Top accent bar
draw.rectangle([0, 0, W, 3], fill='#00d4ff')

# Grid lines (subtle)
for x in range(0, W, 60):
    draw.line([(x, 0), (x, H)], fill=(15, 25, 40), width=1)
for y in range(0, H, 60):
    draw.line([(0, y), (W, y)], fill=(15, 25, 40), width=1)

try:
    tf = ImageFont.truetype("C:/Windows/Fonts/consola.ttf", 72)
    sf = ImageFont.truetype("C:/Windows/Fonts/consola.ttf", 28)
    df = ImageFont.truetype("C:/Windows/Fonts/segoeui.ttf", 22)
    bf = ImageFont.truetype("C:/Windows/Fonts/consolab.ttf", 18)
except:
    tf = sf = df = bf = ImageFont.load_default()

# Big stylized A logo
cx, cy = 130, 300
draw.polygon([(cx-50, cy+60), (cx, cy-70), (cx+50, cy+60)], outline='#00d4ff', width=4)
draw.line([(cx-30, cy+20), (cx+30, cy+20)], fill='#00d4ff', width=3)
draw.ellipse([cx-5, cy+55, cx+5, cy+65], fill='#00ff88')

# Title
draw.text((220, 220), "ALPHA-OMEGA", fill='#e2e8f0', font=tf)
draw.text((220, 310), "Council of Experts Trading System", fill='#4a7a8a', font=sf)

# Divider
draw.line([(220, 380), (1000, 380)], fill='#1a3050', width=1)

# Feature pills
pills = [
    ("5-PILLAR SCORING", "#00ff88"),
    ("REAL-TIME DATA", "#00d4ff"),
    ("AI COUNCIL", "#a78bfa"),
    ("TRADE PLANS", "#fbbf24"),
]
x = 220
for text, color in pills:
    tw = len(text) * 11 + 24
    draw.rounded_rectangle([x, 410, x+tw, 448], radius=6, outline=color, width=1)
    draw.text((x+12, 416), text, fill=color, font=bf)
    x += tw + 16

# Version badge
draw.rounded_rectangle([220, 480, 400, 516], radius=4, fill='#0d2030')
draw.text((232, 486), "SwingTrader v4.3", fill='#00ff88', font=df)

# Live badge
draw.ellipse([1100, 30, 1112, 42], fill='#00ff88')
draw.text((1120, 26), "LIVE", fill='#00ff88', font=sf)

# Bottom bar
draw.rectangle([0, H-3, W, H], fill='#00d4ff')

out = "C:\\Users\\asus\\Alpha-Omega-System\\frontend\\public\\og-image.png"
img.save(out, "PNG", quality=95)
print(f"Saved {out}")
