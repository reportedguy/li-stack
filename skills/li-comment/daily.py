#!/usr/bin/env python3
"""
daily.py - the one-click daily engagement list. Nothing is automated on
LinkedIn: each button opens the post in your normal browser and copies the
drafted comment; you click Like, paste, and post yourself.

Reads   ~/.claude/linkedin/today.json   (written by /li-comment batch mode)
Writes  ticked comments to the "Comments given" table in log.md

  python daily.py            # opens the list in your browser; stop with the Finish button
  python daily.py --port 8766

today.json:
  {"date": "2026-11-16",
   "items": [{"author": "Name", "url": "https://www.linkedin.com/posts/...",
              "first_line": "their first line", "type": "4 Receipt",
              "comment": "drafted text, or null for like-only"}]}
"""

import argparse
import html
import http.server
import json
import os
import sys
import webbrowser

HOME = os.environ.get("LI_STACK_HOME") or os.path.join(os.path.expanduser("~"), ".claude", "linkedin")  # override is for tests
TODAY = os.path.join(HOME, "today.json")
LOG = os.path.join(HOME, "log.md")
ALLOWED = ("https://www.linkedin.com/", "https://linkedin.com/")


def load_items(path=TODAY):
    with open(path, encoding="utf-8-sig") as fh:
        data = json.load(fh)
    items = []
    for i, it in enumerate(data.get("items", [])):
        url = str(it.get("url", ""))
        if not url.startswith(ALLOWED):  # the page only ever opens LinkedIn post links
            raise ValueError(f"item {i + 1}: not a LinkedIn link: {url!r}")
        items.append({"id": i, "author": str(it.get("author", "")), "url": url,
                      "first_line": str(it.get("first_line", "")), "type": str(it.get("type", "")),
                      "comment": it.get("comment") or ""})
    return data.get("date", ""), items


def append_log(item, date, path=LOG):
    def cell(s):
        return str(s).replace("|", "/").replace("\n", " ")
    row = f"| {cell(date)} | {cell(item['author'])} | {cell(item['url'])} | {cell(item['type'] or 'like only')} |  |\n"
    with open(path, "a+", encoding="utf-8") as fh:
        fh.seek(0)
        text = fh.read()
        if text and not text.endswith("\n"):
            fh.write("\n")
        fh.write(row)


PAGE = """<!doctype html><meta charset="utf-8"><title>Today on LinkedIn</title>
<style>
:root{--bg:#fff;--fg:#1a1a1a;--muted:#666;--card:#f6f6f4;--accent:#0a66c2;--done:#e8f3ea}
@media (prefers-color-scheme:dark){:root{--bg:#161616;--fg:#eee;--muted:#aaa;--card:#222;--accent:#4a9ee8;--done:#1f3324}}
body{background:var(--bg);color:var(--fg);font:16px/1.5 system-ui,sans-serif;max-width:720px;margin:24px auto;padding:0 16px}
.item{background:var(--card);border-radius:10px;padding:14px 16px;margin:12px 0}
.item.done{background:var(--done);opacity:.7}
.meta{color:var(--muted);font-size:14px}.c{white-space:pre-wrap;margin:8px 0}
button{font:inherit;padding:8px 14px;border-radius:8px;border:1px solid var(--accent);background:var(--accent);color:#fff;cursor:pointer;margin-right:8px}
button.ghost{background:transparent;color:var(--accent)}
</style>
<h1>Today: <span id="n"></span></h1>
<p class="meta">Open + copy, then on LinkedIn: click Like, paste (Ctrl+V), post. Then Done.</p>
<div id="list"></div>
<button class="ghost" onclick="fetch('/finish',{method:'POST'}).then(()=>document.body.innerHTML='<h1>Finished. You can close this tab.</h1>')">Finish</button>
<script>
const DATA = __DATA__;
const list = document.getElementById('list');
document.getElementById('n').textContent = DATA.items.length + ' posts (' + DATA.items.filter(i => i.comment).length + ' comments)';
for (const it of DATA.items) {
  const d = document.createElement('div'); d.className = 'item';
  const m = document.createElement('div'); m.className = 'meta';
  m.textContent = it.author + (it.type ? '  ·  ' + it.type : '  ·  like only') + '  ·  "' + it.first_line + '"';
  const c = document.createElement('div'); c.className = 'c'; c.textContent = it.comment || '(just like it)';
  const open = document.createElement('button');
  open.textContent = it.comment ? 'Open + copy comment' : 'Open';
  open.onclick = async () => { if (it.comment) { try { await navigator.clipboard.writeText(it.comment); } catch (e) {} } window.open(it.url, '_blank', 'noopener'); };
  const done = document.createElement('button'); done.className = 'ghost'; done.textContent = 'Done';
  done.onclick = () => fetch('/done', {method: 'POST', body: String(it.id)}).then(() => { d.classList.add('done'); done.disabled = true; });
  d.append(m, c, open, done); list.append(d);
}
</script>"""


def render(date, items):
    data = json.dumps({"date": date, "items": items}).replace("</", "<\\/")  # safe inside <script>
    return PAGE.replace("__DATA__", data)


def main():
    for s in (sys.stdout, sys.stderr):
        if hasattr(s, "reconfigure"):
            s.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser(description="One-click daily LinkedIn engagement list.")
    ap.add_argument("--port", type=int, default=8766)
    args = ap.parse_args()
    date, items = load_items()
    page = render(date, items).encode("utf-8")
    state = {"run": True, "done": set()}

    class Handler(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(page)

        def do_POST(self):
            body = self.rfile.read(int(self.headers.get("Content-Length") or 0)).decode()
            if self.path == "/done" and body.isdigit() and int(body) < len(items) and int(body) not in state["done"]:
                state["done"].add(int(body))
                append_log(items[int(body)], date)
            elif self.path == "/finish":
                state["run"] = False
            self.send_response(204)
            self.end_headers()

        def log_message(self, *a):
            pass

    srv = http.server.HTTPServer(("127.0.0.1", args.port), Handler)
    url = f"http://localhost:{args.port}/"
    print(f"Today's list: {url}  ({len(items)} posts). Click Finish on the page when you're done.")
    webbrowser.open(url)
    while state["run"]:
        srv.handle_request()
    print(f"Finished: {len(state['done'])} of {len(items)} done, logged to {LOG}")


if __name__ == "__main__":
    main()
