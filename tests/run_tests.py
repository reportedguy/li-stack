"""li-stack self-tests. Standard library only, offline, nothing posted.

    python tests/run_tests.py          (Windows: python, not python3)

Checks that the bundle still holds together after an edit: every skill loads,
every file and id a skill points at exists, the humanizer still catches the
bad sample and leaves the clean ones alone, the scripts survive a cp1252
console, the robot refuses unfinished posts, and no personal detail leaked
into the bundle.
"""
import datetime as dt
import glob
import importlib.util
import json
import os
import re
import subprocess
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIX = os.path.join(ROOT, "tests", "fixtures")
HUMAN = os.path.join(ROOT, "skills", "li-human")
PUBLISH = os.path.join(ROOT, "skills", "li-publish", "publish.py")
SKILLS = sorted(glob.glob(os.path.join(ROOT, "skills", "*", "SKILL.md")))
# Words that would mean your own details leaked into the bundle. List them, one per
# line, in tests/private_words.txt (gitignored, so the list itself never goes public).
_PW = os.path.join(ROOT, "tests", "private_words.txt")
PERSONAL = [w.rstrip("\r\n") for w in open(_PW, encoding="utf-8") if w.strip()] if os.path.exists(_PW) else []


def read(p):
    with open(p, encoding="utf-8") as fh:
        return fh.read()


def frontmatter(text):
    m = re.match(r"---\n(.*?)\n---\n", text, re.S)
    if not m:
        return None
    fm, out, key = m.group(1), {}, None
    for line in fm.splitlines():
        km = re.match(r"([a-z_]+):\s*(.*)$", line)
        if km:
            key, val = km.group(1), km.group(2)
            out[key] = "" if val in (">-", ">", "|") else val
        elif key and line.startswith("  "):
            out[key] = (out[key] + " " + line.strip()).strip()
    return out


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def run(args, env_extra=None, stdin=None):
    env = dict(os.environ, **(env_extra or {}))
    return subprocess.run([sys.executable] + args, capture_output=True, input=stdin, env=env, timeout=60)


class Skills(unittest.TestCase):
    def test_there_are_16_skills(self):
        self.assertEqual(len(SKILLS), 16, [os.path.basename(os.path.dirname(s)) for s in SKILLS])

    def test_frontmatter_parses_and_name_matches_folder(self):
        for p in SKILLS:
            fm = frontmatter(read(p))
            folder = os.path.basename(os.path.dirname(p))
            self.assertIsNotNone(fm, p)
            self.assertEqual(fm.get("name"), folder, p)
            d = fm.get("description", "")
            self.assertTrue(40 < len(d) <= 1024, f"{folder}: description length {len(d)}")
            self.assertNotIn("—", d, f"{folder}: em dash in description")

    def test_relative_paths_exist(self):
        for p in SKILLS:
            for ref in re.findall(r"`(\.\./\.\./[^`\s]+)`", read(p)):
                self.assertTrue(os.path.exists(os.path.join(os.path.dirname(p), ref)), f"{p}: {ref}")

    def test_files_named_in_a_skill_exist_in_its_folder(self):
        for p in SKILLS:
            here = os.path.dirname(p)
            for f in set(re.findall(r"`?([a-z_]+\.(?:py|json))`?", read(p))):
                if f in ("hooks.json", "slop.json", "rubric.json", "humanize.py", "detect.py", "publish.py", "app.json", "token.json"):
                    if f in ("hooks.json",):
                        self.assertTrue(os.path.exists(os.path.join(ROOT, "shared", f)))
                    elif f in ("app.json", "token.json"):
                        continue  # created by setup, outside the bundle
                    else:
                        self.assertTrue(glob.glob(os.path.join(ROOT, "skills", "*", f)), f"{p}: {f}")

    def test_every_sibling_skill_named_exists(self):
        names = {os.path.basename(os.path.dirname(s)) for s in SKILLS}
        for p in SKILLS + [os.path.join(ROOT, "README.md"), os.path.join(ROOT, "shared", "rules.md")]:
            for s in set(re.findall(r"/(li-[a-z-]+)", read(p))) - {"li-stack"}:
                self.assertIn(s, names, f"{p} names /{s}")

    def test_templates_skills_copy_exist(self):
        for t in ("voice.md", "story-bank.md", "swipe.md", "log.md", "watchlist.md"):
            self.assertTrue(os.path.exists(os.path.join(ROOT, "templates", t)), t)


class Ids(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.hooks = json.loads(read(os.path.join(ROOT, "shared", "hooks.json")))
        cls.hook_ids = {h["id"] for h in cls.hooks["hooks"]}
        cls.angles = read(os.path.join(ROOT, "shared", "angles.md"))
        cls.angle_ids = set(re.findall(r"^\| (S\d+) \|", cls.angles, re.M))

    def test_40_hooks_with_every_field(self):
        self.assertEqual(len(self.hook_ids), 40)
        for h in self.hooks["hooks"]:
            for k in ("template", "example", "trap", "note_2026", "goal", "best_for"):
                self.assertTrue(h.get(k), f"{h['id']} missing {k}")

    def test_goal_lists_use_real_hooks(self):
        for goal, ids in self.hooks["goals"].items():
            self.assertTrue(set(ids) <= self.hook_ids, goal)
        listed = {i for ids in self.hooks["goals"].values() for i in ids}
        self.assertEqual(listed, self.hook_ids, "every hook is under at least one goal")

    def test_angles_are_s1_to_s9(self):
        self.assertEqual(self.angle_ids, {f"S{i}" for i in range(1, 10)})

    def test_every_hook_id_referenced_exists(self):
        files = SKILLS + glob.glob(os.path.join(ROOT, "shared", "*.md")) + glob.glob(os.path.join(ROOT, "templates", "*.md"))
        for p in files:
            text = read(p)
            for h in set(re.findall(r"\bH\d{2}\b", text)) - {"H41"}:  # "add as H41+" in li-hook-extract
                self.assertIn(h, self.hook_ids, f"{p}: {h}")

    def test_every_angle_id_referenced_exists(self):
        files = SKILLS + glob.glob(os.path.join(ROOT, "shared", "*.md")) + glob.glob(os.path.join(ROOT, "templates", "*.md"))
        for p in files:
            for s in set(re.findall(r"\bS(\d{1,2})\b", read(p))):
                self.assertIn(f"S{s}", self.angle_ids, f"{p}: S{s}")


class Contracts(unittest.TestCase):
    def test_interview_spine_matches_post(self):
        lines = ["Moment", "Number", "Correction", "Opposition", "Ask"]
        interview = read(os.path.join(ROOT, "skills", "li-interview", "SKILL.md"))
        post = read(os.path.join(ROOT, "skills", "li-post", "SKILL.md"))
        for l in lines:
            self.assertIn(f"**{l}**", interview, l)
            self.assertIn(l, post, l)

    def test_no_python3_commands_for_windows(self):
        for p in SKILLS + [os.path.join(ROOT, "README.md")]:
            self.assertNotRegex(read(p), r"(?<![!/])\bpython3 ", p)

    def test_no_comment_gate_advised_in_templates(self):
        voice = read(os.path.join(ROOT, "templates", "voice.md"))
        self.assertNotRegex(voice, r"(?i)close with[^\n]*comment \{word\} and I'll")

    def test_no_personal_details_in_bundle(self):
        for folder, dirs, files in os.walk(ROOT):
            dirs[:] = [d for d in dirs if d not in (".git", "__pycache__", "tests")]
            for f in files:
                if f.endswith((".md", ".json", ".py", ".txt")):
                    text = read(os.path.join(folder, f))
                    for w in PERSONAL:
                        self.assertNotIn(w, text, f"{os.path.join(folder, f)} contains {w!r}")

    def test_license_and_marketplace_have_no_placeholders(self):
        for p in ("LICENSE", os.path.join(".claude-plugin", "marketplace.json")):
            self.assertNotIn("{{", read(os.path.join(ROOT, p)), p)
        json.loads(read(os.path.join(ROOT, ".claude-plugin", "marketplace.json")))
        json.loads(read(os.path.join(ROOT, ".claude-plugin", "plugin.json")))


class Humanizer(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        sys.path.insert(0, HUMAN)
        cls.D = load("detect", os.path.join(HUMAN, "detect.py"))
        cls.H = cls.D.H
        cls.lex = cls.H.load_lexicon()

    def verdict(self, text, kind="post"):
        _, overall, verdict, blockers = self.D.run(text, self.lex, kind)
        return overall, verdict, [b["id"] for b in blockers]

    def test_bad_sample_is_flagged(self):
        overall, verdict, blockers = self.verdict(read(os.path.join(FIX, "bad_post.txt")))
        self.assertEqual(verdict, "FLAGGED", overall)
        for b in ("question-opener", "reveal-bridge", "sincerity", "comment-gate", "hashtag-wall"):
            self.assertIn(b, blockers)

    def test_clean_sample_passes(self):
        overall, verdict, blockers = self.verdict(read(os.path.join(FIX, "clean_post.txt")))
        self.assertEqual(verdict, "PASS", (overall, blockers))

    def test_list_decimal_url_and_one_dash_stay_clean(self):
        text = read(os.path.join(FIX, "fp_list.txt"))
        overall, verdict, blockers = self.verdict(text)
        self.assertEqual(verdict, "PASS", (overall, blockers))
        dense = self.H.analyse(text, self.lex)["density"]
        self.assertEqual(dense, [], "marker words inside a URL must not count")
        clean, _ = self.H.humanize(text, self.lex)
        self.assertIn("—", clean, "a single em dash is kept, not stripped")
        self.assertIn("4.5 seconds", clean)
        self.assertIn("https://example.com/leverage-robust-notes", clean, "URLs are never rewritten")

    def test_ps_is_not_two_fragments(self):
        text = ("I shipped the first version of my app in March and five friends used it every day.\n\n"
                "P.S. The setup notes are in the first comment if you want to copy them.")
        frags = [s for s in self.H.sentences(text) if len(self.H.words(s)) <= 3]
        self.assertEqual(frags, [])

    def test_placeholders_survive_cleaning(self):
        clean, report = self.H.humanize("In today's fast-paced world I shipped {{N}} apps for {{my number}} users.", self.lex)
        self.assertIn("{{N}}", clean)
        self.assertIn("{{my number}}", clean)
        self.assertNotIn("fast-paced", clean)

    def test_voice_examples_pass(self):
        for t in (os.path.join(ROOT, "templates", "voice.md"),):
            blocks = re.findall(r"```\n(.*?)```", read(t), re.S)
            self.assertGreaterEqual(len(blocks), 2)
            for b in blocks:
                self.assertEqual(self.verdict(b)[1], "PASS", b[:60])

    def test_rupee_and_emoji_survive_a_cp1252_console(self):
        f = os.path.join(FIX, "rupee_comment.txt")
        env = {"PYTHONIOENCODING": "cp1252"}
        r = run(["-I", os.path.join(HUMAN, "humanize.py"), f, "--report", "--kind", "comment"], env)
        self.assertEqual(r.returncode, 0, r.stderr.decode("utf-8", "replace"))
        self.assertIn("₹4,000".encode("utf-8"), r.stdout)
        self.assertIn("🙃".encode("utf-8"), r.stdout)
        r = run(["-I", os.path.join(HUMAN, "humanize.py"), "-"], env, stdin=read(f).encode("utf-8"))
        self.assertIn("₹333".encode("utf-8"), r.stdout, "stdin is read as UTF-8")
        r = run(["-I", os.path.join(HUMAN, "detect.py"), f, "--kind", "comment"], env)
        self.assertEqual(r.returncode, 0, r.stderr.decode("utf-8", "replace"))


class DailyList(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.D = load("daily", os.path.join(ROOT, "skills", "li-comment", "daily.py"))

    def write(self, home, items):
        p = os.path.join(home, "today.json")
        with open(p, "w", encoding="utf-8") as fh:
            json.dump({"date": "2026-11-16", "items": items}, fh)
        return p

    def test_only_linkedin_links_are_accepted(self):
        with tempfile.TemporaryDirectory() as home:
            p = self.write(home, [{"author": "A", "url": "https://evil.example/x", "comment": "hi"}])
            with self.assertRaises(ValueError):
                self.D.load_items(p)

    def test_comment_text_cannot_break_out_of_the_page(self):
        with tempfile.TemporaryDirectory() as home:
            p = self.write(home, [{"author": "A", "url": "https://www.linkedin.com/posts/a-activity-1",
                                   "comment": "</script><script>alert(1)</script> ₹400"}])
            date, items = self.D.load_items(p)
            page = self.D.render(date, items)
            self.assertEqual(page.count("</script>"), 1, "only the page's own closing tag")
            self.assertIn("\\u20b9400", page, "₹ survives as a JSON escape the browser decodes")

    def test_done_items_are_logged_once_per_click(self):
        with tempfile.TemporaryDirectory() as home:
            log = os.path.join(home, "log.md")
            with open(log, "w", encoding="utf-8") as fh:
                fh.write("| date | author | post url | comment type | reply seen |\n|---|---|---|---|---|")
            item = {"author": "Ana | B", "url": "https://www.linkedin.com/posts/x", "type": "", "comment": ""}
            self.D.append_log(item, "2026-11-16", log)
            text = read(log)
            self.assertIn("|---|---|---|---|---|\n| 2026-11-16 | Ana / B | https://www.linkedin.com/posts/x | like only |", text)


class Publisher(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.P = load("publish", PUBLISH)

    def test_little_text_is_escaped_but_hashtags_stay(self):
        out = self.P.escape_little_text("Cost (₹400) for @team [beta] #buildinpublic")
        self.assertEqual(out, "Cost \\(₹400\\) for \\@team \\[beta\\] #buildinpublic")

    def test_post_ids_from_urls(self):
        self.assertEqual(self.P.parent_urns("https://www.linkedin.com/feed/update/urn:li:activity:7390000000000000001/")[0],
                         "urn:li:share:7390000000000000001")
        self.assertEqual(self.P.parent_urns("https://www.linkedin.com/posts/someone_slug-activity-7390000000000000002-AbCd")[0],
                         "urn:li:share:7390000000000000002")

    def test_queue_refuses_placeholders_and_dry_run_sends_nothing(self):
        with tempfile.TemporaryDirectory() as home:
            env = {"LI_STACK_HOME": home}
            draft = os.path.join(home, "d.txt")
            with open(draft, "w", encoding="utf-8") as fh:
                fh.write("I shipped {{N}} apps.")
            r = run([PUBLISH, "queue", "--at", "2020-01-01 09:00", "--text-file", draft], env)
            self.assertNotEqual(r.returncode, 0)
            self.assertIn(b"placeholders", r.stderr + r.stdout)
            with open(draft, "w", encoding="utf-8") as fh:
                fh.write("I shipped 3 apps (₹0 spent).")
            r = run([PUBLISH, "queue", "--at", "2020-01-01 09:00", "--text-file", draft, "--image", "x.png"], env)
            self.assertEqual(r.returncode, 0, r.stderr)
            r = run([PUBLISH, "list"], env)
            self.assertIn(b"MISSING", r.stdout)
            r = run([PUBLISH, "run", "--dry-run"], env)
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertIn(b"waiting", r.stdout, "a post with a missing image waits")
            self.assertEqual(len(glob.glob(os.path.join(home, "queue", "*.json"))), 1, "nothing was moved")

    def test_second_run_skips_an_item_already_being_sent(self):
        with tempfile.TemporaryDirectory() as home:
            self.use_home(home)
            path = self.queue_item("post-a.json", dt.datetime.now().astimezone())
            claimed = self.P.claim_for_send(path)
            self.assertEqual(claimed["status"], "sending")
            self.assertIsNone(self.P.claim_for_send(path), "a second run must leave a claimed item alone")
            self.assertTrue(os.path.exists(path))

    def test_interrupted_send_is_parked_not_reposted(self):
        with tempfile.TemporaryDirectory() as home:
            self.use_home(home)
            started = dt.datetime.now().astimezone() - dt.timedelta(hours=2)
            path = self.queue_item("post-b.json", started)
            item = self.P.read_json(path)
            item.update(status="sending", sending_at=started.isoformat())
            self.P.write_json(path, item)
            self.assertIsNone(self.P.claim_for_send(path))
            self.assertFalse(os.path.exists(path), "the item leaves the queue")
            parked = os.path.join(self.P.QUEUE, "failed", "post-b.json")
            with open(parked, encoding="utf-8") as fh:
                item = json.load(fh)
            self.assertEqual(item["status"], "failed")
            self.assertIn("interrupted", item["error"])

    def test_run_lock_is_exclusive(self):
        with tempfile.TemporaryDirectory() as home:
            self.use_home(home)
            first = self.P.acquire_run_lock()
            self.assertIsNotNone(first)
            self.assertIsNone(self.P.acquire_run_lock(), "only one run at a time")
            self.P.release_run_lock(first)
            second = self.P.acquire_run_lock()
            self.assertIsNotNone(second)
            self.P.release_run_lock(second)

    def use_home(self, home):
        P = self.P
        P.HOME = home
        P.SECRETS = os.path.join(home, "secrets")
        P.QUEUE = os.path.join(home, "queue")
        P.IMAGES = os.path.join(home, "images")
        P.LOG = os.path.join(home, "publish.log")
        os.makedirs(P.QUEUE, exist_ok=True)
        os.makedirs(P.IMAGES, exist_ok=True)

    def queue_item(self, name, at):
        path = os.path.join(self.P.QUEUE, name)
        self.P.write_json(path, {"kind": "post", "at": at.isoformat(), "text": "Shipping.", "status": "pending"})
        return path


if __name__ == "__main__":
    unittest.main(verbosity=1)
