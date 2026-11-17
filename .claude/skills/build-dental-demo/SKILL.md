---
name: build-dental-demo
description: Build a website concept demo for a dental clinic from the `dental` template (variable-driven, English + Arabic). Use when making, updating or customising a demo for a dental or orthodontic clinic. It is the build step of the clinic-demo skill; use clinic-demo for inputs, tiers, email and takedowns.
---

# Build a dental clinic demo (template route)

Template: `templates/dental` (bright, friendly, rounded; coral CTA; quick facts, treatments grid, first-visit steps, smile slider, insurance pills). Variables and rules are in `templates/README.md`; `CLAUDE.md` rules always apply (concept banner, noindex, only real facts, public repo).

Tier A/B only. Tier C (modern site, single treatment page) is not supported by the templates yet: say so and fall back to the manual route in `clinic-demo`.

## 1. Facts to collect (from the clinic's own pages) and where they go

| Fact | `site.json` key |
|---|---|
| Name, city, country (+ Arabic name if they publish one) | `name`, `city`, `country` (strings or `{en, ar}`) |
| Studio name for the banner (ask once, reuse) | `studio` |
| Logo file; 2-3 brand colours | `logo`; `colors.primary` (mid-dark, white text must be readable), `colors.accent` (CTA colour; default coral) |
| Treatments they really offer, 4-8, high-ticket first (implants, aligners, veneers, whitening...) | `services: [{icon, title, text, price_from?}]` |
| Dentists: names and qualifications as published | `doctors: [{name, title, credentials, bio?, photo?}]` |
| Google rating and review count exactly as shown; real reviews, short, reviewer name as shown | `rating`, `review_count`, `reviews: [{name, rating, text, source}]` |
| Phone, WhatsApp, address, hours, Maps link, email | `contact: {phone, whatsapp, address, hours, maps_url, email}`; `branches` if several |
| Instagram / other social | `social` |
| Insurers and payment options, only if published | `insurance: ["..."]` |
| Current offer, only if published | `offer: {text, until}` |
| Licence number, only if published | `license` |
| Years / patients / team size, only if published | `stats: [{value, suffix, label}]` |
| Their own tagline | `hero_title` (use `*word*` for the accent word), `hero_text` |

Icons for services: tooth, sparkle (whitening), layers (implants), smile (braces/aligners), star (veneers), shield (root canal), baby, alert (emergency), scan, heart, check.

Anything you cannot confirm stays out. Do not invent doctors, reviews, ratings, prices, years or patient counts. Empty keys hide their section automatically.

## 2. Scaffold and fill

```bash
python tools/build.py --new <slug> dental      # <slug> = clinic-name, lowercase-hyphenated
```

Edit `prospects/<slug>/site.json`. Set `"languages": ["en","ar"]` for Gulf clinics or when they publish Arabic; use their own Arabic where it exists. If you write Arabic yourself, tell the user it needs a native check before sending.

## 3. Template defaults: keep, replace or hide

The build warns when default copy is in use. For dental:

- `services` default is a generic list: **always replace** with the clinic's real treatments.
- `faqs`: copy `templates/dental/defaults.json` entries into your `site.json` and **delete any about treatments they don't offer** (kids, implants, whitening...).
- `highlights` (hero chips): replace with their real selling points, or keep only the neutral ones.
- `why`, `tech`: claims about hygiene, digital scanners, hours. Keep only what their pages support; otherwise `"hide": ["why","technology"]`.
- `journey` (first-visit steps) is generic process copy: fine to keep.
- `before_after`: only the clinic's own published, consented cases with real images in `assets/`. Otherwise leave it out.
- Hide ids for this template: `services why journey results technology doctors insurance reviews faq`.

## 4. Images and colours

Save the logo and the clinic's own published photos into `prospects/<slug>/assets/` (not hotlinked; compress under 300 KB). Reference by filename: `logo`, `images.hero`, `images.about`, doctor `photo`. No stock photos presented as their staff or patients; without photos the designed placeholders stay.

Colours: if the logo's primary is very light, use a darker shade as `primary` and the brand colour as `accent`. Check CTA text contrast (4.5:1).

## 5. Build and check

```bash
python tools/build.py <slug>
```

Read every `!` warning and resolve it (missing images, default copy, studio). Then check:

- `grep -n "\[[A-Z][A-Za-z ]*\]" prospects/<slug>/site/index.html` finds no leftover bracket placeholders.
- Render at 390x844 and 1280x900 (Playwright if available, as in `clinic-demo`), in English and, if built, `ar/`. Nothing cut off, text readable, banner shows the clinic and studio names, WhatsApp widget buttons go to `#contact`.

## 6. Publish and hand back

`python tools/build.py <slug> --publish` creates `<slug>-<4 chars>/` at the repo root. Commit only that folder as `Add demo: <Clinic Name>`, push to `main`, confirm the live URL (`https://deployed-ars.github.io/clinic-previews/<folder>/`) returns 200. Then screenshots and the draft email per `clinic-demo` steps 6 onward.

Keep `"live": false`. Never put the clinic's real WhatsApp behind the demo's buttons.
