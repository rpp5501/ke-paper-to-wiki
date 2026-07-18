"""R13 visualize feature — template instantiation, manifest, offline gate.

Design contract: plans/2026-07-17-visualize-and-skillopt-design.md (Deepwiki root).
Templates live in viz_templates/ as self-contained HTML with a {{PARAMS_JSON}}
placeholder. Output is one offline HTML per node plus a viz/manifest.json
sidecar keyed by node id — §5.1 schema is never touched.
"""
from __future__ import annotations

import hashlib
import json
import re
from datetime import date
from pathlib import Path

TEMPLATES_DIR = Path(__file__).parent / "viz_templates"
PLACEHOLDER = "{{PARAMS_JSON}}"
MAX_VIZ_BYTES = 150_000
MANIFEST_NAME = "manifest.json"
REQUIRED_MANIFEST_FIELDS = (
    "kind", "src", "title", "caption", "prompt", "page", "page_sha256",
    "generated",
)

# Network-capable constructs are forbidden; xmlns namespace URIs are fine.
_FORBIDDEN = [
    (re.compile(r"<link\b", re.I), "<link> tag"),
    (re.compile(r"""src\s*=\s*["']\s*https?:""", re.I), "external src="),
    (re.compile(r"""href\s*=\s*["']\s*https?:""", re.I), "external href="),
    (re.compile(r"""url\(\s*["']?https?:""", re.I), "css url(http...)"),
    (re.compile(r"@import\b", re.I), "css @import"),
    (re.compile(r"\bfetch\s*\("), "fetch("),
    (re.compile(r"\bXMLHttpRequest\b"), "XMLHttpRequest"),
    (re.compile(r"\bimport\s*\("), "dynamic import("),
    (re.compile(r"\bWebSocket\s*\("), "WebSocket("),
    (re.compile(r"\bsendBeacon\b"), "sendBeacon"),
    (re.compile(r"\bEventSource\s*\("), "EventSource("),
]

_PARAMS_BLOCK = re.compile(
    r"""<script\s+id=["']params["'][^>]*>(.*?)</script>""", re.S | re.I
)


def escape_params_json(json_text: str) -> str:
    """R12 injection guard: a '</' inside the params JSON could close the
    script element early. '<\\/' is identical JSON but inert in HTML."""
    return json_text.replace("</", "<\\/")


def instantiate_template(template_id: str, params: dict) -> str:
    tpl_path = TEMPLATES_DIR / f"{template_id.replace('-', '_')}.html"
    if not tpl_path.exists():
        raise FileNotFoundError(f"unknown viz template: {template_id}")
    html = tpl_path.read_text(encoding="utf-8")
    if PLACEHOLDER not in html:
        raise ValueError(f"template {template_id} lacks {PLACEHOLDER}")
    payload = escape_params_json(json.dumps(params, ensure_ascii=False))
    return html.replace(PLACEHOLDER, payload)


def page_sha256(page_path: Path) -> str:
    return hashlib.sha256(Path(page_path).read_bytes()).hexdigest()


def load_manifest(out_dir: Path) -> dict:
    p = Path(out_dir) / MANIFEST_NAME
    if p.exists():
        return json.loads(p.read_text(encoding="utf-8"))
    return {}


def write_viz(
    out_dir: Path,
    node_id: str,
    template_id: str,
    params: dict,
    *,
    title: str,
    caption: str,
    prompt: str,
    page_path: Path,
    generated: str | None = None,
) -> dict:
    """Instantiate a template for one node; write HTML + merge manifest entry."""
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    html = instantiate_template(template_id, params)
    src = f"{node_id}.html"
    (out_dir / src).write_text(html, encoding="utf-8")
    entry = {
        "kind": "template",
        "template_id": template_id,
        "src": src,
        "title": title,
        "caption": caption,
        "prompt": prompt,
        "page": Path(page_path).name,
        "page_sha256": page_sha256(page_path),
        "generated": generated or date.today().isoformat(),
    }
    manifest = load_manifest(out_dir)
    manifest[node_id] = entry
    (out_dir / MANIFEST_NAME).write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    return entry


def gate_viz_dir(out_dir: Path) -> list[str]:
    """Offline/injection/size/contract gate. Returns findings; empty = pass."""
    out_dir = Path(out_dir)
    findings: list[str] = []
    manifest_path = out_dir / MANIFEST_NAME
    if not manifest_path.exists():
        return [f"missing {MANIFEST_NAME} in {out_dir}"]
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        return [f"unparseable manifest: {e}"]

    for node_id, entry in manifest.items():
        for field in REQUIRED_MANIFEST_FIELDS:
            if not entry.get(field):
                findings.append(f"{node_id}: manifest missing field '{field}'")
        if entry.get("kind") == "template" and not entry.get("template_id"):
            findings.append(f"{node_id}: template entry missing 'template_id'")
        src = entry.get("src")
        if not src:
            continue
        f = out_dir / src
        if not f.exists():
            findings.append(f"{node_id}: src '{src}' does not exist")
            continue
        raw = f.read_bytes()
        if len(raw) > MAX_VIZ_BYTES:
            findings.append(
                f"{node_id}: {src} is {len(raw)} bytes (cap {MAX_VIZ_BYTES})"
            )
        html = raw.decode("utf-8", errors="replace")
        if PLACEHOLDER in html:
            findings.append(f"{node_id}: {src} has un-instantiated {PLACEHOLDER}")
        for rx, label in _FORBIDDEN:
            if rx.search(html):
                findings.append(f"{node_id}: {src} contains forbidden {label}")
        m = _PARAMS_BLOCK.search(html)
        if m is None:
            findings.append(f"{node_id}: {src} lacks <script id=\"params\"> block")
        elif "</" in m.group(1):
            findings.append(
                f"{node_id}: {src} params block contains raw '</' (injection risk)"
            )
    return findings


# --- CLI: propose (token guard) + build (deterministic) ----------------------
#
# The LLM's only job is authoring a params JSON (see skills/visualize/SKILL.md).
# `propose` never generates anything — it prints a capped candidate list and
# stops. `build` deterministically instantiates templates from the params file
# and runs the gate. Zero tokens are spent unless the owner confirms.

DEFAULT_K = 4
MATH_TIER_MARKERS = ("{#the-math}", "## the math")

TEMPLATE_KEYWORDS: list[tuple[str, tuple[str, ...]]] = [
    ("attention-heatmap", ("attention", "qk", "dot-product")),
    ("softmax-temperature", ("softmax", "temperature", "logit")),
    ("positional-encoding", ("positional", "encoding", "sinusoid")),
    ("gradient-descent-2d", ("gradient", "descent", "loss surface")),
    ("vector-projection", ("projection", "dot product", "cosine")),
]


def suggest_template(node: dict, page_text: str) -> str | None:
    hay = " ".join([node.get("id", ""), node.get("label", ""), page_text]).lower()
    for template_id, keywords in TEMPLATE_KEYWORDS:
        if any(k in hay for k in keywords):
            return template_id
    return None


def propose(plan_graph: dict, pages_dir: Path, k: int = DEFAULT_K) -> list[dict]:
    """Candidates: node has a page on disk containing a The-Math tier.
    Ranked by degree (importance), then level (fundamentals first). Cap k."""
    pages_dir = Path(pages_dir)
    degree: dict[str, int] = {}
    for e in plan_graph.get("edges", []):
        degree[e["src"]] = degree.get(e["src"], 0) + 1
        degree[e["dst"]] = degree.get(e["dst"], 0) + 1
    out = []
    for node in plan_graph.get("nodes", []):
        page = node.get("page")
        if not page or not (pages_dir / page).exists():
            continue
        text = (pages_dir / page).read_text(encoding="utf-8")
        if not any(m in text.lower() for m in MATH_TIER_MARKERS):
            continue
        out.append({
            "id": node["id"],
            "label": node.get("label", node["id"]),
            "level": int(node.get("level", 9)),
            "degree": degree.get(node["id"], 0),
            "page": page,
            "template": suggest_template(node, text),
        })
    out.sort(key=lambda c: (-c["degree"], c["level"], c["id"]))
    return out[:k]


def build_pack(params_by_node: dict, pages_dir: Path, out_dir: Path) -> list[str]:
    """Instantiate every params entry, then gate. Returns gate findings."""
    for node_id, spec in params_by_node.items():
        write_viz(
            Path(out_dir), node_id, spec["template_id"],
            spec.get("params", {}),
            title=spec.get("title", ""),
            caption=spec.get("caption", ""),
            prompt=spec.get("prompt", ""),
            page_path=Path(pages_dir) / spec["page"],
        )
    return gate_viz_dir(Path(out_dir))


def main(argv=None) -> int:
    import argparse
    import sys as _sys

    p = argparse.ArgumentParser(prog="paper_skill.viz")
    sub = p.add_subparsers(dest="cmd", required=True)

    pp = sub.add_parser("propose", help="print capped viz candidates and STOP")
    pp.add_argument("graph")
    pp.add_argument("--pages-dir", required=True)
    pp.add_argument("--k", type=int, default=DEFAULT_K)

    pb = sub.add_parser("build", help="instantiate templates from a params JSON")
    pb.add_argument("--params", required=True)
    pb.add_argument("--pages-dir", required=True)
    pb.add_argument("--out", default="viz")

    a = p.parse_args(argv)
    if a.cmd == "propose":
        graph = json.loads(Path(a.graph).read_text(encoding="utf-8"))
        candidates = propose(graph, Path(a.pages_dir), k=a.k)
        if not candidates:
            print("no viz candidates: no node has a page with a The Math tier")
            return 0
        print(f"viz proposal (cap {a.k}) — PROPOSAL ONLY, nothing generated:")
        for c in candidates:
            tpl = c["template"] or "bespoke (needs explicit owner request)"
            print(f"  {c['id']}  level={c['level']} degree={c['degree']}"
                  f"  page={c['page']}  template={tpl}")
        print("next: confirm with the owner, author a params JSON "
              "(skills/visualize/SKILL.md), then run:\n"
              f"  python -m paper_skill.viz build --params viz_params.json "
              f"--pages-dir {a.pages_dir} --out viz")
        return 0

    try:
        params_by_node = json.loads(Path(a.params).read_text(encoding="utf-8"))
        findings = build_pack(params_by_node, Path(a.pages_dir), Path(a.out))
    except (FileNotFoundError, KeyError, ValueError) as e:
        print(f"FAIL {e}", file=_sys.stderr)
        return 1
    if findings:
        for f in findings:
            print(f"FAIL {f}")
        return 1
    print(f"built {a.out} ({len(params_by_node)} viz) — gate_viz: PASS")
    return 0


if __name__ == "__main__":  # python -m paper_skill.viz
    raise SystemExit(main())
