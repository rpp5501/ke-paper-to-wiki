"""The dag-adjustment template: routing, and that its verdict is computed.

The catalog was five transformer-shaped templates, so a causal-inference or
Bayes-net paper had nothing to instantiate and fell through to the bespoke
path. These tests pin the routing that fixes that, and — more importantly —
that the explorable works the adjustment criterion out rather than displaying
a canned answer, which GUIDELINES.md's faithfulness rule forbids.
"""
import json
import shutil
import subprocess
import textwrap
from pathlib import Path

import pytest

from paper_skill.viz import TEMPLATES_DIR, suggest_template

TEMPLATE = TEMPLATES_DIR / "dag_adjustment.html"

# G is the running four-node example; H adds the single edge B -> C.
G_EDGES = [["A", "B"], ["A", "C"], ["B", "D"], ["C", "D"]]
H_EDGES = G_EDGES + [["B", "C"]]


def test_graph_vocabulary_routes_to_the_dag_template():
    node = {"id": "equivalent-formulation", "label": "An Equivalent Formulation"}
    page = "the estimated parent set is a valid adjustment set for the pair"

    assert suggest_template(node, page) == "dag-adjustment"


def test_dag_template_does_not_steal_transformer_pages():
    node = {"id": "scaled-dot-product-attention", "label": "Scaled Dot-Product Attention"}
    page = "softmax over QK^T scaled by sqrt(d_k), the dot-product attention"

    assert suggest_template(node, page) == "attention-heatmap"


def _verdicts():
    """Run the template's own graph code over the paper's own examples."""
    html = TEMPLATE.read_text(encoding="utf-8")
    algorithm = html.split("/* ---- graph primitives")[1].split("/* ---- rendering")[0]
    algorithm = algorithm.split("\n", 1)[1]

    harness = textwrap.dedent("""
        const [nodes, rawEdges, SRC, TGT, z] = JSON.parse(process.argv[1]);
        const NODES = nodes, EDGES = rawEdges.map(e => ({from: e[0], to: e[1]}));
        __ALGORITHM__
        const r = evaluate(new Set(z));
        console.log(JSON.stringify({
            valid: r.valid,
            open: r.openNonCausal.map(p => p.path.join("-")),
        }));
    """).replace("__ALGORITHM__", algorithm)

    def run(edges, source, target, adjustment):
        payload = json.dumps([[], edges, source, target, adjustment])
        done = subprocess.run(
            ["node", "-e", harness, "--", payload],
            capture_output=True, text=True, timeout=30)
        assert done.returncode == 0, done.stderr
        return json.loads(done.stdout)

    return run


@pytest.mark.skipif(shutil.which("node") is None, reason="node not installed")
def test_verdicts_match_what_the_pages_claim():
    run = _verdicts()

    # alternative-adjustment-sets: {A} is a valid smaller set for C -> D in G.
    assert run(G_EDGES, "C", "D", ["A"])["valid"] is True
    # equivalent-formulation: in H, {A} leaves C <- B -> D open for (C, D).
    rejected = run(H_EDGES, "C", "D", ["A"])
    assert rejected["valid"] is False
    assert "C-B-D" in rejected["open"]
    # The parent set of C in H closes it again.
    assert run(H_EDGES, "C", "D", ["A", "B"])["valid"] is True


@pytest.mark.skipif(shutil.which("node") is None, reason="node not installed")
def test_empty_set_leaves_the_confounding_path_open():
    """Adjusting for nothing must not read as valid -- a canned 'valid' would
    pass the three cases above by accident."""
    result = _verdicts()(G_EDGES, "C", "D", [])

    assert result["valid"] is False
    assert "C-A-B-D" in result["open"]


def test_manifest_prompt_reaches_the_bet(tmp_path):
    """The required `prompt` field is the place-your-bets question, but every
    template reads it from params. Authoring only the documented field used to
    leave the overlay showing a generic placeholder."""
    from paper_skill.viz import write_viz

    page = tmp_path / "16_equivalent-formulation.md"
    page.write_text("# x\n## The Math {#the-math}\n", encoding="utf-8")
    entry = write_viz(
        tmp_path / "viz", "equivalent-formulation", "dag-adjustment",
        {"source": "C", "target": "D", "edges": H_EDGES},
        title="t", caption="c", prompt="Valid for the pair (C, D)?",
        page_path=page)

    html = (tmp_path / "viz" / entry["src"]).read_text(encoding="utf-8")
    assert "Valid for the pair (C, D)?" in html


def test_params_prompt_still_wins(tmp_path):
    from paper_skill.viz import write_viz

    page = tmp_path / "p.md"
    page.write_text("# x\n", encoding="utf-8")
    entry = write_viz(
        tmp_path / "viz", "n", "dag-adjustment",
        {"prompt": "authored in params", "edges": G_EDGES},
        title="t", caption="c", prompt="from the manifest", page_path=page)

    html = (tmp_path / "viz" / entry["src"]).read_text(encoding="utf-8")
    assert "authored in params" in html
    assert "from the manifest" not in html
