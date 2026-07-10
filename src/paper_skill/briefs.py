# src/paper_skill/briefs.py
"""Toc row -> research brief (schema-valid input for the playbook loop)."""


def _siblings(concept_id: str, graph: dict) -> list[str]:
    parents = {e["dst"] for e in graph["edges"]
               if e["src"] == concept_id and e["kind"] == "part-of"}
    return sorted({e["src"] for e in graph["edges"]
                   if e["dst"] in parents and e["kind"] == "part-of"
                   and e["src"] != concept_id})


def build_brief(row: dict, graph: dict, content_type: str = "background") -> dict:
    return {"concept": row["id"],
            "definition": row.get("definition", row["label"]),
            "content_type": content_type,
            "sub_questions": row.get("sub_questions", [])[:4],
            "do_not_research": _siblings(row["id"], graph),
            "budget": {"searches": 3, "fetches": 3, "api_calls": 2}}
