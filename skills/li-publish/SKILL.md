---
name: li-publish
description: >-
  The posting robot. Queues posts the user approved and publishes them at their
  planned time through LinkedIn's official API (text, image, carousel PDF), sends
  planned reshares (max one a day), and checks once whether the user's token may
  like or comment. Runs from Windows Task Scheduler every 15 minutes. Use when a
  post is approved and needs queueing, or the user says "set up posting", "what's
  queued", "did my post go out", "post this at 9", or "test likes".
---

# li-publish

Writes nothing creative. It moves approved text to LinkedIn on time, through
the official API only (`../../shared/rules.md` §5). Script: `publish.py` in
this skill's folder; standard library only. On Windows run it with `python`
(not `python3`) by full path from this skill's base directory.

## One-time setup (the user does the clicking; about 15 minutes)

1. The user goes to developer.linkedin.com → *Create app*. LinkedIn asks for
   a company Page to attach the app to; any Page the user admins works
   (they can create a simple one for their own brand).
2. In the app → *Products*: add **Share on LinkedIn** and **Sign In with
   LinkedIn using OpenID Connect** (both self-serve, free).
3. In *Auth* → *Authorized redirect URLs*: add `http://localhost:8765/callback`.
4. The user runs, **in their own terminal** (it asks for the Client Secret,
   which must never be typed into this chat):
   ```
   python publish.py setup
   ```
   It opens LinkedIn's own sign-in page; the user signs in and clicks Allow.
   The token (valid about 60 days) is saved in `~/.claude/linkedin/secrets/`.
5. Ask before running `python publish.py schedule`: it creates a Windows
   scheduled task (`li-stack-publish`, every 15 minutes) that runs
   `publish.py run`. `unschedule` removes it.

Never ask for, print or copy the Client Secret or the token.

## Queueing (called by /li-post, /li-carousel, /li-comment)

Only after the user said "approve" for that exact text in this conversation:

```
python publish.py queue --at "2026-11-16 08:30" --text-file <draft file> [--image 2026-11-16-slug.png] [--alt "..."] [--first-comment "..."]
python publish.py reshare --at "2026-11-18 12:00" --url <post url> [--text-file <take file>]
```

- Times are the PC's local time (IST for this user).
- The script refuses text with open `{{placeholders}}` or over 3,000
  characters.
- An image or PDF must be in `~/.claude/linkedin/images/` under that exact
  name by post time; until then the post waits and the log says so.
- Reshares: if `reshare_auto` is on in voice.md, queue the planned one
  without asking; otherwise only after "approve". The script sends at most
  one a day.

## Checking

- `python publish.py list`: what's waiting, with MISSING next to absent images.
- `python publish.py run --dry-run`: what would go out now, without sending.
- `~/.claude/linkedin/publish.log`: every send, failure and wait.
- Sent items move to `queue/sent/` with the post URL; copy that URL into the
  post's row in log.md (needed by `/li-monitor`, `/li-engagers`, `/li-audit`).
- Failed items move to `queue/failed/` with the error. Show it to the user;
  don't retry blindly.

## The like/comment test (once, after the first real post)

```
python publish.py test --url <the user's own post url>
```

It tries one like and one comment on the user's own post and logs whether
the token allows each. If the comment test passes, tell the user to delete
the test comment. LinkedIn's docs reserve likes and comments for the
Community Management API (companies only), so expect "not allowed". Either
way, likes and comments on other people's posts stay manual: the bundle
writes them, the user clicks.

## First comments

If a post has `--first-comment` (where the link goes), the script tries to
post it under the post. If the token isn't allowed to comment, the log says
"paste it yourself" with the text. Tell the user right after the post time.

## Never

- Drive a browser on LinkedIn, or use any unofficial endpoint.
- Queue anything the user hasn't approved in this conversation, apart from
  reshares under `reshare_auto`.
- Edit a post in its first 3 hours by deleting and re-posting it.
