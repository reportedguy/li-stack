---
name: li-human
description: >-
  Remove AI tells from any LinkedIn draft (post, comment, reply, DM) and score it
  before it goes out. Runs two local scripts, then a judgement pass for what
  scripts can't fix. Also checks an unpublished draft without rewriting (--audit)
  and builds voice.md from the user's own posts (--profile). Use whenever text
  needs to sound human, when the user says humanize, de-AI, "does this sound like
  AI", "check this draft", "check before I post", or before any skill in this
  bundle shows the user a draft. For posts already published, use /li-audit.
---

# li-human

The humanizer. Every other writing skill runs its draft through this before
the user sees it. Rules it enforces: `../../shared/rules.md` §3-4.

**What it's for:** removing what human readers and LinkedIn's "AI slop" report
button react to (stock vocabulary in clusters, reveal bridges, staccato
rhythm, announced candor, stacked contrasts).

**What it's not for:** beating GPTZero, Pangram or Turnitin. No edit reliably
does that, and on a 200-word post their scores are noise. Never tell the user
a draft is "undetectable".

## Modes

| Mode | Does |
|---|---|
| default | clean + flag + rewrite flagged lines + score |
| `--audit` | flag + score only, no rewrite. Pre-publish check on a finished draft |
| `--profile` | read 3-6 of the user's own posts and fill or update `~/.claude/linkedin/voice.md` §5-6 |
| `--kind comment`, `reply`, `dm` | any mode, for short text: sets the length target and skips post-only checks. Passed straight to both scripts |

## The two scripts (in this skill's folder, no dependencies)

Run them by full path from this skill's base directory (the folder this
SKILL.md is in). On Windows the command is `python` (`python3` is often the
Microsoft Store stub); `py` also works. The scripts print UTF-8 themselves,
so ₹ and emoji are safe in any console.

```bash
python humanize.py draft.txt -o clean.txt --report   # mechanical fixes + flags
python humanize.py draft.txt --check                 # flags only, change nothing
python detect.py draft.txt clean.txt                 # score before → after
# add --kind comment | reply | dm for short text
```

Write the draft to a temp file first. Run with `python -I` if the folder
holds anything you didn't write.

**What `humanize.py` fixes by itself:**
- Invisible characters (zero-width spaces, word joiners, BOMs, tag characters)
- Curly quotes, ellipsis characters, bullet characters
- Em dashes **above the cap** (about 1 per 100 words, max 2), turned into
  commas. It keeps the first ones. Zero dashes is not the goal.
- Stock phrases that carry no meaning ("in today's fast-paced world",
  "let that sink in", "testament to", "game-changer")

**What it flags for you to rewrite** (shapes need judgement, so the script
never touches them):
- **Dense paragraphs:** 3+ marker words (leverage, robust, crucial, insights,
  seamless, foster…) in one paragraph. One is English; three is a signature.
- **Blockers:** question as line 1, "Here's how" as line 1, "The result?",
  "Plot twist:", "Stop X, start Y", "Let me be honest", staccato runs,
  "No X. No Y. Just Z.", one-word paragraphs, comment-gates, announcement
  openers, hashtag walls, all-caps line 1, 2+ contrasts.
- **Warnings:** a single contrast, triads, more than 2 fragments,
  machine-flat paragraphs, long/short seesaw, bait closers, link in body.
- **Notes:** open `{{placeholders}}`, length outside the target.

## Order of operations (default mode)

1. **Scripts.** `humanize.py draft.txt -o clean.txt --report`.
2. **Rewrite every blocker and dense paragraph by hand**, in the user's
   register from `voice.md`, not a generic "plain" register:
   - Reveal bridge → delete it; the next sentence was the point.
   - "It's not X, it's Y" (when it's the second contrast) → two plain
     declaratives.
   - Staccato run → one real sentence with a working clause.
   - Dense paragraph → rewrite the paragraph, don't swap words one by one.
     Never replace a marker with another marker ("leverage" → "harness").
   - Announced candor → delete the announcement, keep the flat fact. If no
     fact follows it, ask the user for one.
   - Question line 1 → the number that answers it; question moves to the close.
3. **Specifics check.** The draft needs at least one number with what it
   measures, one named thing (person, company, tool, date), and one
   first-person concrete detail. If missing, ask. Never invent.
4. **Over-correction guard.** Re-read once and undo anything you made worse:
   - Did you create fragments, one-word lines or a seesaw? Merge back.
   - Did you add a hedge, a confession frame or "honestly"? Remove it.
   - Did you flatten the user's voice: every em dash gone, every triple gone,
     no reaction left, every long sentence chopped? Restore it.
   A clean draft gets 2-3 touches, not a quota. When unsure whether a
   pattern is the user's or the model's, leave it.
5. **Score.** `detect.py draft.txt clean.txt`. PASS needs 70+ overall, no
   check under 55, and no blockers. Two rounds is normal. If it takes five,
   the draft was written by formula: write a different draft.
6. **Show the cleaned text and the score together.** Never the score alone.

## --audit (no rewrite)

Run `humanize.py draft.txt --check` and `detect.py draft.txt`, then add the
checks scripts can't do:

| Check | Pass when |
|---|---|
| Hook | Line 1 is a statement or number, makes sense alone, fits in ~140 chars |
| Payoff | Line 2 pays off line 1 instead of setting up line 3 |
| One idea | The post makes one point. Two ideas = two posts |
| Specifics | Every abstract line is paid off by a specific within two lines |
| Close | One specific question OR one instruction, not both, not "Thoughts?" |
| Truth | Every number is in `story-bank.md` or was given by the user |
| Value | The reader can do something within 60 seconds of finishing (voice.md bar) |
| Links | None in the body; "link in first comment" if needed |

Output: `BLOCKERS` (must fix), `WARNINGS` (should fix), `FIXES` (one line
each), then the score.

## --profile (build voice.md)

1. Ask for 3-6 posts or long comments the user actually wrote. Not ones an
   AI wrote for them.
2. Pull out: sentence rhythm, signature openers, punctuation habits, words
   used a lot, words never used, emoji habits, formatting, how they close.
3. Show the findings and let the user correct them.
4. Update §5-6 of `~/.claude/linkedin/voice.md`. Never delete what the user
   wrote there; add under it and mark what changed.

## The lexicon

`slop.json` holds the stock phrases (`auto`), the marker words (`density`)
and the structural patterns (`structures`), each with a fix. It's meant to be
edited. If the user uses a word on purpose, delete it from the file.

## Credit

Scripts based on Jake Schincariol's `humanize.py` / `detect.py`
(linkedin-agent-skill, MIT). Rules from Serge Bulaev's Humanizer V3
(linkedin-skills, MIT).
