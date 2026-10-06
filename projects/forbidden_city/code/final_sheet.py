"""One labelled sheet of the chosen images, for a final visual check."""
import json
import os

from PIL import Image, ImageDraw, ImageFont

OUT = "artifacts/final_selection.jpg"
CELL = 430
PAD = 8
LABEL_H = 30


def font():
    for n in ("arial.ttf", "segoeui.ttf"):
        try:
            return ImageFont.truetype(n, 22)
        except Exception:  # noqa: BLE001
            pass
    return ImageFont.load_default()


def main():
    with open("images/manifest.json", encoding="utf-8") as fh:
        man = json.load(fh)
    items = sorted(man.values(), key=lambda r: r["id"])
    cols = 3
    rows = (len(items) + cols - 1) // cols
    cw, ch = CELL + PAD, CELL + LABEL_H + PAD
    sheet = Image.new("RGB", (cols * cw + PAD, rows * ch + PAD), (25, 25, 25))
    d = ImageDraw.Draw(sheet)
    f = font()
    for i, rec in enumerate(items):
        r, c = divmod(i, cols)
        x, y = PAD + c * cw, PAD + r * ch
        d.text((x + 4, y + 3), f'{rec["id"]:02d} {rec["name_eng"]}', fill=(255, 230, 120), font=f)
        im = Image.open(os.path.join("images", rec["image"])).convert("RGB")
        im.thumbnail((CELL, CELL))
        sheet.paste(im, (x + (CELL - im.width) // 2, y + LABEL_H + (CELL - im.height) // 2))
    sheet.save(OUT, quality=85)
    print(OUT, sheet.size)


if __name__ == "__main__":
    main()
