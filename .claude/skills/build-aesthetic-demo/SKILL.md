---
name: build-aesthetic-demo
description: Build a website concept demo for an aesthetic or dermatology clinic (laser, skin, injectables) from the `aesthetic` template (variable-driven, English + Arabic). Use when making, updating or customising a demo for a derm, skin, laser or aesthetic clinic. It is the build step of the clinic-demo skill; use clinic-demo for inputs, tiers, email and takedowns.
---

# Build an aesthetic / dermatology demo (template route)

Template: `templates/aesthetic` (editorial and calm: serif display, arch-shaped photos, treatment ticker, numbered treatment rows, technology spotlight, before/after, journal). Variables and rules are in `templates/README.md`; `CLAUDE.md` rules always apply (concept banner, noindex, only real facts, public repo).

Tier A/B only. Tier C (single high-value treatment page, e.g. laser) is not supported by the templates yet: say so and fall back to the manual route in `clinic-demo`.

## 1. Facts to collect (from the clinic's own pages) and where they go

| Fact | `site.json` key |
|---|---|
| Name, city, country (+ Arabic name if published); studio name (ask once) | `name`, `city`, `country`, `studio` |
| Logo; 2-3 brand colours | `logo`; `colors.primary` (dark neutral or deep brand shade: used for buttons and dark sections), `colors.accent` (brand tint: italic words, rules, numbers) |
| Treatments they really offer, 6-10 (laser hair removal, acne/scars, pigmentation, injectables, peels, hair...) | `services: [{icon, title, text, price_from?}]` and `ticker: [names]` for the scrolling strip |
| Devices/technology **by name only if they publish it** | `tech: {title, text, points[]}` |
| Doctors: names, published qualifications | `doctors: [{name, title, credentials, bio?, photo?}]` |
| Branches (many Gulf derm clinics have several) | `branches: [{name, address, phone, hours, maps_url}]` |
| Google rating and count exactly as shown; real reviews | `rating`, `review_count`, `reviews: [...]` |
| Phone, WhatsApp, address, hours, Maps link | `contact: {...}` |
| Current offer, licence number, social | `offer`, `license`, `social` (only if published) |
| Articles they actually publish | `articles: [{title, text, image?}]` |
| Years / patients / branches, only if published | `stats` |
| Their tagline and tone | `hero_title` (`*word*` = italic accent), `hero_text`, `intro` |

Service icons: face, zap (laser), drop (acne), sparkle (pigmentation), star (anti-ageing), leaf (boosters), layers (peels), heart, hand, camera.

Do not invent anything. Empty keys hide their section.

## 2. Scaffold and fill

```bash
python tools/build.py --new <slug> aesthetic
```

Edit `prospects/<slug>/site.json`. `"languages": ["en","ar"]` for Gulf clinics or when they publish Arabic; use their own Arabic where it exists, and flag self-written Arabic for native review.

## 3. Template defaults: keep, replace or hide

- `services` and `ticker`: **always replace** with the clinic's real treatments (the ticker should match the services).
- `intro` (philosophy line) and `hero_text`: rewrite in the clinic's own tone, or keep the neutral default.
- `tech`: default talks about "clinically validated devices" and "all skin tones". Keep only with a published basis; otherwise `"hide": ["technology"]`.
- `faqs`: copy relevant entries from `templates/aesthetic/defaults.json` and **remove any about treatments they don't offer** (e.g. hair restoration, laser).
- `journey` is generic process copy: fine to keep.
- `before_after`: only their own published, consented cases with real images. Otherwise omit. Never create or retouch results.
- Hide ids: `services journey technology results doctors reviews articles faq`.

## 4. Images and colours

Own photos only, saved to `prospects/<slug>/assets/` (under 300 KB): `images.hero` (portrait or clinic interior; shown in an arch), `images.tech`, doctor `photo`, article `image`. Without photos the rose-tinted placeholders stay.

Colours: the template relies on warm, low-saturation palettes. If the brand is loud, use its deepest shade as `primary` and a softened tint as `accent`. Check contrast of button text.

## 5. Build and check

```bash
python tools/build.py <slug>
```

Resolve every `!` warning. Then check:

- `grep -n "\[[A-Z][A-Za-z ]*\]" prospects/<slug>/site/index.html` finds no leftover brackets.
- Render at 390x844 and 1280x900, English and `ar/`. The ticker scrolls, the numbered rows don't wrap badly with long treatment names, the banner shows clinic and studio, widget buttons go to `#contact`.

## 6. Publish and hand back

`python tools/build.py <slug> --publish`, commit only that folder as `Add demo: <Clinic Name>`, push to `main`, confirm `https://deployed-ars.github.io/clinic-previews/<folder>/` returns 200, then screenshots and the draft email per `clinic-demo`. Keep `"live": false`.
