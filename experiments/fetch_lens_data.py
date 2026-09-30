"""Text for training tuned-lens early exits: 2026 arXiv papers from categories NOT used in the
evaluation set, plus recent library source files. Disjoint from data/docs.jsonl by construction.
Output: data/lens_docs.jsonl
"""
import json, pathlib, random, re, time, sys
sys.path.insert(0, str(pathlib.Path(__file__).parent))

ROOT = pathlib.Path(__file__).parent
CATS = ["cs.AI", "cs.CV", "math.NT", "hep-th", "physics.bio-ph", "q-bio.QM", "stat.ML",
        "cs.SE", "cs.DS", "econ.EM"]
PER_CAT = 4


def main():
    import fetch_data as FD
    have = {json.loads(l)["id"] for l in open(ROOT / "data" / "docs.jsonl")}
    docs, seen = [], set(have)
    for cat in CATS:
        got = 0
        try:
            ids = FD.arxiv_ids(cat, PER_CAT)
        except Exception as ex:
            print("list fail", cat, ex); continue
        time.sleep(3)
        for aid in ids:
            if got >= PER_CAT or aid in seen:
                continue
            seen.add(aid)
            try:
                html = FD.get(f"https://arxiv.org/html/{aid}")
            except Exception:
                time.sleep(1); continue
            p = FD.ArticleText(); p.feed(html)
            text = re.sub(r"[ \t]+", " ", "".join(p.out))
            text = re.sub(r"\n\s*\n+", "\n\n", text).strip()
            text = text.replace("Content selection saved. Describe the issue below:", "").strip()
            if len(text) < 6000:
                continue
            docs.append({"id": aid, "domain": "prose", "cat": cat, "text": text[:12000]})
            got += 1
            print("ok", cat, aid, flush=True)
            time.sleep(1.5)
    site = next(pathlib.Path(sys.executable).parent.parent.glob("lib/python3*/site-packages"))
    files = [f for pk in ("sklearn", "scipy/stats", "transformers/generation")
             for f in sorted((site / pk).rglob("*.py"))
             if "test" not in str(f) and f.stat().st_size > 8000]
    random.Random(0).shuffle(files)
    for f in files[:20]:
        docs.append({"id": str(f.relative_to(site)), "domain": "code",
                     "text": f.read_text(errors="replace")[:12000]})
    with open(ROOT / "data" / "lens_docs.jsonl", "w") as fh:
        for d in docs:
            fh.write(json.dumps(d) + "\n")
    print("wrote", len(docs))


if __name__ == "__main__":
    main()
