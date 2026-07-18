"""Build the AIAYN fixture viz pack (R13 slice 1 acceptance artifact).

Writes fixtures/viz/{scaled-dot-product-attention,attention}.html + manifest.json
with hand-written params (slice 1 has no LLM param mapping yet), then runs the gate.

Usage: python scripts/build_viz_fixture.py
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from paper_skill.viz import gate_viz_dir, write_viz  # noqa: E402

OUT = ROOT / "fixtures" / "viz"
PAGES = ROOT / "fixtures" / "pages"


def main() -> int:
    write_viz(
        OUT,
        "scaled-dot-product-attention",
        "attention-heatmap",
        {
            "title": "Scaled dot-product attention, live",
            "tokens": ["the", "animal", "crossed", "it"],
            "queryIndex": 3,
            "biasTarget": 1,
            "seed": 42,
            "prompt": "Before you scrub: which token do you bet “it” attends to most?",
        },
        title="Scaled dot-product attention, live",
        caption="Scrub d_k and toggle √d_k scaling; watch QKᵀ → softmax reweight the values.",
        prompt="Before you scrub: which token do you bet “it” attends to most?",
        page_path=PAGES / "04_sdpa.md",
    )
    write_viz(
        OUT,
        "attention",
        "softmax-temperature",
        {
            "title": "Softmax as a relevance dial",
            "labels": ["the", "animal", "crossed"],
            "logits": [0.8, 2.4, 0.3],
            "betTemperature": 0.5,
            "prompt": "At T=0.5, which key do you bet takes more than half the attention?",
        },
        title="Softmax as a relevance dial",
        caption="Scrub logits and temperature; T→0 sharpens toward argmax, T→∞ flattens.",
        prompt="At T=0.5, which key do you bet takes more than half the attention?",
        # fixture ships only 04_sdpa.md; its Intuition tier ("softmax as a
        # relevance dial") is the evidence this viz illustrates
        page_path=PAGES / "04_sdpa.md",
    )
    findings = gate_viz_dir(OUT)
    if findings:
        for f in findings:
            print(f"FAIL {f}")
        return 1
    print(f"built {OUT} — gate_viz: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
