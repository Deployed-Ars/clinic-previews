# Clinic templates

Three base templates, one build script. A prospect is just a `site.json` (plus a few images); the template supplies design, section order and sensible default copy.

| Template | Target | Look |
|---|---|---|
| `dental` | Dental clinics | Bright, friendly, rounded cards, coral CTA. Quick facts, treatments grid, first-visit steps, smile slider, insurance. |
| `aesthetic` | Aesthetic / dermatology clinics | Editorial and calm. Serif display, arch-shaped photos, treatment ticker, numbered treatment rows, technology spotlight, before/after, journal. |
| `cosmetic-surgery` | Cosmetic / plastic surgery | Dark and discreet, gold accent. Tabbed procedures (Face / Breast / Body / Non-surgical), journey rail, safety section, surgeons, "private consultation". |

All three include: bilingual EN/AR (RTL), floating WhatsApp widget with quick replies, request form that hands off to WhatsApp, FAQ, reviews carousel, before/after slider, schema.org JSON-LD, mobile-first layout. Output is plain static HTML/CSS/JS for GitHub Pages.

## Workflow

```bash
python tools/prospect.py new <slug>               # intake: screenshots, colours, Google details (existing)
python tools/build.py --new <slug> dental         # scaffold prospects/<slug>/site.json  (dental | aesthetic | cosmetic-surgery)
# edit site.json, drop images in prospects/<slug>/assets/
python tools/build.py <slug>                      # -> prospects/<slug>/site/index.html (+ ar/index.html)
python tools/build.py <slug> --publish            # build and copy to <slug>-<4 chars>/ at the repo root (GitHub Pages)
python tools/build.py --all                       # rebuild every prospect
```

The build prints warnings: images it could not find (a placeholder is used), sections hidden for lack of data, and whether colours came from `extracted/brand.json`. `site/` is generated: edit `site.json` or the template, never the output.

Requires `pip install jinja2`.

## Variables (`site.json`)

Any text can be a plain string or `{"en": "...", "ar": "..."}`. Empty values fall back to the template's `defaults.json`. Wrap a word in `*stars*` inside titles to get the accent word.

| Key | Purpose |
|---|---|
| `template` | `dental`, `aesthetic` or `cosmetic-surgery` |
| `languages` | `["en"]`, `["ar"]`-style lists; `["en","ar"]` builds `/` and `/ar/` with a language switch |
| `name`, `city`, `country` | Used everywhere; `{name}`, `{city}`, `{country}` work inside any copy |
| `colors.primary`, `colors.accent` | Brand colours. All tints/shades and text contrast are derived. Optional `ink`, `bg`. If omitted, `extracted/brand.json` palette is used, then template defaults |
| `logo` | File in `assets/`; or drop one in `logo/` and it is picked up |
| `images.hero`, `images.about`, `images.tech` | Files in `assets/`. Missing = designed placeholder |
| `contact` | `phone`, `whatsapp` (digits, with country code), `email`, `address`, `hours` (string or `[{days,time}]`), `maps_url` |
| `branches` | `[{name, address, phone, hours, maps_url}]`; replaces single-location contact block |
| `social` | `instagram`, `facebook`, `tiktok`, ... (URLs) |
| `license`, `rating`, `review_count` | Shown only if provided. Never invented |
| `stats` | `[{value: 12, suffix: "+", label}]`. Hidden if empty |
| `services` | `[{title, text, icon, price_from}]`. Overrides default treatments (dental, aesthetic). Icons: tooth, sparkle, shield, heart, smile, clock, star, check, phone, pin, mail, face, drop, leaf, zap, calendar, user, award, alert, layers, camera, baby, scan, hand, body |
| `procedures` | cosmetic-surgery only: `[{name, treatments: [{title, text}]}]` |
| `doctors` | `[{name, title, credentials, bio, photo}]`. Hidden if empty |
| `reviews` | `[{name, rating, text, source}]`. Use real reviews only. Hidden if empty |
| `before_after` | `[{label, before, after}]` images in `assets/`. Only with patient consent. Hidden if empty |
| `faqs`, `journey`, `why`, `tech`, `safety`, `articles` | Override default sections (see each `defaults.json` for shape) |
| `insurance` (dental), `financing` (cosmetic) | List of strings shown as pills |
| `offer` | `{text, until}` banner |
| `hide` | Section ids to suppress, e.g. `["why","technology","faq"]` |
| `meta_title`, `meta_description`, `footer_text`, `preview_note` | SEO and footer text |

## Repo rules built in (see CLAUDE.md)

- Every page gets the concept banner ("Website concept prepared for {name} by {studio}...") and `noindex, nofollow`. Set `studio` in `site.json`; the build warns if it is missing. `banner` overrides the whole text (used by the template previews).
- `"live": false` (default): WhatsApp widget buttons go to `#contact` and the form shows "this is a concept" instead of contacting the clinic. Set `"live": true` only for a real handover, with the clinic's own number in `contact.whatsapp`.
- Template default copy (treatments, FAQs, why us, safety...) is generic: the build warns when it is in use. Replace it with what the clinic really offers.

## Content rules

- Reviews, doctors, stats, rating, licence and before/afters appear **only** when you supply real data. Don't fabricate them.
- Default copy (treatments, FAQs, "why us", safety points) is generic. Review it against what the clinic really offers and claims before sending a demo.
- Before/after photos need patient consent. Keep the results disclaimer.
- Forms send via WhatsApp (static hosting, no backend). That is a demo behaviour, not a lead-capture system.

## Adding or changing a template

`templates/<name>/{index.html.j2, style.css, defaults.json}`. Shared pieces live in `_shared/`: `layout.html.j2` (head, header, footer, WhatsApp), `parts.j2` (macros: stats, faq, reviews, doctors, journey, slider, contact), `base.css`, `app.js`, `ui.json` (EN/AR interface strings). Register a new name in `TEMPLATES` in `tools/build.py`.
