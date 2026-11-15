# Security

Please report security problems privately through GitHub: open the
repository's **Security** tab and choose **Report a vulnerability**. Don't
open a public issue for them.

Never paste a LinkedIn access token, client secret, or the contents of
`~/.claude/linkedin/secrets/` into an issue, PR or discussion. If you posted
one by mistake, revoke it in your LinkedIn developer app and run
`python skills/li-publish/publish.py setup` again.
