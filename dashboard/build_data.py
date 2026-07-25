"""Bundle pipeline artifacts into src/data.gen.ts (design doc §3-§4).

Everything deterministic; runs without internet access. No runtime fetch exists in the
dashboard, so this file IS the data path.
"""
import argparse
import json
import re
import subprocess
from collections import defaultdict
from itertools import islice
from pathlib import Path

import networkx as nx
import yaml

_IMG = re.compile(r"!\[[^\]]*\]\([^)]*\)")
_SOURCE_LOCATION = re.compile(
    r"^(?P<path>.+):(?:L|line\s*)?(?P<line>[1-9]\d*)"
    r"(?:-(?:L)?(?P<end>[1-9]\d*))?$", re.IGNORECASE)
_DEPENDENT_SIDE = {"part-of": "dst", "prerequisite": "dst", "builds-on": "src"}
_CODE_KINDS = {"function", "class", "file", "route"}


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


_TLDR_RE = re.compile(r"^##\s+.+?\{#tldr\}\s*$(.*?)(?=^##\s|\Z)", re.M | re.S)


def _page_for(node, pages):
    if node.get("id") in pages:
        return pages[node["id"]]
    stem = re.sub(r"\.md$", "", node.get("page") or "", flags=re.I)
    stem = re.sub(r"^\d+_", "", stem)
    return pages.get(stem)


def _first_sentence(markdown, limit=180):
    match = _TLDR_RE.search(markdown or "")
    if not match:
        return ""
    body = match.group(1).strip()
    body = re.sub(r"\$\$.*?\$\$", "", body, flags=re.S)
    body = re.sub(r"\\\(.*?\\\)", "", body, flags=re.S)
    body = re.sub(r"[#*_`>\[\]]", "", body)
    body = " ".join(body.split())
    if not body:
        return ""
    sentence = re.split(r"(?<=[.!?])\s", body)[0]
    return sentence if len(sentence) <= limit else sentence[: limit - 1].rstrip() + "…"


def _tour(plan_graph, hotspots, pages):
    nodes = {n["id"]: n for n in plan_graph["nodes"]}
    if plan_graph["meta"].get("kind") == "code" and hotspots:
        picks = [h["id"] for h in hotspots[:5]]
        fallback = "High-churn, high-dependency hotspot — start here."
    else:
        picks = reading_path(plan_graph)[:5]
        fallback = "Next stop on the dependency-ordered reading path."
    steps = []
    for i, p in enumerate(picks):
        node = nodes.get(p, {"id": p, "label": p})
        blurb = _first_sentence(_page_for(node, pages)) or fallback
        steps.append({"order": i + 1, "title": node.get("label", p),
                      "description": blurb, "nodeIds": [p]})
    return steps


def section_key(value):
    """Join pack ids such as sec_3_2_1 to graph refs such as sec:3.2.1."""
    value = str(value or "").strip().lower().replace("§", "")
    value = re.sub(r"^sec(?:tion)?[:._-]*", "", value)
    parts = re.findall(r"\d+|[a-z]+", value)
    return ".".join(parts)


def _eq_index(plan_graph, pack):
    if not pack:
        return {}

    sec_of_eq = {
        e["id"]: section_key(e.get("section"))
        for e in pack.get("equations", [])
    }
    by_sec = defaultdict(list)
    for n in plan_graph["nodes"]:
        ref = section_key(n.get("source_ref"))
        if not ref:
            continue
        by_sec[ref].append(n["id"])
    return {
        eq: sorted(by_sec.get(sec, [])) if sec else []
        for eq, sec in sec_of_eq.items()
    }


def _page_key(value):
    stem = Path(value).stem
    return stem.split("_", 1)[1] if "_" in stem else stem


def _load_pages(pages_dir):
    pages = {}
    if not pages_dir:
        return pages, 0
    stripped = 0
    for f in sorted(Path(pages_dir).glob("*.md")):
        cid = _page_key(f)
        text, n = strip_images(f.read_text(encoding="utf-8"))
        stripped += n
        pages[cid] = text
    return pages, stripped


def _load_notes(wiki_dir, fallback_date):
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
        trace_date = note.get("date") or note.get("generated") or fallback_date
        note["date"] = trace_date
        trace.append({"nodeId": cid, "phase": "researched",
                      "status": note.get("status", "unknown"),
                      "date": trace_date})
    return notes, glossary, trace


def _source_dates(plan_graph, repo_dir):
    repo = Path(repo_dir)
    fallback_date = plan_graph["meta"].get("generated", "")
    dates = {}
    for node in plan_graph["nodes"]:
        if node.get("kind") not in _CODE_KINDS:
            continue
        dates[node["id"]] = fallback_date
        source_ref = node.get("source_ref")
        if not source_ref:
            continue
        relative_path = source_ref.rsplit(":", 1)[0]
        if not (repo / relative_path).is_file():
            continue
        try:
            result = subprocess.run(
                ["git", "log", "-1", "--format=%cs", "--", relative_path],
                cwd=repo, capture_output=True, text=True, check=False,
            )
            git_date = result.stdout.strip() if result.returncode == 0 else ""
        except OSError:
            git_date = ""
        if git_date:
            dates[node["id"]] = git_date
    return dates


def _excerpts(plan_graph, hotspots, repo_dir):
    if not repo_dir or plan_graph["meta"].get("kind") not in {
            "code", "bridged"}:
        return {}

    keep = {
        hotspot["id"] for hotspot in hotspots[:20]
        if isinstance(hotspot, dict) and hotspot.get("id")
    }
    keep.update(
        edge["src"] for edge in plan_graph["edges"]
        if edge.get("kind") == "implements" and edge.get("src")
    )
    try:
        repo = Path(repo_dir).resolve()
    except (OSError, RuntimeError):
        return {}
    excerpts = {}
    for node in plan_graph["nodes"]:
        if node["id"] not in keep:
            continue
        match = _SOURCE_LOCATION.fullmatch(node.get("source_ref") or "")
        if not match:
            continue
        try:
            start_line = int(match.group("line"))
            end_line = int(match.group("end")) if match.group("end") else None
            if end_line is not None and end_line < start_line:
                continue
            relative_path = Path(match.group("path"))
            if relative_path.is_absolute():
                continue
            source_path = (repo / relative_path).resolve()
            source_path.relative_to(repo)
            if not source_path.is_file():
                continue
            start = start_line - 1
            stop = min(end_line or start_line + 79, start_line + 79)
            with source_path.open(
                    "r", encoding="utf-8", errors="replace") as source:
                lines = [
                    line.rstrip("\r\n")
                    for line in islice(source, start, stop)
                ]
        except (OSError, RuntimeError, ValueError):
            continue
        excerpt = "\n".join(lines)
        if excerpt:
            excerpts[node["id"]] = excerpt
    return excerpts


def _provenance_ref(raw, known_sections, label):
    """R16.C2 — keep a source_ref only when it resolves to an emitted section.

    A chip that goes nowhere is worse than no chip, so an unresolvable ref is
    warned about and dropped while its item or visual survives. With no
    sections map (no --pack) there is nothing to check against, so refs pass
    through untouched rather than every item warning.
    """
    ref = raw or ""
    if not ref or not known_sections:
        return ref
    if section_key(ref) in known_sections:
        return ref
    print(f"{label}: source_ref '{ref}' matches no section, chip dropped")
    return ""


def _load_quiz(path, known_node_ids, known_sections=None):
    """R15.2: quiz.json → validated items. Contract per item:
    {id, nodeId, prompt, options: [{text, explain}]x>=2, correct: idx,
    sourceRef?}. Items with unknown nodes or contract violations are dropped
    with a warning — the build never breaks on quiz content."""
    doc = json.loads(Path(path).read_text(encoding="utf-8"))
    out = []
    for item in (doc or {}).get("items", []):
        label = item.get("id") or item.get("prompt", "?")[:40]
        options = item.get("options", [])
        problems = []
        if item.get("nodeId") not in known_node_ids:
            problems.append(f"unknown nodeId '{item.get('nodeId')}'")
        if not item.get("id"):
            problems.append("missing id")
        if not item.get("prompt"):
            problems.append("missing prompt")
        if len(options) < 2:
            problems.append("needs >=2 options")
        if any(not o.get("text") or not o.get("explain") for o in options):
            problems.append("every option needs text+explain")
        if not isinstance(item.get("correct"), int) \
                or not 0 <= item.get("correct", -1) < len(options):
            problems.append("correct index out of range")
        if problems:
            print(f"quiz: '{label}' dropped: {'; '.join(problems)}")
            continue
        out.append({
            "id": item["id"],
            "nodeId": item["nodeId"],
            "prompt": item["prompt"],
            "options": [{"text": o["text"], "explain": o["explain"]}
                        for o in options],
            "correct": item["correct"],
            # `sourceRef` is R15.2's in-page anchor (e.g. '#the-math') and is
            # unvalidated. R16.C2's paper-span ref is a separate input field,
            # `source_ref`, surfaced as `sectionRef`.
            "sourceRef": item.get("sourceRef", ""),
            "sectionRef": _provenance_ref(
                item.get("source_ref", ""), known_sections, f"quiz: '{label}'"),
        })
    return out


def parse_data_ts(text):
    """Inverse of to_data_ts — recover the bundle from src/data.gen.ts."""
    start = text.index("KE_DATA = ") + len("KE_DATA = ")
    return json.loads(text[start:text.rindex(";")])


def _load_next_steps(path, known_node_ids):
    """R15.1: next_steps ideas.yaml/json → [{title, rationale, kind, nodes,
    sources, confirmed}]. Confirmed ideas sort first. Anchor node ids not in
    the graph are dropped with a warning (provenance discipline) — an idea
    whose every anchor is unknown is skipped entirely."""
    import yaml
    raw = Path(path).read_text(encoding="utf-8")
    doc = yaml.safe_load(raw) if str(path).endswith((".yaml", ".yml")) \
        else json.loads(raw)
    out = []
    for idea in (doc or {}).get("ideas", []):
        anchors = idea.get("anchors", {})
        nodes = [n for n in anchors.get("nodes", []) if n in known_node_ids]
        dropped = set(anchors.get("nodes", [])) - set(nodes)
        if dropped:
            print(f"next-steps: '{idea.get('title', '?')}': "
                  f"unknown anchor nodes dropped: {sorted(dropped)}")
        if not nodes:
            print(f"next-steps: '{idea.get('title', '?')}' skipped "
                  f"(no known anchor nodes)")
            continue
        out.append({
            "title": idea.get("title", ""),
            "rationale": idea.get("rationale", ""),
            "kind": idea.get("kind", ""),
            "nodes": nodes,
            "sources": anchors.get("sources", []),
            "confirmed": bool(idea.get("confirmed")),
        })
    out.sort(key=lambda i: (not i["confirmed"], i["title"]))
    return out


def _load_viz(viz_dir, pages_dir, known_sections=None):
    """R13: viz/manifest.json + per-node HTML → {nodeId: entry+srcdoc+stale}.

    Staleness = manifest page_sha256 no longer matches the current page file.
    A missing page file is stale too (evidence gone). Never raises on a bad
    entry — it is skipped with a warning, the build must not break on viz.
    """
    import hashlib
    viz_dir = Path(viz_dir)
    manifest_path = viz_dir / "manifest.json"
    if not manifest_path.exists():
        print(f"viz: no manifest.json in {viz_dir}, skipping")
        return {}
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    out = {}
    for node_id, entry in manifest.items():
        html_path = viz_dir / entry.get("src", "")
        if not entry.get("src") or not html_path.exists():
            print(f"viz: {node_id}: missing src, skipped")
            continue
        stale = True
        page = entry.get("page")
        if pages_dir and page and (Path(pages_dir) / page).exists():
            digest = hashlib.sha256(
                (Path(pages_dir) / page).read_bytes()).hexdigest()
            stale = digest != entry.get("page_sha256")
        if stale:
            print(f"viz: {node_id}: page evidence stale or missing")
        out[node_id] = {
            "kind": entry.get("kind", "template"),
            "templateId": entry.get("template_id"),
            "title": entry.get("title", ""),
            "caption": entry.get("caption", ""),
            "prompt": entry.get("prompt", ""),
            "srcdoc": html_path.read_text(encoding="utf-8"),
            "stale": stale,
            "sectionRef": _provenance_ref(
                entry.get("source_ref", ""), known_sections, f"viz: {node_id}"),
        }
    return out


def build_bundle(plan_graph, pack=None, pages_dir=None, wiki_dir=None,
                 hotspots=None, repo_dir=None, viz_dir=None,
                 next_steps=None, quiz=None):
    hotspots = hotspots or []
    pages, stripped = _load_pages(pages_dir)
    notes, glossary, trace = _load_notes(
        wiki_dir, plan_graph["meta"].get("generated", ""))
    page_owners = {
        _page_key(node["page"]): node["id"]
        for node in plan_graph["nodes"]
        if node.get("page")
    }
    for cid in pages:
        trace.append({"nodeId": page_owners.get(cid, cid),
                      "phase": "written", "status": "ok",
                      "date": plan_graph["meta"].get("generated", "")})
    if stripped:
        print(f"stripped {stripped} image block(s) (rich media is v2)")
    bundle = {"meta": plan_graph["meta"], "nodes": plan_graph["nodes"],
              "edges": plan_graph["edges"], "pages": pages, "notes": notes,
              "hotspots": hotspots, "clusters": _clusters(plan_graph),
              "tour": _tour(plan_graph, hotspots, pages),
              "provenance": (pack or {}).get("extraction", {}),
              "centrality": _centrality(plan_graph),
              "eqIndex": _eq_index(plan_graph, pack),
              "trace": sorted(trace, key=lambda t: (t["nodeId"], t["phase"])),
              "glossary": glossary,
              "excerpts": _excerpts(plan_graph, hotspots, repo_dir),
              "dependentSide": _DEPENDENT_SIDE}
    if repo_dir:
        bundle["mtimes"] = _source_dates(plan_graph, repo_dir)
    # R16.C2 — sections are resolved before quiz and viz, which validate their
    # source_ref against these keys.
    sections = {
        section_key(s["id"]): {"title": s.get("title", ""),
                               "text": s.get("text", "")}
        for s in (pack or {}).get("sections", []) if section_key(s["id"])
    }
    if viz_dir:  # R13: opt-in only — absent flag leaves the bundle untouched
        bundle["viz"] = _load_viz(viz_dir, pages_dir, sections)
    if next_steps:  # R15.1: same opt-in discipline
        bundle["nextSteps"] = _load_next_steps(
            next_steps, {n["id"] for n in plan_graph["nodes"]})
    if quiz:  # R15.2: same opt-in discipline
        bundle["quiz"] = _load_quiz(
            quiz, {n["id"] for n in plan_graph["nodes"]}, sections)
    if pack:  # R15.11: same opt-in discipline
        bundle["sections"] = sections
    return bundle


def to_data_ts(bundle) -> str:
    payload = json.dumps(bundle, ensure_ascii=False, indent=1)
    return ("// generated by build_data.py — do not edit\n"
            "export const KE_DATA = " + payload + ";\n")


def main(argv=None):
    p = argparse.ArgumentParser(prog="build_data")
    p.add_argument("--graph")
    p.add_argument("--pack")
    p.add_argument("--pages-dir")
    p.add_argument("--wiki-dir")
    p.add_argument("--hotspots")
    p.add_argument("--repo-dir")
    p.add_argument("--viz-dir", help="R13 viz pack dir (viz/manifest.json); "
                                     "omit for a viz-free build")
    p.add_argument("--next-steps", help="R15.1 next_steps ideas.yaml/json; "
                                        "omit to leave the bundle untouched")
    p.add_argument("--quiz", help="R15.2 quiz.json; "
                                  "omit to leave the bundle untouched")
    p.add_argument("--update", action="store_true",
                   help="patch opt-in sections (--viz-dir/--next-steps/--quiz)"
                        " into the existing --out without a full rebuild")
    p.add_argument("--out", default="src/data.gen.ts")
    a = p.parse_args(argv)
    load = lambda x: json.loads(Path(x).read_text(encoding="utf-8")) if x else None

    if a.update:
        if not any([a.viz_dir, a.next_steps, a.quiz]):
            p.error("--update needs at least one of "
                    "--viz-dir / --next-steps / --quiz")
        bundle = parse_data_ts(Path(a.out).read_text(encoding="utf-8"))
        known = {n["id"] for n in bundle["nodes"]}
        # R16.C2 — patch mode validates refs against the sections already in
        # the bundle, so a partial rebuild applies the same provenance rule.
        sections = bundle.get("sections") or {}
        changed = []
        if a.viz_dir:
            bundle["viz"] = _load_viz(a.viz_dir, a.pages_dir, sections)
            changed.append("viz")
        if a.next_steps:
            bundle["nextSteps"] = _load_next_steps(a.next_steps, known)
            changed.append("nextSteps")
        if a.quiz:
            bundle["quiz"] = _load_quiz(a.quiz, known, sections)
            changed.append("quiz")
        Path(a.out).write_bytes(to_data_ts(bundle).encode("utf-8"))
        print(f"{a.out}: updated sections: {', '.join(changed)}")
        return 0

    if not a.graph:
        p.error("--graph is required (or use --update to patch an "
                "existing build)")
    bundle = build_bundle(load(a.graph), pack=load(a.pack),
                          pages_dir=a.pages_dir, wiki_dir=a.wiki_dir,
                          hotspots=(load(a.hotspots) or {}).get("hotspots")
                          if a.hotspots else None,
                          repo_dir=a.repo_dir, viz_dir=a.viz_dir,
                          next_steps=a.next_steps, quiz=a.quiz)
    Path(a.out).write_bytes(to_data_ts(bundle).encode("utf-8"))
    print(f"{a.out}: {len(bundle['nodes'])} nodes, {len(bundle['tour'])} tour steps")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
