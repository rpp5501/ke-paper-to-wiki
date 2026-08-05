"""M6 bridge: propose (deterministic) -> verify (leased) -> confirm (human)."""
import datetime
import re
from pathlib import Path

import yaml

_CAMEL = re.compile(r"(?<=[a-z0-9])(?=[A-Z])|[_\-\s.:]+")
# Function words carry no evidence that code implements a concept: a shared
# "on" paired _reachable_on_non_directed_path with an unrelated concept.
_STOP = {"the", "a", "an", "of", "and", "on", "in", "to", "for", "with", "by",
         "from", "at", "as", "is", "are", "be", "or", "not", "that", "this",
         "it", "its", "into", "over", "per", "via", "up", "out"}
_VERDICT = re.compile(r"(YES|NO):[ \t]*(\S[^\r\n]*)")


def _tokens(name: str) -> set:
    return {t.lower() for t in _CAMEL.split(name) if t and t.lower() not in _STOP}


# Scaled by the share of the code name the definition covers, so a code entity
# whose name is *entirely* accounted for by the definition (parallel_heads vs
# "...heads in parallel...") clears the 0.25 gate on its own, while partial
# coverage does not. Below the label weight throughout: a matching name is
# stronger evidence than a matching word in a sentence.
DEFINITION_WEIGHT = 0.3


def propose_candidates(concept_graph: dict, code_graph: dict,
                       top: int = 30, definitions: dict | None = None) -> list[dict]:
    """Deterministic concept<->code candidates. Zero tokens.

    ``definitions`` maps concept id -> the paper's own one-line definition, as
    written by P2 into the TOC rows. Label-only matching compares prose
    ("Equivalent Graphical Formulation") against identifiers
    (_compute_path_matrix) and scores near zero unless the names coincide: on
    pgmpy's sid.py all 30 candidates hit the single token "sid" and the two
    functions implementing the algorithms drew none at all. Definition text is
    the vocabulary the two halves share, so it contributes -- at a lower weight,
    because a matching *name* is stronger evidence than a matching word in a
    sentence.
    """
    definitions = definitions or {}
    out = []
    for c in concept_graph["nodes"]:
        ct = _tokens(c["label"])
        if not ct:
            continue
        dt = _tokens(definitions.get(c["id"], "")) - ct
        for k in code_graph["nodes"]:
            kt = _tokens(k["label"])
            if not kt:
                continue
            jac = len(ct & kt) / len(ct | kt)
            source_path = k.get("source_ref", "").split(":L", 1)[0]
            filename = re.split(r"[\\/]", source_path)[-1].lower()
            bonus = 0.2 if any(t in filename for t in ct) else 0.0
            shared_def = dt & kt
            def_score = (DEFINITION_WEIGHT * len(shared_def) / len(kt)
                         if shared_def else 0.0)
            score = round(jac + bonus + def_score, 3)
            if score >= 0.25:
                evidence = f"shared tokens: {sorted(ct & kt)}"
                if shared_def:
                    evidence += f"; via definition: {sorted(shared_def)}"
                out.append({"concept": c["id"], "code": k["id"], "score": score,
                            "evidence": evidence})

    # Order for truncation by round-robin over CODE entities, best first within
    # each. Pure score order let a few pairs sharing one loud token ("sid") take
    # all 30 slots while half the code entities drew nothing -- and the verifier
    # can only reject what it is shown. Ranking within each entity means every
    # function gets its best candidate considered before any gets a second.
    rank: dict[str, int] = {}
    ordered = []
    for cand in sorted(out, key=lambda r: (-r["score"], r["concept"], r["code"])):
        rank[cand["code"]] = rank.get(cand["code"], -1) + 1
        ordered.append((rank[cand["code"]], -cand["score"],
                        cand["concept"], cand["code"], cand))
    ordered.sort(key=lambda t: t[:4])
    return [t[4] for t in ordered[:top]]


# The source is inlined rather than referenced. Naming a path and not showing it
# made an agentic spawn go open the file -- from the caller's cwd, where a path
# recorded against another repo does not resolve -- so every parseable verdict
# in the first real run was a variation on "No file named sid.py exists in this
# repository". That is not an answer to the question being asked.
VERIFY_PROMPT = """Does this code entity implement this paper concept?
Concept: {label} — {definition}
Code: {code_label} at {source_ref}
{code_excerpt}
Judge only from what is written above. Do not open, read, or search for any
file; the source you need is already here, and the path is from another
repository. If the evidence above is insufficient, answer NO.
Answer with exactly one line: "YES: <reason>" or "NO: <reason>"."""

CODE_EXCERPT_LINES = 40


def _code_excerpt(node: dict, repo_dir) -> str:
    """The source behind ``node``, or a line saying it is unavailable.

    Never raises and never returns something that invites a lookup: a stale
    path must produce a verdict on the evidence, not a filesystem question.
    """
    if not repo_dir:
        return "(source not provided)"
    ref = str(node.get("source_ref", ""))
    path, _, line = ref.partition(":L")
    target = Path(repo_dir) / path
    if not target.is_file():
        return "(source unavailable — judge from the labels above)"
    try:
        lines = target.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return "(source unavailable — judge from the labels above)"
    start = max(0, int(line) - 1) if line.isdigit() else 0
    body = "\n".join(lines[start:start + CODE_EXCERPT_LINES]).strip()
    return f"Source:\n{body}" if body else (
        "(source unavailable — judge from the labels above)")


def verify_candidates(cands: list[dict], concept_graph: dict, code_graph: dict,
                      spawn, definitions: dict | None = None,
                      repo_dir=None) -> list[dict]:
    """One leased verdict per candidate.

    ``definitions`` is the same TOC-sourced map propose_candidates takes.
    Without it the prompt reads "Concept: X -- X", because P2 moves definition
    onto the TOC rows and off the graph nodes, so the node-level .get() here
    always fell through to its label fallback.
    """
    definitions = definitions or {}
    concepts = {n["id"]: n for n in concept_graph["nodes"]}
    code = {n["id"]: n for n in code_graph["nodes"]}
    out = []
    for c in cands:
        cn, kn = concepts[c["concept"]], code[c["code"]]
        try:
            raw = spawn(VERIFY_PROMPT.format(
                label=cn["label"],
                definition=(definitions.get(c["concept"])
                            or cn.get("definition") or cn["label"]),
                code_label=kn["label"],
                source_ref=kn.get("source_ref", "?"),
                code_excerpt=_code_excerpt(kn, repo_dir))).strip()
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
