# algorithm.md — what the 2026 feed rewards

Use this as background, not law. Every number here describes someone else's
corpus. Your own `log.md` beats all of it after about 20 posts
(`/li-audit` tells you when).

**Evidence tags:**
- **[platform]** LinkedIn's own statements or press coverage of them
- **[crowd]** analytics-tool aggregates (AuthoredUp, 3M posts, Mar 2025-Feb 2026)
- **[vendor]** single-vendor studies (MagicPost, 1.2M posts; proprietary scoring)
- **[consensus]** crowd-sourced AI-tell lists (Mollick, Forbes, tropes.fyi)
- **[reported]** widely repeated, no primary source found. Directional only.

Sources: Serge Bulaev's linkedin-skills research (360Brew paper arXiv
2501.16450, AuthoredUp, MagicPost, van der Blom 2026) and Jake Schincariol's
linkedin-agent-skill.

---

## The first line

| Move | Effect | Tag |
|---|---|---|
| Odd-precision number in line 1 ("41%", "$873", "14 March") | +34% median likes | [vendor] |
| Question as line 1 | -34% median likes, every follower band | [vendor] |
| "Here's what / here's how" opener | -4.3% | [vendor] |
| "Stop X, start Y" frame | -6.7% | [vendor] |
| "It's not X, it's Y" as the post's frame | -4.9% | [vendor] |
| "The result?" / "Plot twist:" bridge | -4.8% | [vendor] |
| "How I" instead of "How to" | 2-3x | [reported] |
| Real failure in the first 3 lines | outperforms polished framing | [reported] |

**Truncation:** about **140 characters on mobile**, about 210 on desktop,
before "…see more". Write for 140.

## The close

| Move | Effect | Tag |
|---|---|---|
| Specific closing question | +3%, and 20-40% more replies than "Thoughts?" | [vendor] / [reported] |
| P.S. line with a real follow-up | +7.5% | [vendor] |
| Comment-gate ("comment X to get Y") | named target of the March 2026 authenticity update | [platform] |
| "AI slop" report button (Jul 2026) | flagged posts lose about 40% of views | [platform] |
| Reflex bait ("Agree?", "Thoughts?", "Tag someone") | suppressed | [platform] |

## Length and layout

- **Sweet spot 900-1,300 characters** (150-220 words). 1,000+ characters is
  1.18x reach; 20+ sentences is 1.14x [crowd].
- Under 400 reads as a thought. Over 2,000 has to earn every line.
- 1-2 sentence paragraphs with blank lines between them: the recommended
  mobile layout, not an AI tell [crowd].
- Hard limit: 3,000 characters.

## Formats

| Format | vs. single image | Tag |
|---|---|---|
| Document carousel (PDF) | 1.7-2.3x reach; ~6x engagement vs text with 6-9 slides | [crowd] |
| Multi-image (3-4 real photos) | 6.6% engagement rate, the highest format | [crowd] |
| Poll | +206% reach vs average post | [crowd] |
| Text-only | 1.0-1.3x | [crowd] |
| Single image | now ~30% below text-only | [crowd] |
| Native video (30-90s, captioned, 9:16) | reach -35% YoY, still works with a strong hook | [crowd] |
| External link in body | 0.4-0.6x | [crowd] |

## Hashtags and links

- 0 hashtags performs as well as 5+. 1-3 niche tags give ~5%. 5+ look spammy
  [crowd]. The ranker reads meaning, not tags.
- Link in the first comment: about 2.1x impressions vs in-body [crowd].

## What the ranker weights (reported, not confirmed)

- A save is worth about 5 likes; a long comment about 4 one-word reactions.
- Comments outweigh likes about 3x. Back-and-forth threads get about 3x reach.
- Dwell time sweet spot: 31-60 seconds. Opening "see more" then leaving in
  under 3 seconds counts as clickbait.
- The first 60-90 minutes decide most of a post's reach. Replying to every
  real comment in that window matters.

## Timing

- For an Indian founder/builder audience: **Tue-Thu, 8:00-10:00 IST**,
  with 12:30-14:00 IST as a second slot. This is the general B2B
  "at a desk" default moved to IST, not a measured Indian dataset, so let
  your own `log.md` overrule it. For a US audience: Tue-Thu 8:00-10:00 ET.
  Always use the audience's timezone, not yours.
- Weekends: personal stories or nothing.
- **Timing matters far less than line 1.** Fix hooks before you touch the clock.

## Penalties to avoid

- **Engagement pods and coordinated commenting:** detected and suppressed
  [platform]. Signs: 15+ comments inside 90 seconds, the same accounts at the
  same minute every day.
- **Recycled reply templates** on your own post read as automation.
- **2+ posts a day** split your own reach. 3-5 a week is the range.
- **Big edits in the first 3 hours** (over ~20% of the text) can reset
  distribution [reported]. Typo fixes are fine after the first 90 minutes.

## Benchmarks by follower count

| Followers | Typical engagement rate |
|---|---|
| 1K-5K | 4-8% |
| 5K-10K | 3-5% |
| 10K-50K | 2-4% |
| 50K+ | 1-3% |

Under 1K followers there's no reliable band: samples are too small. Compare
against your own last 10 posts instead.

Engagement rate = (reactions + comments + reposts) / impressions. Check
against your band before deciding a post "flopped".
