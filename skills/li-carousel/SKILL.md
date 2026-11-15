---
name: li-carousel
description: >-
  Build a LinkedIn document post (carousel): slide-by-slide copy, the cover that
  earns the swipe, the 2-3 lines of post text above it, and the PDF to upload.
  Use when the user says "carousel", "document post", "slides for LinkedIn",
  "turn this into a carousel", or has a list- or step-shaped idea that would die
  as a text post.
---

# li-carousel

Document posts are one of the highest-reach formats (about 1.7-2.3x a single
image; much higher engagement than text when they're 6-9 tight slides). A
swipe counts as engagement; a scroll doesn't. The format rewards one idea in
steps. It punishes a text post chopped into pieces.

## When to use it instead of a text post

Use a carousel when the idea has **sequence**: steps, a framework with parts,
a before/after, a teardown screen by screen, a checklist. Use a text post
when the idea is one claim. If the user has one claim, say so and hand them
to `/li-post`.

Good builder fits: startup teardowns (S3, H16), exact setups (S2, H40),
open-source drops (S5, H07), build logs (S1, H08).

## Structure: 7-10 slides

Under 6 is a text post. Past about 10, completion drops off.

```
1      COVER     the hook, 6 words or fewer, plus one line of promise
2      STAKE     why this matters, one sentence (a number if you have one)
3..N   ONE IDEA PER SLIDE: headline of 3-7 words, at most ~25 words under it
N+1    RECAP     the whole thing as a list, so the screenshot is useful alone
LAST   CTA       one action: follow, save, or "template in the comments"
```

## Slide rules

- **The cover is most of the result.** Six words, big. The rest can't save a
  cover nobody swipes.
- **Number every slide** (3/9). Completion goes up when people can see the end.
- **No paragraphs.** If a slide needs more than ~25 words, it's two slides.
- **The recap slide is what people screenshot.** Make it stand alone.
- **Handle on every slide**, small, bottom corner. Screenshots travel
  without you.
- **Type no smaller than 28px.** People read these on a phone at thumbnail
  size.
- Density rule (`../../shared/rules.md` §4) applies to the whole deck: one
  contrast, one triple.

## Making the PDF

LinkedIn wants a PDF, **1080x1350 (4:5)**, under 100MB.

1. Write one HTML file with one `<section>` per slide:
   `width:1080px; height:1350px; page-break-after:always; overflow:hidden`.
2. One accent colour, a plain background, one font. If voice.md or the
   project has a brand colour or design system, use it. Don't invent a
   palette.
3. Print to PDF with Playwright using the installed Edge (no Chromium
   download): `python -m pip install playwright`, then
   `p.chromium.launch(channel="msedge")` and
   `page.pdf(width="1080px", height="1350px", print_background=True)`.
   Save it to `~/.claude/linkedin/images/{{yyyy-mm-dd}}-{{slug}}.pdf`.
4. Open the PDF and check every page before handing it over: no overflow,
   no cut-off text, page count = slide count.

## Output

1. The slide-by-slide copy as a numbered list the user can read in 10 seconds.
2. The **post text** above the carousel (2-3 lines: this is the real hook in
   the feed), run through `/li-human`.
3. Only after the user approves the copy: build the PDF and send it.

Once approved, `/li-post` queues it like any post, with the PDF as the
attachment, and `/li-publish` uploads it at the planned time.
