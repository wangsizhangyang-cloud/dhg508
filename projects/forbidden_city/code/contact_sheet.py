"""Build a labelled contact sheet per building so candidates can be compared."""
import os
import sys

from PIL import Image, ImageDraw, ImageFont

SRC = "artifacts/candidates"
OUT = "artifacts/contact_sheets"
CELL = 420
PAD = 8
LABEL_H = 26


def load_font():
    for name in ("arial.ttf", "segoeui.ttf", "DejaVuSans.ttf"):
        try:
            return ImageFont.truetype(name, 20)
        except Exception:  # noqa: BLE001
            continue
    return ImageFont.load_default()


def main():
    os.makedirs(OUT, exist_ok=True)
    font = load_font()
    files = sorted(os.listdir(SRC))
    groups = {}
    for f in files:
        key = f.rsplit("-", 1)[0]
        groups.setdefault(key, []).append(f)

    for key, items in groups.items():
        items.sort()
        cols = 2
        rows = (len(items) + cols - 1) // cols
        cw = CELL + PAD
        ch = CELL + LABEL_H + PAD
        sheet = Image.new("RGB", (cols * cw + PAD, rows * ch + PAD), (30, 30, 30))
        draw = ImageDraw.Draw(sheet)
        for i, fname in enumerate(items):
            r, c = divmod(i, cols)
            x = PAD + c * cw
            y = PAD + r * ch
            draw.text((x + 4, y + 2), fname.rsplit(".", 1)[0], fill=(255, 235, 120), font=font)
            try:
                im = Image.open(os.path.join(SRC, fname)).convert("RGB")
            except Exception as exc:  # noqa: BLE001
                draw.text((x + 4, y + LABEL_H + 4), "ERR " + str(exc), fill=(255, 0, 0), font=font)
                continue
            im.thumbnail((CELL, CELL))
            sheet.paste(im, (x + (CELL - im.width) // 2, y + LABEL_H + (CELL - im.height) // 2))
        out = os.path.join(OUT, key + ".jpg")
        sheet.save(out, quality=82)
        print(out, sheet.size, len(items), file=sys.stderr)


if __name__ == "__main__":
    main()
