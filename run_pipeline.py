"""Run P1-P6 end to end for one or more arXiv papers.

The pipeline's stages are individually resumable (p3_done/, p4_done/), and
every stage writes its output to the artifact dir, so re-running this script
picks up where it stopped rather than re-spending on finished work.

The P2 checkpoint is normally a human reading concept_toc.yaml before any
token spend. Running unattended, this holds the same gate mechanically: the
toc is approved only if the graph passes graph_quality_findings and is not a
table-of-contents fallback, and the approval note records that it was
automatic so the provenance is not misread later.
"""
import argparse, json, sys, time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT.parent / "research-mcp" / "src"))

from paper_skill.concepts import (
    extract_concepts, graph_quality, graph_quality_findings, is_toc_graph,
    require_ok,
)
from paper_skill.llm_spawn import claude_spawn
from paper_skill.p3_research import run_research
from paper_skill.p4_write import annotate_graph, write_pages
from paper_skill.p5_lint import lint_page
from paper_skill.p6_explorer import build_explorer
from paper_skill.paper2pack import build_pack
from paper_skill.toc import write_toc

P2_ATTEMPTS = 3

PAPERS = {
    "ddim": "arXiv:2010.02502",
    "chain-of-thought": "arXiv:2201.11903",
    "resnet": "arXiv:1512.03385",
    # Safety/interpretability set, in the owner's stated priority order.
    # Tier 1 -- highest strategic alignment
    "lottery-ticket": "arXiv:1803.03635",
    "agentic-misalignment": "arXiv:2510.05179",
    "ai-control": "arXiv:2312.06942",
    # Tier 2 -- representation geometry
    "refusal-direction": "arXiv:2406.11717",
    "representation-engineering": "arXiv:2310.01405",
    "linear-representation": "arXiv:2311.03658",
    "geometry-of-truth": "arXiv:2310.06824",
    # Tier 3 -- adjacent safety
    "sleeper-agents": "arXiv:2401.05566",
    "unfaithful-cot": "arXiv:2305.04388",
    # Tier 4 -- jailbreaks and benchmarks
    "autodan": "arXiv:2310.04451",
    "universal-adversarial": "arXiv:2307.15043",
    "pair-jailbreak": "arXiv:2310.08419",
    "harmbench": "arXiv:2402.04249",
}

TIERED = ["lottery-ticket", "agentic-misalignment", "ai-control",
          "refusal-direction", "representation-engineering",
          "linear-representation", "geometry-of-truth",
          "sleeper-agents", "unfaithful-cot",
          "autodan", "universal-adversarial", "pair-jailbreak", "harmbench"]


def log(*a):
    print(f"[{time.strftime('%H:%M:%S')}]", *a, flush=True)


def stage_pack(art: Path, target: str) -> dict:
    out = art / "pack.json"
    if out.is_file():
        log("P1 cached")
        return json.loads(out.read_text(encoding="utf-8"))
    pack = build_pack(target, assets_dir=art / "assets")
    if "sections" not in pack:
        raise SystemExit(f"P1 failed for {target}: {pack}")
    out.write_text(json.dumps(pack, ensure_ascii=False, indent=1),
                   encoding="utf-8")
    log(f'P1 ok: {pack["extraction"]["path"]} rung, {len(pack["sections"])} '
        f'sections, {len(pack["equations"])} eq, {len(pack.get("tables", []))} '
        f'tables, {len(pack.get("figures", []))} figures, '
        f'{len(pack.get("references", []))} refs')
    return pack


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("papers", nargs="*", default=list(PAPERS))
    ap.add_argument("--artifacts", default=str(ROOT / "artifacts"))
    a = ap.parse_args(argv)

    for name in (a.papers or list(PAPERS)):
        target = PAPERS[name]
        art = Path(a.artifacts) / f"{name}-live"
        art.mkdir(parents=True, exist_ok=True)
        log(f"=== {name} ({target}) -> {art} ===")
        # One paper's failure must not cost the others their run. The first
        # version raised SystemExit out of the loop, so chain-of-thought's
        # held quality gate also cancelled resnet, which had nothing wrong
        # with it.
        try:
            run_one(name, target, art)
        except Exception as exc:
            log(f"!! {name} aborted: {type(exc).__name__}: {exc}")


def run_one(name: str, target: str, art: Path):
    pack = stage_pack(art, target)

    graph_p, toc_p = art / "concept_graph.json", art / "concept_toc.yaml"
    if graph_p.is_file() and toc_p.is_file():
        log("P2 cached")
        graph = json.loads(graph_p.read_text(encoding="utf-8"))
    else:
        # Concept extraction is one stochastic LLM call, so a graph that comes
        # back flat is worth re-asking before giving up on the paper -- but the
        # gate still has the last word, because spending P4 on a flat graph is
        # the expensive mistake it exists to prevent.
        graph = toc = findings = None
        for attempt in range(P2_ATTEMPTS):
            result = require_ok(extract_concepts(pack, claude_spawn))
            graph, toc = result["graph"], result["toc"]
            findings = graph_quality_findings(graph)
            if is_toc_graph(graph):
                findings.append("graph looks like the paper's table of contents")
            m = graph_quality(graph)
            log(f'P2 attempt {attempt + 1}: {m["node_count"]} nodes, '
                f'{m["edge_count"]} edges, part-of '
                f'{m["part_of_coverage"]:.0%}, orphans {m["orphan_ratio"]:.0%}, '
                f'research flags {sum(1 for r in toc if r.get("research"))}'
                + (f" -- {findings}" if findings else ""))
            if not findings:
                break
        if findings:
            raise SystemExit(f"P2 gate held for {name} after "
                             f"{P2_ATTEMPTS} attempts: {findings}")
        graph_p.write_text(json.dumps(graph, ensure_ascii=False, indent=1),
                           encoding="utf-8")
        write_toc(toc, toc_p)
        doc = toc_p.read_text(encoding="utf-8")
        toc_p.write_text(doc.replace(
            "approved: false",
            "approved: true", 1).replace(
            "note: 'review:",
            f"note: 'AUTO-APPROVED by run_pipeline.py -- {m['node_count']} "
            f"nodes, no quality findings. original: review:", 1),
            encoding="utf-8")
        log("P2 auto-approved")

    home = art / "research_home"
    r3 = run_research(toc_p, graph, home=home, workdir=art)
    log(f'P3 done={len(r3["done"])} failed={len(r3["failed"])} '
        f'skipped={len(r3["skipped"])} {r3["failed"] or ""}')

    from paper_skill.toc import load_approved_toc
    rows = load_approved_toc(toc_p)["rows"]
    r4 = write_pages(pack, graph, rows, home=home, out_dir=art / "pages",
                     workdir=art)
    log(f'P4 done={len(r4["done"])} failed={len(r4["failed"])} '
        f'skipped={len(r4["skipped"])} {r4["failed"] or ""}')
    graph = annotate_graph(graph, r4["pages"])
    graph_p.write_text(json.dumps(graph, ensure_ascii=False, indent=1),
                       encoding="utf-8")

    lint = {}
    for page in sorted((art / "pages").glob("*.md")):
        probs = lint_page(page.read_text(encoding="utf-8"), pack)
        if probs:
            lint[page.name] = probs
    log(f"P5 {len(lint)} page(s) with findings"
        + (f": {json.dumps(lint, indent=1)[:1500]}" if lint else ""))
    (art / "p5_report.json").write_text(json.dumps(lint, indent=1),
                                        encoding="utf-8")

    try:
        r6 = build_explorer(pack, graph, art / "pages",
                            art / f"{name}_explorer.html")
        log(f"P6 {r6}")
    except Exception as exc:
        log(f"P6 failed: {exc}")


if __name__ == "__main__":
    main()
