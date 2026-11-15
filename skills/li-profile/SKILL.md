---
name: li-profile
description: >-
  Score a LinkedIn profile out of 100 against a 13-part rubric built for a
  builder with a founder-style persona, then rewrite the parts that lose the most points:
  headline, About, Featured, Experience, Projects, banner. Use when the user says
  "optimize my profile", "score my LinkedIn", "rewrite my headline", "fix my
  About", "make my profile founder-ready", or pastes their profile.
---

# li-profile

A profile isn't a resume. A resume answers "what have you done". A profile
answers "should I message this person", in about four seconds, from the
headline and the first two lines of About.

For a builder, the reader is usually a **founder or another builder** who
just saw a post or a comment. They're looking for proof you ship and think
clearly about products.

## Input

Ask the user to paste: headline, About, experience entries, projects, and
whether they have a banner, Featured items and recommendations. A screenshot
of the top card is enough for a first pass. **Don't log in to LinkedIn or
scrape the profile.**

Read `~/.claude/linkedin/voice.md` and `story-bank.md`: the receipts for the
rewrite come from there, never invented.

## 1. Score

Read `rubric.json` in this folder. Score all 13 items, show the table, give
the total. Be honest: most first-pass profiles land in the 30s-40s.

```
PROFILE SCORE  43/100

  headline          4/12   "Student at {{college}}", no role, no proof, no keywords
  about_open        2/10   opens with "Passionate about"
  featured          0/10   empty
  projects          3/8    listed, no numbers or links
  ...
```

## 2. Rewrite, biggest loss first

Don't rewrite everything at once: the user has to paste each piece in.

**Headline (220 characters).** Formula:
`{target role / what you build} | {proof} | {keywords}`
- "Building {{what}} with AI | Shipped {{N}} open-source apps | Digitised a
  {{kind of}} business | AI, SaaS, B2B" beats "Student at {{college}}".
- Don't open with "Helping X do Y" (every second profile does).
- Recruiters search the headline. Include the role noun, the domain, a skill.
- Give three options.

**About, first ~265 characters.** Everything after is behind "see more", so
this is the About for most readers. Say what you build, for whom, and one
number. No "passionate", no third person, no "Welcome to my profile".

**About, body (1,000-1,500 characters).** First person:
1. Hook (a claim or number)
2. What you do and build
3. One or two receipts with numbers (from story-bank.md)
4. How you think about products (one line, specific)
5. One human line
6. Keyword line (Product Management, SaaS, the tools you use)
7. Next step: email, portfolio, repo. Not "Let's connect!"

**Featured.** Three items: your best post, one proof asset (teardown, PRD,
case-comp deck, demo video), one repo or portfolio.

**Experience.** One line of scope, then 2-3 bullets that are outcomes with
numbers, not duties. "Built the order dashboard; order processing went from
{{X}} to {{Y}}" beats "Responsible for dashboard development".

**Projects.** Problem → what you built → number → link. For a builder this
is often the strongest section on the page.

**Banner.** One line of positioning and one way to see your work.

## 3. Output

Score table, then each rewrite as a copy-ready block in fix-first order,
each run through `/li-human`. Then re-score and show the delta honestly: if
it gets to 82, say 82, and say what the rest needs (usually recommendations,
a real banner and posting activity, none of which a rewrite can create).

Every number in a rewrite comes from story-bank.md or the user. Missing →
`{{my number}}` and a flag.

**Nothing is saved to LinkedIn.** The user pastes each section in.
