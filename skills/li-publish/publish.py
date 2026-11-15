#!/usr/bin/env python3
"""
publish.py - post approved LinkedIn posts at their time, through LinkedIn's
official API only (products: "Share on LinkedIn" + "Sign In with LinkedIn
using OpenID Connect"; scopes: openid profile w_member_social). No browser
automation, no scraping, no third-party service. Standard library only.

Everything lives in ~/.claude/linkedin/ (never in the bundle or git):
  secrets/app.json      client id + secret   (written by `setup`, typed by you)
  secrets/token.json    access token          (written by `setup`)
  queue/*.json          approved items waiting for their time
  queue/sent/, failed/  what happened to each item
  images/               images / PDFs you dropped in for queued posts
  publish.log           one line per action

Commands
  python publish.py setup                         # once: you log in to LinkedIn yourself
  python publish.py queue --at "2026-11-16 08:30" --text-file post.txt [--image f.png] [--first-comment "..."]
  python publish.py reshare --at "2026-11-18 12:00" --url <post url> [--text-file take.txt]
  python publish.py list
  python publish.py run [--dry-run]               # send everything that is due
  python publish.py test --url <your own post url> # can this token like/comment?
  python publish.py schedule | unschedule         # Windows Task Scheduler, every 15 min
"""

import argparse
import datetime as dt
import glob
import http.server
import json
import mimetypes
import os
import re
import secrets as pysecrets
import shutil
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request
import webbrowser

HOME = os.environ.get("LI_STACK_HOME") or os.path.join(os.path.expanduser("~"), ".claude", "linkedin")  # override is for tests
SECRETS = os.path.join(HOME, "secrets")
QUEUE = os.path.join(HOME, "queue")
IMAGES = os.path.join(HOME, "images")
LOG = os.path.join(HOME, "publish.log")
API = "https://api.linkedin.com"
REDIRECT = "http://localhost:8765/callback"
SCOPES = "openid profile w_member_social"
TASK = "li-stack-publish"
RESHARES_PER_DAY = 1
SENDING = "sending"
STALE_SENDING = dt.timedelta(hours=1)  # a claim older than this was interrupted mid-send
LITTLE_TEXT = re.compile(r"([\\|{}@\[\]()<>#*_~])")  # reserved in the Posts API "little text" format


def utf8_console():
    for s in (sys.stdout, sys.stderr):
        if hasattr(s, "reconfigure"):
            s.reconfigure(encoding="utf-8", errors="replace")


def now():
    return dt.datetime.now().astimezone()


def log(msg):
    os.makedirs(HOME, exist_ok=True)
    line = f"{now():%Y-%m-%d %H:%M:%S%z}  {msg}"
    with open(LOG, "a", encoding="utf-8") as fh:
        fh.write(line + "\n")
    print(line)


def read_json(path, default=None):
    try:
        with open(path, encoding="utf-8-sig") as fh:  # Notepad may add a BOM
            return json.load(fh)
    except FileNotFoundError:
        return default


def write_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2, ensure_ascii=False)
    os.replace(tmp, path)


def parse_at(s):
    t = dt.datetime.strptime(s, "%Y-%m-%d %H:%M")
    return t.astimezone()  # local time of this PC


def escape_little_text(text):
    """Hashtags stay live; everything else reserved is escaped."""
    out = LITTLE_TEXT.sub(r"\\\1", text)
    return re.sub(r"\\#(?=\w)", "#", out)


# ---------------------------------------------------------------- HTTP

class ApiError(Exception):
    def __init__(self, status, body):
        super().__init__(f"HTTP {status}: {body[:300]}")
        self.status, self.body = status, body


def request(method, url, token=None, body=None, headers=None, raw=None):
    h = dict(headers or {})
    if token:
        h["Authorization"] = f"Bearer {token}"
    data = raw
    if body is not None:
        data = json.dumps(body).encode("utf-8")
        h["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, method=method, headers=h)
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            text = r.read().decode("utf-8", "replace")
            return r.status, dict(r.headers), (json.loads(text) if text.strip().startswith("{") else text)
    except urllib.error.HTTPError as e:
        raise ApiError(e.code, e.read().decode("utf-8", "replace"))


def versions():
    """Newest LinkedIn-Version first; LinkedIn keeps roughly a year of monthly versions."""
    d = now().replace(day=1)
    for _ in range(10):
        d = (d - dt.timedelta(days=1)).replace(day=1)
        yield f"{d:%Y%m}"


def rest(method, path, tok, body=None):
    cfg = read_json(os.path.join(SECRETS, "token.json"), {})
    order = [cfg["version"]] if cfg.get("version") else []
    order += [v for v in versions() if v not in order]
    last = None
    for v in order:
        try:
            res = request(method, API + path, tok, body,
                          {"LinkedIn-Version": v, "X-Restli-Protocol-Version": "2.0.0"})
            if cfg and cfg.get("version") != v:
                cfg["version"] = v
                write_json(os.path.join(SECRETS, "token.json"), cfg)
            return res
        except ApiError as e:
            last = e
            if e.status == 426 or "VERSION" in e.body.upper():
                continue  # version not active; try the next one
            raise
    raise last


# ---------------------------------------------------------------- auth

def token():
    t = read_json(os.path.join(SECRETS, "token.json"))
    if not t:
        sys.exit("No token. Run: python publish.py setup")
    left = dt.datetime.fromisoformat(t["expires"]) - now()
    if left.total_seconds() <= 0:
        sys.exit("Token expired. Run: python publish.py setup")
    if left.days < 7:
        print(f"! token expires in {left.days} days; run setup again soon")
    return t["access_token"], t["person"]


def cmd_setup(args):
    import getpass
    app_path = os.path.join(SECRETS, "app.json")
    app = read_json(app_path)
    if not app:
        print("Paste your LinkedIn app's Client ID and Client Secret "
              "(developer.linkedin.com > your app > Auth). The secret is not shown.")
        app = {"client_id": input("Client ID: ").strip(), "client_secret": getpass.getpass("Client Secret: ").strip()}
        write_json(app_path, app)
    state = pysecrets.token_urlsafe(16)
    got = {}

    class Handler(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            q = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
            got.update({k: v[0] for k, v in q.items()})
            self.send_response(200)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.end_headers()
            self.wfile.write("li-stack: done. You can close this tab.".encode())

        def log_message(self, *a):
            pass

    url = "https://www.linkedin.com/oauth/v2/authorization?" + urllib.parse.urlencode({
        "response_type": "code", "client_id": app["client_id"], "redirect_uri": REDIRECT,
        "scope": SCOPES, "state": state})
    print("Opening LinkedIn's sign-in page in your browser. Sign in and click Allow.")
    print("If it doesn't open, paste this into your browser:\n" + url)
    webbrowser.open(url)
    srv = http.server.HTTPServer(("127.0.0.1", 8765), Handler)
    while "code" not in got and "error" not in got:
        srv.handle_request()
    if got.get("state") != state:
        sys.exit("State mismatch; aborting.")
    if "error" in got:
        sys.exit(f"LinkedIn said: {got.get('error')} {got.get('error_description', '')}")
    _, _, tok = request("POST", "https://www.linkedin.com/oauth/v2/accessToken",
                        raw=urllib.parse.urlencode({
                            "grant_type": "authorization_code", "code": got["code"],
                            "redirect_uri": REDIRECT, "client_id": app["client_id"],
                            "client_secret": app["client_secret"]}).encode(),
                        headers={"Content-Type": "application/x-www-form-urlencoded"})
    _, _, me = request("GET", API + "/v2/userinfo", tok["access_token"])
    expires = now() + dt.timedelta(seconds=int(tok.get("expires_in", 5184000)))
    write_json(os.path.join(SECRETS, "token.json"), {
        "access_token": tok["access_token"], "person": f"urn:li:person:{me['sub']}",
        "expires": expires.isoformat(), "name": me.get("name", "")})
    log(f"setup ok for {me.get('name', 'you')}; token valid until {expires:%Y-%m-%d}")


# ---------------------------------------------------------------- queue

def slug(text):
    s = re.sub(r"[^a-z0-9]+", "-", text.lower())[:40].strip("-")
    return s or "post"


def item_path(at, name):
    return os.path.join(QUEUE, f"{at:%Y%m%d-%H%M}-{slug(name)}.json")


def check_text(text):
    holes = re.findall(r"\{\{[^}]*\}\}", text)
    if holes:
        sys.exit(f"Refusing: open placeholders {sorted(set(holes))}. Fill them first.")
    if len(text) > 3000:
        sys.exit(f"Refusing: {len(text)} characters; LinkedIn's limit is 3,000.")


def cmd_queue(args):
    with open(args.text_file, encoding="utf-8-sig") as fh:
        text = fh.read().strip()
    check_text(text)
    at = parse_at(args.at)
    item = {"kind": "post", "at": at.isoformat(), "text": text, "status": "pending",
            "image": args.image, "first_comment": args.first_comment, "alt": args.alt or ""}
    path = item_path(at, text.splitlines()[0])
    write_json(path, item)
    log(f"queued post for {at:%a %d %b %H:%M}: {os.path.basename(path)}")
    if args.image and not os.path.exists(os.path.join(IMAGES, args.image)):
        print(f"! drop {args.image} into {IMAGES} before then, or the post waits")


def cmd_reshare(args):
    text = ""
    if args.text_file:
        with open(args.text_file, encoding="utf-8-sig") as fh:
            text = fh.read().strip()
        check_text(text)
    at = parse_at(args.at)
    path = item_path(at, "reshare-" + args.url.rstrip("/").split("/")[-1])
    write_json(path, {"kind": "reshare", "at": at.isoformat(), "url": args.url, "text": text, "status": "pending"})
    log(f"queued reshare for {at:%a %d %b %H:%M}: {args.url}")


def pending():
    for p in sorted(glob.glob(os.path.join(QUEUE, "*.json"))):
        yield p, read_json(p)


def cmd_list(args):
    rows = list(pending())
    if not rows:
        print("queue empty")
    for p, it in rows:
        what = it.get("url") if it["kind"] == "reshare" else it["text"].splitlines()[0][:70]
        img = f"  [{it['image']}{'' if os.path.exists(os.path.join(IMAGES, it['image'])) else ' MISSING'}]" if it.get("image") else ""
        print(f"{dt.datetime.fromisoformat(it['at']):%a %d %b %H:%M}  {it['kind']:<7} {what}{img}")


# ---------------------------------------------------------------- publishing

def upload(tok, person, filename):
    path = os.path.join(IMAGES, filename)
    kind = "documents" if filename.lower().endswith(".pdf") else "images"
    _, _, init = rest("POST", f"/rest/{kind}?action=initializeUpload", tok,
                      {"initializeUploadRequest": {"owner": person}})
    v = init["value"]
    with open(path, "rb") as fh:
        request("PUT", v["uploadUrl"], tok, raw=fh.read(),
                headers={"Content-Type": mimetypes.guess_type(path)[0] or "application/octet-stream"})
    return v.get("image") or v.get("document"), kind


def parent_urns(url):
    """Candidate share URNs for a post URL. The activity id usually equals the share id."""
    m = re.search(r"urn:li:(share|ugcPost|activity):(\d+)", urllib.parse.unquote(url))
    ids = [m.group(2)] if m else re.findall(r"(?:activity|share|ugcPost)[-:](\d{15,})", url)
    if not ids:
        raise ValueError(f"can't find a post id in {url}")
    return [f"urn:li:share:{ids[0]}", f"urn:li:ugcPost:{ids[0]}"]


def base_post(person, text):
    return {"author": person, "commentary": escape_little_text(text), "visibility": "PUBLIC",
            "distribution": {"feedDistribution": "MAIN_FEED", "targetEntities": [],
                             "thirdPartyDistributionChannels": []},
            "lifecycleState": "PUBLISHED", "isReshareDisabledByAuthor": False}


def send(item, tok, person):
    if item["kind"] == "reshare":
        last = None
        for urn in parent_urns(item["url"]):
            body = base_post(person, item.get("text", ""))
            body["reshareContext"] = {"parent": urn}
            try:
                _, h, _ = rest("POST", "/rest/posts", tok, body)
                return h.get("x-restli-id") or h.get("X-RestLi-Id")
            except ApiError as e:
                last = e
        raise last
    body = base_post(person, item["text"])
    if item.get("image"):
        urn, kind = upload(tok, person, item["image"])
        body["content"] = {"media": {"id": urn, "title": item.get("alt") or item["text"].splitlines()[0][:100]}
                           if kind == "documents" else {"id": urn, "altText": item.get("alt", "")}}
    _, h, _ = rest("POST", "/rest/posts", tok, body)
    return h.get("x-restli-id") or h.get("X-RestLi-Id")


def comment(tok, person, post_urn, text):
    path = f"/rest/socialActions/{urllib.parse.quote(post_urn, safe='')}/comments"
    rest("POST", path, tok, {"actor": person, "object": post_urn, "message": {"text": text}})


def reshares_today():
    today = now().date()
    n = 0
    for p in glob.glob(os.path.join(QUEUE, "sent", "*.json")):
        it = read_json(p, {})
        if it.get("kind") == "reshare" and it.get("sent_at") and dt.datetime.fromisoformat(it["sent_at"]).date() == today:
            n += 1
    return n


def move(path, item, folder):
    item_dest = os.path.join(QUEUE, folder, os.path.basename(path))
    write_json(item_dest, item)
    os.remove(path)


def acquire_run_lock():
    """Take the run lock; None when another run is still working the queue."""
    os.makedirs(HOME, exist_ok=True)
    fh = open(os.path.join(HOME, "run.lock"), "a+b")
    try:
        fh.write(b"x")
        fh.flush()
        fh.seek(0)
        if os.name == "nt":
            import msvcrt
            msvcrt.locking(fh.fileno(), msvcrt.LK_NBLCK, 1)
        else:
            import fcntl
            fcntl.flock(fh.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError:
        fh.close()
        return None
    return fh


def release_run_lock(fh):
    if fh is None:
        return
    try:
        if os.name == "nt":
            import msvcrt
            fh.seek(0)
            msvcrt.locking(fh.fileno(), msvcrt.LK_UNLCK, 1)
        else:
            import fcntl
            fcntl.flock(fh.fileno(), fcntl.LOCK_UN)
    finally:
        fh.close()


def claim_for_send(path):
    """Mark a due item as being sent, before send() runs.

    Returns the updated item, or None when another run owns it, or when the
    item was interrupted mid-send earlier (it is parked in failed/, never
    posted twice).
    """
    it = read_json(path)
    if it is None:
        return None
    if it.get("status") == SENDING:
        try:
            fresh = now() - dt.datetime.fromisoformat(it["sending_at"]) < STALE_SENDING
        except (KeyError, TypeError, ValueError):
            fresh = False
        if fresh:
            return None
        it.update(status="failed", failed_at=now().isoformat(),
                  error="interrupted while sending; check the feed before retrying")
        move(path, it, "failed")
        log(f"FAILED {os.path.basename(path)}: interrupted while sending (moved to failed, not re-sent)")
        return None
    it.update(status=SENDING, sending_at=now().isoformat())
    write_json(path, it)
    return it


def cmd_run(args):
    lock = None if args.dry_run else acquire_run_lock()
    if not args.dry_run and lock is None:
        log("another run is still sending; skipping this one")
        return
    try:
        run_due(args)
    finally:
        release_run_lock(lock)


def run_due(args):
    due = [(p, it) for p, it in pending() if dt.datetime.fromisoformat(it["at"]) <= now()]
    if not due:
        return
    tok, person = (None, None) if args.dry_run else token()
    for path, it in due:
        label = os.path.basename(path)
        if it.get("image") and not os.path.exists(os.path.join(IMAGES, it["image"])):
            log(f"waiting: {label} needs {it['image']} in {IMAGES}")
            continue
        if it["kind"] == "reshare" and reshares_today() >= RESHARES_PER_DAY:
            log(f"waiting: {label} (already {RESHARES_PER_DAY} reshare today)")
            continue
        if args.dry_run:
            log(f"dry-run: would send {label}")
            continue
        it = claim_for_send(path)
        if it is None:
            continue
        try:
            urn = send(it, tok, person)
            it.update(status="sent", sent_at=now().isoformat(), urn=urn,
                      url=it.get("url") if it["kind"] == "reshare" else f"https://www.linkedin.com/feed/update/{urn}/")
            log(f"sent {label} -> {it['url'] if it['kind'] == 'post' else urn}")
            if it.get("first_comment"):
                try:
                    comment(tok, person, urn, it["first_comment"])
                    it["first_comment_status"] = "posted"
                except ApiError as e:
                    it["first_comment_status"] = f"paste it yourself ({e.status})"
                    log(f"first comment not allowed by this token ({e.status}); paste it yourself: {it['first_comment']}")
            move(path, it, "sent")
        except (ApiError, ValueError, OSError) as e:
            it.update(status="failed", error=str(e), failed_at=now().isoformat())
            move(path, it, "failed")
            log(f"FAILED {label}: {e}")


def cmd_test(args):
    tok, person = token()
    urn = parent_urns(args.url)[0]
    results = {}
    try:
        rest("POST", f"/rest/reactions?actor={urllib.parse.quote(person, safe='')}", tok,
             {"root": urn, "reactionType": "LIKE"})
        results["like"] = "allowed"
    except ApiError as e:
        results["like"] = f"not allowed ({e.status})"
    try:
        comment(tok, person, urn, "Testing (posted by li-stack's API check, delete me)")
        results["comment"] = "allowed (delete the test comment)"
    except ApiError as e:
        results["comment"] = f"not allowed ({e.status})"
    for k, v in results.items():
        log(f"test {k}: {v}")


# ---------------------------------------------------------------- scheduling (Windows)

def cmd_schedule(args):
    bindir = os.path.join(HOME, "bin")
    os.makedirs(bindir, exist_ok=True)
    target = os.path.join(bindir, "publish.py")
    shutil.copyfile(os.path.abspath(__file__), target)  # survives plugin updates moving the original
    exe = sys.executable.replace("python.exe", "pythonw.exe")  # no console window every 15 minutes
    if not os.path.exists(exe):
        exe = sys.executable
    tr = f'"{exe}" "{target}" run'
    subprocess.run(["schtasks", "/Create", "/F", "/SC", "MINUTE", "/MO", "15", "/TN", TASK, "/TR", tr], check=True)
    # Windows defaults skip tasks on battery and never catch up after sleep; a laptop missed a post that way.
    subprocess.run(["powershell", "-NoProfile", "-Command",
                    "Set-ScheduledTask -TaskName '" + TASK + "' -Settings (New-ScheduledTaskSettingsSet "
                    "-AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable) | Out-Null"], check=True)
    log(f"scheduled '{TASK}' every 15 minutes: {tr}")


def cmd_unschedule(args):
    subprocess.run(["schtasks", "/Delete", "/F", "/TN", TASK], check=True)
    log(f"removed scheduled task '{TASK}'")


def main():
    utf8_console()
    ap = argparse.ArgumentParser(description="Post approved LinkedIn posts via the official API.")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("setup")
    q = sub.add_parser("queue")
    q.add_argument("--at", required=True, help='local time, "YYYY-MM-DD HH:MM"')
    q.add_argument("--text-file", required=True)
    q.add_argument("--image", help="file name inside ~/.claude/linkedin/images/ (.png/.jpg, or .pdf for a carousel)")
    q.add_argument("--alt", help="alt text (image) or title (PDF)")
    q.add_argument("--first-comment")
    r = sub.add_parser("reshare")
    r.add_argument("--at", required=True)
    r.add_argument("--url", required=True)
    r.add_argument("--text-file")
    sub.add_parser("list")
    run = sub.add_parser("run")
    run.add_argument("--dry-run", action="store_true")
    t = sub.add_parser("test")
    t.add_argument("--url", required=True, help="one of YOUR OWN posts")
    sub.add_parser("schedule")
    sub.add_parser("unschedule")
    args = ap.parse_args()
    {"setup": cmd_setup, "queue": cmd_queue, "reshare": cmd_reshare, "list": cmd_list, "run": cmd_run,
     "test": cmd_test, "schedule": cmd_schedule, "unschedule": cmd_unschedule}[args.cmd](args)


if __name__ == "__main__":
    main()
