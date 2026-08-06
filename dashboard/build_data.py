"""Bundle pipeline artifacts into src/data.gen.ts (design doc §3-§4).

Everything deterministic; runs without internet access. No runtime fetch exists in the
dashboard, so this file IS the data path.
"""
import argparse
import ast
import json
import re
import subprocess
from collections import Counter, defaultdict
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
        # On a bridged graph the `implements` edges run code -> concept, so the
        # code nodes are roots of the dependency order and reading_path hands
        # back five pgmpy functions before any concept. None has a page, so the
        # tour walked the reader through empty panels -- and the article, whose
        # chapters are built from these same steps, rendered nothing at all.
        # The tour is about the paper; a step with no page has nothing to show.
        # Filtering on kind, not on "has a page": a concept whose page is
        # missing still belongs on the reading path, with the fallback blurb.
        order = reading_path(plan_graph)
        concepts = [p for p in order
                    if nodes.get(p, {}).get("kind", "concept") == "concept"]
        picks = (concepts or order)[:5]
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


# A note under this id carries terminology for the whole paper rather than
# research about one concept. Terms like "d-separation" or "Markov" belong to
# the paper, and keying the glossary per concept meant repeating them in every
# note that used them.
PAPER_GLOSSARY_ID = "_paper"


def _load_notes(wiki_dir, fallback_date):
    notes, glossary, trace = {}, {}, []
    shared = {}
    if not wiki_dir:
        return notes, glossary, trace, shared
    for f in sorted(Path(wiki_dir).glob("*.yaml")):
        note = yaml.safe_load(f.read_text(encoding="utf-8"))
        cid = note.get("concept", f.stem)
        if cid == PAPER_GLOSSARY_ID:
            # Terminology only: it is not a concept, so it earns no note entry
            # and no trace row for a node that does not exist.
            shared.update(note.get("glossary") or {})
            continue
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
    return notes, glossary, trace, shared


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


# How many source excerpts a bundle will carry. Spent on the top hotspots of a
# whole-repo graph, or on every code node when there are few enough to fit.
EXCERPT_BUDGET = 20
CODE_PREVIEW_LINES = 40


def _definition_spans(tree):
    spans = []

    def visit(parent, node):
        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                start = child.lineno
                decorators = getattr(child, "decorator_list", [])
                if decorators:
                    start = min(start, *(decorator.lineno for decorator in decorators))
                kind = "class" if isinstance(child, ast.ClassDef) else (
                    "method" if isinstance(parent, ast.ClassDef) else "function")
                spans.append({"line": child.lineno, "start": start,
                              "end": child.end_lineno, "kind": kind})
            visit(child, child)

    visit(None, tree)
    return spans


def _is_code_node(node):
    return node.get("kind") in _CODE_KINDS | {"method"}


def _unresolved_listing(node):
    match = _SOURCE_LOCATION.fullmatch(node.get("source_ref") or "")
    raw_path = match.group("path") if match else ""
    suffix = Path(raw_path).suffix.lower()
    kind = node.get("kind")
    return {
        "path": Path(raw_path).as_posix() if raw_path else "",
        "language": "python" if suffix == ".py" else suffix.lstrip(".") or "text",
        "symbolKind": kind if kind in {"file", "class", "function", "method"}
        else "function",
        "startLine": 0,
        "endLine": 0,
        "previewEndLine": 0,
        "preview": "",
        "full": "",
        "rangeResolved": False,
    }


def _code_listings(plan_graph, repo_dir):
    """Build disclosed previews plus complete source symbols.

    Python's AST supplies inclusive end lines and correct class/method kinds.
    Other languages still receive an honest range when the graph provides one;
    a start-only location is marked unresolved instead of silently pretending
    the preview is complete.
    """
    repo = None
    if repo_dir:
        try:
            repo = Path(repo_dir).resolve()
        except (OSError, RuntimeError):
            pass
    listings = {}
    enriched = []
    for original in plan_graph["nodes"]:
        node = dict(original)
        if not _is_code_node(node):
            enriched.append(node)
            continue
        listing = _unresolved_listing(node)
        match = _SOURCE_LOCATION.fullmatch(node.get("source_ref") or "")
        if match and repo is not None:
            try:
                relative_path = Path(match.group("path"))
                if relative_path.is_absolute():
                    raise ValueError("absolute source path")
                source_path = (repo / relative_path).resolve()
                source_path.relative_to(repo)
                if not source_path.is_file():
                    raise ValueError("missing source path")
                lines = source_path.read_text(
                    encoding="utf-8", errors="replace").splitlines()
                requested = int(match.group("line"))
                explicit_end = (int(match.group("end"))
                                if match.group("end") else None)
                if explicit_end is not None and (
                        explicit_end < requested or explicit_end > len(lines)):
                    raise ValueError("invalid source range")

                start = requested
                end = explicit_end
                symbol_kind = node.get("kind", "function")
                resolved = explicit_end is not None
                if source_path.suffix.lower() == ".py":
                    try:
                        spans = _definition_spans(ast.parse("\n".join(lines)))
                    except SyntaxError:
                        spans = []
                    label_names_file = (
                        Path(str(node.get("label", ""))).name == relative_path.name)
                    if node.get("kind") == "file" or label_names_file:
                        start, end, symbol_kind, resolved = 1, len(lines), "file", True
                    else:
                        exact = next(
                            (span for span in spans if span["line"] == requested), None)
                        if exact:
                            start = exact["start"]
                            end = max(explicit_end or 0, exact["end"])
                            symbol_kind = exact["kind"]
                            resolved = end is not None

                if end is None:
                    end = min(len(lines), start + CODE_PREVIEW_LINES - 1)
                if start < 1 or start > len(lines) or end < start:
                    raise ValueError("source range outside file")
                end = min(end, len(lines))
                preview_end = min(end, start + CODE_PREVIEW_LINES - 1)
                path = relative_path.as_posix()
                listing = {
                    "path": path,
                    "language": ("python" if source_path.suffix.lower() == ".py"
                                 else source_path.suffix.lstrip(".") or "text"),
                    "symbolKind": symbol_kind if symbol_kind in {
                        "file", "class", "function", "method"} else "function",
                    "startLine": start,
                    "endLine": end,
                    "previewEndLine": preview_end,
                    "preview": "\n".join(lines[start - 1:preview_end]),
                    "full": "\n".join(lines[start - 1:end]),
                    "rangeResolved": resolved,
                }
            except (OSError, RuntimeError, ValueError, SyntaxError):
                pass
        listings[node["id"]] = listing
        if listing["rangeResolved"]:
            node["kind"] = listing["symbolKind"]
            node["source_ref"] = (
                f"{listing['path']}:L{listing['startLine']}-L{listing['endLine']}")
        enriched.append(node)
    return listings, enriched


def _excerpts(plan_graph, hotspots, repo_dir):
    if not repo_dir or plan_graph["meta"].get("kind") not in {
            "code", "bridged"}:
        return {}

    keep = {
        hotspot["id"] for hotspot in hotspots[:EXCERPT_BUDGET]
        if isinstance(hotspot, dict) and hotspot.get("id")
    }
    keep.update(
        edge["src"] for edge in plan_graph["edges"]
        if edge.get("kind") == "implements" and edge.get("src")
    )
    # A code node has no page and no research note, so without its source the
    # drawer says "no page or note for this node yet" and shows nothing at all
    # -- which is what an unbridged function looked like. When the code side is
    # small enough to fit the same budget the hotspot cap already spends, every
    # node carries its excerpt; a whole-repo graph stays bounded by the cap.
    # Bridged only: a whole-repo code graph stays hotspot-scoped however small,
    # because there "which functions matter" is the question the graph answers.
    code_nodes = [node["id"] for node in plan_graph["nodes"]
                  if node.get("kind") not in {"concept", None}]
    if (plan_graph["meta"].get("kind") == "bridged"
            and len(code_nodes) <= EXCERPT_BUDGET):
        keep.update(code_nodes)
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


_CHAPTER_FIELDS = {
    "id", "title", "question", "outcome", "conceptIds",
    "foundationConceptIds", "advancedConceptIds", "checkpointIds",
    "estimatedCoreMinutes", "estimatedFullMinutes",
}


def _authored_node_ids(plan_graph, pages):
    return [node["id"] for node in plan_graph["nodes"]
            if _page_for(node, pages)]


def _fallback_learning_path(plan_graph, hotspots, pages):
    chapters = []
    for step in _tour(plan_graph, hotspots, pages):
        node_id = step["nodeIds"][0]
        chapters.append({
            "id": node_id,
            "title": step["title"],
            "question": step["description"],
            "outcome": f"Explain {step['title']}.",
            "conceptIds": [node_id],
            "foundationConceptIds": [],
            "advancedConceptIds": [],
            "checkpointIds": [],
            "estimatedCoreMinutes": 0,
            "estimatedFullMinutes": 0,
        })
    return {"version": 1, "reviewed": False, "chapters": chapters}


def _load_learning_path(path, plan_graph, pages):
    raw = (json.loads(Path(path).read_text(encoding="utf-8"))
           if not isinstance(path, dict) else path)
    if "reviewed" in raw and not isinstance(raw["reviewed"], bool):
        raise ValueError("learning path reviewed must be a boolean")
    reviewed = raw.get("reviewed", False)
    chapters = raw.get("chapters") or []
    if not chapters:
        raise ValueError("learning path needs at least one chapter")
    known = {node["id"] for node in plan_graph["nodes"]}
    seen = set()
    chapter_ids = set()
    for chapter in chapters:
        missing = sorted(_CHAPTER_FIELDS - set(chapter))
        if missing:
            raise ValueError(
                f"learning chapter '{chapter.get('id', '?')}' missing: {', '.join(missing)}")
        if chapter["id"] in chapter_ids:
            raise ValueError(f"duplicate learning chapter id '{chapter['id']}'")
        chapter_ids.add(chapter["id"])
        for field in ("conceptIds", "foundationConceptIds", "advancedConceptIds"):
            repeated = sorted({node_id for node_id in chapter[field]
                               if chapter[field].count(node_id) > 1})
            if repeated:
                raise ValueError(
                    f"learning chapter '{chapter['id']}' repeats {field}: "
                    f"{', '.join(repeated)}")
            unknown = sorted(set(chapter[field]) - known)
            if unknown:
                raise ValueError(
                    f"learning chapter '{chapter['id']}' has unknown nodes: {', '.join(unknown)}")
        members = set(chapter["conceptIds"])
        for field in ("foundationConceptIds", "advancedConceptIds"):
            outside_chapter = sorted(set(chapter[field]) - members)
            if outside_chapter:
                raise ValueError(
                    f"learning chapter '{chapter['id']}' {field} must be included "
                    f"in conceptIds: {', '.join(outside_chapter)}")
        depth_overlap = sorted(
            set(chapter["foundationConceptIds"])
            & set(chapter["advancedConceptIds"]))
        if depth_overlap:
            raise ValueError(
                f"learning chapter '{chapter['id']}' foundationConceptIds and "
                f"advancedConceptIds overlap: {', '.join(depth_overlap)}")
        duplicates = seen.intersection(chapter["conceptIds"])
        if duplicates:
            raise ValueError(f"concept appears in multiple chapters: {', '.join(sorted(duplicates))}")
        seen.update(chapter["conceptIds"])

    authored = _authored_node_ids(plan_graph, pages)
    uncovered = [node_id for node_id in authored if node_id not in seen]
    if uncovered:
        raise ValueError(f"uncovered authored concepts: {', '.join(uncovered)}")

    ordered = [node_id for chapter in chapters
               for node_id in chapter["conceptIds"]]
    position = {node_id: index for index, node_id in enumerate(ordered)}
    for edge in plan_graph.get("edges", []):
        kind = edge.get("kind")
        if kind == "prerequisite":
            prerequisite = edge.get("src")
            dependent = edge.get("dst")
        elif kind == "builds-on":
            # Graph direction is dependent -> dependency for builds-on.
            prerequisite = edge.get("dst")
            dependent = edge.get("src")
        else:
            continue
        if prerequisite in position and dependent in position \
                and position[prerequisite] > position[dependent]:
            relation = "prerequisite" if kind == "prerequisite" else "builds-on dependency"
            raise ValueError(
                f"{relation} '{prerequisite}' appears after '{dependent}'")
    return {"version": raw.get("version", 1), "reviewed": reviewed,
            "chapters": chapters}


def _is_metadata_section(section):
    title = re.sub(r"[^a-z]+", " ",
                   str(section.get("title") or "").lower()).strip()
    return (title.startswith("acknowledg")
            or title.startswith("reference")
            or title.startswith("bibliograph"))


def _has_substantive_pack(pack):
    sections = (pack or {}).get("sections", [])
    equations = (pack or {}).get("equations", [])
    return (any(str(section.get("text") or "").strip()
                and not _is_metadata_section(section)
                for section in sections)
            or any(str(equation.get("latex") or "").strip()
                   for equation in equations))


def _section_coverage(plan_graph, pages, learning_path, pack):
    sections = (pack or {}).get("sections", [])
    included = {
        node_id for chapter in learning_path["chapters"]
        for node_id in chapter["conceptIds"]
    }
    covered_by_ref = defaultdict(set)
    equation_sections = {
        equation.get("id"): section_key(equation.get("section"))
        for equation in (pack or {}).get("equations", [])
        if equation.get("id")
    }
    for node in plan_graph["nodes"]:
        if node.get("id") not in included:
            continue
        markdown = _page_for(node, pages)
        if not markdown:
            continue
        refs = {section_key(node.get("source_ref"))}
        for evidence in _EVIDENCE_REF.findall(markdown):
            refs.add(equation_sections.get(evidence) or section_key(evidence))
        for ref in refs - {""}:
            covered_by_ref[ref].add(node["id"])

    rows = []
    for section in sections:
        section_id = section.get("id")
        key = section_key(section_id)
        if not section_id or not key:
            continue
        rows.append({
            "id": section_id,
            "key": key,
            "title": section.get("title", ""),
            "level": section.get("level"),
            "substantive": (bool(str(section.get("text") or "").strip())
                            and not _is_metadata_section(section)),
            "coveredByConceptIds": sorted(covered_by_ref.get(key, [])),
        })

    top_level = []
    uncovered = []
    for row in rows:
        if row["substantive"] and not row["coveredByConceptIds"]:
            uncovered.append(row["id"])
        if row["level"] != 1:
            continue
        descendants = [candidate for candidate in rows
                       if candidate["key"].startswith(row["key"] + ".")]
        substantive = [candidate for candidate in descendants
                       if candidate["substantive"]]
        covered_by = sorted({
            node_id for candidate in [row, *descendants]
            for node_id in candidate["coveredByConceptIds"]
        })
        covered = bool(row["coveredByConceptIds"]) if row["substantive"] \
            else all(candidate["coveredByConceptIds"] for candidate in substantive)
        top_level.append({
            "id": row["id"],
            "title": row["title"],
            "covered": covered,
            "coveredByConceptIds": covered_by,
            "subsections": [{
                "id": candidate["id"],
                "title": candidate["title"],
                "covered": bool(candidate["coveredByConceptIds"]),
                "coveredByConceptIds": candidate["coveredByConceptIds"],
            } for candidate in substantive],
        })
    return {"topLevelSections": top_level,
            "uncoveredSectionIds": sorted(uncovered)}


def _coverage(plan_graph, pages, learning_path, pack=None):
    authored = _authored_node_ids(plan_graph, pages)
    covered = {node_id for chapter in learning_path["chapters"]
               for node_id in chapter["conceptIds"]}
    uncovered = [node_id for node_id in authored if node_id not in covered]
    return {"authoredConcepts": len(authored),
            "coveredConcepts": len(authored) - len(uncovered),
            "uncoveredConceptIds": uncovered,
            **_section_coverage(plan_graph, pages, learning_path, pack)}


_CHECKPOINT_KINDS = {"prediction", "application", "debug", "interpretation"}
_CHECKPOINT_PLACEMENTS = {
    "after-intuition", "after-mechanics", "chapter-end",
}


def _validate_reviewed_checkpoints(learning_path, quiz_items):
    by_id = {}
    for item in quiz_items:
        if item["id"] in by_id:
            raise ValueError(f"duplicate quiz item id '{item['id']}'")
        by_id[item["id"]] = item
    claimed_by = {}
    chapters = {chapter["id"]: chapter
                for chapter in learning_path["chapters"]}
    for chapter in learning_path["chapters"]:
        members = set(chapter["conceptIds"])
        for checkpoint_id in chapter["checkpointIds"]:
            if checkpoint_id in claimed_by:
                raise ValueError(f"duplicate checkpoint id '{checkpoint_id}'")
            claimed_by[checkpoint_id] = chapter["id"]
            item = by_id.get(checkpoint_id)
            if item is None:
                raise ValueError(
                    f"learning chapter '{chapter['id']}' checkpoint "
                    f"missing loaded quiz item '{checkpoint_id}'")
            if item["chapterId"] != chapter["id"]:
                raise ValueError(
                    f"checkpoint '{checkpoint_id}' belongs to chapter "
                    f"'{item['chapterId']}', not '{chapter['id']}'")
            if item["kind"] not in _CHECKPOINT_KINDS:
                raise ValueError(
                    f"checkpoint '{checkpoint_id}' has invalid kind '{item['kind']}'")
            if item["placement"] not in _CHECKPOINT_PLACEMENTS:
                raise ValueError(
                    f"checkpoint '{checkpoint_id}' has invalid placement "
                    f"'{item['placement']}'")
            if item["nodeId"] not in members:
                raise ValueError(
                    f"checkpoint '{checkpoint_id}' node '{item['nodeId']}' "
                    f"is not a member of chapter '{chapter['id']}'")
    for item in quiz_items:
        chapter_id = item.get("chapterId")
        if chapter_id in chapters and claimed_by.get(item["id"]) != chapter_id:
            raise ValueError(
                f"quiz item '{item['id']}' names reviewed chapter "
                f"'{chapter_id}' but is not listed exactly once by that chapter")


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
            "chapterId": item.get("chapterId", ""),
            "kind": item.get("kind", "interpretation"),
            "placement": item.get("placement", "chapter-end"),
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
            content = (Path(pages_dir) / page).read_bytes()
            content = content.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
            digest = hashlib.sha256(content).hexdigest()
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
            # R13.1 placement, chosen by the visualize skill.
            "anchorTier": entry.get("anchor_tier", "after-intuition"),
            "sectionRef": _provenance_ref(
                entry.get("source_ref", ""), known_sections, f"viz: {node_id}"),
        }
    return out


_WORD = re.compile(r"[A-Za-z0-9]+(?:[-'][A-Za-z0-9]+)?")
_LIST_ITEM = re.compile(r"^(?:[-+*]|\d+[.)])\s+(?P<content>.+)$")
_WORKED_EVIDENCE = re.compile(
    r"\b(?P<kind>worked\s+example|counterexample|prediction\s+check|"
    r"boundary\s+(?:case|condition))\b", re.IGNORECASE)
_EVIDENCE_REF = re.compile(r"\[(§[A-Za-z0-9_]+|eq_[A-Za-z0-9_]+|S\d+)\]")


def _prose_paragraphs(markdown):
    """Yield prose paragraphs; only blocks that are not reader prose are exempt."""
    paragraphs, current = [], []
    in_fence = False
    in_equation = False

    def flush():
        if current:
            paragraphs.append(" ".join(current).strip())
            current.clear()

    for raw_line in markdown.splitlines() + [""]:
        line = raw_line.strip()
        if line.startswith("```"):
            flush()
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        if line.startswith("$$") or (in_equation and "$$" in line):
            flush()
            if line.count("$$") == 1:
                in_equation = not in_equation
            continue
        if in_equation:
            continue
        if not line:
            flush()
            continue
        item = _LIST_ITEM.match(line)
        if raw_line.startswith(("    ", "\t")) and not item:
            flush()
            continue
        if line.startswith("#") or line.startswith("|"):
            flush()
            continue
        if item:
            flush()
            paragraphs.append(item.group("content").strip())
            continue
        if line.startswith(">"):
            line = re.sub(r"^(?:>\s?)+", "", line)
        current.append(line)
    return paragraphs


# Retrieval practice only does work when it is spaced through the reading. The
# first SID build carried 9 checkpoints across 20k words -- one per ~2,250 --
# and put 5 of them in a single chapter, which is a feature that exists rather
# than one that teaches.
CHECKPOINT_WORDS_PER_ITEM = 800
CHECKPOINT_MIN_PER_CHAPTER = 2


def _checkpoint_density(pages, quiz_items, learning_path):
    """Are checkpoints spaced through the reading, or clumped into one chapter?

    Reported, never raised: quiz content follows the same never-break-the-build
    rule as _load_quiz. It reaches releasePass, so a release build still has to
    answer for it.
    """
    # Prose words only. Diagram source and fenced teaching blocks are read, not
    # waded through, and counting them would raise the checkpoint budget every
    # time a page gained a diagram -- charging the author for illustrating.
    words = sum(
        len(_WORD.findall(re.sub(r"```.*?```", " ", markdown, flags=re.S)))
        for markdown in pages.values())
    expected = max(1, round(words / CHECKPOINT_WORDS_PER_ITEM))
    per_chapter = Counter(
        item.get("chapterId", "") for item in quiz_items if item.get("chapterId"))
    chapters = [chapter["id"] for chapter in (learning_path or {}).get("chapters", [])]
    thin = sorted(
        chapter for chapter in chapters
        if per_chapter.get(chapter, 0) < CHECKPOINT_MIN_PER_CHAPTER)
    return {
        "words": words,
        "items": len(quiz_items),
        "expectedItems": expected,
        "wordsPerItem": round(words / len(quiz_items)) if quiz_items else None,
        "perChapter": dict(sorted(per_chapter.items())),
        "thinChapterIds": thin,
        "pass": len(quiz_items) >= expected and not thin,
    }


def _content_quality_report(pages, coverage=None, known_refs=None,
                            required_example_ids=None, checkpoints=None):
    warnings, errors = [], []
    paragraph_rows = []
    duplicate_owners = defaultdict(list)
    unresolved = []
    equations_by_ref = defaultdict(set)
    conflicting_complexity = []
    known_refs = set(known_refs or [])
    required_example_ids = sorted(set(required_example_ids or []))
    example_evidence = []

    for node_id, markdown in pages.items():
        prose = _prose_paragraphs(markdown)
        evidence = _WORKED_EVIDENCE.search("\n".join(prose))
        if evidence:
            example_evidence.append({
                "nodeId": node_id,
                "kind": evidence.group("kind").lower(),
            })
        for index, paragraph in enumerate(prose, start=1):
            words = len(_WORD.findall(paragraph))
            row = {"nodeId": node_id, "paragraph": index, "words": words}
            paragraph_rows.append(row)
            if words > 100:
                errors.append(row)
            elif words > 60:
                warnings.append(row)
            if words >= 15:
                normalized = re.sub(r"\s+", " ", paragraph.lower()).strip()
                duplicate_owners[normalized].append(node_id)

        if known_refs:
            for ref in _EVIDENCE_REF.findall(markdown):
                normalized = ref[1:] if ref.startswith("§") else ref
                if normalized not in known_refs:
                    unresolved.append({"nodeId": node_id, "reference": ref})

        for match in re.finditer(
                r"\$\$(.*?)\$\$\s*\[(eq_[A-Za-z0-9_]+)\]",
                markdown, flags=re.DOTALL):
            formula, equation_ref = match.groups()
            normalized_formula = re.sub(r"\s+", "", formula)
            normalized_formula = re.sub(r"^\(\*\)", "", normalized_formula)
            equations_by_ref[equation_ref].add(normalized_formula)

        lower = markdown.lower()
        scaling_terms = [term for term in ("quadratic", "cubic", "quartic")
                         if term in lower]
        if len(scaling_terms) >= 2 \
                and not ("worst-case" in lower and "empirical" in lower):
            conflicting_complexity.append({"nodeId": node_id,
                                            "terms": scaling_terms})

    duplicates = [
        {"nodeIds": sorted(set(owners)), "words": text}
        for text, owners in duplicate_owners.items()
        if len(set(owners)) > 1
    ]
    contradictory = [
        {"equationRef": equation_ref, "formulas": sorted(values)}
        for equation_ref, values in equations_by_ref.items() if len(values) > 1
    ]
    long_count = len(warnings) + len(errors)
    paragraph_count = len(paragraph_rows)
    readability = {
        "paragraphs": paragraph_count,
        "warnings": warnings,
        "errors": errors,
        "longParagraphRatio": (long_count / paragraph_count
                               if paragraph_count else 0.0),
    }
    uncovered_sections = (coverage or {}).get("uncoveredSectionIds", [])
    example_covered_ids = sorted(
        entry["nodeId"] for entry in example_evidence
        if entry["nodeId"] in required_example_ids)
    missing_example_ids = sorted(
        set(required_example_ids) - set(example_covered_ids))
    worked_example_coverage = {
        "requiredConceptIds": required_example_ids,
        "coveredConceptIds": example_covered_ids,
        "missingConceptIds": missing_example_ids,
        "evidence": sorted(example_evidence, key=lambda entry: entry["nodeId"]),
    }
    return {
        "coverage": coverage or {},
        "readability": readability,
        "unresolvedReferences": unresolved,
        "duplicatedExplanations": duplicates,
        "contradictoryFormulas": contradictory,
        "conflictingComplexityClaims": conflicting_complexity,
        "workedExampleCoverage": worked_example_coverage,
        "checkpointDensity": checkpoints or {},
        "releasePass": (not errors
                        and (not paragraph_count
                             or long_count / paragraph_count <= 0.10)
                        and not unresolved
                        and not duplicates
                        and not contradictory
                        and not conflicting_complexity
                        and not uncovered_sections
                        and not missing_example_ids
                        # An absent quiz is a viz-free-style opt-out, not a
                        # failure; a quiz that is present has to be spaced.
                        and (not checkpoints or checkpoints.get("pass", True))),
    }


def build_bundle(plan_graph, pack=None, pages_dir=None, wiki_dir=None,
                 hotspots=None, repo_dir=None, viz_dir=None,
                 next_steps=None, quiz=None, learning_path=None, release=False):
    hotspots = hotspots or []
    pages, stripped = _load_pages(pages_dir)
    code_listings, enriched_nodes = _code_listings(plan_graph, repo_dir)
    graph = {**plan_graph, "nodes": enriched_nodes}
    if release and not learning_path:
        raise ValueError("release build requires a reviewed --learning-path manifest")
    sections = {
        section_key(s["id"]): {"title": s.get("title", ""),
                               "text": s.get("text", "")}
        for s in (pack or {}).get("sections", []) if section_key(s["id"])
    }
    quiz_items = (_load_quiz(
        quiz, {n["id"] for n in graph["nodes"]}, sections) if quiz else [])
    learning = (_load_learning_path(learning_path, graph, pages)
                if learning_path else
                _fallback_learning_path(graph, hotspots, pages))
    if release and not learning["reviewed"]:
        raise ValueError("release build requires a reviewed learning-path manifest")
    if release and not pages:
        raise ValueError("release build requires a nonempty --pages-dir")
    if release and not _has_substantive_pack(pack):
        raise ValueError(
            "release build requires --pack with substantive sections or equations")
    if release or learning["reviewed"]:
        _validate_reviewed_checkpoints(learning, quiz_items)
    coverage = _coverage(graph, pages, learning, pack)
    if release and (not coverage["authoredConcepts"]
                    or not coverage["coveredConcepts"]):
        raise ValueError(
            "release build requires at least one authored and covered concept")
    known_refs = {
        item["id"] for group in ("sections", "equations")
        for item in (pack or {}).get(group, []) if item.get("id")
    }
    quality_report = _content_quality_report(
        pages, coverage=coverage, known_refs=known_refs,
        required_example_ids=_authored_node_ids(graph, pages),
        checkpoints=_checkpoint_density(pages, quiz_items, learning)
        if quiz else None)
    if release and not quality_report["releasePass"]:
        raise ValueError("release build requires qualityReport.releasePass=true")
    notes, glossary, trace, shared_terms = _load_notes(
        wiki_dir, plan_graph["meta"].get("generated", ""))
    if shared_terms:
        # Paper-wide terms reach every concept; a concept that defines the same
        # term keeps its own, more precise sense.
        glossary = {node["id"]: {**shared_terms, **glossary.get(node["id"], {})}
                    for node in graph["nodes"]}
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
    bundle = {"bundleVersion": 2,
              "meta": graph["meta"], "nodes": graph["nodes"],
              "edges": graph["edges"], "pages": pages, "notes": notes,
              "hotspots": hotspots, "clusters": _clusters(graph),
              "tour": _tour(graph, hotspots, pages),
              "learningPath": learning,
              "coverage": coverage,
              "qualityReport": quality_report,
              "provenance": (pack or {}).get("extraction", {}),
              "centrality": _centrality(graph),
              "eqIndex": _eq_index(graph, pack),
              "trace": sorted(trace, key=lambda t: (t["nodeId"], t["phase"])),
              "glossary": glossary,
              "excerpts": _excerpts(graph, hotspots, repo_dir),
              "codeListings": code_listings,
              "dependentSide": _DEPENDENT_SIDE}
    if repo_dir:
        bundle["mtimes"] = _source_dates(graph, repo_dir)
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
            next_steps, {n["id"] for n in graph["nodes"]})
    if quiz:  # R15.2: same opt-in discipline
        bundle["checkpoints"] = quiz_items
        # One-cycle compatibility alias for pre-v2 dashboard consumers.
        bundle["quiz"] = quiz_items
    if pack:  # R15.11: same opt-in discipline
        bundle["sections"] = sections
        # The paper's own \newcommand table. Equations are copied verbatim from
        # the source, so their notation is the paper's, not KaTeX's defaults.
        # An older pack predates the field and yields {} rather than KeyError.
        bundle["macros"] = pack.get("macros") or {}
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
    p.add_argument("--learning-path", help="reviewed learning-path.json; "
                                           "omit for an unreviewed fallback")
    p.add_argument("--release", action="store_true",
                   help="fail closed on reviewed learning-path and quality checks")
    p.add_argument("--update", action="store_true",
                   help="patch opt-in sections (--viz-dir/--next-steps/--quiz)"
                        " into the existing --out without a full rebuild")
    p.add_argument("--out", default="src/data.gen.ts")
    a = p.parse_args(argv)
    load = lambda x: json.loads(Path(x).read_text(encoding="utf-8")) if x else None

    if a.update:
        if a.release:
            p.error("--release requires a full build, not --update")
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
            quiz_items = _load_quiz(a.quiz, known, sections)
            bundle["checkpoints"] = quiz_items
            # One-cycle compatibility alias for pre-v2 dashboard consumers.
            bundle["quiz"] = quiz_items
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
                          next_steps=a.next_steps, quiz=a.quiz,
                          learning_path=a.learning_path, release=a.release)
    Path(a.out).write_bytes(to_data_ts(bundle).encode("utf-8"))
    print(f"{a.out}: {len(bundle['nodes'])} nodes, {len(bundle['tour'])} tour steps")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
