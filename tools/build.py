#!/usr/bin/env python3
"""Render a prospect's static demo site from a template + variables.

  python tools/build.py <slug>        build prospects/<slug>/site/ from prospects/<slug>/site.json
  python tools/build.py <slug> --publish   build, then copy to the repo root as <slug>-<4 chars>/ (GitHub Pages folder)
  python tools/build.py --all         build every prospect that has a site.json
  python tools/build.py --list        list templates
  python tools/build.py --new <slug> <template>   scaffold prospects/<slug>/site.json (+ assets/)

site.json: {"template": "dental|aesthetic|cosmetic-surgery", "languages": ["en","ar"], ...}
Any text value may be {"en": "...", "ar": "..."}; plain strings are used for every language.
Empty values fall back to the template's defaults.json. Sections with no data are hidden.
See templates/README.md for every variable.

Repo rules (see CLAUDE.md): every page gets the concept banner and noindex; "live": false (default) keeps WhatsApp/form
buttons pointing at #contact instead of the clinic's real number; only real facts - sections without data are hidden.

Output is static (GitHub Pages ready): site/index.html, site/ar/index.html (if Arabic), site/assets/, site/media/.
"""
import colorsys, json, random, re, shutil, string, sys
from pathlib import Path
from urllib.parse import quote

from jinja2 import Environment, FileSystemLoader
from markupsafe import Markup, escape

ROOT = Path(__file__).resolve().parent.parent
TPL = ROOT / "templates"
PROS = ROOT / "prospects"
TEMPLATES = ["dental", "aesthetic", "cosmetic-surgery"]
IMG = {".png", ".jpg", ".jpeg", ".webp", ".svg", ".gif", ".avif"}
REVIEW_DEFAULTS = ["services", "procedures", "why", "journey", "tech", "safety", "faqs", "highlights", "assurances", "ticker"]
SCHEMA = {"dental": "Dentist", "aesthetic": "MedicalClinic", "cosmetic-surgery": "MedicalClinic"}


# ---------- data helpers ----------
def load_json(p):
    return json.loads(Path(p).read_text(encoding="utf-8"))


def is_i18n(d):
    return isinstance(d, dict) and d and set(d) <= {"en", "ar"}


def empty(v):
    return v is None or v == "" or v == [] or v == {}


def merge(base, over):
    """Deep-merge dicts; lists and i18n dicts are replaced; empty values in `over` are ignored."""
    out = dict(base)
    for k, v in over.items():
        if k.startswith("_") or empty(v):
            continue
        if isinstance(v, dict) and isinstance(out.get(k), dict) and not is_i18n(v) and not is_i18n(out[k]):
            out[k] = merge(out[k], v)
        else:
            out[k] = v
    return out


def resolve(o, lang):
    if is_i18n(o):
        return o.get(lang) or o.get("en") or next(iter(o.values()))
    if isinstance(o, dict):
        return {k: resolve(v, lang) for k, v in o.items()}
    if isinstance(o, list):
        return [resolve(v, lang) for v in o]
    return o


def subst(o, tokens):
    if isinstance(o, str):
        for k, v in tokens.items():
            o = o.replace("{" + k + "}", v)
        return o
    if isinstance(o, dict):
        return {k: subst(v, tokens) for k, v in o.items()}
    if isinstance(o, list):
        return [subst(v, tokens) for v in o]
    return o


# ---------- colour helpers ----------
def rgb(h):
    h = h.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def hx(c):
    return "#%02x%02x%02x" % tuple(max(0, min(255, round(x))) for x in c)


def mix(a, b, t):
    A, B = rgb(a), rgb(b)
    return hx(tuple(A[i] * (1 - t) + B[i] * t for i in range(3)))


def lum(h):
    def f(c):
        c /= 255
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = (f(x) for x in rgb(h))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def ink_on(h):
    return "#ffffff" if lum(h) < 0.38 else "#14181c"


def valid_hex(v):
    return isinstance(v, str) and re.fullmatch(r"#?[0-9a-fA-F]{3}([0-9a-fA-F]{3})?", v.strip() or "x") is not None


def colour_vars(c):
    p, a = c["primary"], c["accent"]
    ink, bg = c["ink"], c["bg"]
    return {
        "primary": p, "primary-deep": mix(p, "#000000", .35), "primary-soft": mix(p, "#ffffff", .90),
        "primary-mid": mix(p, "#ffffff", .70), "primary-ink": ink_on(p),
        "accent": a, "accent-deep": mix(a, "#000000", .25), "accent-soft": mix(a, "#ffffff", .86), "accent-ink": ink_on(a),
        "ink": ink, "muted": mix(ink, bg, .38), "line": mix(ink, bg, .88), "bg": bg, "bg-alt": mix(bg, p, .05),
        "night": mix(p, "#000000", .80), "night-2": mix(p, "#000000", .66),
    }


# ---------- jinja ----------
def f_accent(s):
    return Markup(re.sub(r"\*(.+?)\*", r"<em>\1</em>", str(escape(s or ""))))


def f_digits(s):
    return re.sub(r"\D", "", str(s or ""))


def f_wa(number, text=""):
    n = f_digits(number)
    return f"https://wa.me/{n}" + (f"?text={quote(text)}" if text else "")


def make_env(tpl):
    env = Environment(loader=FileSystemLoader([str(TPL / tpl), str(TPL / "_shared")]), autoescape=True,
                      trim_blocks=True, lstrip_blocks=True)
    env.filters.update(accent=f_accent, digits=f_digits, wa=f_wa)
    return env


# ---------- build ----------
def find_logo(d, site):
    if site.get("logo"):
        return site["logo"]
    for p in sorted((d / "logo").glob("*")) if (d / "logo").exists() else []:
        if p.suffix.lower() in IMG:
            return "logo/" + p.name
    return ""


def media_exists(d, ref):
    return bool(ref) and (d / "assets" / ref).exists() or (d / ref).exists()


def collect_images(data):
    refs = []
    for k in ("logo",):
        refs.append(data.get(k))
    refs += list((data.get("images") or {}).values())
    for grp in ("doctors", "before_after", "gallery", "articles"):
        for it in data.get(grp) or []:
            if isinstance(it, dict):
                refs += [it.get("photo"), it.get("before"), it.get("after"), it.get("image")]
            else:
                refs.append(it)
    return [r for r in refs if isinstance(r, str) and r]


def build(slug):
    d = PROS / slug
    sf = d / "site.json"
    if not sf.exists():
        sys.exit(f"No {sf} - scaffold one with: python tools/build.py --new {slug} <template>")
    site = load_json(sf)
    tpl = site.get("template")
    if tpl not in TEMPLATES:
        sys.exit(f"site.json: template must be one of {TEMPLATES} (got {tpl!r})")
    defaults = load_json(TPL / tpl / "defaults.json")
    ui = load_json(TPL / "_shared" / "ui.json")
    data = merge(defaults, site)
    warn = []

    # colours: site.json > intake brand palette > template defaults
    brand = d / "extracted" / "brand.json"
    cols = dict(defaults["colors"])
    if brand.exists() and not (site.get("colors") or {}).get("primary"):
        pal = [c for c in load_json(brand).get("palette", []) if valid_hex(c)]
        if pal:
            cols["primary"] = pal[0]
            if len(pal) > 1:
                cols["accent"] = pal[1]
            warn.append(f"colours taken from extracted/brand.json ({pal[:2]}); set colors in site.json to override")
    for k, v in (site.get("colors") or {}).items():
        if valid_hex(v):
            cols[k] = v if v.startswith("#") else "#" + v
    cv = colour_vars(cols)

    data["logo"] = find_logo(d, site)
    if not data.get("studio") and not data.get("banner"):
        data["studio"] = "[YOUR STUDIO]"
        warn.append('no "studio" in site.json: banner shows [YOUR STUDIO] (required by CLAUDE.md)')
    used = [k for k in REVIEW_DEFAULTS if k in defaults and empty(site.get(k))]
    if used and not site.get("banner"):
        warn.append("template default copy in use, check it against what the clinic really offers: " + ", ".join(used))
    langs = [l for l in (data.get("languages") or ["en"]) if l in ("en", "ar")] or ["en"]

    # media
    out = d / "site"
    (out / "assets").mkdir(parents=True, exist_ok=True)
    for src, name in ((TPL / "_shared" / "base.css", "base.css"), (TPL / "_shared" / "app.js", "app.js"),
                      (TPL / tpl / "style.css", "style.css")):
        shutil.copyfile(src, out / "assets" / name)
    media = out / "media"
    for sub in ("assets", "logo"):
        s = d / sub
        if s.exists():
            shutil.copytree(s, media / (sub if sub == "logo" else "."), dirs_exist_ok=True)
    for ref in collect_images(data):
        if not ((media / ref).exists()):
            warn.append(f"image not found, placeholder used: {ref}  (put it in prospects/{slug}/assets/)")
            _mark_missing(data, ref)

    env = make_env(tpl)
    for lang in langs:
        s = subst(resolve(data, lang), {"studio": str(resolve(data.get("studio"), lang) or ""),
                                        "name": str(resolve(data.get("name"), lang) or ""),
                                        "city": str(resolve(data.get("city"), lang) or ""),
                                        "country": str(resolve(data.get("country"), lang) or "")})
        U = subst(resolve(ui, lang), {"studio": s.get("studio", ""), "name": s.get("name", ""), "city": s.get("city", ""), "country": s.get("country", "")})
        root = "" if lang == "en" else "../"
        other = [l for l in langs if l != lang]
        alt = {"lang": other[0], "href": ("ar/" if other[0] == "ar" else ("../" if lang == "ar" else "./"))} if other else None
        ctx = dict(s=s, ui=U, lang=lang, dir="rtl" if lang == "ar" else "ltr", root=root, alt=alt, cv=cv, tpl=tpl,
                   ld=Markup(json.dumps(json_ld(s, tpl), ensure_ascii=False)), hide=set(s.get("hide") or []))
        html = env.get_template("index.html.j2").render(**ctx)
        dest = out / ("index.html" if lang == "en" else f"{lang}/index.html")
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(html, encoding="utf-8")
        print(f"  wrote {dest.relative_to(ROOT)}")

    for sec, why in missing_sections(data):
        warn.append(f"section hidden: {sec} ({why})")
    if data.get("live"):
        warn.append('"live": true - WhatsApp widget and form now contact the clinic\'s real number')
    print(f"Built {slug} [{tpl}] languages={langs}")
    for w in warn:
        print("  ! " + w)
    return out


def publish(slug, out):
    """Copy site/ to <repo root>/<folder>/. Reuses the same folder on reruns (prospects/<slug>/publish.txt)."""
    mark = PROS / slug / "publish.txt"
    if mark.exists():
        folder = mark.read_text(encoding="utf-8").strip()
    else:
        folder = slug if slug.startswith("demo-") else slug + "-" + "".join(random.choices(string.ascii_lowercase + string.digits, k=4))
        mark.write_text(folder, encoding="utf-8")
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]*", folder) or folder in {"templates", "tools", "prospects", "references", "screens"}:
        sys.exit(f"refusing to publish into folder {folder!r}")
    dest = ROOT / folder
    if dest.exists():
        shutil.rmtree(dest)
    shutil.copytree(out, dest)
    print(f"Published -> {dest}")
    print(f"  live (after push): https://deployed-ars.github.io/clinic-previews/{folder}/")


def _mark_missing(data, ref):
    """Blank out unresolvable image refs so templates fall back to placeholders."""
    def walk(o):
        if isinstance(o, dict):
            for k, v in o.items():
                if v == ref and k in ("photo", "before", "after", "image", "logo", "hero", "about"):
                    o[k] = ""
                else:
                    walk(v)
        elif isinstance(o, list):
            for v in o:
                walk(v)
    walk(data)


def missing_sections(data):
    need = [("reviews", "add real Google reviews"), ("doctors", "add real doctor names/credentials"),
            ("stats", "add real numbers"), ("before_after", "add consented photos")]
    return [(k, w) for k, w in need if not data.get(k)]


def json_ld(s, tpl):
    c = s.get("contact") or {}
    o = {"@context": "https://schema.org", "@type": SCHEMA[tpl], "name": s.get("name"), "url": ""}
    o.pop("url")
    if c.get("phone"):
        o["telephone"] = c["phone"]
    if c.get("address"):
        o["address"] = {"@type": "PostalAddress", "streetAddress": c["address"], "addressLocality": s.get("city", ""),
                        "addressCountry": s.get("country", "")}
    if s.get("rating") and s.get("review_count"):
        o["aggregateRating"] = {"@type": "AggregateRating", "ratingValue": str(s["rating"]), "reviewCount": str(s["review_count"])}
    return o


def scaffold(slug, tpl):
    if tpl not in TEMPLATES:
        sys.exit(f"template must be one of {TEMPLATES}")
    d = PROS / slug
    (d / "assets").mkdir(parents=True, exist_ok=True)
    f = d / "site.json"
    if f.exists():
        sys.exit(f"{f} already exists")
    ex = load_json(TPL / "site.example.json")
    ex["template"] = tpl
    f.write_text(json.dumps(ex, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Created {f}\n  fill it in, drop images in {d / 'assets'}, then: python tools/build.py {slug}")


def main():
    a = sys.argv[1:]
    if not a:
        print(__doc__)
    elif a[0] == "--list":
        print("\n".join(TEMPLATES))
    elif a[0] == "--all":
        for p in sorted(PROS.glob("*/site.json")):
            build(p.parent.name)
    elif a[0] == "--new" and len(a) == 3:
        scaffold(a[1], a[2])
    else:
        out = build(a[0])
        if "--publish" in a:
            publish(a[0], out)


if __name__ == "__main__":
    main()
