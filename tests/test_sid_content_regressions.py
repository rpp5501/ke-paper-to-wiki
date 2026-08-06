import json
from collections import Counter
from pathlib import Path


PAGES = Path(__file__).parents[1] / "artifacts" / "p1306.1043-live" / "pages"
QUIZ = PAGES.parent / "quiz.json"


def _page(name: str) -> str:
    return (PAGES / name).read_text(encoding="utf-8")


def test_symmetrized_sid_is_the_arithmetic_mean() -> None:
    page = _page("30_symmetrization.md")
    overview = _page("11_structural-intervention-distance.md")

    assert r"\\frac{\\mathrm{SID}(G,H) + \\mathrm{SID}(H,G)}{2}" in page
    assert r"\big(\mathrm{SID}(G,H) + \mathrm{SID}(H,G)\big)/2" in overview
    assert "min-style" not in page


def test_single_intervention_pair_count_is_quadratic() -> None:
    page = _page("25_multiple-interventions-extension.md")

    assert "p(p-1)" in page
    assert "quadratic" in page.lower()
    assert "linear in p" not in page


def test_worst_case_and_empirical_scaling_are_reconciled() -> None:
    implementation = _page("09_sid-implementation.md").lower()
    scalability = _page("22_sid-scalability.md").lower()

    assert "worst-case" in implementation
    assert "empirical" in implementation
    assert "do not contradict" in implementation
    assert "worst-case" in scalability
    assert "empirical" in scalability
    assert "do not contradict" in scalability


def test_running_four_node_dag_persists_across_all_five_chapters() -> None:
    chapter_pages = (
        "07_graph-comparison-problem.md",
        "10_intervention-distributions.md",
        "11_structural-intervention-distance.md",
        "09_sid-implementation.md",
        "29_proof-sidsuper.md",
    )

    for name in chapter_pages:
        page = _page(name)
        assert "A\\to B" in page
        assert "A\\to C" in page
        assert "B\\to D" in page
        assert "C\\to D" in page
        assert "B\\to C" in page

    sid_page = _page("11_structural-intervention-distance.md")
    assert r"\mathrm{SID}(G,H)=0" in sid_page
    assert r"\mathrm{SID}(H,G)=2" in sid_page
    assert "$(C,B)$" in sid_page
    assert "$(C,D)$" in sid_page


def test_missing_extracted_percentage_is_disclosed_not_invented() -> None:
    page = _page("23_alternative-adjustment-sets.md")

    assert "[X]%" not in page
    assert "exact equality percentage is missing from the extracted source" in page


def test_mastery_is_reachable_from_two_distinct_application_checks() -> None:
    quiz = json.loads(QUIZ.read_text(encoding="utf-8"))
    applications = Counter(
        item["nodeId"] for item in quiz["items"]
        if item.get("kind") == "application"
    )

    assert applications["structural-intervention-distance"] >= 2
