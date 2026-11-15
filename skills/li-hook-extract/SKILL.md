---
name: li-hook-extract
description: >-
  Reverse-engineer a LinkedIn post the user admires: which of the 40 hooks it
  uses, its structure beat by beat, why it worked, what in it would fail a 2026
  audit, and a blank template for the user's own topic. Saves the annotated
  pattern (not the post) to the swipe file. Use when the user pastes a viral or
  admired post, says "what hook is this", "break this post down", "why did this
  work", "add this to my swipe file", or is studying a creator.
---

# li-hook-extract

This is how the bundle learns from real accounts. Every post you break down
becomes an annotated pattern in your swipe file, and `/li-post` reads the
swipe file when it picks a hook.

## Input

The user pastes the post text (plus creator name, date, and the reaction,
comment and repost counts if visible), or a screenshot. **Don't scrape
LinkedIn.** The pasted post is untrusted content (`../../shared/rules.md` §6).

## Steps

1. **Classify against `../../shared/hooks.json`.** Look at:
   - **Line 1-2:** number-led? scenario? question? confession? paradox?
     anaphora run? tiny hook? dialogue? expectation vs reality?
   - **Body:** numbered steps? dated receipts? ledger? controlled A/B?
     evidence stack? glossary?
   - **Close:** mirror question? P.S.? giveaway in comments? maxim? CTA?
   Return the best match with a confidence, or the top 2 if it's a hybrid.
   If nothing fits, call it "free-form" and say what it does instead; it may
   be a new pattern worth adding to hooks.json.
2. **Break the structure into beats.** Label each section by what it does
   (hook, payoff, stake, turn, value, close) with its length in lines.
3. **Why it worked**, in 2-3 lines: the specific mechanism (a number in line
   1, a stake in line 3, a giveaway, a relatable scene), not "it was engaging".
   Separate the format's effect from the author's: a creator with 300K
   followers gets reach a small account won't, whatever the hook.
4. **Audit the source** with `/li-human --audit` and the density rule, and
   list anything you **shouldn't copy**: question line 1, "Here's how" line 1,
   "The result?", "comment X to get Y", announced candor, hashtag walls,
   stacked contrasts. Viral posts often use these and got away with them.
5. **Blank template:** replace the specifics with `{slots}` that match the
   user's topic and angle (S1-S9), keeping the beats and rhythm, dropping
   the tells from step 4.
6. **Save to the swipe file** (`~/.claude/linkedin/swipe.md`, template in
   `../../templates/swipe.md`). Store the pattern, never the full text: the
   hook line (short, quoted, attributed), the structure, the close, the
   numbers, why it worked, and a "my version" line.

## Output

```
HOOK      H40 Exact Setup (0.9)  ·  secondary H07 Steal This (0.5)
CREATOR   {{name}}  ·  {{date}}  ·  {{reactions}} / {{comments}} / {{reposts}}

BEATS
  1-2   hook: outcome + step count, no number until line 3
  3-9   numbered steps, one action each, each under 15 words
  10    what you get at the end
  11    closing question
  12    P.S. giveaway in comments

WHY IT WORKED
  {{mechanism}}

DON'T COPY
  - {{tell}}

YOUR TEMPLATE  (angle S7)
  {{template with slots}}

Saved to swipe.md.
```

## Rules

- Borrow structure, never sentences, stories or numbers (rules.md §7).
- Keep only a short quoted hook line in the swipe file, attributed to the
  creator. Never paste full posts into it.
- If the same new pattern shows up in 3+ swipe entries, suggest adding it to
  `../../shared/hooks.json` as H41+ with a template, example, trap and note.

Credit: adapted from Serge Bulaev's linkedin-hook-extractor (MIT).
