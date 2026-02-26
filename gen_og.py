from PIL import Image, ImageDraw, ImageFont

W, H = 1200, 630
img = Image.new('RGB', (W, H), '#0a1020')
draw = ImageDraw.Draw(img)

# Lighter background so text pops
for y in range(H):
    b = int(32 + (y/H)*20)
    draw.line([(0, y), (W, y)], fill=(10, 16, b))

# Top cyan bar
draw.rectangle([0, 0, W, 5], fill='#00d4ff')
# Bottom bar
draw.rectangle([0, H-5, W, H], fill='#00d4ff')

try:
    tf = ImageFont.truetype("C:/Windows/Fonts/consolab.ttf", 80)
    sf = ImageFont.truetype("C:/Windows/Fonts/consola.ttf", 30)
    df = ImageFont.truetype("C:/Windows/Fonts/segoeui.ttf", 24)
    bf = ImageFont.truetype("C:/Windows/Fonts/consolab.ttf", 20)
except:
    tf = sf = df = bf = ImageFont.load_default()

# Large A logo on left
cx, cy = 160, 310
# Glow circle behind
for r in range(80, 0, -2):
    alpha = int(6 * (80-r)/80)
    draw.ellipse([cx-r, cy-r, cx+r, cy+r], fill=(0, 50+alpha, 80+alpha))
# The A
draw.polygon([(cx-55, cy+65), (cx, cy-75), (cx+55, cy+65)], outline='#00d4ff', width=5)
draw.line([(cx-33, cy+20), (cx+33, cy+20)], fill='#00d4ff', width=3)
draw.ellipse([cx-6, cy+58, cx+6, cy+70], fill='#00ff88')

# Title - WHITE and BOLD for visibility
draw.text((280, 200), "ALPHA-OMEGA", fill='#ffffff', font=tf)
draw.text((280, 300), "AI TRADING SYSTEM", fill='#00d4ff', font=sf)
draw.text((280, 350), "Council of Experts  |  Multi-Agent Analysis", fill='#8899aa', font=df)

# Feature boxes with solid backgrounds
pills = [
    ("5-PILLAR SCORING", "#00ff88"),
    ("REAL-TIME DATA", "#00d4ff"),
    ("SWING SCAN v4.3", "#fbbf24"),
    ("TRADE PLANS", "#a78bfa"),
]
x = 280
for text, color in pills:
    tw = len(text) * 12 + 28
    draw.rounded_rectangle([x, 430, x+tw, 470], radius=6, fill='#0d1a2a', outline=color, width=2)
    draw.text((x+14, 438), text, fill=color, font=bf)
    x += tw + 14

# LIVE badge
draw.rounded_rectangle([1040, 20, 1150, 55], radius=8, fill='#00ff88')
draw.text((1060, 24), "● LIVE", fill='#000000', font=sf)

out = "C:\\Users\\asus\\Alpha-Omega-System\\frontend\\public\\og-image.png"
img.save(out, "PNG")
print("Done")
