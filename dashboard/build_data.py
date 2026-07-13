"""Bundle pipeline artifacts into src/data.gen.ts (design doc §3-§4).

Everything deterministic; runs without internet access. No runtime fetch exists in the
dashboard, so this file IS the data path.
"""
import argparse
import datetime
import json
import re
from collections import defaultdict
from pathlib import Path

import networkx as nx
import yaml

_IMG = re.compile(r"!\[[^\]]*\]\([^)]*\)")
_DEPENDENT_SIDE = {"part-of": "dst", "prerequisite": "dst", "builds-on": "src"}


def reading_path(plan_graph):
    """Kahn topo over prerequisite/builds-on (mirror of fork exporter;
    duplicated deliberately — 30 lines beats a cross-repo import)."""
    nodes = {n["id"]: n for n in plan_graph["nodes"]}
    after = {i: set() for i in nodes}
    indeg = {i: 0 for i in nodes}
    for e in plan_graph["edges"]:
        if e["kind"] == "prerequisite":
            first, later = e["src"], e["dst"]
        elif e["kind"] == "builds-on":
            first, later = e["dst"], e["src"]
        else:
            continue
        if later not in after[first]:
            after[first].add(later)
            indeg[later] += 1
    key = lambda i: (nodes[i].get("level", 0), nodes[i].get("label", ""))
    ready = sorted((i for i in nodes if indeg[i] == 0), key=key)
    order = []
    while ready:
        cur = ready.pop(0)
        order.append(cur)
        for nxt in sorted(after[cur], key=key):
            indeg[nxt] -= 1
            if indeg[nxt] == 0:
                ready.append(nxt)
        ready.sort(key=key)
    order += [i for i in sorted(nodes, key=key) if i not in order]
    return order


def strip_images(md: str):
    n = len(_IMG.findall(md))
    return _IMG.sub("", md), n


def _clusters(plan_graph):
    nodes = {n["id"]: n for n in plan_graph["nodes"]}
    if any("community" in n for n in plan_graph["nodes"]):
        groups = defaultdict(list)
        for n in plan_graph["nodes"]:
            groups[n.get("community", -1)].append(n["id"])
        return [{"id": f"community-{c}", "label": f"Community {c}",
                 "nodeIds": sorted(ms)} for c, ms in sorted(groups.items())]
    # fallback: every L1 node + its transitive part-of descendants
    children = defaultdict(list)
    for e in plan_graph["edges"]:
        if e["kind"] == "part-of":
            children[e["dst"]].append(e["src"])

    def desc(i):
        out = []
        for k in children.get(i, []):
            out += [k] + desc(k)
        return out
    return [{"id": n["id"], "label": n["label"],
             "nodeIds": sorted(set([n["id"]] + desc(n["id"])))}
            for n in plan_graph["nodes"] if n.get("level", 0) == 1]


def _centrality(plan_graph):
    g = nx.DiGraph()
    g.add_nodes_from(n["id"] for n in plan_graph["nodes"])
    g.add_edges_from((e["src"], e["dst"]) for e in plan_graph["edges"])
    return {k: round(v, 4) for k, v in nx.betweenness_centrality(g).items()}


def _tour(plan_graph, hotspots):
    labels = {n["id"]: n["label"] for n in plan_graph["nodes"]}
    if plan_graph["meta"].get("kind") == "code" and hotspots:
        picks = [h["id"] for h in hotspots[:5]]
        blurb = "High-churn, high-dependency hotspot — start here."
    else:
        picks = reading_path(plan_graph)[:5]
        blurb = "Next stop on the dependency-ordered reading path."
    return [{"order": i + 1, "title": labels.get(p, p), "description": blurb,
             "nodeIds": [p]} for i, p in enumerate(picks)]


def _eq_index(plan_graph, pack):
    if not pack:
        return {}
    sec_of_eq = {e["id"]: e["section"] for e in pack.get("equations", [])}
    by_sec = defaultdict(list)
    for n in plan_graph["nodes"]:
        ref = (n.get("source_ref") or "").replace("§", "")
        by_sec[ref].append(n["id"])
    return {eq: sorted(by_sec.get(sec, [])) for eq, sec in sec_of_eq.items()}


def _load_pages(pages_dir):
    pages = {}
    if not pages_dir:
        return pages, 0
    stripped = 0
    for f in sorted(Path(pages_dir).glob("*.md")):
        cid = f.stem.split("_", 1)[1] if "_" in f.stem else f.stem
        text, n = strip_images(f.read_text(encoding="utf-8"))
        stripped += n
        pages[cid] = text
    return pages, stripped


def _load_notes(wiki_dir):
    notes, glossary, trace = {}, {}, []
    if not wiki_dir:
        return notes, glossary, trace
    for f in sorted(Path(wiki_dir).glob("*.yaml")):
        note = yaml.safe_load(f.read_text(encoding="utf-8"))
        cid = note.get("concept", f.stem)
        text, _ = strip_images(note.get("synthesis", ""))
        note["synthesis"] = text
        notes[cid] = note
        if note.get("glossary"):
            glossary[cid] = note["glossary"]
        trace.append({"nodeId": cid, "phase": "researched",
                      "status": note.get("status", "unknown"),
                      "date": datetime.date.fromtimestamp(
                          f.stat().st_mtime).isoformat()})
    return notes, glossary, trace


def build_bundle(plan_graph, pack=None, pages_dir=None, wiki_dir=None,
                 hotspots=None, repo_dir=None):
    hotspots = hotspots or []
    pages, stripped = _load_pages(pages_dir)
    notes, glossary, trace = _load_notes(wiki_dir)
    for cid in pages:
        trace.append({"nodeId": cid, "phase": "written", "status": "ok",
                      "date": plan_graph["meta"].get("generated", "")})
    if stripped:
        print(f"stripped {stripped} image block(s) (rich media is v2)")
    return {"meta": plan_graph["meta"], "nodes": plan_graph["nodes"],
            "edges": plan_graph["edges"], "pages": pages, "notes": notes,
            "hotspots": hotspots, "clusters": _clusters(plan_graph),
            "tour": _tour(plan_graph, hotspots),
            "provenance": (pack or {}).get("extraction", {}),
            "centrality": _centrality(plan_graph),
            "eqIndex": _eq_index(plan_graph, pack),
            "trace": sorted(trace, key=lambda t: (t["nodeId"], t["phase"])),
            "glossary": glossary,
            "dependentSide": _DEPENDENT_SIDE}


def to_data_ts(bundle) -> str:
    payload = json.dumps(bundle, ensure_ascii=False, indent=1)
    return ("// generated by build_data.py — do not edit\n"
            "export const KE_DATA = " + payload + ";\n")


def main(argv=None):
    p = argparse.ArgumentParser(prog="build_data")
    p.add_argument("--graph", required=True)
    p.add_argument("--pack")
    p.add_argument("--pages-dir")
    p.add_argument("--wiki-dir")
    p.add_argument("--hotspots")
    p.add_argument("--repo-dir")
    p.add_argument("--out", default="src/data.gen.ts")
    a = p.parse_args(argv)
    load = lambda x: json.loads(Path(x).read_text(encoding="utf-8")) if x else None
    bundle = build_bundle(load(a.graph), pack=load(a.pack),
                          pages_dir=a.pages_dir, wiki_dir=a.wiki_dir,
                          hotspots=(load(a.hotspots) or {}).get("hotspots")
                          if a.hotspots else None,
                          repo_dir=a.repo_dir)
    Path(a.out).write_text(to_data_ts(bundle), encoding="utf-8")
    print(f"{a.out}: {len(bundle['nodes'])} nodes, {len(bundle['tour'])} tour steps")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
