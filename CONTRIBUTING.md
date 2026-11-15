# Contributing

Thanks for helping. Keep changes small and easy to review.

1. **Run the tests before you open a PR.** Standard library only, offline,
   nothing is posted:

   ```
   python tests/run_tests.py
   ```

   On Windows use `python` (or `py`), not `python3`.

2. **One skill per PR.** A change to `skills/li-post/` and a change to
   `skills/li-dm/` are two PRs. Changes to `shared/` that several skills use
   are fine in one PR; say which skills they affect.

3. **Never commit personal files.** Your `voice.md`, `story-bank.md`,
   `swipe.md`, `log.md`, `plan.md`, `watchlist.md`, and the `secrets/`,
   `queue/` and `images/` folders live in `~/.claude/linkedin/`, not in this
   repo. Only the blank versions in `templates/` belong here. No real names,
   numbers, tokens or post text from your own account in fixtures either.

4. **Keep the safety rules.** No change may post without the user's approval,
   automate likes, comments, connection requests or DMs, drive a browser on
   LinkedIn, or fill in a number the user didn't give.

Optional: list words that must never appear in the bundle (your company name,
for example), one per line, in `tests/private_words.txt`. That file is
gitignored; the tests fail if any listed word shows up.
