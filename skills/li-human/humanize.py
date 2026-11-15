#!/usr/bin/env python3
"""
humanize.py - clean the mechanical AI tells out of a draft, and flag the rest.

Based on Jake Schincariol's humanize.py, rewritten to follow Serge Bulaev's
Humanizer V3 rules (2026 evidence):

  1. INVISIBLE   delete zero-width joiners, word joiners, soft hyphens, BOMs,
                 Unicode tag characters; turn odd spaces into normal ones.
  2. TYPOGRAPHY  curly quotes -> straight, ellipsis -> "...", bullets -> "-".
                 Em dashes are CAPPED, not stripped: about 1 per 100 words,
                 max 2 per post. Only the excess becomes a comma. Never a
                 period (that creates fragment stacks).
  3. LEXICAL     "auto" phrases (carry no meaning) are replaced every time.
                 "density" words are ordinary English and only read as AI in
                 clusters, so they are counted per paragraph and a paragraph
                 with 3+ is flagged for a rewrite. --aggressive replaces them.
  4. FLAGS       structural tells and post-level checks are REPORTED, never
                 auto-rewritten: changing a sentence's shape needs judgement.

It never adds rhythm, hedges or confessions. Forced variance is a tell.

Usage
  python humanize.py draft.txt --report
  python humanize.py draft.txt -o clean.txt --report
  python humanize.py draft.txt --kind comment --report
  python humanize.py draft.txt --check          # flags only, no changes
  python humanize.py draft.txt --json
  cat draft.txt | python humanize.py - --report
"""

import argparse
import json
import os
import re
import statistics
import sys
import unicodedata

HERE = os.path.dirname(os.path.abspath(__file__))
LEX = os.path.join(HERE, "slop.json")

URL_RE = re.compile(r"https?://\S+|www\.\S+|\S+@\S+\.\S+")
SENT_RE = re.compile(r"[^.!?\n]+[.!?]*")
WORD_RE = re.compile(r"[A-Za-z0-9']+")
PLACEHOLDER_RE = re.compile(r"\{\{[^}]+\}\}")
HASHTAG_RE = re.compile(r"(?<![\w&])#\w+")
CLAUSE_WORDS = re.compile(r"(?i)\b(because|which|when|after|while|although|since|until|unless|so that|if)\b")

LENGTHS = {  # characters: (soft min, soft max)
    "post": (900, 1300),
    "comment": (120, 500),
    "reply": (60, 300),
    "dm": (60, 600),
    "any": (0, 100000),
}


# ---------------------------------------------------------------- helpers

def utf8_console():
    """Windows consoles default to cp1252, which can't print ₹ or emoji."""
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")


def read_text(path):
    if path == "-":
        return sys.stdin.buffer.read().decode("utf-8-sig")
    with open(path, encoding="utf-8-sig") as fh:
        return fh.read()


def load_lexicon(path=LEX):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def _cp(spec):
    if "-" in spec:
        a, b = spec.split("-")
        return (int(a[2:], 16), int(b[2:], 16))
    return int(spec[2:], 16)


def protect(text):
    """Swap URLs and {{placeholders}} out so no pass rewrites inside them."""
    found = []

    def stash(m):
        found.append(m.group(0))
        return f"\x00K{len(found) - 1}\x00"

    text = URL_RE.sub(stash, text)
    text = PLACEHOLDER_RE.sub(stash, text)
    return text, found


def restore(text, found):
    for i, s in enumerate(found):
        text = text.replace(f"\x00K{i}\x00", s)
    return text


def paragraphs(text):
    return [p for p in re.split(r"\n\s*\n", text) if p.strip()]


LIST_MARK = re.compile(r"(?m)^\s*(?:\d{1,2}[.)]|[-*•→]|->)\s+")
DECIMAL = re.compile(r"(?<=\d)\.(?=\d)")


def is_list_para(p):
    lines = [l for l in p.splitlines() if l.strip()]
    return bool(lines) and sum(bool(LIST_MARK.match(l)) for l in lines) >= max(2, len(lines) * 0.6)


def sentences(text):
    """Sentences, ignoring list markers ("1.", "-"), decimals ("4.5") and "P.S."."""
    text = LIST_MARK.sub("", text)
    text = DECIMAL.sub("\x01", text)
    text = re.sub(r"\bP\.\s?S\.", "PS", text)
    return [s.strip().replace("\x01", ".") for s in SENT_RE.findall(text)
            if s.strip() and words(s)]


def words(text):
    return WORD_RE.findall(text)


def term_pattern(find):
    body = re.escape(find).replace(r"\ ", r"\s+")
    lead = r"\b" if find[:1].isalnum() else ""
    tail = r"\b" if find[-1:].isalnum() else ""
    return re.compile(lead + body + tail, re.IGNORECASE)


def em_dash_cap(text):
    n = len(words(text))
    return max(1, min(2, round(n / 100)))


# ---------------------------------------------------------------- passes

def pass_invisible(text, lex):
    hits = []
    for entry in lex["invisible"]:
        cp = _cp(entry["cp"])
        if isinstance(cp, tuple):
            pattern = "[" + re.escape(chr(cp[0])) + "-" + re.escape(chr(cp[1])) + "]"
        else:
            pattern = re.escape(chr(cp))
        n = len(re.findall(pattern, text))
        if n:
            hits.append({"name": entry["cp"] + " " + entry["name"], "count": n,
                         "action": entry["action"]})
            text = re.sub(pattern, "" if entry["action"] == "delete" else " ", text)
    stray = [c for c in text if unicodedata.category(c) == "Cf" and c != "\x00"]
    if stray:
        hits.append({"name": "other invisible format chars", "count": len(stray),
                     "action": "delete"})
        text = "".join(c for c in text if unicodedata.category(c) != "Cf" or c == "\x00")
    return text, hits


def pass_typographic(text, lex):
    hits = []
    for entry in lex["typographic"]:
        n = text.count(entry["from"])
        if n:
            hits.append({"name": f"{entry['from']} {entry['name']}", "count": n,
                         "to": entry["to"].strip() or "(space)"})
            text = text.replace(entry["from"], entry["to"])

    # Double hyphen used as a dash -> comma.
    n = len(re.findall(r"\s--\s|\w--\w", text))
    if n:
        hits.append({"name": "-- double hyphen", "count": n, "to": ","})
        text = re.sub(r"\s*--\s*", ", ", text)

    # En dash: number ranges become hyphens; used as a dash between words -> comma.
    n = text.count("–")
    if n:
        hits.append({"name": "– EN DASH", "count": n, "to": "- (ranges) or ,"})
        text = re.sub(r"(?<=\d)\s*–\s*(?=\d)", "-", text)
        text = re.sub(r"\s*–\s*", ", ", text)

    # Em dash: keep up to the cap, turn only the excess into commas.
    cap = em_dash_cap(text)
    total = text.count("—")
    if total > cap:
        kept = 0
        out = []
        for part in re.split(r"(\s*—\s*)", text):
            if "—" in part:
                kept += 1
                out.append(part if kept <= cap else ", ")
            else:
                out.append(part)
        text = "".join(out)
        hits.append({"name": f"— EM DASH (kept {cap}, cap is ~1 per 100 words)",
                     "count": total - cap, "to": ","})

    text = re.sub(r",\s*([,.;:!?])", r"\1", text)
    text = re.sub(r",[ \t]*\n", "\n", text)
    return text, hits


def _match_case(src, repl):
    if not repl:
        return repl
    if src.isupper() and len(src) > 1:
        return repl.upper()
    if src[0].isupper():
        return repl[0].upper() + repl[1:]
    return repl


def _replace_terms(text, entries):
    hits = []
    for entry in sorted(entries, key=lambda e: len(e["find"]), reverse=True):
        if entry["replace"].startswith("<"):
            continue  # needs a human: "<a number>", "<say the thing>"
        pattern = term_pattern(entry["find"])
        found = pattern.findall(text)
        if not found:
            continue
        hits.append({"find": entry["find"], "replace": entry["replace"] or "(deleted)",
                     "count": len(found), "family": entry["family"]})
        def sub(m, repl=entry["replace"]):
            before = text[:m.start()].rstrip(" \t")
            starts_sentence = not before or before[-1] in ".!?\n"
            out = _match_case(m.group(0), repl)
            if out and not starts_sentence and not m.group(0).isupper():
                out = out[0].lower() + out[1:]
            return out
        text = pattern.sub(sub, text)
    return text, hits


def _tidy(text):
    text = re.sub(r"[ \t]{2,}", " ", text)
    text = re.sub(r"(?m)^[ \t]*[,;:]\s*", "", text)
    text = re.sub(r"\s+([,.;:!?])", r"\1", text)
    text = re.sub(r"([.!?])\s*,", r"\1", text)
    text = re.sub(r"(?m)^[ \t]+$", "", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    # Capitalise a sentence whose first word was deleted.
    text = re.sub(r"(^|[.!?]\s+|\n)([a-z])", lambda m: m.group(1) + m.group(2).upper(), text)
    return text


def pass_lexical(text, lex, aggressive=False):
    text, auto_hits = _replace_terms(text, lex["auto"])
    dens_hits = []
    if aggressive:
        text, dens_hits = _replace_terms(text, lex["density"])
    return _tidy(text), auto_hits + dens_hits


# ---------------------------------------------------------------- checks

def density_by_paragraph(text, lex):
    """Count density markers per paragraph. 3+ = rewrite, 2 = replace the weakest."""
    out = []
    for i, p in enumerate(paragraphs(text), 1):
        found = []
        for e in lex["density"]:
            for m in term_pattern(e["find"]).finditer(p):
                found.append(m.group(0).lower())
        if re.search(r"(?m)\b\w+ matters\.\s*$", p):
            found.append("'X matters.'")
        if len(found) >= 2:
            out.append({"paragraph": i, "count": len(found), "markers": found,
                        "action": "REWRITE PARAGRAPH" if len(found) >= 3 else "replace the weakest one"})
    return out


def scan_structures(text, lex):
    flags = []
    for s in lex["structures"]:
        try:
            pattern = re.compile(s["regex"])
        except re.error:
            continue
        found = pattern.findall(text)
        if found:
            flags.append({"id": s["id"], "severity": s["severity"], "name": s["name"],
                          "count": len(found), "fix": s["fix"]})
    return flags


def post_checks(text, kind="post"):
    """Post-level checks that are not a single regex."""
    flags = []
    lines = [l for l in text.splitlines() if l.strip()]
    first = lines[0].strip() if lines else ""
    paras = paragraphs(text)

    def add(fid, sev, name, fix, count=1):
        flags.append({"id": fid, "severity": sev, "name": name, "count": count, "fix": fix})

    if first.endswith("?") and kind in ("post", "any"):
        add("question-opener", "blocker", "Line 1 is a question (-34% median likes)",
            "Invert it into the number that answers it. Move the question to the close.")
    if re.match(r"(?i)here'?s (?:what|how|why|the thing)\b", first) and kind in ("post", "any"):
        add("heres-line1", "blocker", "Line 1 opens with \"Here's what/how\" (-4.3%)",
            "Lead with the number or the outcome instead.")
    letters = [c for c in first if c.isalpha()]
    if len(letters) >= 8 and sum(c.isupper() for c in letters) / len(letters) > 0.8:
        add("caps-opener", "blocker", "All-caps first line",
            "Carry the intensity with word choice, not caps. One CAPS word max.")
    if kind == "post" and len(first) > 140:
        add("long-hook", "warn", f"Line 1 is {len(first)} chars; mobile cuts at ~140",
            "Get the hook (and its number) inside the first 140 characters.")

    # Fragments: sentences of 1-3 words outside lists. Cap is 2 per post.
    prose = "\n\n".join(p for p in paras if not is_list_para(p))
    frags = [s for s in sentences(prose) if 0 < len(words(s)) <= 3]
    if len(frags) > 2:
        add("fragments", "warn", f"{len(frags)} standalone fragments (cap is 2)",
            "Fold the extras back into full sentences.", len(frags))

    # One-word paragraphs ("Still.", "Exactly.")
    one_word = [p for p in paras if re.fullmatch(r"\s*\w+[.!]\s*", p)]
    if one_word:
        add("one-word-para", "blocker", "One-word paragraph", "Merge it into the sentence before or after.",
            len(one_word))

    # Machine-flat paragraphs: 4+ sentences, all within +/-3 words of the mean, no working clause.
    flat = 0
    for p in paras:
        if is_list_para(p):
            continue  # a list is supposed to be parallel
        ss = [s for s in sentences(p) if len(words(s)) > 3]
        if len(ss) >= 4:
            ls = [len(words(s)) for s in ss]
            m = statistics.mean(ls)
            if all(abs(n - m) <= 3 for n in ls) and not any(CLAUSE_WORDS.search(s) for s in ss):
                flat += 1
    if flat:
        add("machine-flat", "warn", f"{flat} paragraph(s) read machine-flat",
            "Join ONE sentence to its neighbour with a clause that does work (because, which, when). Don't chop or alternate.",
            flat)

    # Seesaw: long/short/long/short across 6+ sentences.
    ls = [len(words(s)) for s in sentences(prose)]
    if len(ls) >= 8:
        signs = [1 if b > a * 1.8 else (-1 if a > b * 1.8 else 0) for a, b in zip(ls, ls[1:])]
        alternations = sum(1 for x, y in zip(signs, signs[1:]) if x and y and x == -y)
        if alternations >= max(4, (len(ls) - 2) * 0.5):
            add("seesaw", "warn", "Long/short/long/short seesaw rhythm",
                "That's a humanizer fingerprint. Let some neighbouring sentences be similar lengths.")

    # Hashtags, links, placeholders
    tags = HASHTAG_RE.findall(text)
    if len(tags) >= 5:
        add("hashtag-wall", "blocker", f"Hashtag wall ({len(tags)})", "0-2 hashtags, at the end.")
    elif len(tags) > 2:
        add("hashtags", "warn", f"{len(tags)} hashtags", "0-2 hashtags, at the end.")
    links = URL_RE.findall(text)
    if links and kind == "post":
        add("link-in-body", "warn", f"{len(links)} link(s) in the post body (0.4-0.6x reach)",
            "Move links to the first comment and say 'link in comments'.")
    holes = PLACEHOLDER_RE.findall(text)
    if holes:
        add("placeholders", "info", f"{len(holes)} open slot(s): " + ", ".join(sorted(set(holes))[:5]),
            "Fill each with a real number or detail before posting. Never invent one.", len(holes))

    # Length
    lo, hi = LENGTHS.get(kind, LENGTHS["any"])
    n = len(text.strip())
    if n and (n < lo or n > hi):
        add("length", "info", f"{n} characters (target {lo}-{hi} for a {kind})",
            "Fine if deliberate. Over 3,000 won't post.")
    if n > 3000 and kind == "post":
        flags[-1]["severity"] = "blocker"
    return flags


def count_contrasts(structure_flags):
    return sum(f["count"] for f in structure_flags if f["id"] in ("not-just", "isnt-its", "not-but", "not-only"))


def count_triads(structure_flags):
    return sum(f["count"] for f in structure_flags if f["id"] == "triad")


def without_urls(text):
    """URLs and emails carry words like 'leverage-robust' that aren't prose."""
    return URL_RE.sub(" ", text)


def analyse(text, lex, kind="post"):
    """All flags for a text, without changing it."""
    s = scan_structures(without_urls(text), lex)
    pc = post_checks(text, kind)
    if any(f["id"] == "heres-line1" for f in pc):
        for f in s:
            if f["id"] == "heres-opener":
                f["count"] -= 1
        s = [f for f in s if f["count"] > 0]
    flags = s + pc
    c = count_contrasts(s)
    if c >= 2:
        flags.append({"id": "contrast-density", "severity": "blocker",
                      "name": f"{c} contrasts (density rule: one per post)", "count": c,
                      "fix": "Keep the strongest contrast, rewrite the rest as plain statements."})
    t = count_triads(s)
    if t >= 2:
        flags.append({"id": "triad-density", "severity": "warn",
                      "name": f"{t} triads (density rule: one per post)", "count": t,
                      "fix": "Keep one concrete triple. Make the others two items or four."})
    return {"structures": flags, "density": density_by_paragraph(without_urls(text), lex)}


def humanize(text, lex, kind="post", aggressive=False):
    text, kept = protect(text)
    text, inv = pass_invisible(text, lex)
    text, typo = pass_typographic(text, lex)
    text, lexi = pass_lexical(text, lex, aggressive)
    text = restore(text, kept)
    clean = text.strip() + "\n"
    report = {"invisible": inv, "typographic": typo, "lexical": lexi}
    report.update(analyse(clean, lex, kind))
    return clean, report


# ---------------------------------------------------------------- output

def render_report(report, out=sys.stderr):
    def head(title):
        print(f"\n{title}\n" + "-" * len(title), file=out)

    fixed = sum(h["count"] for k in ("invisible", "typographic", "lexical") for h in report.get(k, []))
    blockers = [f for f in report["structures"] if f["severity"] == "blocker"]
    warns = [f for f in report["structures"] if f["severity"] == "warn"]
    infos = [f for f in report["structures"] if f["severity"] == "info"]

    head("HUMANIZE REPORT")
    print(f"{fixed} mechanical fixes applied · {len(blockers)} blockers · {len(warns)} warnings · "
          f"{len(report['density'])} dense paragraph(s)", file=out)

    if report.get("invisible"):
        head("1. INVISIBLE CHARACTERS (fixed)")
        for h in report["invisible"]:
            print(f"  {h['count']:>3}x  {h['name']}  -> {h['action']}", file=out)
    if report.get("typographic"):
        head("2. TYPOGRAPHY (fixed)")
        for h in report["typographic"]:
            print(f"  {h['count']:>3}x  {h['name']}  -> {h['to']}", file=out)
    if report.get("lexical"):
        head("3. STOCK PHRASES (fixed)")
        for h in report["lexical"]:
            print(f"  {h['count']:>3}x  {h['find']}  -> {h['replace']}", file=out)
    if report["density"]:
        head("4. DENSE PARAGRAPHS (rewrite by hand)")
        for d in report["density"]:
            print(f"  para {d['paragraph']}: {d['count']} markers ({', '.join(d['markers'][:6])}) -> {d['action']}",
                  file=out)
    if blockers or warns:
        head("5. STRUCTURE (rewrite by hand)")
        for f in blockers + warns:
            tag = "BLOCK" if f["severity"] == "blocker" else "warn "
            print(f"  [{tag}] {f['count']}x {f['name']}\n           {f['fix']}", file=out)
    if infos:
        head("6. NOTES")
        for f in infos:
            print(f"  {f['name']}\n    {f['fix']}", file=out)
    if not fixed and not blockers and not warns and not report["density"]:
        head("CLEAN")
        print("  Nothing to fix. Don't invent edits.", file=out)
    print("", file=out)


def main():
    ap = argparse.ArgumentParser(description="Clean mechanical AI tells out of a draft and flag the rest.")
    ap.add_argument("input", nargs="?", default="-", help="file, or - for stdin")
    ap.add_argument("-o", "--out", help="write cleaned text here instead of stdout")
    ap.add_argument("--kind", choices=sorted(LENGTHS), default="post", help="sets length and opener checks")
    ap.add_argument("--report", action="store_true", help="print what changed and what to rewrite (stderr)")
    ap.add_argument("--check", action="store_true", help="flags only; print nothing else, change nothing")
    ap.add_argument("--aggressive", action="store_true", help="also replace density words (blunt)")
    ap.add_argument("--json", action="store_true", help="emit {text, report} as JSON")
    ap.add_argument("--lexicon", default=LEX, help="path to slop.json")
    args = ap.parse_args()
    utf8_console()

    raw = read_text(args.input)
    lex = load_lexicon(args.lexicon)

    if args.check:
        report = {"invisible": [], "typographic": [], "lexical": []}
        report.update(analyse(raw, lex, args.kind))
        if args.json:
            print(json.dumps(report, indent=2, ensure_ascii=False))
        else:
            render_report(report, out=sys.stdout)
        return

    clean, report = humanize(raw, lex, args.kind, args.aggressive)
    if args.json:
        print(json.dumps({"text": clean, "report": report}, indent=2, ensure_ascii=False))
        return
    if args.out:
        with open(args.out, "w", encoding="utf-8") as fh:
            fh.write(clean)
        print(f"wrote {args.out}", file=sys.stderr)
    else:
        sys.stdout.write(clean)
    if args.report:
        render_report(report)


if __name__ == "__main__":
    main()
