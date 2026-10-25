"""Genera las imágenes sociales OG (1200x630): og.png (ES) y og-en.png (EN).

Uso: python3 tools/make_og.py [Inter.ttf] [JetBrainsMono.ttf]
Requiere Pillow. Con las fuentes variables Inter y JetBrains Mono (convertidas
desde assets/fonts/*.woff2 con fontTools) coincide con la web; sin ellas usa
Noto Sans o DejaVu como alternativa.
"""
import os
import sys
from PIL import Image, ImageDraw, ImageFont

W, H = 1200, 630
BG = (10, 14, 20)
TEXT = (230, 237, 243)
MUTED = (154, 167, 182)
ACCENT = (94, 234, 212)
ACCENT2 = (167, 139, 250)

SANS = ["/usr/share/fonts/noto/NotoSans-Regular.ttf", "/usr/share/fonts/TTF/DejaVuSans.ttf"]
SANS_B = ["/usr/share/fonts/noto/NotoSans-Bold.ttf", "/usr/share/fonts/TTF/DejaVuSans-Bold.ttf"]
MONO = ["/usr/share/fonts/TTF/DejaVuSansMono.ttf", "/usr/share/fonts/dejavu/DejaVuSansMono.ttf"]


def load(custom, fallbacks, size, weight=None):
    paths = ([custom] if custom else []) + fallbacks
    for p in paths:
        if p and os.path.exists(p):
            f = ImageFont.truetype(p, size)
            if weight is not None and p == custom:
                try:
                    f.set_variation_by_axes([weight])
                except Exception:
                    pass
            return f
    return ImageFont.load_default()


inter = sys.argv[1] if len(sys.argv) > 1 else None
mono = sys.argv[2] if len(sys.argv) > 2 else None

PAGES = {
    "og.png": {
        "role": "Desarrollador web · Técnico de soporte TIC",
        "line": "web a medida · aplicaciones · IA y automatización · SEO",
    },
    "og-en.png": {
        "role": "Web Developer · IT Support Technician",
        "line": "custom websites · applications · AI & automation · SEO",
    },
}


def glow(img, cx, cy, radius, color, alpha):
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    steps = 80
    for i in range(steps, 0, -1):
        r = int(radius * i / steps)
        a = int(alpha * (1 - i / steps) ** 1.7)
        od.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(*color, a))
    img.paste(overlay, (0, 0), overlay)


out_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "img")
for filename, t in PAGES.items():
    img = Image.new("RGB", (W, H), BG)
    glow(img, 1020, 40, 620, ACCENT2, 70)
    glow(img, 90, 120, 560, ACCENT, 48)
    d = ImageDraw.Draw(img)

    d.text((92, 130), "~/portfolio $ whoami", font=load(mono, MONO, 28, 400), fill=ACCENT)
    name_f = load(inter, SANS_B, 98, 600)
    d.text((90, 190), "Demian ", font=name_f, fill=TEXT)
    x = 90 + d.textlength("Demian ", font=name_f)
    d.text((x, 190), "Soria Vicente", font=name_f, fill=ACCENT)
    d.text((92, 330), t["role"], font=load(inter, SANS, 38, 400), fill=MUTED)
    d.text((92, 410), "> " + t["line"], font=load(mono, MONO, 27, 400), fill=TEXT)
    d.line([92, 480, 92 + 140, 480], fill=ACCENT2, width=3)
    d.text((92, 530), "demiansoriavicente.github.io", font=load(mono, MONO, 26, 400), fill=MUTED)

    path = os.path.join(out_dir, filename)
    img.save(path, "PNG", optimize=True)
    print("OK", path, os.path.getsize(path), "bytes")
