---
name: li-audit
description: >-
  Post-mortem on what the user has already published: which posts worked, why,
  and what to stop doing, ranked by engagement rate and reach multiple, not
  impressions. Feeds the findings into the next week's plan. Use when the user
  pastes LinkedIn analytics or past posts and asks "what's working", "why did
  this flop", "read my analytics", "audit my content", or what to double down on.
  For checking a draft before it's published, use /li-human --audit instead.
---

# li-audit

The only honest source of what works for an account is that account. Every
rule in this bundle, `../../shared/algorithm.md` included, is a prior. The user's own last
20-30 posts are the evidence.

## Input

Whichever the user has:
- The analytics export (LinkedIn: Analytics → Content → Export), CSV or XLSX.
- A screenshot per post with impressions, reactions, comments, reposts.
- Just the posts and their reaction counts (enough for a first pass).
- The engagers summary from `/li-engagers`, if it ran.

Also read `~/.claude/linkedin/log.md` for the hook and angle each post used,
and the follower count at the time.

Work the numbers in code (a short Python script; pandas and openpyxl read
the export), not in your head, and show the working. On Windows run
`python`, not `python3`.

## Measure these, not impressions

Raw impressions mostly reflect how many people already follow you.

| Metric | How | What it tells you |
|---|---|---|
| **Engagement rate** | (reactions + comments + reposts) / impressions | did the post earn its reach |
| **Comment ratio** | comments / reactions | did it start something or just get a nod |
| **Reach multiple** | impressions / follower count | did it travel past your existing audience |
| **Save / send rate** | if available | the strongest predictor of future reach |

Rank by engagement rate and reach multiple. A post with 900 impressions and
40 comments beat the one with 12,000 impressions and 6.

Compare against the follower-count band in `../../shared/algorithm.md`
before calling anything a flop. Under 1K followers, compare against the
user's own median instead.

## Find the pattern

Put the top 5 and bottom 5 side by side and look for what separates them. Be
willing to conclude something the user won't like.

1. **Hook** (H01-H40 from log.md): which are in the top 5?
2. **Angle** (S1-S9).
3. **Format:** text, carousel, image, poll.
4. **Value vs story vs light** (the voice.md mix).
5. **Length.**
6. **First-hour replies:** posts the user replied to within an hour vs not.
7. **Day and time: check last,** and only if nothing above explains it. It's
   almost never the cause, and it's where people want it to be.

State each finding as a claim with the evidence and how confident it is.
With 30 posts you can see a pattern. With 6 you can't, and you should say
that instead of inventing one.

## Output

```
AUDIT  ·  {{N}} posts  ·  {{date range}}  ·  {{followers}} followers

TOP 5 BY ENGAGEMENT RATE
  {{rate}}  {{hook}}  {{angle}}  "{{first line}}"   {{impressions}} imp
  ...

BOTTOM 5
  ...

WHAT THE DATA SAYS
1. {{finding}}: {{evidence}}. n={{N}}. Confidence: {{high/medium/low}}.
2. ...
3. Day of week shows nothing. Stop optimising it.

STOP:     {{one thing}}
DO MORE:  {{one thing}}
```

Then:
- Fill the results columns in `~/.claude/linkedin/log.md`.
- Hand the findings to `/li-plan` so next week is built on the user's own
  evidence instead of defaults.
- Once there are 20+ logged posts, tell the user their own data now
  outranks `../../shared/algorithm.md` wherever the two disagree.
