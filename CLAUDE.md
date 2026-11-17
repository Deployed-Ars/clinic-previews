# Clinic previews — project instructions

This repo hosts **website concept demos** for cold outreach to dental, cosmetic surgery and aesthetic/dermatology clinics. Each clinic gets a free one-page demo of a modern website in its own branding. The demo link goes in a personalised cold email, followed up on WhatsApp.

Live site: `https://deployed-ars.github.io/clinic-previews/<clinic-folder>/` (GitHub Pages, `main` branch, root). A push to `main` goes live in about a minute.

To make a demo, follow the `clinic-demo` skill in `.claude/skills/clinic-demo/SKILL.md`.

## Repo layout

- `_template/index.html` — the original one-file base demo. Copy it for every new clinic; never edit a clinic's demo into the template.
- `templates/` — the three variable-driven templates (`dental`, `aesthetic`, `cosmetic-surgery`) plus shared parts. Rendered by `python tools/build.py <slug> --publish`; see `templates/README.md`. The build adds the concept banner and noindex automatically. Change a template only when the change should apply to every clinic of that type.
- `demo-dental/`, `demo-aesthetic/`, `demo-cosmetic-surgery/` — live previews of the three templates with placeholder content only (no real clinic).
- `tools/` — `build.py` (templates to static site), `prospect.py` (intake: colours, Google details).
- `prospects/` and `references/` — local working data (intake, screenshots, per-clinic `site.json`, design notes). Gitignored; never commit them.
- `<clinic-slug>-<4 random chars>/` — one folder per clinic, e.g. `bright-smile-dental-7f3k/`. The random suffix stops people guessing other clinics' links.
- `index.html`, `robots.txt`, `.nojekyll` — keep the site out of search engines and make GitHub publish folders starting with `_`. Don't remove them.
- `screens/` — email screenshots. Gitignored; never commit it.

## Rules that always apply

1. **Every demo keeps the concept banner** at the top: "Website concept prepared for [Clinic] by [Studio]. This is a proposal, not the clinic's live site." Never make a demo that could pass as the clinic's real site.
2. **Every demo keeps** `<meta name="robots" content="noindex, nofollow">`.
3. **Only real facts.** Use names, treatments, ratings, review counts, photos, addresses and qualifications only as the clinic itself publishes them (its website, Instagram, Google Business Profile). Never invent reviews, testimonials, prices, before/after results, credentials or statistics. If a fact can't be confirmed, leave it out or keep a clearly marked `[PLACEHOLDER]`.
4. **Photos:** use the clinic's own published images, saved into its folder (not hotlinked). If you can't get them, keep the template's labelled placeholders. No stock photos of people presented as the clinic's patients or staff.
5. **Takedowns:** if the user says a clinic asked for its demo to be removed, delete the folder and push straight away.
6. The repo is **public**. Don't commit lead data, contact details beyond what the clinic publishes, notes, or email drafts.

## The outreach this supports

Clinics are tiered by their current web presence, and the demo's focus follows the tier:

| Tier | Current presence | Demo focus |
| --- | --- | --- |
| A | No website, Instagram only | Full homepage built from their Instagram: logo, colours, best posts as gallery, treatments, Book Now |
| B | Old or broken website | Full homepage, plus a side-by-side screenshot of their current homepage vs the demo for the email |
| C | Modern website | One high-value treatment page (e.g. veneers, rhinoplasty, laser), not a full rebuild |

Target time per demo: 15–20 minutes. Volume: 10 a day.

## Commits

Commit each clinic as its own commit: `Add demo: <Clinic Name>`. Push to `main`.
