---
name: li-interview
description: >-
  Interview the user for the raw material posts are made of. Bank mode builds a
  lasting Story Bank (projects, internships, case comps, receipts with numbers,
  turning points, scars, positions, resources). Post mode runs a short interview
  on one topic and hands a five-line spine to /li-post. Use when a draft has
  nothing concrete to draw on, the story bank is empty or stale, or the user says
  "interview me", "ask me questions", "help me figure out what to post".
---

# li-interview

Every writing skill demands specifics: a number with what it measures, a
dated moment, a position someone would argue with. When the user hasn't
given them, the rule is to ask, not invent. This skill does the asking
properly, once, and keeps the answers.

| | `voice.md` | `story-bank.md` |
|---|---|---|
| Holds | how you sound | what you have to say |
| Built by | you + `/li-human --profile` | this skill |

Writes to `~/.claude/linkedin/story-bank.md` (template:
`../../templates/story-bank.md`). It lives outside the bundle so it never
gets pushed to git.

## Modes

### `--mode bank` (default): 20-40 minutes, resumable

1. **Read what exists.** If the bank has material, interview only the thin
   sections. Never re-ask something already answered.
2. **Open wide, not with a form.** "What have you been working on that you
   can't stop thinking about?" beats "List your achievements". Follow what
   they get animated about.
3. **Press every soft answer once.** This is the whole job:
   - "it improved a lot" → "by how much, measured how, over what period?"
   - "a while back" → "which month?"
   - "a big client" → "can I name them, or keep it anonymous?"
   Press once, accept the answer, move on. Twice is an interrogation.
4. **Chase the reversal.** What did you believe a year ago that you don't
   now, and what did it cost to find out? Turning points and scars carry
   posts better than wins.
5. **Find the position.** What do you think is true that most builders or
   founders around you disagree with? What does holding it cost?
6. **Collect resources.** What have you made that you'd hand to anyone
   (templates, notes, prompts, repos)? These feed S7 / H07.
7. **Settle names and limits explicitly.** Who and what can appear in
   public, who can't, what stays out entirely (NDA work, a past employer's
   numbers). Ask; never infer.
8. **Write the bank.** Keep their phrasing verbatim where it's vivid, set
   `filled: yes`, date it, and list the thin sections.
9. **Show what it unlocks:** name 2-3 specific posts (angle + hook) the new
   material could produce.

### `--mode post`: 5-8 questions on one topic

1. Take the topic, or offer three from the bank.
2. **The moment, not the theme:** "When did this last actually happen?"
3. **The number and the date.** Don't proceed on "recently" or "a lot".
4. **What you got wrong** at the time.
5. **Who disagrees** (this names the audience).
6. **What the reader should do differently** (this is the close).
7. **Read back the spine** and let them correct it. Their correction is
   usually the best line in the post; keep it verbatim.

| Line | Holds |
|---|---|
| **Moment** | the scene and its date |
| **Number** | one figure, what it measures, how it was measured |
| **Correction** | what they believed before, and what changed it |
| **Opposition** | who disagrees |
| **Ask** | what the reader should do differently |

A line with nothing real stays **empty and labelled empty**. Hand the five
lines to `/li-post` verbatim, and append anything concrete to the bank.

## Questions that work (by section)

- **Timeline:** "What were you brought in to do, and what did you end up
  doing?" · "Which month did that start?"
- **Receipts:** "Put a number on that, even a rough one, and say it's rough."
  · "What was it before, and after?" · "How long, how many people?" · "How
  would you prove it to someone who doubted you?"
- **Shipped:** "What exists now that wouldn't if you hadn't built it?" ·
  "Which part was actually yours?" (stops a post claiming a team's work)
- **Turning points:** "What did you have to be talked out of?" · "When did
  the plan change under you?"
- **Scars:** "What's the most expensive mistake you've made on a project?" ·
  "What do you check now that you never used to?" Ask once, don't press.
- **Positions:** "What advice does everyone give builders that you think is
  wrong?" · "Who'd argue with you, and what would they say?"
- **Recurring stories:** "Which 3 stories do you already tell people?"

**Questions that waste the session:** "Tell me about yourself" (a CV),
"What are your strengths?" (adjectives), "What makes you unique?"
(hedging), "Describe a challenge you overcame" (a rehearsed answer).

## Hard rules

- **Never invent an answer** or fill a gap with a plausible one. An
  unverified number in the bank becomes an unverified number in a post.
- **One question at a time.** Stacked questions get the last one answered.
- **Their words, not yours.** Paraphrase loses what made it usable.
- **"I'd rather not say" ends that line for good.** Record it under Off
  limits so nothing asks again, and say you've done so.
- Don't fill the bank from a LinkedIn profile or resume instead of the
  person. A profile lists roles; an interview gets what happened inside them.
- Don't write the post. That's `/li-post`.

Credit: adapted from Serge Bulaev's linkedin-interviewer (MIT).
