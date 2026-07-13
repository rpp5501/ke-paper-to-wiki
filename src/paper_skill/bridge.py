"""M6 bridge: propose (deterministic) -> verify (leased) -> confirm (human)."""
import datetime
import re
from pathlib import Path

import yaml

_CAMEL = re.compile(r"(?<=[a-z0-9])(?=[A-Z])|[_\-\s.:]+")
_STOP = {"the", "a", "an", "of", "and"}
_VERDICT = re.compile(r"(YES|NO):[ \t]*(\S[^\r\n]*)")


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
            source_path = k.get("source_ref", "").split(":L", 1)[0]
            filename = re.split(r"[\\/]", source_path)[-1].lower()
            bonus = 0.2 if any(t in filename for t in ct) else 0.0
            score = round(jac + bonus, 3)
            if score >= 0.25:
                out.append({"concept": c["id"], "code": k["id"], "score": score,
                            "evidence": f"shared tokens: {sorted(ct & kt)}"})
    out.sort(key=lambda r: (-r["score"], r["concept"], r["code"]))
    return out[:top]


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
        try:
            raw = spawn(VERIFY_PROMPT.format(
                label=cn["label"], definition=cn.get("definition", cn["label"]),
                code_label=kn["label"],
                source_ref=kn.get("source_ref", "?"))).strip()
        except Exception as exc:
            out.append({**c, "verdict": "no",
                        "reason": f"verifier error: {type(exc).__name__}"})
            continue
        match = _VERDICT.fullmatch(raw)
        if match:
            verdict, reason = match.group(1).lower(), match.group(2).strip()
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
    rows = [c for c in doc["candidates"] if c.get("confirmed") is True]
    if doc.get("include_unconfirmed") is True:
        rows += [c for c in doc["candidates"]
                 if c.get("confirmed") is not True and c.get("verdict") == "yes"]
    return rows


def merge_bridge(concept_graph: dict, code_graph: dict,
                 confirmed: list[dict]) -> dict:
    concept_ids = {node["id"] for node in concept_graph["nodes"]}
    code_ids = {node["id"] for node in code_graph["nodes"]}
    collisions = sorted(concept_ids & code_ids)
    if collisions:
        raise ValueError(f"node id collision across graphs: {', '.join(collisions)}")

    pairs = {}
    for candidate in confirmed:
        code_id = candidate["code"]
        concept_id = candidate["concept"]
        if code_id not in code_ids:
            raise ValueError(f"unknown code candidate endpoint: {code_id}")
        if concept_id not in concept_ids:
            raise ValueError(f"unknown concept candidate endpoint: {concept_id}")
        pair = (code_id, concept_id)
        pairs[pair] = pairs.get(pair, False) or candidate.get("confirmed") is True

    edges = concept_graph["edges"] + code_graph["edges"]
    for (code_id, concept_id), strong in pairs.items():
        edges.append({"src": code_id, "dst": concept_id, "kind": "implements",
                      "weight": 1.0,
                      "confidence": "extracted" if strong else "inferred",
                      "confidence_score": 1.0 if strong else 0.6})
    return {"meta": {"kind": "bridged",
                     "source": f'{concept_graph["meta"].get("source", "?")} + '
                               f'{code_graph["meta"].get("source", "?")}',
                     "generated": datetime.date.today().isoformat(), "version": 1},
            "nodes": concept_graph["nodes"] + code_graph["nodes"], "edges": edges}
