"""P8 inputs: 40 rendered SPECIMEN certificates in five administration styles, with clean, rotated, blurred,
low-light and noisy variants. Holder names and numbers are synthetic. Writes eval/specimens/*.png and truth.json."""
from __future__ import annotations

import json
import random
from datetime import date, timedelta
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = Path(__file__).resolve().parent
OUT = HERE / "specimens"
rng = random.Random(8)
STYLES = [
    ("India", "%d/%m/%Y", "Directorate General of Shipping"),
    ("United Kingdom", "%d %B %Y", "Maritime and Coastguard Agency"),
    ("Singapore", "%d %b %Y", "Maritime and Port Authority"),
    ("Australia", "%d/%m/%Y", "Australian Maritime Safety Authority"),
    ("Nigeria", "%d-%m-%Y", "Nigerian Maritime Administration"),
]
TITLES = ["Medical Fitness Certificate", "Certificate of Competency", "Basic Safety Training Certificate", "Endorsement Certificate", "Medical Fitness Certificate"]
VARIANTS = ["clean", "clean", "rot_left", "rot_right", "blur", "lowlight", "noise", "rot_blur"]
NAMES = ["ARJUN MENON", "RAVI NAIR", "SAMIR PILLAI", "KIRAN SHETTY", "DEV KAMATH", "ANIL IYER", "VIKRAM REDDY", "NEIL BOSE", "ROHAN DAS", "TARUN RAO"]


def font(size):
    for f in ("C:/Windows/Fonts/arial.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"):
        if Path(f).exists():
            return ImageFont.truetype(f, size)
    return ImageFont.load_default()


def main():
    OUT.mkdir(exist_ok=True)
    truth = []
    n = 0
    for si, (country, fmt, authority) in enumerate(STYLES):
        for vi, var in enumerate(VARIANTS):
            n += 1
            holder = NAMES[(si * 2 + vi) % 10]
            coc = f"{rng.randint(100000, 999999)}/{rng.choice(['MUM', 'LON', 'SIN', 'SYD', 'LOS'])}/{rng.randint(2015, 2024)}"
            ppt = rng.choice("ABCDEFGHJKLMNPRSTUVWY") + str(rng.randint(1000000, 9999999))
            exp = date(2027, 1, 1) + timedelta(days=rng.randint(0, 900))
            iss = exp - timedelta(days=rng.choice([730, 1095, 1825]))
            lines = ["SPECIMEN", TITLES[si], f"Issued by: {authority}", f"Country: {country}", f"Holder: {holder}",
                     f"CoC No: {coc}", f"Passport: {ppt}", f"Date of issue: {iss.strftime(fmt)}", f"Date of expiry: {exp.strftime(fmt)}"]
            im = Image.new("L", (1000, 640), 245)
            d = ImageDraw.Draw(im)
            y = 40
            for i, l in enumerate(lines):
                d.text((60, y), l, fill=20, font=font(40 if i < 2 else 32))
                y += 62
            if var in ("rot_left", "rot_blur"):
                im = im.rotate(3, fillcolor=245, expand=False)
            if var == "rot_right":
                im = im.rotate(-4, fillcolor=245, expand=False)
            if var in ("blur", "rot_blur"):
                im = im.filter(ImageFilter.GaussianBlur(1.1))
            if var == "lowlight":
                im = im.point(lambda p: int(p * 0.45))
            if var == "noise":
                px = im.load()
                for _ in range(9000):
                    px[rng.randrange(im.width), rng.randrange(im.height)] = rng.randrange(0, 255)
            name = f"S{n:02d}"
            im.save(OUT / f"{name}.png")
            truth.append({"id": name, "style": country, "variant": var, "expiry": exp.isoformat(), "administration_hint": country.split()[0].lower(),
                          "identifiers": {"NAME": holder, "COC": coc, "PASSPORT": ppt}, "synthetic": True, "specimen": True})
    (OUT / "truth.json").write_text(json.dumps(truth, indent=1), encoding="utf-8", newline="\n")
    print(len(truth), "specimens")


if __name__ == "__main__":
    main()
