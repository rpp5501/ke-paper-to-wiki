"""M6 bridge: propose (deterministic) -> verify (leased) -> confirm (human)."""
import re

_CAMEL = re.compile(r"(?<=[a-z0-9])(?=[A-Z])|[_\-\s.:]+")
_STOP = {"the", "a", "an", "of", "and"}


def _tokens(name: str) -> set:
    return {t.lower() for t in _CAMEL.split(name) if t and t.lower() not in _STOP}


def propose_candidates(concept_graph: dict, code_graph: dict,
                       top: int = 30) -> list[dict]:
    out = []
    for c in concept_graph["nodes"]:
        ct = _tokens(c["label"])
        if not ct:
            continue
        for k in code_graph["nodes"]:
            kt = _tokens(k["label"])
            if not kt:
                continue
            jac = len(ct & kt) / len(ct | kt)
            bonus = 0.2 if any(t in k.get("source_ref", "").lower() for t in ct) else 0.0
            score = round(jac + bonus, 3)
            if score >= 0.25:
                out.append({"concept": c["id"], "code": k["id"], "score": score,
                            "evidence": f"shared tokens: {sorted(ct & kt)}"})
    out.sort(key=lambda r: -r["score"])
    return out[:top]


import datetime
from pathlib import Path
import yaml

VERIFY_PROMPT = """Does this code entity implement this paper concept?
Concept: {label} — {definition}
Code: {code_label} at {source_ref}
Answer with exactly one line: "YES: <reason>" or "NO: <reason>"."""


def verify_candidates(cands: list[dict], concept_graph: dict, code_graph: dict,
                      spawn) -> list[dict]:
    concepts = {n["id"]: n for n in concept_graph["nodes"]}
    code = {n["id"]: n for n in code_graph["nodes"]}
    out = []
    for c in cands:
        cn, kn = concepts[c["concept"]], code[c["code"]]
        raw = spawn(VERIFY_PROMPT.format(
            label=cn["label"], definition=cn.get("definition", cn["label"]),
            code_label=kn["label"], source_ref=kn.get("source_ref", "?"))).strip()
        if raw.upper().startswith("YES"):
            verdict, reason = "yes", raw[3:].lstrip(": ").strip()
        elif raw.upper().startswith("NO"):
            verdict, reason = "no", raw[2:].lstrip(": ").strip()
        else:
            verdict, reason = "no", f"unparseable verdict: {raw[:60]}"
        out.append({**c, "verdict": verdict, "reason": reason})
    return out


def write_candidates_yaml(cands: list[dict], path) -> None:
    Path(path).write_text(yaml.safe_dump(
        {"include_unconfirmed": False,
         "note": "set confirmed: true per row you accept, then rerun merge",
         "candidates": [{**c, "confirmed": False} for c in cands]},
        allow_unicode=True, sort_keys=False), encoding="utf-8")


def load_confirmed(path) -> list[dict]:
    doc = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    rows = [c for c in doc["candidates"] if c.get("confirmed")]
    if doc.get("include_unconfirmed"):
        rows += [c for c in doc["candidates"]
                 if not c.get("confirmed") and c.get("verdict") == "yes"]
    return rows


def merge_bridge(concept_graph: dict, code_graph: dict,
                 confirmed: list[dict]) -> dict:
    edges = concept_graph["edges"] + code_graph["edges"]
    for c in confirmed:
        strong = c.get("confirmed", False)
        edges.append({"src": c["code"], "dst": c["concept"], "kind": "implements",
                      "weight": 1.0,
                      "confidence": "extracted" if strong else "inferred",
                      "confidence_score": 1.0 if strong else 0.6})
    return {"meta": {"kind": "bridged",
                     "source": f'{concept_graph["meta"].get("source", "?")} + '
                               f'{code_graph["meta"].get("source", "?")}',
                     "generated": datetime.date.today().isoformat(), "version": 1},
            "nodes": concept_graph["nodes"] + code_graph["nodes"], "edges": edges}
