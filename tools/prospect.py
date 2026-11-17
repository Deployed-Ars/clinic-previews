#!/usr/bin/env python3
"""Prospect intake: scaffold a folder, then extract brand colours + Google Business details.

  python tools/prospect.py new <slug>        create prospects/<slug>/ with intake.json + folders
  python tools/prospect.py extract <slug>    run colour + Google extraction, write brief.md
  python tools/prospect.py colors <slug>     colours only
  python tools/prospect.py google <slug>     Google details only

Env: GOOGLE_MAPS_API_KEY (optional; enables Places API details. Without it you get
the URL-parsed basics and a gbp.json to fill by hand).
"""
import colorsys, json, os, re, sys
from collections import Counter
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parent.parent / "prospects"
IMG = {".png", ".jpg", ".jpeg", ".webp"}

INTAKE = {
    "name": "",
    "instagram": "",            # handle or URL
    "google_maps_url": "",      # share link or full maps URL
    "website": "",
    "language": "en",           # en / ar / both
    "brand_colors": [],         # manual override, e.g. ["#0a3d62", "#f8c291"] - wins over auto-detect
    "notes": "",
}


def pdir(slug):
    d = ROOT / slug
    if not d.exists():
        sys.exit(f"No such prospect: {d}  (run: new {slug})")
    return d


def load(d):
    return json.loads((d / "intake.json").read_text(encoding="utf-8"))


# ---------- scaffold ----------
def cmd_new(slug):
    d = ROOT / slug
    for sub in ("screenshots", "logo", "extracted"):
        (d / sub).mkdir(parents=True, exist_ok=True)
    f = d / "intake.json"
    if not f.exists():
        f.write_text(json.dumps(INTAKE, indent=2), encoding="utf-8")
    print(f"Created {d}\n  1. fill intake.json\n  2. drop Instagram screenshots in screenshots/ (logo in logo/)\n  3. python tools/prospect.py extract {slug}")


# ---------- colours ----------
def hexc(c):
    return "#%02x%02x%02x" % tuple(c)


def candidates(path, weight):
    from PIL import Image
    im = Image.open(path).convert("RGB")
    im.thumbnail((200, 200))
    q = im.quantize(colors=24, method=Image.Quantize.MEDIANCUT)
    pal = q.getpalette()
    out = Counter()
    for n, idx in q.getcolors():
        rgb = tuple(pal[idx * 3: idx * 3 + 3])
        out[rgb] += n * weight
    return out


def is_noise(rgb):
    h, s, v = colorsys.rgb_to_hsv(*[x / 255 for x in rgb])
    if v > 0.93 and s < 0.12:
        return True  # white UI
    if v < 0.10:
        return True  # black
    if s < 0.10:
        return True  # grey
    if 0.55 < h < 0.60 and s > 0.9 and v > 0.9:
        return True  # Instagram blue links
    return False


def dist(a, b):
    return sum((x - y) ** 2 for x, y in zip(a, b)) ** 0.5


def cmd_colors(slug):
    d = pdir(slug)
    intake = load(d)
    files = [(p, 3) for p in (d / "logo").glob("*") if p.suffix.lower() in IMG] + \
            [(p, 1) for p in (d / "screenshots").glob("*") if p.suffix.lower() in IMG]
    manual = intake.get("brand_colors") or []
    brand = {"source": "manual" if manual else "auto", "palette": [], "neutrals": []}
    if manual:
        brand["palette"] = [c.lower() for c in manual]
    elif files:
        tot = Counter()
        for p, w in files:
            tot.update(candidates(p, w))
        picked = []
        for rgb, n in tot.most_common():
            if is_noise(rgb) or any(dist(rgb, p) < 50 for p, _ in picked):
                continue
            picked.append((rgb, n))
            if len(picked) == 6:
                break
        brand["palette"] = [hexc(c) for c, _ in picked]
        dark = [c for c in tot if 90 < sum(c) < 250]
        light = [c for c in tot if 690 < sum(c) < 760]
        if dark:
            brand["neutrals"].append(hexc(max(dark, key=tot.get)))
        if light:
            brand["neutrals"].append(hexc(max(light, key=tot.get)))
    else:
        print("No images found in logo/ or screenshots/")
        return
    p = brand["palette"]
    n = brand["neutrals"]
    css = ":root{\n" + "".join(f"  --brand-{i + 1}: {c};\n" for i, c in enumerate(p))
    if len(n) == 2:
        css += f"  --ink: {n[0]};\n  --paper: {n[1]};\n"
    brand["css"] = css + "}"
    out = d / "extracted"
    out.mkdir(exist_ok=True)
    (out / "brand.json").write_text(json.dumps(brand, indent=2), encoding="utf-8")
    try:
        from PIL import Image, ImageDraw
        sw = Image.new("RGB", (120 * max(1, len(p)), 120), "white")
        dr = ImageDraw.Draw(sw)
        for i, c in enumerate(p):
            dr.rectangle([i * 120, 0, i * 120 + 119, 99], fill=c)
            dr.text((i * 120 + 8, 104), c, fill="black")
        sw.save(out / "swatches.png")
    except Exception:
        pass
    print("Palette:", " ".join(p), f"({brand['source']})")


# ---------- google ----------
def resolve(url):
    import requests
    if re.search(r"goo\.gl|maps\.app", url):
        r = requests.get(url, allow_redirects=True, timeout=20, headers={"User-Agent": "Mozilla/5.0"})
        return r.url
    return url


def parse_maps(url):
    info = {"resolved_url": url}
    m = re.search(r"/maps/place/([^/@?]+)", url)
    if m:
        info["name_from_url"] = unquote(m.group(1)).replace("+", " ")
    m = re.search(r"@(-?\d+\.\d+),(-?\d+\.\d+)", url) or re.search(r"!3d(-?\d+\.\d+)!4d(-?\d+\.\d+)", url)
    if m:
        info["lat"], info["lng"] = float(m.group(1)), float(m.group(2))
    m = re.search(r"!1s(0x[0-9a-f]+:0x[0-9a-f]+)", url)
    if m:
        info["ftid"] = m.group(1)
    m = re.search(r"place_id[=:]([\w-]+)", url)
    if m:
        info["place_id"] = m.group(1)
    return info


def places_api(info, key, fallback_name):
    import requests
    H = {"X-Goog-Api-Key": key, "Content-Type": "application/json"}
    pid = info.get("place_id")
    if not pid:
        q = info.get("name_from_url") or fallback_name
        if not q:
            return None
        body = {"textQuery": q}
        if "lat" in info:
            body["locationBias"] = {"circle": {"center": {"latitude": info["lat"], "longitude": info["lng"]}, "radius": 500.0}}
        r = requests.post("https://places.googleapis.com/v1/places:searchText",
                          headers={**H, "X-Goog-FieldMask": "places.id"}, json=body, timeout=20)
        r.raise_for_status()
        ps = r.json().get("places", [])
        if not ps:
            return None
        pid = ps[0]["id"]
    fields = ("id,displayName,formattedAddress,nationalPhoneNumber,internationalPhoneNumber,websiteUri,googleMapsUri,"
              "rating,userRatingCount,regularOpeningHours,primaryTypeDisplayName,types,editorialSummary,reviews,photos,location,businessStatus")
    r = requests.get(f"https://places.googleapis.com/v1/places/{pid}", headers={**H, "X-Goog-FieldMask": fields}, timeout=20)
    r.raise_for_status()
    return r.json()


def cmd_google(slug):
    d = pdir(slug)
    intake = load(d)
    url = intake.get("google_maps_url", "").strip()
    out = d / "extracted"
    out.mkdir(exist_ok=True)
    if not url:
        print("intake.json has no google_maps_url")
        return
    info = parse_maps(resolve(url))
    (out / "gbp_url_parse.json").write_text(json.dumps(info, indent=2, ensure_ascii=False), encoding="utf-8")
    print("Parsed URL:", {k: v for k, v in info.items() if k != "resolved_url"})
    key = os.environ.get("GOOGLE_MAPS_API_KEY")
    if not key:
        tpl = out / "gbp.json"
        if not tpl.exists():
            tpl.write_text(json.dumps({"name": info.get("name_from_url", ""), "address": "", "phone": "", "website": "",
                                       "hours": [], "rating": None, "review_count": None, "category": "",
                                       "reviews": [], "services": []}, indent=2), encoding="utf-8")
        print("No GOOGLE_MAPS_API_KEY -> fill extracted/gbp.json by hand, or ask Claude in-session (it has a get_business_profile tool).")
        return
    data = places_api(info, key, intake.get("name"))
    if not data:
        print("Place not found via API")
        return
    (out / "gbp.json").write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    import requests
    pd = out / "gbp_photos"
    pd.mkdir(exist_ok=True)
    for i, ph in enumerate(data.get("photos", [])[:6]):
        r = requests.get(f"https://places.googleapis.com/v1/{ph['name']}/media?maxWidthPx=1600&key={key}", timeout=30)
        if r.ok:
            (pd / f"{i + 1}.jpg").write_bytes(r.content)
    print("Saved gbp.json +", len(list(pd.glob("*.jpg"))), "photos")


# ---------- brief ----------
def cmd_brief(slug):
    d = pdir(slug)
    intake = load(d)
    e = d / "extracted"
    L = [f"# Build brief: {intake.get('name') or slug}", ""]
    L += [f"- Instagram: {intake.get('instagram')}", f"- Google Maps: {intake.get('google_maps_url')}",
          f"- Website: {intake.get('website')}", f"- Language: {intake.get('language')}", f"- Notes: {intake.get('notes')}", ""]
    if (e / "brand.json").exists():
        b = json.loads((e / "brand.json").read_text(encoding="utf-8"))
        L += ["## Brand colours", ", ".join(b["palette"]), "", "```css", b["css"], "```", ""]
    if (e / "gbp.json").exists():
        L += ["## Google Business profile", "```json", (e / "gbp.json").read_text(encoding="utf-8")[:6000], "```", ""]
    shots = sorted(p.name for p in (d / "screenshots").glob("*") if p.suffix.lower() in IMG)
    L += ["## Instagram screenshots (read these visually)"] + [f"- screenshots/{s}" for s in shots]
    L += ["", "## Reference patterns", "See memory: clinic-reference-sites (stats in hero, licence no., WhatsApp, named doctors, treatment tiles)."]
    (d / "brief.md").write_text("\n".join(L), encoding="utf-8")
    print(f"Wrote {d / 'brief.md'}")


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        return
    cmd, slug = sys.argv[1], sys.argv[2]
    if cmd == "new":
        cmd_new(slug)
    elif cmd == "colors":
        cmd_colors(slug)
    elif cmd == "google":
        cmd_google(slug)
    elif cmd == "extract":
        cmd_colors(slug)
        cmd_google(slug)
        cmd_brief(slug)
    else:
        print(__doc__)


if __name__ == "__main__":
    main()
