"""concept_toc.yaml: THE human checkpoint before token spend (P4)."""
from pathlib import Path
import yaml


def write_toc(rows: list, path) -> None:
    Path(path).write_text(yaml.safe_dump(
        {"approved": False,
         "note": "review: prune concepts, set research flags, then set approved: true",
         "concepts": rows}, allow_unicode=True, sort_keys=False), encoding="utf-8")


def load_approved_toc(path) -> dict:
    p = Path(path)
    if not p.is_file():
        return {"status": "not_approved", "hint": f"{p} does not exist — run P2 first"}
    doc = yaml.safe_load(p.read_text(encoding="utf-8"))
    if not doc.get("approved"):
        return {"status": "not_approved",
                "hint": "set approved: true in concept_toc.yaml after review"}
    return {"status": "ok",
            "rows": [r for r in doc.get("concepts", []) if r.get("include")]}
