"""M7: deterministic gap harvest and anchored next-step synthesis."""
import re
from pathlib import Path

import yaml


_LIMIT_TITLES = re.compile(r"limitation|future|discussion|conclusion", re.I)
_TODO = re.compile(r"#\s*(TODO|FIXME|HACK)[:\s](.*)")


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
