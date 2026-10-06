"""Search Commons for candidate photos for each Forbidden City building."""
import json
import os
import sys
import time

from commons import search

BUILDINGS = [
    ("wumen", "Meridian Gate Forbidden City"),
    ("taihemen", "Gate of Supreme Harmony"),
    ("taihedian", "Hall of Supreme Harmony"),
    ("zhonghedian", "Hall of Central Harmony"),
    ("baohedian", "Hall of Preserving Harmony"),
    ("qianqinggong", "Palace of Heavenly Purity"),
    ("jiaotaidian", "Hall of Union Forbidden City"),
    ("kunninggong", "Palace of Earthly Tranquility"),
    ("qinandian", "Hall of Imperial Peace"),
    ("shenwumen", "Gate of Divine Prowess"),
    ("jiaolou", "Corner Tower Forbidden City"),
    ("wenhuadian", "Hall of Literary Glory"),
    ("wuyingdian", "Hall of Martial Valor"),
    ("wenyuange", "Wenyuan Pavilion"),
    ("yangxindian", "Hall of Mental Cultivation"),
    ("cininggong", "Palace of Compassion and Tranquility"),
    ("chuxiugong", "Palace of Gathered Elegance"),
    ("yuhuage", "Tower of Rain and Flowers"),
    ("fengxiandian", "Hall of Ancestral Worship Forbidden City"),
    ("jiulongbi", "Nine Dragon Wall Forbidden City"),
    ("donghuamen", "Donghua Gate Forbidden City"),
    ("xihuamen", "Xihua Gate Forbidden City"),
    ("wuyingdian2", "Wuying Hall"),
]

PATH = "research/notes/candidates.json"


def main():
    out = {}
    if os.path.exists(PATH):
        with open(PATH, encoding="utf-8") as fh:
            out = json.load(fh)
    for key, term in BUILDINGS:
        if out.get(key, {}).get("candidates"):
            continue
        try:
            out[key] = {"term": term, "candidates": search(term, 20)}
        except Exception as exc:  # noqa: BLE001
            out[key] = {"term": term, "error": str(exc)}
        print(key, len(out[key].get("candidates", [])), file=sys.stderr)
        time.sleep(2)
    with open(PATH, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1)
    print("wrote", PATH)


if __name__ == "__main__":
    main()
