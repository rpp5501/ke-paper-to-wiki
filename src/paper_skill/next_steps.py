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
    for section in pack["sections"]:
        if _LIMIT_TITLES.search(section["title"]):
            gaps.append({
                "kind": "paper-limitation",
                "text": section["text"][:300],
                "anchors": {"nodes": [],
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

    if concept_graph.get("meta", {}).get("kind") == "bridged":
        implemented = {edge["dst"] for edge in concept_graph["edges"]
                       if edge["kind"] == "implements"}
        for node in concept_graph["nodes"]:
            if node["kind"] == "concept" and node["id"] not in implemented:
                gaps.append({
                    "kind": "no-implements-concept",
                    "text": f'no implementation linked for {node["label"]}',
                    "anchors": {"nodes": [node["id"]],
                                "sources": ["bridge"]},
                })

    if repo_dir is not None:
        for source_file in sorted(Path(repo_dir).rglob("*.py")):
            lines = source_file.read_text(
                encoding="utf-8", errors="replace").splitlines()
            for line_number, line in enumerate(lines, 1):
                match = _TODO.search(line)
                if match:
                    gaps.append({
                        "kind": "todo-comment",
                        "text": match.group(2).strip(),
                        "anchors": {"nodes": [],
                                    "sources": [f"{source_file.name}:{line_number}"]},
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
            match = re.search(r"\{.*\}", raw, re.S)
            document = _json.loads(match.group(0))
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
        title = idea.get("title") or "?"
        if not idea.get("title"):
            problems.append(f"idea missing title: {index}")
        if not idea.get("rationale"):
            problems.append(f"idea missing rationale: {title}")
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
