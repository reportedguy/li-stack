---
name: li-post
description: >-
  Write a LinkedIn post from a raw idea in the user's own voice, using the
  40-hook library and the founder/builder angle library, humanized before it's
  shown. Produces three hook options, one full draft and a copy-ready block.
  Suggests an image prompt when an image would help, and queues the approved post
  for /li-publish. Use whenever the user wants a LinkedIn post, a hook, "post
  about X", "turn this into a LinkedIn post", "write Tuesday" from a plan, or
  hook options for an idea.
---

# li-post

One true thing → one post that sounds like the user and leaves the reader
with something they can use.

## Read first (every time)

1. `~/.claude/linkedin/voice.md`: tone layer, value layer, pillars, mix,
   formats, hard rules. If missing, set it up per `../../shared/rules.md` §1.
2. `~/.claude/linkedin/story-bank.md`: take numbers, dates and names from
   here instead of asking. If it's empty, say once that `/li-interview`
   fills it, then carry on.
3. `../../shared/hooks.json` (40 hooks), `../../shared/angles.md`
   (S1-S9), `../../shared/rules.md`.
4. `~/.claude/linkedin/swipe.md` if it exists: real examples of the hook
   you pick.
5. `~/.claude/linkedin/plan.md` and `log.md` if they exist: what this slot
   is for, and which hooks were used in the last 7 days.

## Step 1: get one true thing

A post needs **one moment with a date** and **one number with what it
measures**. If the idea is thin ("post about AI"), don't pad it. Ask one
batched question:

> What happened, when, and what did it cost or return (a number)?

If the user wants to go deeper, hand off to `/li-interview --mode post`. A
five-line spine (Moment, Number, Correction, Opposition, Ask) from it is the
skeleton: don't re-ask anything it already has, and leave empty lines empty.

## Step 2: pick the angle and the goal

- **Angle:** match the idea to S1-S9 in `../../shared/angles.md`.
- **Goal:** comments, reposts, likes or saves. Take it from `plan.md` if the
  slot has one, otherwise from the voice.md mix (out of every 4 posts:
  2 value, 1 story, 1 light). Value posts usually aim for saves.

## Step 3: three hooks, not one

Shortlist from `../../shared/hooks.json` → `goals[goal]` ∩ the angle's hook list.
Choose **three different formulas** (not three versions of one), skip any
used in the last 7 days, and read each one's `trap` and `note_2026`.

```
HOOKS
1. H32 Time Saved     I built {{feature}} in {{N}} hours with Claude Code. By hand it took {{N}} days.
2. H40 Exact Setup    The (exact) CLAUDE.md setup I use for every new app, in 4 steps:
3. H10 Comparison     Same feature, two ways: {{N}} hours by hand, {{N}} with an agent. What changed:

Shipping #1: it's your own number, line 1 is a number, and builders save it.
```

## Step 4: draft on the strongest hook

**Shape:**
```
Line 1    the hook. Alone. Inside ~140 characters. Statement or number, never a question.
Line 2    pays off line 1. Not setup for line 3.
Body      1-2 sentence paragraphs, blank line between each. The white space is the format.
The turn  one line that reframes what came before.
Value     the step / template / number the reader can use within 60 seconds.
Close     one specific question OR one instruction. Never both.
P.S.      optional, only for a real follow-up ("template in the first comment").
```

**Rules on top of `../../shared/rules.md`:**
- **One idea per post.** Two ideas = two posts. Say so.
- **Length:** whatever the user asked for. Default 900-1,300 characters.
  If they asked for long (1,500-1,900), write long. Hard limit 3,000.
- **Value bar (from voice.md):** a value post passes only if someone could
  act on it from their phone. Name the tool, the field, the step, the number.
- **Tone layer:** one self-roast line max, hype the reader not yourself,
  Hinglish and CAPS as voice.md says (default 0-2 words, one CAPS word).
- **Self-promo:** one mention of your own project, only as the natural
  conclusion, never the pitch.
- **Every post needs one real stake:** a cost, a failure, a risk, a number
  you're not proud of. Pure insight doesn't land.
- **Never fabricate.** A missing number stays `{{my number}}` and gets flagged.

## Step 5: humanize

Write the draft to a temp file and run `/li-human` (default mode) on it.
Every draft ships humanized. Fix blockers before showing anything.

## Step 5b: image or not

If voice.md says `image_every_post: yes`, every post gets one; otherwise
suggest an image only when it earns its place: a real screenshot of the
app, a before/after, a diagram of steps, a chart of real numbers. Never
prompt for a fake realistic photo of people or events. Not for
opinion posts (S4) or light posts that work as text. Multi-image posts with
real photos and carousels outperform single stock-looking images
(`../../shared/algorithm.md`), so prefer the user's own screenshot when one
exists.

When you suggest one, give a **complete, paste-ready prompt** the user can
drop into any image generator:

```
IMAGE  (optional, suggested because: {{reason}})
file name:  {{yyyy-mm-dd}}-{{slug}}.png  →  save to ~/.claude/linkedin/images/
size:       1200x1200 (square) or 1080x1350 (portrait)
prompt:     {{subject}}, {{composition}}, {{style: flat / photo / diagram}},
            {{colours from voice.md or the app's brand}}, {{any text on the
            image, max 6 words, spelled exactly}}, no logos of other
            companies, no fake UI numbers
```

Never put a number in an image prompt that isn't in the post. If the image
is a screenshot of the user's app, say "use a real screenshot" instead of a
prompt.

## Step 6: show it

The post in a fenced block, exactly as it should be pasted, then:

```
READY
hook:      H32 Time Saved  ·  angle S2  ·  goal saves
length:    1,142 characters
humanizer: 4 fixes, score 84 PASS
flags:     {{N}} x4 still open
post at:   Tue 8:30 IST (from plan.md) or Tue-Thu 8-10 IST
image:     suggested (prompt above) / none
first comment: "Teardown template: {{link}}"

Say "approve" to queue it for that time, or tell me what to change.
```

## Step 7: on "approve"

1. **Refuse to queue while any `{{placeholder}}` is open.** Ask for the
   real value, or for the user to cut the line.
2. Write the post to `~/.claude/linkedin/queue/` with `/li-publish`'s
   `queue` command (time, text, image file name if any, first comment).
   If the user said "I'll post it myself", skip the queue.
3. Append a row to `~/.claude/linkedin/log.md` (date, hook, angle, format,
   characters, first line).
4. Remind the user to drop the image into `~/.claude/linkedin/images/` under
   the exact file name before the post time, if one was suggested.

Also suggest: reply to every real comment in the first 60-90 minutes
(`/li-reply`), and leave 3-5 real comments on others' posts before posting
(`/li-comment`).

## Never

- Publish anything the user hasn't approved in this conversation, or open
  LinkedIn in a browser. Publishing goes through `/li-publish` only.
- Copy a sentence or story from `swipe.md`. Borrow the shape only.
- Use "comment X to get Y". Put the resource in the first comment instead.
- Write about confidential material (client data, a past employer's
  numbers) or anything under *Off limits*.
