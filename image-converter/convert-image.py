# Converts any picture into image.jpg for the CYD screen.
# Usage: drag a picture onto "Drop picture here.bat", or run:
#   python convert-image.py my_photo.png

# ======================= SETTINGS (edit these) =======================
FILL_SCREEN = True    # True = crop edges to fill the screen. False = add black bars.
COLOR_BOOST = 1.2     # 1.0 = unchanged. Higher = more vivid (helps on this screen).
CONTRAST    = 1.1     # 1.0 = unchanged.
# =====================================================================

import sys
from io import BytesIO
from pathlib import Path
from PIL import Image, ImageEnhance, ImageOps

OUTPUT_FILE = Path(__file__).resolve().parent.parent / "image.jpg"  # image.jpg in the repo
SCREEN = (320, 240)
MAX_BYTES = 50_000

img = Image.open(sys.argv[1])
img = ImageOps.exif_transpose(img)          # Phone photos: fix sideways pictures
if img.mode != "RGB":                        # Transparent PNGs get a black background
    img = img.convert("RGBA")
    background = Image.new("RGB", img.size, (0, 0, 0))
    background.paste(img, mask=img.getchannel("A"))
    img = background

if FILL_SCREEN:
    img = ImageOps.fit(img, SCREEN, Image.LANCZOS)
else:
    img = ImageOps.pad(img, SCREEN, Image.LANCZOS, color=(0, 0, 0))

img = ImageEnhance.Color(img).enhance(COLOR_BOOST)
img = ImageEnhance.Contrast(img).enhance(CONTRAST)

# Save as a plain (baseline) JPEG under 50 KB. The screen can't show progressive JPEGs.
for quality in range(92, 30, -5):
    data = BytesIO()
    img.save(data, "JPEG", quality=quality, progressive=False, optimize=True)
    if data.tell() <= MAX_BYTES:
        break

with open(OUTPUT_FILE, "wb") as f:
    f.write(data.getvalue())
print(f"Saved {OUTPUT_FILE} ({data.tell() // 1024} KB, quality {quality})")
