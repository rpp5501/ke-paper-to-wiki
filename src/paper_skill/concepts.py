"""P2: pack -> §5.1 concept graph + toc rows. LLM via injectable spawn."""
import datetime, json, re

CONCEPT_PROMPT = """You are extracting a concept graph from a research paper.
Paper: {title}

Sections (id: title — first sentence):
{sections_digest}

Emit ONLY a JSON object — no prose, no markdown fences — shaped exactly:
{{"nodes": [{{"id": "kebab-slug", "kind": "concept|equation|figure",
  "label": "...", "level": 0-3, "source_ref": "sec_x",
  "definition": "paper's own one-line definition",
  "sub_questions": ["2-4 research questions"], "research": true|false}}],
 "edges": [{{"src": "...", "dst": "...",
  "kind": "part-of|prerequisite|builds-on|defined-in|contrasts-with"}}]}}

Rules: 15-25 nodes for a full paper; exactly one level-0 node (the thesis);
every node's source_ref must be a real section id from the list above;
mark research:true only where the paper's own text is insufficient."""

_TOC_KEYS = ("definition", "sub_questions", "research")


def _digest(pack: dict) -> str:
    return "\n".join(f'{s["id"]}: {s["title"]} — {s["text"][:120]}'
                     for s in pack["sections"])


def _parse(raw: str) -> dict | None:
    m = re.search(r"\{.*\}", raw, re.S)
    if not m:
        return None
    try:
        return json.loads(m.group(0))
    except json.JSONDecodeError:
        return None


def _problems(doc: dict, pack: dict) -> list[str]:
    probs = []
    if not isinstance(doc, dict) or "nodes" not in doc or "edges" not in doc:
        return ["missing nodes/edges"]
    section_ids = {s["id"] for s in pack["sections"]}
    node_ids = set()
    for n in doc["nodes"]:
        for k in ("id", "kind", "label", "level", "source_ref"):
            if k not in n:
                probs.append(f"node missing {k}: {n.get('id', '?')}")
        if n.get("source_ref") not in section_ids:
            probs.append(f"unknown source_ref: {n.get('source_ref')}")
        node_ids.add(n.get("id"))
    for e in doc["edges"]:
        if e.get("src") not in node_ids or e.get("dst") not in node_ids:
            probs.append(f"dangling edge: {e}")
    if sum(1 for n in doc["nodes"] if n.get("level") == 0) != 1:
        probs.append("exactly one level-0 node required")
    return probs


def extract_concepts(pack: dict, spawn, max_retries: int = 1) -> dict:
    prompt = CONCEPT_PROMPT.format(title=pack["meta"]["title"],
                                   sections_digest=_digest(pack))
    problems = []
    for attempt in range(1 + max_retries):
        doc = _parse(spawn(prompt if attempt == 0 else
                           prompt + f"\n\nYour previous output was invalid: "
                                    f"{problems}. Emit ONLY the JSON object."))
        problems = _problems(doc, pack) if doc else ["not parseable JSON"]
        if not problems:
            break
    if problems:
        return {"status": "failed-orchestration", "problems": problems}
    toc, nodes = [], []
    for n in doc["nodes"]:
        toc.append({"id": n["id"], "label": n["label"], "level": n["level"],
                    "include": True,
                    **{k: n.get(k) for k in _TOC_KEYS}})
        nodes.append({k: v for k, v in n.items() if k not in _TOC_KEYS})
    for e in doc["edges"]:
        e.setdefault("weight", 1.0)
        e.setdefault("confidence", "inferred")
        e.setdefault("confidence_score", 0.7)
    graph = {"meta": {"kind": "concept", "source": pack["meta"]["source"],
                      "generated": datetime.date.today().isoformat(), "version": 1},
             "nodes": nodes, "edges": doc["edges"]}
    return {"status": "ok", "graph": graph, "toc": toc}
