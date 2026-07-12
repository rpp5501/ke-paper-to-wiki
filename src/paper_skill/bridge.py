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
