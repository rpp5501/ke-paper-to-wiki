"""Dual-level context assembly (round-2): global for TL;DR/Intuition,
local for Mechanics/Math. Deterministic, zero tokens."""


def _neighborhood(graph: dict, concept_id: str) -> list[str]:
    labels = {n["id"]: n["label"] for n in graph["nodes"]}
    out = []
    for e in graph["edges"]:
        if e["src"] == concept_id:
            out.append(f'{e["kind"]} → {labels.get(e["dst"], e["dst"])}')
        elif e["dst"] == concept_id:
            out.append(f'{labels.get(e["src"], e["src"])} → {e["kind"]}')
    return out


def assemble_context(pack: dict, graph: dict, concept_id: str,
                     note: dict | None) -> dict:
    node = next(n for n in graph["nodes"] if n["id"] == concept_id)
    sec_id = node.get("source_ref", "")
    section = next((s for s in pack["sections"] if s["id"] == sec_id), None)
    eqs = [e for e in pack["equations"] if e["section"] == sec_id]

    global_slice = "\n".join([
        f'Paper: {pack["meta"]["title"]}',
        f'Concept: {node["label"]} (level L{node.get("level", 0)})',
        "Neighborhood:",
        *(f"  {line}" for line in _neighborhood(graph, concept_id)),
    ])

    local_parts = [f'Section {sec_id}: {section["title"]}' if section else
                   f"Section {sec_id}: (text unavailable)"]
    if section:
        local_parts.append(section["text"])
    for e in eqs:
        local_parts.append(f'[{e["id"]}] {e["latex"]}')
    if note:
        local_parts.append(f'Research note: {note["synthesis"]}')
        for r in note.get("resources", []):
            local_parts.append(f'  resource: {r["title"]} — {r["why"]} — {r["url"]}')
    else:
        local_parts.append("Research note: none (no research note for this concept)")
    return {"global_slice": global_slice, "local_slice": "\n".join(local_parts)}
