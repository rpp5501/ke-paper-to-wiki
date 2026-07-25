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
    if (not isinstance(doc, dict) or not isinstance(doc.get("nodes"), list)
            or not isinstance(doc.get("edges"), list)):
        return ["missing or non-list nodes/edges"]
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


class ConceptExtractionError(RuntimeError):
    """Raised when concept extraction did not produce a validated graph."""


def require_ok(result: dict) -> dict:
    """Return the extraction ``result`` only if it is a real concept graph.

    The pipeline's crash-safe habit is to swallow a failed extraction and reuse
    the pack's section list as the graph -- that is exactly the "every dashboard
    is the paper's table of contents" bug. Call this at the boundary that would
    write ``graph.json`` so a failed extraction stops the build loudly instead
    of shipping a TOC dashboard.
    """
    if result.get("status") != "ok":
        raise ConceptExtractionError(
            "concept extraction failed -- refusing to build a table-of-contents "
            f"dashboard from section headings. problems={result.get('problems')}"
        )
    return result


# R16 §5.1c — zero-token graph-quality metrics, the deterministic half of
# kg-gen's MINE benchmark idea. Advisory, not a tripwire: is_toc_graph raises
# because a TOC graph is the *wrong* graph, whereas a graph with orphans is
# merely a thin one and stopping the build on it would be the wrong trade.
ORPHAN_RATIO_LIMIT = 0.2
PART_OF_COVERAGE_FLOOR = 0.5


def normalize_slug(value: str) -> str:
    """Canonical kebab form, so 'Self Attention' and 'self_attention' collide.

    Pure string normalization by design — the embedding clustering and entity
    linking rungs of the usual dedup ladder stay declined (keyless pin).
    """
    lowered = re.sub(r"[^a-z0-9]+", "-", str(value).lower())
    return lowered.strip("-")


def graph_quality(graph: dict) -> dict:
    """Deterministic health metrics for a concept graph. Never raises."""
    nodes = graph.get("nodes", []) or []
    edges = graph.get("edges", []) or []
    ids = [str(n.get("id", "")) for n in nodes]
    total = len(ids)

    touched: set[str] = set()
    in_tree: set[str] = set()
    for edge in edges:
        src, dst = str(edge.get("src", "")), str(edge.get("dst", ""))
        touched.update((src, dst))
        if edge.get("kind") == "part-of":
            in_tree.update((src, dst))

    groups: dict[str, list[str]] = {}
    for node_id in ids:
        groups.setdefault(normalize_slug(node_id), []).append(node_id)

    return {
        "node_count": total,
        "edge_count": len(edges),
        "orphan_ratio": (
            sum(1 for i in ids if i not in touched) / total if total else 0.0),
        "part_of_coverage": (
            sum(1 for i in ids if i in in_tree) / total if total else 0.0),
        "duplicate_slugs": {
            slug: sorted(members)
            for slug, members in groups.items() if len(members) > 1
        },
    }


def graph_quality_findings(graph: dict) -> list[str]:
    """Human-readable warnings from :func:`graph_quality`; empty = healthy."""
    m = graph_quality(graph)
    findings: list[str] = []

    if m["orphan_ratio"] > ORPHAN_RATIO_LIMIT:
        findings.append(
            f"orphan ratio {m['orphan_ratio']:.0%} exceeds "
            f"{ORPHAN_RATIO_LIMIT:.0%}: nodes with no edges at all")
    for slug, members in sorted(m["duplicate_slugs"].items()):
        findings.append(
            f"duplicate slug candidates for '{slug}': {', '.join(members)}")
    if m["node_count"] and m["part_of_coverage"] < PART_OF_COVERAGE_FLOOR:
        findings.append(
            f"part-of coverage {m['part_of_coverage']:.0%} below "
            f"{PART_OF_COVERAGE_FLOOR:.0%}: most nodes sit outside the "
            "hierarchy, so the mind map will be flat")
    return findings


def is_toc_graph(graph: dict) -> bool:
    """Heuristic: does this graph look like raw section headings, not concepts?

    A TOC fallback graph has ``sec_N`` node ids and only structural edges.
    Useful as a build-time tripwire on graphs from unknown provenance.
    """
    nodes = graph.get("nodes", [])
    if not nodes:
        return True
    sec_like = sum(1 for n in nodes if re.fullmatch(r"sec_[\d_]+", str(n.get("id", ""))))
    kinds = {e.get("kind") for e in graph.get("edges", [])}
    return sec_like >= max(1, len(nodes) // 2) and kinds <= {"prerequisite", None}
