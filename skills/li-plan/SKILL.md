---
name: li-plan
description: >-
  Plan the LinkedIn week: one post a day across the seven founder/builder
  pillars, each with its hook, goal, time and story-bank material, plus a daily
  engagement list (who to comment on and like), founders to discover, and up to
  one reshare a day. Use when the user says "plan my week", "what should I
  post", "content calendar", "I have nothing to post about", or wants a posting
  schedule and an engagement list.
---

# li-plan

The control room. Everything else in the bundle executes; this decides what
gets executed. Run it once a week, same day each week (Saturday works: the
week starts Sunday).

## Read first

- `~/.claude/linkedin/voice.md`: pillars and material, mix, schedule,
  Hinglish, `reshare_auto`.
- `~/.claude/linkedin/story-bank.md`: the material each slot draws from.
- `~/.claude/linkedin/log.md`: the last 2 weeks (don't repeat a hook or a
  story) and what worked (`/li-audit` findings outrank the defaults).
- `~/.claude/linkedin/watchlist.md`: the founders and builders to engage.
- `../../shared/angles.md` (S1-S9), `../../shared/hooks.json`,
  `../../shared/algorithm.md` (timing).

If the story bank is empty, say once that `/li-interview` fills it, then ask
four things in one message:
1. What actually happened this week (built, shipped, broke, learned, a
   number, a conversation)?
2. Anything coming up (a launch, a release, an event)?
3. Any resource you made that you'd give away?
4. Any startup decision you noticed and have an opinion on?

## What to post

**Default: 7 posts, one a day**, following the pillar for each day in
`angles.md` (S1 Mon … S7 Sun). Never 2 in one day: it splits your own reach.
If a slot has no real material, say so and offer a swap (S8 Reaction, S9
Founder Conversation) or an empty day, never a filler post. Fewer real posts
beat seven thin ones; after 3-4 weeks `/li-audit` can show whether 7 is
paying off.

**Checks before you hand it over:**
- [ ] Every slot names its **angle (S1-S9)**, **hook (H01-H40)**, **goal**
      and **story-bank section**
- [ ] No hook repeated inside 7 days (check log.md)
- [ ] No app or story carries more than one post this week
- [ ] All four goals covered (comments, reposts, likes, saves)
- [ ] At least one post has a real stake (a cost, a failure)
- [ ] At least one post gives something away whole
- [ ] No slot needs a number that isn't in the bank or from the user

Give each slot an **angle, not a topic**. "AI" is not a plan. "The CLAUDE.md
that cut my build time from {{N}} days to {{N}} hours" is a post.

## Format mix

Text by default. A carousel (`/li-carousel`) when the idea has steps; an
image when `/li-post` says one earns its place; a poll at most once a
fortnight. See `../../shared/algorithm.md`.

## When to post

The audience's timezone (voice.md). India default: Tue-Thu 8:00-10:00 IST
for the heavy posts, other weekdays 8:30-9:30 IST, weekends 10:00-12:00 IST
for the lighter ones. **The hour matters far less than line 1.**

## Who to engage with (daily)

Build a list from `watchlist.md`. If it has fewer than 20 people, offer to
find more with Agent Reach (`mcporter call linkedin.search_people
keywords="founder AI" location="India"`, a few searches at most, inside the
40-reads-a-day cap in `../../shared/rules.md` §5). Show the candidates; add
only the ones the user picks.

Per day, about **7 comments and 9 likes**, spread across:
- **reach:** founders and builders with the audience you want. Comment
  before they have 20 comments.
- **peers:** builders at your level who reply and reciprocate.
- **targets:** founders you'd like to know. Comment for weeks before any DM;
  never pitch in a comment.

Spread across people and days so it doesn't look like a pod. Comments are
drafted by `/li-comment`; the user likes and pastes by hand.

## Reshares

Suggest at most one reshare a day: a post from the watchlist that the user's
audience would genuinely want, with a one-line take (`/li-comment` reshare
mode). If `reshare_auto` is on in voice.md, put it on the plan and
`/li-publish` sends it at its time; otherwise mark it "needs approve".

## Output

```
WEEK OF {{date}}

SUN  10:30 IST  S7 Chaos Diary       H35 Chaos Log        "{{angle}}"   bank: Recurring stories   goal: likes
MON   8:45 IST  S1 Build Log         H08 Receipt          "{{angle}}"   bank: Shipped             goal: comments
TUE   8:30 IST  S2 Built with AI     H32 Time Saved       "{{angle}}"   bank: Resources           goal: saves     image
WED   8:30 IST  S3 Startup Teardown  H38 Problem Reframe  "{{angle}}"   bank: Positions           goal: reposts
THU   8:30 IST  S4 Builder Take      H01 Contrarian       "{{angle}}"   bank: Positions           goal: comments
FRI   9:00 IST  S5 Open-Source Drop  H07 Steal This       "{{angle}}"   bank: Resources           goal: saves     carousel
SAT  11:00 IST  S6 Business Lessons  H25 Insider View     "{{angle}}"   bank: Timeline            goal: likes

ENGAGE (daily, ~7 comments / 9 likes)
  reach:   {{names}}
  peers:   {{names}}
  targets: {{names}}

RESHARES  WED  {{author}}'s post on {{topic}}  (auto)

CHECKS  ✓ hooks unique  ✓ 4/4 goals  ✓ stake  ✓ giveaway  ✓ one post per app

Say "write Tuesday" and I'll draft it.
```

Write the plan to `~/.claude/linkedin/plan.md` so `/li-post` and
`/li-monitor` can read it. Posts are only queued after the user approves each
one in `/li-post`.
