"""Fetch evaluation text that post-dates the Pythia training data (the Pile, 2020).

Three domains:
  prose  - full-text of 2026 arXiv papers (arxiv.org/html), first ~12k chars each
  code   - Python source files from recently released packages in a local venv
  (noise variants are generated later, in run_pilot.py, from the prose docs)

Output: data/docs.jsonl with {"id", "domain", "text"} per line.
"""
import json, re, sys, time, random, pathlib, urllib.request, urllib.parse
from html.parser import HTMLParser
import xml.etree.ElementTree as ET

OUT = pathlib.Path(__file__).parent / "data" / "docs.jsonl"
UA = {"User-Agent": "research-pilot/0.1 (single-user academic script)"}
CATS = ["cs.CL", "cs.LG", "q-bio.NC", "math.PR", "physics.optics", "econ.GN",
        "astro-ph.GA", "cond-mat.stat-mech", "stat.ME", "eess.SY", "cs.CR", "q-fin.ST"]
PER_CAT = 5
MAX_CHARS = 12000


def get(url, timeout=60):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode("utf-8", errors="replace")


class ArticleText(HTMLParser):
    """Keep paragraph text from arXiv HTML; replace MathML by its LaTeX alttext."""
    def __init__(self):
        super().__init__()
        self.out, self.in_p, self.math_depth, self.skip_depth = [], 0, 0, 0

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag in ("script", "style", "nav", "footer", "header"):
            self.skip_depth += 1
        if tag == "math":
            if self.math_depth == 0 and self.in_p and not self.skip_depth:
                self.out.append(" $" + a.get("alttext", "") + "$ ")
            self.math_depth += 1
        if tag == "p":
            self.in_p += 1

    def handle_endtag(self, tag):
        if tag in ("script", "style", "nav", "footer", "header") and self.skip_depth:
            self.skip_depth -= 1
        if tag == "math" and self.math_depth:
            self.math_depth -= 1
        if tag == "p" and self.in_p:
            self.in_p -= 1
            self.out.append("\n\n")

    def handle_data(self, data):
        if self.in_p and not self.math_depth and not self.skip_depth:
            self.out.append(data)


def arxiv_ids(cat, n):
    # The export API rate-limits quickly (HTTP 406); the "new submissions" listing is enough.
    page = get(f"https://arxiv.org/list/{cat}/new")
    ids = list(dict.fromkeys(re.findall(r"arXiv:(\d{4}\.\d{5})", page)))
    return ids[: n * 4]


def fetch_prose():
    docs, seen = [], set()
    for cat in CATS:
        got = 0
        try:
            ids = arxiv_ids(cat, PER_CAT)
        except Exception as ex:
            print("list fail", cat, ex); continue
        time.sleep(3)
        for aid in ids:
            if got >= PER_CAT:
                break
            if aid in seen:
                continue
            seen.add(aid)
            try:
                html = get(f"https://arxiv.org/html/{aid}")
            except Exception:
                time.sleep(1); continue
            p = ArticleText(); p.feed(html)
            text = re.sub(r"[ \t]+", " ", "".join(p.out))
            text = re.sub(r"\n\s*\n+", "\n\n", text).strip()
            if len(text) < 6000:
                continue
            docs.append({"id": aid, "domain": "prose", "cat": cat, "text": text[:MAX_CHARS]})
            got += 1
            print("ok", cat, aid, len(text))
            time.sleep(1.5)
    return docs


def fetch_code(venv_site):
    # Recently released packages (versions from 2025-2026) that are pure Python.
    pkgs = ["huggingface_hub", "httpx2", "httpcore2", "pandas/core", "aiohttp", "yarl", "anyio"]
    files = []
    for pk in pkgs:
        for f in sorted((venv_site / pk).rglob("*.py")):
            if "test" in f.name or f.stat().st_size < 8000:
                continue
            files.append(f)
    random.Random(0).shuffle(files)
    docs = []
    for f in files[:60]:
        text = f.read_text(errors="replace")[:MAX_CHARS]
        docs.append({"id": str(f.relative_to(venv_site)), "domain": "code", "text": text})
    return docs


if __name__ == "__main__":
    site = next(pathlib.Path(sys.executable).parent.parent.glob("lib/python3*/site-packages"))
    docs = fetch_prose() + fetch_code(site)
    with open(OUT, "w") as fh:
        for d in docs:
            fh.write(json.dumps(d) + "\n")
    print("wrote", len(docs), "docs to", OUT)
