"""R15.2 — export quiz.json to an Anki-importable TSV (front/back/tags).

Usage: python scripts/quiz_to_anki.py fixtures/quiz/quiz.json [out.tsv]
Import in Anki: File > Import, fields separated by Tab, allow HTML.
"""
import json
import sys
from pathlib import Path


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    src = Path(sys.argv[1])
    out = Path(sys.argv[2]) if len(sys.argv) > 2 else src.with_suffix(".anki.tsv")
    doc = json.loads(src.read_text(encoding="utf-8"))
    rows = []
    for item in doc.get("items", []):
        options = item.get("options", [])
        correct = options[item["correct"]]
        front = item["prompt"] + "<br><br>" + "<br>".join(
            f"{chr(65 + i)}. {o['text']}" for i, o in enumerate(options))
        back = (f"{chr(65 + item['correct'])}. {correct['text']}"
                f"<br><br>{correct['explain']}")
        tags = f"{item.get('nodeId', '')} paper-quiz"
        rows.append("\t".join(
            field.replace("\t", " ").replace("\n", "<br>")
            for field in (front, back, tags)))
    out.write_text("\n".join(rows) + "\n", encoding="utf-8")
    print(f"{out}: {len(rows)} cards")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
