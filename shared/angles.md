# angles.md — what to write about (founder / builder edition)

Hooks (`hooks.json`) decide the *shape* of a post. Angles decide the
*territory*. Pick the angle first, then let it suggest the hook.

The audience is **founders and builders**. The persona is a builder who ships
in public, tells the truth about small numbers, and gives the work away.
The week runs on seven different pillars (one per day) so the feed never
repeats itself, plus two swap-in slots.

## The seven pillars

| # | Day | Angle | One-line prompt | Feeds from | Hooks that fit | Goal |
|---|---|---|---|---|---|---|
| S1 | Mon | **Build Log** | This week's real numbers on one app (rotate apps week to week): shipped, broke, users, cost. Small numbers stated plainly | Shipped, Receipts | H08, H23, H06 | comments |
| S2 | Tue | **Built with AI** | "I built X in Y hours with Claude Code": the exact prompts, stack, cost, what the AI got wrong | Shipped, Resources | H32, H40, H10 | saves |
| S3 | Wed | **Startup Teardown** | One decision a real startup made (pricing, launch, onboarding), taken apart like a founder would | Positions | H16, H19, H38 | comments / reposts |
| S4 | Thu | **Builder Take** | A position you can back with your own receipt that most builders would argue with | Positions, Turning points | H01, H28, H33 | comments |
| S5 | Fri | **Open-Source Drop** | A repo, prompt or template given away whole (often a carousel) | Resources, Shipped | H07, H40, H09 | saves |
| S6 | Sat | **Real Business Lessons** | What digitising a real offline business taught you about how small Indian businesses actually work | Timeline, Receipts, Scars | H25, H03, H05 | likes / comments |
| S7 | Sun | **Chaos Diary** | Running N projects at 20, told light, ending with one usable line | Recurring stories, Scars | H35, H36, H29 | likes |

## Keep the week varied

- Seven different pillars, seven different stories. No storyline ties the
  week together, and no single app carries more than one post.
- S1 rotates across the user's apps (listed in voice.md). Use the true
  numbers from voice.md §8 and the story bank, however small, and say
  exactly what they are. Never round up, never count friends as strangers.

## Swap-in slots (replace one pillar that day)

| # | Angle | When | Hooks that fit | Goal |
|---|---|---|---|---|
| S8 | **Reaction** | Something big drops in AI or startups (a model release, a major launch). Your take within 24 hours, with one thing you tried yourself | H02, H37, H06 | reposts / comments |
| S9 | **Founder Conversation** | You asked a founder one sharp question and they said you may share the answer. Credit them by name | H15, H20, H25 | reposts |

S9 doubles as outreach: the question is the DM (`/li-dm`), the post is the
thank-you. Never post a conversation without the founder's explicit OK.

## How to fill an angle

1. Find the material in `~/.claude/linkedin/story-bank.md` under the listed
   section. If it's empty, run `/li-interview --mode post` on that angle.
2. Pick the hook from the shortlist that matches the slot's goal.
3. Every angle needs **one number with what it measures** and **one moment
   with a date**. Without both, it isn't ready.

## Angles to avoid

- **Numbers you'd have to inflate.** If the truth is 4 users, the post says 4.
- **Advice beyond your receipts.** "How to raise a seed round" from someone
  who hasn't is a credibility leak. "What I learned pitching {{N}} people"
  earns it.
- **Dunking on a named founder or startup.** Teardowns (S3) critique a
  decision, with respect, and say what you'd do instead.
- **Work you can't share:** client data from an internship, other people's
  private numbers, anything under *Off limits*.
- **"Grateful to announce" posts** with no lesson.
