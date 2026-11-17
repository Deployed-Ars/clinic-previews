---
name: build-cosmetic-surgery-demo
description: Build a website concept demo for a cosmetic or plastic surgery clinic from the `cosmetic-surgery` template (dark, discreet, variable-driven, English + Arabic). Use when making, updating or customising a demo for a cosmetic, plastic or aesthetic surgery clinic or surgeon. It is the build step of the clinic-demo skill; use clinic-demo for inputs, tiers, email and takedowns.
---

# Build a cosmetic surgery demo (template route)

Template: `templates/cosmetic-surgery` (dark and discreet, gold accent; tabbed procedures Face / Breast / Body / Non-surgical, journey rail, safety section, surgeons, "private consultation"). Variables and rules are in `templates/README.md`; `CLAUDE.md` rules always apply (concept banner, noindex, only real facts, public repo).

Tier A/B only. Tier C (single procedure page, e.g. rhinoplasty) is not supported by the templates yet: say so and fall back to the manual route in `clinic-demo`.

This is the most sensitive of the three. Tone is private and restrained; claims are medical.

## 1. Facts to collect (from the clinic's own pages) and where they go

| Fact | `site.json` key |
|---|---|
| Name, city, country (+ Arabic name if published); studio name (ask once) | `name`, `city`, `country`, `studio` |
| Logo; brand colours | `logo`; `colors.primary` (any shade: the dark hero and footer are derived from it), `colors.accent` (must read on near-black, like gold or a light tint) |
| Procedures they actually perform, grouped | `procedures: [{name: "Face", treatments: [{title, text}]}, ...]`. Rename, drop or add groups to match (Face, Breast, Body, Non-surgical, Hair...) |
| Surgeons: names, specialty, qualifications **exactly as published** | `doctors: [{name, title, credentials, bio?, photo?}]` |
| Where they operate (hospital/facility), anaesthesia team, follow-up | `safety: {title, text, points[]}` only if published |
| Licence / advertising permit number, if they show one | `license` |
| Google rating and count; real reviews | `rating`, `review_count`, `reviews` |
| Phone, WhatsApp, address, hours, Maps link | `contact` |
| Payment/financing options, only if published | `financing: ["..."]` |
| Years in practice / team size, only if published | `stats` |
| Their tagline | `hero_title` (`*word*` = gold italic), `hero_text`, `intro` |

Do not invent surgeons, credentials, accreditations, prices, recovery times or results. Empty keys hide their section.

## 2. Scaffold and fill

```bash
python tools/build.py --new <slug> cosmetic-surgery
```

Edit `prospects/<slug>/site.json`. `"languages": ["en","ar"]` for Gulf clinics; use their own Arabic where published, and flag self-written Arabic for native review. For a single surgeon's practice, name the surgeon in the hero copy and keep `doctors` to that person.

## 3. Template defaults: keep, replace or hide

- `procedures` default is a broad generic menu: **replace** with only what they perform. Do not leave breast or body procedures if they only do face work.
- `safety`: default points ("licensed facilities", "qualified anaesthesia team", "follow-up visits") are claims. Keep only those supported by their pages; otherwise `"hide": ["safety"]`.
- `assurances` (hero checklist) and `journey`: generic process copy; edit if the clinic describes its process differently.
- `faqs`: recovery and privacy answers are deliberately non-specific; keep, but remove questions about procedures they don't offer. Never add specific recovery times, prices or guarantees.
- `before_after`: **only** the clinic's own published, consented cases. Omit otherwise. No generated or retouched imagery. Keep the results disclaimer.
- Avoid superlatives and guarantees ("best", "safe", "permanent", "guaranteed"): medical advertising is regulated in many markets.
- Hide ids: `procedures journey safety surgeons results financing reviews faq`.

## 4. Images and colours

Own photos only, in `prospects/<slug>/assets/` (under 300 KB): `images.hero` (portrait of the surgeon or a clinic interior; shown with a gold offset frame), doctor `photo`. Prefer interiors and surgeon portraits over body imagery. Without photos the dark placeholders stay.

Colours: `night` is `primary` mixed 80% with black, so bright brands still give a dark site. Pick `accent` with at least 4.5:1 contrast on near-black; check it on the gold-style CTA button text too.

## 5. Build and check

```bash
python tools/build.py <slug>
```

Resolve every `!` warning. Then check:

- `grep -n "\[[A-Z][A-Za-z ]*\]" prospects/<slug>/site/index.html` finds no leftover brackets.
- Render at 390x844 and 1280x900, English and `ar/`. Tabs switch, long procedure names fit, the header is readable over the dark hero and after scrolling, banner shows clinic and studio, widget buttons go to `#contact`.

## 6. Publish and hand back

`python tools/build.py <slug> --publish`, commit only that folder as `Add demo: <Clinic Name>`, push to `main`, confirm `https://deployed-ars.github.io/clinic-previews/<folder>/` returns 200, then screenshots and the draft email per `clinic-demo`. Keep `"live": false`.
