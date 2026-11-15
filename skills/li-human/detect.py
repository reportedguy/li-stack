#!/usr/bin/env python3
"""
detect.py - a five-check panel for how machine-written a draft reads.

Based on Jake Schincariol's detect.py, recalibrated to Serge Bulaev's V3
evidence. The big change: RHYTHM replaces BURSTINESS. The old check rewarded
sentence-length variation, but forced variance is now the #1 humanizer tell
and doesn't move LinkedIn engagement either way. RHYTHM only penalises
machine-flat paragraphs, staccato runs and long/short seesaws.

What this is NOT: GPTZero, Originality, Copyleaks, Pangram or Turnitin. It
doesn't call them and can't promise their verdict. Nothing is uploaded.
On 100-300 word posts, even real detectors are mostly noise. This measures
what human readers and LinkedIn's "AI slop" report button react to.

Each check scores 0-100, higher = more human. Checks that can't judge a
short text (e.g. a 2-line comment) say n/a and are left out of the verdict.

Usage
  python detect.py draft.txt
  python detect.py draft.txt --kind comment
  python detect.py before.txt after.txt      # show the delta
  python detect.py draft.txt --json
"""

import argparse
import importlib.util
import json
import os
import re
import statistics
import sys
import unicodedata

HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location("humanize", os.path.join(HERE, "humanize.py"))
H = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(H)

CONTRACTIONS = re.compile(r"\b\w+'(?:s|t|re|ve|ll|d|m)\b", re.IGNORECASE)
PRONOUNS = re.compile(r"\b(i|me|my|mine|we|us|our|you|your)\b", re.IGNORECASE)
NUMBERS = re.compile(r"(?:[$₹€£]\s?)?\b\d[\d,.]*\s?(?:%|x|k|hrs?|hours|days|weeks|months|mins?)?\b")
PROPER = re.compile(r"(?<![.!?]\s)(?<!^)\b[A-Z][a-zA-Z]{2,}\b", re.MULTILINE)
CHECKS = ["RHYTHM", "SPECIFICITY", "SLOP DENSITY", "FINGERPRINT", "VOICE"]


def clamp(n):
    return max(0.0, min(100.0, n))


def scale(value, human, machine):
    if human == machine:
        return 50.0
    return clamp((value - machine) / (human - machine) * 100)


def check_rhythm(text, flags):
    ss = [s for s in H.sentences(text) if H.words(s)]
    if len(ss) < 4:
        return None, "too short to judge"
    penalty, notes = 0, []
    for f in flags:
        if f["id"] in ("staccato-run", "no-no-just", "all-none", "one-word-para"):
            penalty += 25 * f["count"]; notes.append(f["id"])
        elif f["id"] == "machine-flat":
            penalty += 20 * f["count"]; notes.append("machine-flat")
        elif f["id"] == "seesaw":
            penalty += 15; notes.append("seesaw")
        elif f["id"] == "fragments":
            penalty += 10 * (f["count"] - 2); notes.append(f"{f['count']} fragments")
        elif f["id"] in ("reveal-bridge", "socratic"):
            penalty += 15 * f["count"]; notes.append(f["id"])
    return clamp(100 - penalty), ("no staged rhythm" if not notes else ", ".join(notes))


def check_specificity(text):
    w = H.words(text)
    if len(w) < 25:
        return None, "too short to judge"
    hits = len(NUMBERS.findall(text)) + len(set(PROPER.findall(text))) + len(H.PLACEHOLDER_RE.findall(text))
    density = hits * 100 / len(w)
    return scale(density, human=6.0, machine=0.5), f"{hits} concrete markers, {density:.1f} per 100 words (want 4+)"


def check_slop(text, lex, dense):
    text = H.without_urls(text)
    w = H.words(text)
    if not w:
        return None, "empty"
    hits, found = 0, []
    for e in lex["auto"]:
        n = len(H.term_pattern(e["find"]).findall(text))
        if n:
            hits += n; found.append(e["find"])
    dens = sum(d["count"] for d in dense)
    for e in lex["density"]:
        if H.term_pattern(e["find"]).search(text):
            found.append(e["find"])
    allm = sum(len(H.term_pattern(e["find"]).findall(text)) for e in lex["density"])
    per100 = (hits * 2 + allm) * 100 / len(w)
    score = scale(per100, human=0.0, machine=5.0)
    if any(d["count"] >= 3 for d in dense):
        score = min(score, 40.0)
    detail = f"{hits} stock phrases, {allm} marker words, {per100:.1f} weighted per 100 words"
    if dens:
        detail += f"; {len(dense)} dense paragraph(s)"
    if found:
        detail += " (" + ", ".join(sorted(set(found))[:4]) + (", ..." if len(set(found)) > 4 else "") + ")"
    return score, detail


def check_fingerprint(text):
    invisible = sum(1 for c in text if unicodedata.category(c) == "Cf")
    em_excess = max(0, text.count("—") - H.em_dash_cap(text))
    curly = sum(text.count(c) for c in "‘’“”")
    ellip = text.count("…")
    odd_space = sum(text.count(c) for c in "    ")
    total = invisible * 4 + em_excess * 3 + curly + ellip + odd_space
    per1k = total * 1000 / max(len(text), 1)
    return (scale(per1k, human=0.0, machine=12.0),
            f"{invisible} invisible, {em_excess} em dash over cap, {curly} curly quote, "
            f"{ellip} ellipsis, {odd_space} odd space")


def check_voice(text, flags):
    w = H.words(text)
    blockers = [f for f in flags if f["severity"] == "blocker"]
    warns = [f for f in flags if f["severity"] == "warn" and f["id"] not in ("length", "long-hook", "triad")]
    tells = sum(f["count"] for f in blockers) * 1.0 + sum(f["count"] for f in warns) * 0.5
    names = [f["id"] for f in blockers + warns][:4]
    if len(w) < 25:
        if not tells:
            return None, "too short to judge"
        return clamp(100 - tells * 25), f"{tells:g} tell(s) [{', '.join(names)}]"
    per100 = 100 / len(w)
    contractions = len(CONTRACTIONS.findall(text)) * per100
    person = len(PRONOUNS.findall(text)) * per100
    score = (scale(contractions, human=3.0, machine=0.0) * 0.35
             + scale(person, human=8.0, machine=1.0) * 0.35
             + clamp(100 - tells * 22) * 0.30)
    detail = f"{contractions:.1f} contractions, {person:.1f} personal pronouns per 100 words, {tells:g} tell(s)"
    if names:
        detail += " [" + ", ".join(names) + "]"
    return clamp(score), detail


def run(text, lex, kind="post"):
    a = H.analyse(text, lex, kind)
    flags, dense = a["structures"], a["density"]
    results = {
        "RHYTHM": check_rhythm(text, flags),
        "SPECIFICITY": check_specificity(text),
        "SLOP DENSITY": check_slop(text, lex, dense),
        "FINGERPRINT": check_fingerprint(text),
        "VOICE": check_voice(text, flags),
    }
    scores = [v[0] for v in results.values() if v[0] is not None]
    blockers = [f for f in flags if f["severity"] == "blocker"]
    if not scores:
        return results, None, "TOO SHORT", blockers
    overall = statistics.mean(scores) * 0.6 + min(scores) * 0.4
    if overall >= 70 and min(scores) >= 55 and not blockers:
        verdict = "PASS"
    elif overall >= 50:
        verdict = "REVIEW"
    else:
        verdict = "FLAGGED"
    return results, overall, verdict, blockers


def bar(score, width=24):
    filled = int(round(score / 100 * width))
    return "#" * filled + "." * (width - filled)


def render(results, overall, verdict, blockers, label=None, out=sys.stdout):
    print(("\n" + label) if label else "", file=out)
    print("READS-HUMAN PANEL (local heuristics, not a detector)", file=out)
    print("=" * 62, file=out)
    for name in CHECKS:
        score, detail = results[name]
        if score is None:
            print(f"  {name:<13} {'n/a':>30}", file=out)
        else:
            print(f"  {name:<13} {bar(score)} {score:5.1f}", file=out)
        print(f"                {detail}", file=out)
    print("-" * 62, file=out)
    if overall is None:
        print("  HUMAN SCORE   n/a (too short for any check; read it aloud instead)", file=out)
        return
    print(f"  HUMAN SCORE   {bar(overall)} {overall:5.1f}   {verdict}", file=out)
    if blockers:
        print(f"\n  {len(blockers)} blocker(s) keep this below PASS: "
              + ", ".join(b["id"] for b in blockers), file=out)
    if verdict != "PASS":
        judged = {k: v[0] for k, v in results.items() if v[0] is not None}
        weakest = min(judged, key=judged.get)
        print(f"  Weakest signal: {weakest}. Fix that first.", file=out)


def main():
    ap = argparse.ArgumentParser(description="Five-check reads-human panel.")
    ap.add_argument("inputs", nargs="+", help="one file, or two to compare (before after); - for stdin")
    ap.add_argument("--kind", choices=sorted(H.LENGTHS), default="post")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--lexicon", default=H.LEX)
    args = ap.parse_args()
    H.utf8_console()
    lex = H.load_lexicon(args.lexicon)

    payload = []
    for path in args.inputs[:2]:
        text = H.read_text(path)
        results, overall, verdict, blockers = run(text, lex, args.kind)
        payload.append({"file": path, "results": results, "overall": overall,
                        "verdict": verdict, "blockers": blockers})

    if args.json:
        print(json.dumps(payload, indent=2, ensure_ascii=False, default=str))
    else:
        for p in payload:
            render(p["results"], p["overall"], p["verdict"], p["blockers"],
                   label=p["file"] if len(payload) > 1 else None)
        if len(payload) == 2 and None not in (payload[0]["overall"], payload[1]["overall"]):
            d = payload[1]["overall"] - payload[0]["overall"]
            print(f"\n  DELTA  {d:+.1f}  ({payload[0]['verdict']} -> {payload[1]['verdict']})")
        print("")
    sys.exit(0 if payload[-1]["verdict"] == "PASS" else 1)


if __name__ == "__main__":
    main()
