---
name: clinic-demo
description: Build and publish a website concept demo for a dental, cosmetic surgery or aesthetic clinic from its name and links, then return the live link, email screenshots and a draft cold email. Use when asked to make, build or update a demo or preview for a clinic, or to take one down.
---

# Make a clinic demo

## 1. Get the inputs

Ask only for what's missing. Needed:

- Clinic name and city/area
- At least one link: Instagram, Google Maps listing, or current website
- Tier (A = Instagram only, B = old/broken site, C = modern site). Work it out from the links if not given.
- Decision maker's name if known (for the email)
- Studio name and sender name for the banner and email (ask once, then reuse)

Instagram often blocks automated reading. If a page can't be read, ask the user for screenshots of the profile, logo and 4–6 best posts, or for the image files. Don't guess.

## 2. Gather the facts

From the clinic's own pages, collect and list back to the user in a short block before building:

- Logo, and 2–3 brand colours (from logo or feed): main, dark shade for text, very light tint
- Treatments they actually offer (top 3–6, high-ticket first)
- Lead doctor's name and published qualifications
- Google rating and review count, exactly as shown
- Address, opening hours, phone/WhatsApp as published
- Bio or tagline wording
- Tier B only: 2–3 specific issues with the current site (not mobile-friendly, no booking, slow, broken links, outdated photos, no HTTPS). Note them for the email.

Anything you can't confirm stays out (see CLAUDE.md rule 3).

## 3. Build

1. Copy `_template/` to `<clinic-slug>-<4 random lowercase letters/digits>/`.
2. In its `index.html`:
   - Set `--brand`, `--brand-dark`, `--brand-soft` at the top of the `<style>`. Check text on `--brand` buttons stays readable (4.5:1 contrast).
   - Fill the `<title>`, banner (clinic + studio name), nav logo, hero, treatments, gallery, doctor, reviews, contact and footer with the gathered facts.
   - Save images into the folder and replace each grey `.ph` placeholder with an `<img>` with real `alt` text. Compress to under 300 KB each.
   - Remove sections you have nothing real for rather than leaving brackets, except the hero image slot.
   - Point "Book" and "WhatsApp us" buttons at `#contact` (not the clinic's real booking links).
   - Tier C: replace the homepage content with a single treatment page: what it is, who it's for, the process, results gallery, FAQ from the clinic's own published info, booking call-to-action.
3. Search the file for any remaining `[` placeholders and resolve or remove them.
4. Keep the concept banner and the noindex meta tag. Never remove them.

## 4. Check it

Render with Playwright at 390×844 (phone) and 1280×900 (desktop). Look at both screenshots: nothing cut off, no overlapping text, images load, colours readable. Fix and re-check.

## 5. Publish

Commit only that clinic's folder: `Add demo: <Clinic Name>`. Push to `main`. Live link:
`https://arshadhax.github.io/clinic-previews/<folder>/`

Wait about a minute, then confirm the link loads (HTTP 200).

## 6. Hand back to the user

1. The live link.
2. Email screenshots saved in `screens/<folder>/` (gitignored): `hero-mobile.png` and `hero-desktop.png`, first screen only, under 200 KB each. Tier B: also `before-after.png`, their current homepage beside the demo.
3. A draft Email 1 in the matching tier template below, under 120 words, first line specific to this clinic.

### Email 1 templates

**Tier A — subject:** [Clinic] website concept
> Hi Dr [Last name],
> I came across [Clinic] through your Instagram — [specific genuine observation about a recent post or treatment].
> I noticed you don't have a website yet, so patients searching "[treatment] in [area]" on Google find other clinics, and Instagram can't take a booking at 11pm.
> I put together a quick concept of what a [Clinic] site could look like, in your branding:
> [hero image]
> Full preview: [link]
> Happy to walk you through it in 15 minutes this week if it's useful.
> [Sender] · [Studio] · [WhatsApp]
> Not relevant? Reply "no" and I won't contact you again.

**Tier B — subject:** A refresh idea for [Clinic]
> Hi Dr [Last name],
> I was looking at [Clinic]'s website and noticed [issue 1] and [issue 2].
> With [X] reviews on Google, the site is underselling you. I mocked up how your homepage could look:
> [before/after image]
> Full preview: [link]
> Worth a 15-minute look this week?
> [Signature + opt-out line]

**Tier C — subject:** [Treatment] page for [Clinic]
> Hi Dr [Last name],
> Your site looks great. One gap: [treatment] doesn't have its own page with results and booking, which is usually where high-value enquiries convert.
> I drafted one in your branding: [link]
> Open to a quick chat?
> [Signature + opt-out line]

Use only facts gathered in step 2. If there's no doctor's name, open with "Hi [Clinic] team,".

## Taking a demo down

When the user says a clinic wants its demo removed: `git rm -r <folder>`, commit `Remove demo: <Clinic Name>`, push, and confirm the link now returns 404.
