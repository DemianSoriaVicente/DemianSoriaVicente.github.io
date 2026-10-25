"""Genera las imágenes sociales OG (1200x630): og.png (ES) y og-en.png (EN).

Uso: python3 tools/make_og.py [Bricolage.ttf] [JetBrainsMono.ttf]
Requiere Pillow. Las fuentes variables de assets/fonts/*.woff2 se convierten a
.ttf con fontTools; sin ellas usa DejaVu como alternativa.
"""
import os
import sys
from PIL import Image, ImageDraw, ImageFont

W, H = 1200, 630
BG = (237, 239, 253)
INK = (14, 15, 20)
BLUE = (43, 57, 255)
LIME = (201, 255, 61)

FALLBACK = ["/usr/share/fonts/TTF/DejaVuSans-Bold.ttf", "/usr/share/fonts/dejavu/DejaVuSans-Bold.ttf"]
FALLBACK_MONO = ["/usr/share/fonts/TTF/DejaVuSansMono.ttf", "/usr/share/fonts/dejavu/DejaVuSansMono.ttf"]

display_path = sys.argv[1] if len(sys.argv) > 1 else None
sans_path = display_path
mono_path = sys.argv[2] if len(sys.argv) > 2 else None


def font(path, fallbacks, size, axes=None):
    for p in ([path] if path else []) + fallbacks:
        if p and os.path.exists(p):
            f = ImageFont.truetype(p, size)
            if axes and p == path:
                try:
                    f.set_variation_by_axes(axes)
                except Exception:
                    pass
            return f
    return ImageFont.load_default()


PAGES = {
    "og.png": ["Desarrollo web", "IA y automatización", "SEO"],
    "og-en.png": ["Web development", "AI & automation", "SEO"],
}


def sticker(img, text, center, angle, bg, fg, size=34):
    f = font(sans_path, FALLBACK, size, [12, 600, 100])
    tmp = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
    tw = tmp.textlength(text, font=f)
    pw, ph = int(tw + 56), int(size * 2)
    layer = Image.new("RGBA", (pw + 8, ph + 8), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    d.rounded_rectangle([4, 4, 4 + pw, 4 + ph], radius=ph // 2, fill=bg)
    d.text((4 + pw / 2, 4 + ph / 2 - 2), text, font=f, fill=fg, anchor="mm")
    layer = layer.rotate(angle, expand=True, resample=Image.BICUBIC)
    img.paste(layer, (int(center[0] - layer.width / 2), int(center[1] - layer.height / 2)), layer)


out_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "img")
for filename, tags in PAGES.items():
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    big = font(display_path, FALLBACK, 230, [96, 800, 75])
    d.text((70, 70), "DEMIAN", font=big, fill=BLUE)
    d.text((70, 275), "SORIA VICENTE", font=big, fill=BLUE)
    sticker(img, tags[0], (300, 82), -5, INK, BG)
    sticker(img, tags[1], (900, 170), 4, LIME, INK)
    sticker(img, tags[2], (640, 528), 3, INK, BG)
    d.text((70, 575), "demiansoriavicente.github.io", font=font(mono_path, FALLBACK_MONO, 26), fill=INK)
    path = os.path.join(out_dir, filename)
    img.save(path, "PNG", optimize=True)
    print("OK", path, os.path.getsize(path), "bytes")
