#!/usr/bin/env python3
"""Build the main-menu lockup: Deadlock wheel + wordmark, with
"THE LIBRARY REREAD" set under the wordmark at the same width.

    python tools/make_logo.py

Input:  game/images/ui/deadlock_logo.png  (Valve's logo, git-ignored)
Fonts:  game/fonts/forevsdemo-bold.otf    (from the game files, git-ignored)
Output: game/images/ui/library_logo.png   (git-ignored)
"""
import os
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UI = os.path.join(ROOT, "game", "images", "ui")
FONT = os.path.join(ROOT, "game", "fonts", "forevsdemo-bold.otf")
SUBTITLE = "THE LIBRARY REREAD"
CREAM = (255, 241, 220, 255)

logo = Image.open(os.path.join(UI, "deadlock_logo.png")).convert("RGBA")
W, H = logo.size

# split the logo into the wheel and the wordmark (separated by an empty gap)
alpha = logo.split()[3]
cols = [alpha.crop((x, 0, x + 1, H)).getbbox() is not None for x in range(W)]
wheel_end = cols.index(False)
word_start = wheel_end + cols[wheel_end:].index(True)
wheel = logo.crop((0, 0, wheel_end, H))
word = logo.crop((word_start, 0, W, H))
word = word.crop(word.getbbox())
wheel = wheel.crop(wheel.getbbox())

# subtitle: letter-spaced so it spans exactly the wordmark width
target_w = word.width
font_px = int(word.height * 0.34)
font = ImageFont.truetype(FONT, font_px)

def width(spacing):
    return sum(font.getlength(ch) for ch in SUBTITLE) + spacing * (len(SUBTITLE) - 1)

spacing = (target_w - width(0)) / (len(SUBTITLE) - 1)
while spacing < 2 and font_px > 10:          # too long: shrink the font
    font_px -= 2
    font = ImageFont.truetype(FONT, font_px)
    spacing = (target_w - width(0)) / (len(SUBTITLE) - 1)

ascent, descent = font.getmetrics()
gap = int(word.height * 0.22)
rule_h = max(2, word.height // 60)
text_h = ascent
right_h = word.height + gap + rule_h + gap + text_h

# wheel spans the full height of both lines
wheel_h = right_h
wheel = wheel.resize((int(wheel.width * wheel_h / wheel.height), wheel_h), Image.LANCZOS)
pad = int(wheel_h * 0.16)

out = Image.new("RGBA", (wheel.width + pad + word.width, right_h), (0, 0, 0, 0))
out.alpha_composite(wheel, (0, 0))
x0 = wheel.width + pad
out.alpha_composite(word, (x0, 0))
d = ImageDraw.Draw(out)
y_rule = word.height + gap
d.rectangle((x0, y_rule, x0 + word.width, y_rule + rule_h - 1), fill=(255, 241, 220, 110))
x = x0
y_text = y_rule + rule_h + gap
for ch in SUBTITLE:
    d.text((x, y_text), ch, font=font, fill=CREAM)
    x += font.getlength(ch) + spacing

out.save(os.path.join(UI, "library_logo.png"))
print("library_logo.png", out.size)
