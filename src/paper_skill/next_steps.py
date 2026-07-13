"""M7: deterministic gap harvest and anchored next-step synthesis."""
import datetime
import json as _json
import re
from pathlib import Path

import yaml


_LIMIT_TITLES = re.compile(r"limitation|future|discussion|conclusion", re.I)
_TODO = re.compile(r"#\s*(TODO|FIXME|HACK)[:\s](.*)")

SYNTHESIS_PROMPT = """Synthesize research/engineering directions from these
verified gaps. Dedupe aggressively; rank by leverage. Emit ONLY JSON:
{{"ideas": [{{"title": "...", "rationale": "2 sentences max",
  "anchors": {{"nodes": ["graph node ids"], "sources": ["§sec_x / file:line / note file"]}}}}]}}
Every idea MUST reuse anchors from the gap list — inventing anchors is failure.

GAPS:
{gaps_json}
"""


def harvest(pack: dict, concept_graph: dict, code_graph: dict | None = None,
            wiki_home=None, repo_dir=None) -> list[dict]:
    gaps: list[dict] = []
    graphs = [concept_graph]
    if code_graph is not None and code_graph is not concept_graph:
        graphs.append(code_graph)
    for section in pack["sections"]:
        if _LIMIT_TITLES.search(section["title"]):
            nodes = sorted({
                node["id"] for graph in graphs for node in graph["nodes"]
                if node["kind"] == "concept" and
                node.get("source_ref") == section["id"]
            })
            gaps.append({
                "kind": "paper-limitation",
                "text": section["text"][:300],
                "anchors": {"nodes": nodes,
                            "sources": [f'§{section["id"]}']},
            })

    if wiki_home is not None:
        wiki = Path(wiki_home) / "_research_wiki"
        note_files = sorted(wiki.glob("*.yaml")) if wiki.is_dir() else []
        for note_file in note_files:
            note = yaml.safe_load(note_file.read_text(encoding="utf-8"))
            for unresolved in note.get("unresolved") or []:
                gaps.append({
                    "kind": "unresolved-note",
                    "text": unresolved,
                    "anchors": {"nodes": [note["concept"]],
                                "sources": [note_file.name]},
                })

    bridged_graph = next((graph for graph in graphs
                          if
                          graph.get("meta", {}).get("kind") == "bridged"), None)
    if bridged_graph is not None:
        implemented = {edge["dst"] for edge in bridged_graph["edges"]
                       if edge["kind"] == "implements"}
        for node in bridged_graph["nodes"]:
            if node["kind"] == "concept" and node["id"] not in implemented:
                gaps.append({
                    "kind": "no-implements-concept",
                    "text": f'no implementation linked for {node["label"]}',
                    "anchors": {"nodes": [node["id"]],
                                "sources": ["bridge"]},
                })

    if repo_dir is not None:
        repo_root = Path(repo_dir)
        for source_file in sorted(repo_root.rglob("*.py")):
            relative_path = source_file.relative_to(repo_root).as_posix()
            nodes = sorted({
                node["id"] for graph in graphs for node in graph["nodes"]
                if node["kind"] in {"file", "class", "function", "route"}
                and node.get("source_ref", "").split(":L", 1)[0]
                .replace("\\", "/").removeprefix("./") == relative_path
            })
            lines = source_file.read_text(
                encoding="utf-8", errors="replace").splitlines()
            for line_number, line in enumerate(lines, 1):
                match = _TODO.search(line)
                if match:
                    gaps.append({
                        "kind": "todo-comment",
                        "text": match.group(2).strip(),
                        "anchors": {"nodes": nodes,
                                    "sources": [f"{relative_path}:{line_number}"]},
                    })
    return gaps


def forward_gaps(paper_id: str, walk=None) -> list[dict]:
    if walk is None:
        from research_mcp.citation_walk import citation_walk
        walk = citation_walk
    result = walk(paper_id, direction="in", limit=15)
    return [{
        "kind": "field-follow-up",
        "text": paper["title"],
        "anchors": {"nodes": [], "sources": [paper["id"]]},
    } for paper in result.get("papers", [])]


def synthesize_ideas(gaps: list[dict], spawn, top: int = 8) -> dict:
    prompt = SYNTHESIS_PROMPT.format(
        gaps_json=_json.dumps(gaps, ensure_ascii=False, indent=1))
    problems: list[str] = []
    for attempt in range(2):
        attempt_prompt = prompt if attempt == 0 else (
            prompt + f"\nPrevious output invalid: {problems}. JSON only.")
        try:
            raw = spawn(attempt_prompt)
        except Exception as exc:
            return {
                "status": "failed-orchestration",
                "problems": [f"synthesis worker error: {type(exc).__name__}"],
                "ideas": [],
            }
        try:
            document = _json.loads(raw.strip())
            ideas = document["ideas"]
            if not isinstance(ideas, list):
                raise TypeError("ideas must be a list")
        except (AttributeError, KeyError, TypeError, _json.JSONDecodeError):
            problems = ["not parseable JSON with an ideas list"]
            continue

        problems = lint_ideas(ideas)
        if not problems:
            problems = _lint_anchor_provenance(ideas, gaps)
        if not problems:
            return {"status": "ok", "ideas": ideas[:top]}
    return {"status": "failed-orchestration",
            "problems": problems, "ideas": []}


def lint_ideas(ideas: list[dict]) -> list[str]:
    problems: list[str] = []
    for index, idea in enumerate(ideas):
        if not isinstance(idea, dict):
            problems.append(f"idea {index} must be an object")
            continue
        raw_title = idea.get("title")
        title_valid = isinstance(raw_title, str) and bool(raw_title.strip())
        title = raw_title if title_valid else "?"
        if not title_valid:
            problems.append(
                f"idea title must be a non-empty string: {index}")
        rationale = idea.get("rationale")
        if not isinstance(rationale, str) or not rationale.strip():
            problems.append(
                f"idea rationale must be a non-empty string: {title}")
        anchors = idea.get("anchors") or {}
        if not isinstance(anchors, dict):
            problems.append(f"idea anchors must be an object: {title}")
            continue
        nodes = anchors.get("nodes")
        sources = anchors.get("sources")
        if not isinstance(nodes, list):
            problems.append(f"idea anchor nodes must be a list: {title}")
        if not isinstance(sources, list):
            problems.append(f"idea anchor sources must be a list: {title}")
        if not isinstance(nodes, list) or not isinstance(sources, list):
            continue
        nodes_valid = all(isinstance(node, str) and node.strip()
                          for node in nodes)
        sources_valid = all(isinstance(source, str) and source.strip()
                            for source in sources)
        if not nodes_valid:
            problems.append(
                f"idea anchor nodes must contain non-empty strings: {title}")
        if not sources_valid:
            problems.append(
                f"idea anchor sources must contain non-empty strings: {title}")
        if not nodes_valid or not sources_valid:
            continue
        if not nodes and not sources:
            problems.append(f"unanchored idea: {title}")
        elif not nodes:
            problems.append(f"idea missing node anchors: {title}")
        elif not sources:
            problems.append(f"idea missing source anchors: {title}")
    return problems


def _lint_anchor_provenance(ideas: list[dict], gaps: list[dict]) -> list[str]:
    allowed_nodes = {node for gap in gaps
                     for node in gap["anchors"].get("nodes", [])}
    allowed_sources = {source for gap in gaps
                       for source in gap["anchors"].get("sources", [])}
    problems = []
    for idea in ideas:
        title = idea["title"]
        nodes = set(idea["anchors"]["nodes"])
        sources = set(idea["anchors"]["sources"])
        invented_nodes = sorted(nodes - allowed_nodes)
        invented_sources = sorted(sources - allowed_sources)
        if invented_nodes:
            problems.append(
                f"invented node anchors for {title}: {invented_nodes}")
        if invented_sources:
            problems.append(
                f"invented source anchors for {title}: {invented_sources}")
    return problems


def write_outputs(ideas: list[dict], out_dir) -> None:
    problems = lint_ideas(ideas)
    if problems:
        raise ValueError("; ".join(problems))

    output = Path(out_dir)
    output.mkdir(parents=True, exist_ok=True)
    markdown = [
        f"# Next steps — generated {datetime.date.today().isoformat()}", "",
    ]
    for idea in ideas:
        markdown += [
            f"## {idea['title']}",
            idea["rationale"],
            f"anchors: nodes={idea['anchors']['nodes']} "
            f"sources={idea['anchors']['sources']}",
            "",
        ]
    (output / "NEXT_STEPS.md").write_text(
        "\n".join(markdown), encoding="utf-8")
    (output / "ideas.yaml").write_text(yaml.safe_dump(
        {"note": "confirm per idea; N3 novelty runs only on confirmed/top-k",
         "ideas": [{**idea, "confirmed": False} for idea in ideas]},
        allow_unicode=True, sort_keys=False), encoding="utf-8")


def novelty_briefs(ideas: list[dict], top: int = 3) -> list[dict]:
    briefs = []
    for idea in ideas[:top]:
        slug = re.sub(r"[^a-z0-9]+", "-", idea["title"].lower()).strip("-")
        briefs.append({
            "concept": f"novelty--{slug}",
            "definition": idea["rationale"],
            "content_type": "background",
            "sub_questions": [
                "Has this been done? Find the closest prior work.",
                "What would differentiate this from existing work?",
            ],
            "do_not_research": [],
            "budget": {"searches": 3, "fetches": 3, "api_calls": 2},
        })
    return briefs
