"""R13 viz gate CLI — offline/injection/size/manifest checks over a viz dir.

Usage: python scripts/gate_viz.py <viz-dir>
Exit 0 = pass; exit 1 = findings printed, one per line.
Logic lives in paper_skill.viz.gate_viz_dir (tested in tests/test_viz.py).
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from paper_skill.viz import gate_viz_dir  # noqa: E402


def main() -> int:
    if len(sys.argv) != 2:
        print(__doc__)
        return 2
    findings = gate_viz_dir(Path(sys.argv[1]))
    if findings:
        for f in findings:
            print(f"FAIL {f}")
        return 1
    print("gate_viz: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
