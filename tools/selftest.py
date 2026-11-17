"""Smoke test: synthetic screenshot + maps URL through the pipeline (no network needed for full URLs)."""
import json, subprocess, sys
from pathlib import Path
from PIL import Image, ImageDraw

root = Path(__file__).resolve().parent.parent
run = lambda *a: subprocess.run([sys.executable, str(root / "tools" / "prospect.py"), *a], check=True)
run("new", "_selftest")
d = root / "prospects" / "_selftest"
im = Image.new("RGB", (400, 600), "white")
g = ImageDraw.Draw(im)
g.rectangle([0, 0, 400, 300], fill=(14, 90, 110))
g.rectangle([0, 300, 400, 400], fill=(230, 190, 120))
g.rectangle([0, 400, 400, 450], fill=(0, 149, 246))
im.save(d / "screenshots" / "a.png")
f = d / "intake.json"
j = json.loads(f.read_text())
j["name"] = "Selftest"
j["google_maps_url"] = "https://www.google.com/maps/place/Test+Clinic/@23.5880,58.3829,17z/data=!3m1"
f.write_text(json.dumps(j))
run("extract", "_selftest")
