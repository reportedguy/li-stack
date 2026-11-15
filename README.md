# li-stack

A Claude Code plugin that plans, writes and humanizes your LinkedIn posts, and publishes only the ones you approve through LinkedIn's official API.

16 LinkedIn skills for a builder with a founder-style persona, writing for
founders and builders. Claude plans the week, writes every post, comment,
reply and DM in your voice, checks it doesn't read like AI, and posts your
approved posts on time through LinkedIn's official API.

Built by merging two MIT bundles:

- **[sergebulaev/linkedin-skills](https://github.com/sergebulaev/linkedin-skills)**
  for the *knowledge*: hook formulas with 2026 reach notes, the algorithm
  research, Humanizer V3, the story-bank interviewer, the thread monitor and
  engager analytics, untrusted-content rules.
- **[Jakeschincariol/linkedin-agent-skill](https://github.com/Jakeschincariol/linkedin-agent-skill)**
  for the *structure*: short, opinionated skills, hooks with traps, the
  runnable humanizer scripts, audit / carousel / DM / inbox skills.
- Plus a **founder/builder layer**: 7 daily pillars, a voice built from
  creators you study, image prompts, and a posting robot.

## What's automated and what isn't

| | How |
|---|---|
| Writing everything | the skills below |
| Posting your approved posts (text, image, carousel PDF) | `/li-publish`, LinkedIn's official API, on schedule |
| Reshares the plan suggests | `/li-publish`, max one a day (`reshare_auto` in voice.md) |
| Reading LinkedIn (watchlist posts, engager profiles) | Agent Reach, capped at 40 reads a day |
| Liking and commenting on others' posts, connection requests, DMs | you, from the drafted daily list (LinkedIn gives individuals no API for these) |

## Safety rules

- **Posts go out only through LinkedIn's official API, and only after you
  approve them.** The one exception is reshares, and only if you switch
  `reshare_auto` on.
- **Likes, comments, connection requests and DMs stay manual.** li-stack
  drafts them; you click and send.
- **It never invents numbers.** A missing fact stays as a `{{placeholder}}`,
  and the posting robot refuses any post that still has one.
- **It never drives a browser on LinkedIn.** Reading goes through Agent
  Reach with a daily cap; posting goes through the API.

## The 16 skills

| Command | What it does | From |
|---|---|---|
| `/li-plan` | The week: 7 posts across the pillars, daily engagement list, reshares | Jake + Serge |
| `/li-post` | Idea → 3 hooks → full draft, humanized, image prompt if useful, queued on "approve" | Jake + Serge |
| `/li-interview` | Builds your story bank; five-line spines for single posts | Serge |
| `/li-human` | Cleans AI tells, flags the rest, scores it. `--audit`, `--profile`, `--kind` | Jake's scripts, Serge's V3 rules |
| `/li-comment` | 10 comment types, 2 options per post, batch mode, reshare mode | Jake + Serge |
| `/li-reply` | Filters, sorts and answers comments on your post | Jake + Serge |
| `/li-monitor` | Threads you commented on (who replied, how warm) + new watchlist posts | Serge, via Agent Reach |
| `/li-engagers` | Who engaged with your post, which are founders/builders, who to follow up | Serge, via Agent Reach |
| `/li-publish` | The posting robot: queue, schedule, send, like/comment test | new |
| `/li-profile` | 100-point score + rewrites for a builder persona | Jake's rubric + Serge's rules |
| `/li-carousel` | Slide copy + post text + the PDF | Jake + Serge |
| `/li-repurpose` | One README / notes / transcript → several posts | Jake + Serge |
| `/li-dm` | Invite note, first message, 2 follow-ups, Founder Conversation ask | Jake |
| `/li-inbox` | Triage DMs, spot sequences and fake recruiters | Jake |
| `/li-audit` | Post-mortem on your published posts | Jake + Serge |
| `/li-hook-extract` | Breaks down a post you admire, saves the pattern to your swipe file | Serge |

Installed as a plugin, commands may show as `/li-stack:li-post`.

## Shared knowledge (`shared/`)

| File | What it holds |
|---|---|
| `rules.md` | The one rulebook: files, priority order, voice, density rule, what's automated, untrusted content, borrowing |
| `hooks.json` | 40 hooks, each with template, example, goal, trap and 2026 note |
| `angles.md` | 7 daily pillars (S1-S7) + 2 swap-ins (S8 Reaction, S9 Founder Conversation) |
| `algorithm.md` | What the 2026 feed rewards, each number tagged by how solid it is |

## Your files (never inside the bundle)

```
~/.claude/linkedin/
  voice.md  story-bank.md  swipe.md  log.md  watchlist.md  plan.md
  queue/  images/  secrets/  publish.log
```

They live outside the bundle so git never sees your numbers, names, plans
or API token. Skills copy missing templates there on first run.

## Install (Claude Code)

You need [Claude Code](https://claude.com/claude-code), git and Python 3
(standard library only, nothing to `pip install`).

1. Download the folder:

   ```
   git clone https://github.com/reportedguy/li-stack.git
   ```

2. In Claude Code, add it as a local marketplace and install the plugin:

   ```
   /plugin marketplace add <path to the li-stack folder>
   /plugin install li-stack@li-stack
   ```

   Path example on Windows: `C:\Users\you\li-stack`. On a Mac: `~/li-stack`.

Keep the folder together: skills read `../../shared/` and `../../templates/`.

## Posting robot, once

See `skills/li-publish/SKILL.md`: create a free LinkedIn developer app
(products *Share on LinkedIn* + *Sign In with LinkedIn using OpenID
Connect*), then in your own terminal:

```
python skills/li-publish/publish.py setup
python skills/li-publish/publish.py schedule
```

`schedule` uses Windows Task Scheduler, so it works on Windows only. On a
Mac, queueing and `python skills/li-publish/publish.py run` work, but for now
you need to put `run` on a timer yourself (for example with cron).

## Tests

```
python tests/run_tests.py
```

On Windows use `python` (or `py`); `python3` is often the Microsoft Store stub.

## Contributing and security

See `CONTRIBUTING.md` and `SECURITY.md`. MIT licensed (`LICENSE`).

## Credits

Adapted from Serge Bulaev's
[linkedin-skills](https://github.com/sergebulaev/linkedin-skills) and Jake
Schincariol's
[linkedin-agent-skill](https://github.com/Jakeschincariol/linkedin-agent-skill),
both MIT. Their copyright notices are kept in `NOTICE.md`. Voice references in
`templates/voice.md` are observations of public creators' styles; no posts
are copied.
