"""Full-length versions (up to 60k characters) of the evaluation documents, for long-context
runs (Qwen, 4k+ tokens). Same papers / files as data/docs.jsonl. Output: data/docs_long.jsonl"""
import json, pathlib, re, time, sys
sys.path.insert(0, str(pathlib.Path(__file__).parent))
import fetch_data as FD
ROOT = pathlib.Path(__file__).parent
MAX = 60000
docs = [json.loads(l) for l in open(ROOT / "data" / "docs.jsonl")]
site = next(pathlib.Path(sys.executable).parent.parent.glob("lib/python3*/site-packages"))
out = []
for d in docs:
    if d["domain"] == "prose":
        try:
            html = FD.get(f"https://arxiv.org/html/{d['id']}")
        except Exception as ex:
            print("fail", d["id"], ex); continue
        p = FD.ArticleText(); p.feed(html)
        text = re.sub(r"[ \t]+", " ", "".join(p.out)); text = re.sub(r"\n\s*\n+", "\n\n", text).strip()
        text = text.replace("Content selection saved. Describe the issue below:", "").strip()
        out.append(dict(d, text=text[:MAX])); time.sleep(1.2)
    else:
        out.append(dict(d, text=(site / d["id"]).read_text(errors="replace")[:MAX]))
    print(d["domain"], d["id"], len(out[-1]["text"]), flush=True)
with open(ROOT / "data" / "docs_long.jsonl", "w") as fh:
    for d in out:
        fh.write(json.dumps(d) + "\n")
print("wrote", len(out))
