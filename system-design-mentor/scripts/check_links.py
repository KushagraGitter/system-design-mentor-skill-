#!/usr/bin/env python3
"""Check every URL in the skill's markdown files and report the broken ones.

Usage: check_links.py [--json] [--timeout 15] [files...]
Default files: references/*.md and the repo README (if present).

YouTube videos are checked through YouTube's oEmbed endpoint, which returns 404/401 for removed or
private videos (the watch page itself always returns 200). YouTube *search* links are skipped —
they can't break. Exit code 1 when anything is broken, so CI fails and the owner gets notified.
"""
from __future__ import annotations

import concurrent.futures as cf
import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

SKILL = Path(__file__).resolve().parent.parent
URL_RE = re.compile(r"https?://[^\s)<>\"'`]+")
UA = "Mozilla/5.0 (link-checker for system-design-mentor skill)"
# sites that block bots with 403/429 even when the page is fine — report as "unverified", not broken
SOFT_BLOCK = ("amazon.com", "oreilly.com", "medium.com", "linkedin.com", "teamblind.com")


def collect(files):
    found = {}
    for f in files:
        for n, line in enumerate(Path(f).read_text(encoding="utf-8").splitlines(), 1):
            for url in URL_RE.findall(line):
                url = url.rstrip(".,;:*")
                found.setdefault(url, []).append(f"{Path(f).name}:{n}")
    return found


def fetch(url, timeout):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "*/*"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, ""
    except urllib.error.HTTPError as e:
        return e.code, e.reason
    except Exception as e:  # DNS, TLS, timeout
        return None, str(e)[:120]


def check(url, timeout):
    host = urllib.parse.urlparse(url).netloc.lower()
    if "youtube.com/results" in url:
        return "skipped", None, "search link"
    if "youtube.com/watch" in url or "youtu.be/" in url:
        oembed = "https://www.youtube.com/oembed?format=json&url=" + urllib.parse.quote(url, safe="")
        code, why = fetch(oembed, timeout)
        if code == 200:
            return "ok", code, ""
        return "broken", code, "video removed or private" if code in (401, 403, 404) else why
    code, why = fetch(url, timeout)
    if code and code < 400:
        return "ok", code, ""
    if code in (401, 403, 405, 429) and any(h in host for h in SOFT_BLOCK + ("github.com",)):
        return "unverified", code, "site blocks automated checks"
    if code in (403, 405, 429):
        return "unverified", code, why
    return "broken", code, why


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    as_json = "--json" in sys.argv
    timeout = 15
    if "--timeout" in sys.argv:
        timeout = int(sys.argv[sys.argv.index("--timeout") + 1])
        args = [a for a in args if a != str(timeout)]
    files = args or [str(p) for p in sorted((SKILL / "references").glob("*.md"))]
    readme = SKILL.parent / "README.md"
    if not args and readme.exists():
        files.append(str(readme))
    urls = collect(files)
    results = {}
    with cf.ThreadPoolExecutor(max_workers=12) as ex:
        futs = {ex.submit(check, u, timeout): u for u in urls}
        for f in cf.as_completed(futs):
            results[futs[f]] = f.result()
    broken = {u: r for u, r in results.items() if r[0] == "broken"}
    if as_json:
        print(json.dumps({u: {"status": r[0], "code": r[1], "note": r[2], "where": urls[u]}
                          for u, r in sorted(results.items())}, indent=2))
    else:
        counts = {}
        for r in results.values():
            counts[r[0]] = counts.get(r[0], 0) + 1
        print(f"Checked {len(results)} URLs: " + ", ".join(f"{v} {k}" for k, v in sorted(counts.items())))
        for u, r in sorted(broken.items()):
            print(f"BROKEN {r[1] or '-'} {u}  ({r[2]})  at {', '.join(urls[u][:3])}")
        for u, r in sorted(results.items()):
            if r[0] == "unverified":
                print(f"unverified {r[1]} {u}  ({r[2]})")
    sys.exit(1 if broken else 0)


if __name__ == "__main__":
    main()
