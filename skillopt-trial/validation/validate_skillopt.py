"""Deterministic offline gate for the paper-tutor SkillOpt trial.

The checker validates files produced by an external scorer. It never invokes
SkillOpt, a model, or an execution backend.
"""

from __future__ import annotations

import argparse
import difflib
import hashlib
import json
import re
import sys
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any


SCHEMA_VERSION = 2
EXPECTED_TASK_MANIFEST_SHA256 = (
    "56e7dcbece4c91b3b3a6296a91b610345afb4e83ff663cf9df465405ec3aaa43"
)
EXPECTED_TARGET_SKILL = "skills/write-paper-tutor/SKILL.md"
RUBRIC_WEIGHTS = {
    "factual_evidence_accuracy": 30,
    "conceptual_depth": 20,
    "prerequisite_clarity": 15,
    "worked_examples": 15,
    "scanability": 10,
    "checkpoint_quality": 10,
}
RUBRIC_TABLE_DIMENSIONS = {
    "Factual and evidence accuracy": "factual_evidence_accuracy",
    "Conceptual depth": "conceptual_depth",
    "Prerequisite clarity": "prerequisite_clarity",
    "Worked examples": "worked_examples",
    "Scanability": "scanability",
    "Checkpoint quality": "checkpoint_quality",
}
AUTOMATIC_REJECTION_FLAGS = (
    "invented_formula",
    "altered_formula",
    "nonexistent_source",
    "fabricated_implementation_bridge",
    "unsupported_result",
    "concealed_missing_evidence",
    "unresolved_critical_reference",
)
DETERMINISTIC_GATES = (
    "correctness",
    "equation",
    "evidence_citation",
    "schema",
    "component",
    "accessibility",
)
MINIMUM_AGGREGATE_IMPROVEMENT = 3
MAXIMUM_PAPER_REGRESSION = 2
STAGE_SPLITS = {
    "tuning": "train",
    "selection": "selection",
    "final-test": "final-test",
}
PAPER_ARTIFACTS = {
    "sid": "artifacts/p1306.1043-live",
    "transformer": "artifacts/aiayn-live",
    "backdoor": "artifacts/p2205.06900-live",
    "privacy": "artifacts/p2504.04033-live",
}
SPLIT_PAPERS = {
    "train": {"sid", "transformer"},
    "selection": {"backdoor"},
    "final-test": {"privacy"},
}
LEDGER_STAGES = ("tuning", "selection", "final-test", "human-review")
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


@dataclass(frozen=True)
class AcceptanceDecision:
    accepted: bool
    aggregate_baseline: float | None
    aggregate_candidate: float | None
    aggregate_improvement: float | None
    paper_deltas: dict[str, float]
    reasons: list[str]
    validation_errors: list[str]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def load_json(path: str | Path) -> dict[str, Any]:
    with Path(path).open(encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def _canonical_json(value: Any) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")


def _json_sha256(value: Any) -> str:
    return hashlib.sha256(_canonical_json(value)).hexdigest()


def _file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def _default_trial_root() -> Path:
    return Path(__file__).resolve().parent.parent


def _default_project_root() -> Path:
    return _default_trial_root().parent


def _exact_keys(value: Any, expected: set[str], label: str, errors: list[str]) -> bool:
    if not isinstance(value, dict):
        errors.append(f"{label} must be an object")
        return False
    actual = set(value)
    if actual != expected:
        errors.append(
            f"{label} fields must be exactly {sorted(expected)}; got {sorted(actual)}"
        )
        return False
    return True


def _task_index(
    tasks_document: dict[str, Any], project_root: str | Path | None = None
) -> tuple[dict[str, dict[str, Any]], list[str]]:
    errors: list[str] = []
    tasks = tasks_document.get("tasks")
    if not isinstance(tasks, list) or not tasks:
        return {}, ["tasks.json requires a non-empty 'tasks' array"]

    root = Path(project_root) if project_root is not None else _default_project_root()
    root = root.resolve()
    index: dict[str, dict[str, Any]] = {}
    for position, task in enumerate(tasks):
        if not isinstance(task, dict):
            errors.append(f"task {position} must be an object")
            continue
        task_id = task.get("id")
        split = task.get("split")
        paper = task.get("paper")
        artifact_dir = task.get("artifactDir")
        if not isinstance(task_id, str) or not task_id:
            errors.append(f"task {position} needs a non-empty id")
            continue
        if task_id in index:
            errors.append(f"duplicate task id: {task_id}")
            continue
        index[task_id] = task
        if split not in SPLIT_PAPERS:
            errors.append(f"task {task_id} has an unknown split: {split!r}")
            continue
        if paper not in SPLIT_PAPERS[split]:
            errors.append(
                f"task {task_id} puts paper {paper!r} in {split!r}; "
                f"allowed papers are {sorted(SPLIT_PAPERS[split])}"
            )
        expected_artifact = PAPER_ARTIFACTS.get(paper)
        if artifact_dir != expected_artifact:
            errors.append(
                f"task {task_id} artifactDir must be {expected_artifact!r} for paper "
                f"{paper!r}, not {artifact_dir!r}"
            )
        elif isinstance(artifact_dir, str):
            artifact_path = (root / artifact_dir).resolve()
            if not artifact_path.is_relative_to(root) or not artifact_path.is_dir():
                errors.append(
                    f"task {task_id} artifactDir does not resolve to a project directory: "
                    f"{artifact_dir}"
                )
        for field in ("conceptId", "prompt"):
            if not isinstance(task.get(field), str) or not task[field].strip():
                errors.append(f"task {task_id} needs a non-empty {field}")
    return index, errors


def validate_task_splits(
    tasks_document: dict[str, Any], project_root: str | Path | None = None
) -> list[str]:
    index, errors = _task_index(tasks_document, project_root)
    if not index:
        return errors
    by_split: dict[str, set[str]] = {split: set() for split in SPLIT_PAPERS}
    for task in index.values():
        if task.get("split") in by_split:
            by_split[task["split"]].add(task.get("paper"))
    for split, required_papers in SPLIT_PAPERS.items():
        if by_split[split] != required_papers:
            errors.append(
                f"{split} split must contain exactly {sorted(required_papers)}, "
                f"not {sorted(by_split[split])}"
            )
    return errors


def _machine_policy(rubric_path: str | Path) -> dict[str, Any]:
    text = Path(rubric_path).read_text(encoding="utf-8")
    match = re.search(r"```json\s*(\{.*?\})\s*```", text, flags=re.DOTALL)
    if not match:
        raise ValueError("rubric.md needs one machine-readable JSON policy block")
    value = json.loads(match.group(1))
    if not isinstance(value, dict):
        raise ValueError("machine-readable rubric policy must be a JSON object")
    return value


def _human_rubric_weights(rubric_path: str | Path) -> dict[str, int]:
    text = Path(rubric_path).read_text(encoding="utf-8")
    weights: dict[str, int] = {}
    for label, dimension in RUBRIC_TABLE_DIMENSIONS.items():
        match = re.search(
            rf"^\|\s*{re.escape(label)}\s*\|\s*(\d+)%\s*\|",
            text,
            flags=re.MULTILINE,
        )
        if match:
            weights[dimension] = int(match.group(1))
    return weights


def validate_policy(
    tasks_document: dict[str, Any],
    rubric_path: str | Path,
    project_root: str | Path | None = None,
) -> list[str]:
    errors = validate_task_splits(tasks_document, project_root)
    if _json_sha256(tasks_document) != EXPECTED_TASK_MANIFEST_SHA256:
        errors.append(
            "task manifest hash does not match the locked IDs, prompts, artifactDir, "
            "conceptId, paper/split mapping, and metadata"
        )
    meta = tasks_document.get("meta")
    if not isinstance(meta, dict) or meta.get("targetSkill") != EXPECTED_TARGET_SKILL:
        errors.append(f"task manifest targetSkill must be {EXPECTED_TARGET_SKILL!r}")
    try:
        policy = _machine_policy(rubric_path)
        human_weights = _human_rubric_weights(rubric_path)
    except (OSError, ValueError, json.JSONDecodeError) as error:
        return errors + [str(error)]

    expected_policy = {
        "weights": RUBRIC_WEIGHTS,
        "automaticRejectionFlags": list(AUTOMATIC_REJECTION_FLAGS),
        "minimumAggregateImprovement": MINIMUM_AGGREGATE_IMPROVEMENT,
        "maximumPaperRegression": MAXIMUM_PAPER_REGRESSION,
        "deterministicGates": list(DETERMINISTIC_GATES),
        "humanReviewRequired": True,
        "finalTestExcludedFromTuning": True,
    }
    if human_weights != RUBRIC_WEIGHTS:
        errors.append("human-readable rubric weights must exactly match the locked policy")
    if policy != expected_policy:
        errors.append("machine-readable rubric policy must exactly match the locked policy")
    return errors


def _validate_sha(value: Any, label: str, errors: list[str]) -> bool:
    if not isinstance(value, str) or not SHA256_RE.fullmatch(value):
        errors.append(f"{label} must be a lowercase SHA-256 hex digest")
        return False
    return True


def _validate_file_ref(
    value: Any, label: str, trial_root: str | Path, errors: list[str]
) -> Path | None:
    if not _exact_keys(value, {"path", "sha256"}, label, errors):
        return None
    path_text = value["path"]
    if not isinstance(path_text, str) or not path_text:
        errors.append(f"{label}.path must be a non-empty relative path")
        return None
    if not _validate_sha(value["sha256"], f"{label}.sha256", errors):
        return None
    root = Path(trial_root).resolve()
    supplied = Path(path_text)
    if supplied.is_absolute():
        errors.append(f"{label}.path must be relative to the trial root")
        return None
    resolved = (root / supplied).resolve()
    if not resolved.is_relative_to(root):
        errors.append(f"{label}.path escapes the trial root")
        return None
    if not resolved.is_file():
        errors.append(f"{label}.path does not exist as a file: {path_text}")
        return None
    if resolved.stat().st_size == 0:
        errors.append(f"{label}.path must not be empty: {path_text}")
        return None
    actual = _file_sha256(resolved)
    if actual != value["sha256"]:
        errors.append(
            f"{label} hash mismatch for {path_text}: expected {value['sha256']}, got {actual}"
        )
    return resolved


def validate_report(
    tasks_document: dict[str, Any],
    report: dict[str, Any],
    trial_root: str | Path | None = None,
) -> list[str]:
    root = Path(trial_root) if trial_root is not None else _default_trial_root()
    index, errors = _task_index(tasks_document, root.parent)
    if not index:
        return errors
    if not _exact_keys(
        report,
        {
            "schemaVersion",
            "reportKind",
            "stage",
            "skillArtifact",
            "rows",
            "deterministicGates",
        },
        "report",
        errors,
    ):
        return errors
    if report["schemaVersion"] != SCHEMA_VERSION:
        errors.append(f"schemaVersion must be {SCHEMA_VERSION}")
    if report["reportKind"] not in {"baseline", "candidate"}:
        errors.append("reportKind must be 'baseline' or 'candidate'")
    _validate_file_ref(report["skillArtifact"], "skillArtifact", root, errors)

    stage = report["stage"]
    if stage not in STAGE_SPLITS:
        errors.append("stage must be 'tuning', 'selection', or 'final-test'")
        return errors
    expected_split = STAGE_SPLITS[stage]
    expected_ids = {
        task_id for task_id, task in index.items() if task.get("split") == expected_split
    }
    rows = report["rows"]
    if not isinstance(rows, list):
        errors.append("rows must be an array")
        rows = []
    actual_ids: set[str] = set()
    for position, row in enumerate(rows):
        label = f"row {position}"
        if not _exact_keys(
            row,
            {"taskId", "scores", "automaticRejectionFlags", "rawOutput"},
            label,
            errors,
        ):
            continue
        task_id = row["taskId"]
        if not isinstance(task_id, str) or task_id not in index:
            errors.append(f"{label} has an unknown taskId: {task_id!r}")
            continue
        if task_id in actual_ids:
            errors.append(f"duplicate result row for taskId: {task_id}")
            continue
        actual_ids.add(task_id)
        task_split = index[task_id].get("split")
        if task_split == "final-test" and stage != "final-test":
            errors.append(f"final-test task {task_id} cannot be used in {stage} input")
        elif task_split != expected_split:
            errors.append(f"task {task_id} belongs to {task_split}, not the {stage} stage")

        scores = row["scores"]
        if _exact_keys(scores, set(RUBRIC_WEIGHTS), f"{label}.scores", errors):
            for dimension, score in scores.items():
                if isinstance(score, bool) or not isinstance(score, (int, float)):
                    errors.append(f"{label}.scores.{dimension} must be a number from 0 to 100")
                elif not 0 <= score <= 100:
                    errors.append(f"{label}.scores.{dimension} must be from 0 to 100")
        flags = row["automaticRejectionFlags"]
        if not isinstance(flags, list) or not all(isinstance(flag, str) for flag in flags):
            errors.append(f"{label}.automaticRejectionFlags must be a string array")
        elif len(flags) != len(set(flags)):
            errors.append(f"{label}.automaticRejectionFlags must not repeat a flag")
        else:
            unknown = sorted(set(flags) - set(AUTOMATIC_REJECTION_FLAGS))
            if unknown:
                errors.append(f"{label} has unknown automatic rejection flags: {unknown}")
        _validate_file_ref(row["rawOutput"], f"{label}.rawOutput", root, errors)

    if actual_ids != expected_ids:
        errors.append(
            f"{stage} report must contain exactly {sorted(expected_ids)}, "
            f"not {sorted(actual_ids)}"
        )

    gates = report["deterministicGates"]
    if _exact_keys(gates, set(DETERMINISTIC_GATES), "deterministicGates", errors):
        for gate, result in gates.items():
            label = f"deterministicGates.{gate}"
            if not _exact_keys(result, {"green", "evidence"}, label, errors):
                continue
            if not isinstance(result["green"], bool):
                errors.append(f"{label}.green must be a boolean")
            _validate_file_ref(result["evidence"], f"{label}.evidence", root, errors)
    return errors


def _parse_timestamp(value: Any, label: str, errors: list[str]) -> datetime | None:
    if not isinstance(value, str):
        errors.append(f"{label} must be an ISO-8601 timestamp with timezone")
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        errors.append(f"{label} must be an ISO-8601 timestamp with timezone")
        return None
    if parsed.tzinfo is None:
        errors.append(f"{label} must include a timezone")
        return None
    return parsed


def _event_hash(event: dict[str, Any]) -> str:
    return _json_sha256({key: value for key, value in event.items() if key != "eventSha256"})


def _validate_report_binding(
    value: Any, label: str, trial_root: Path, errors: list[str]
) -> tuple[str | None, Path | None]:
    if not _exact_keys(value, {"role", "path", "sha256"}, label, errors):
        return None, None
    role = value["role"]
    if not isinstance(role, str):
        errors.append(f"{label}.role must be a string")
        return None, None
    if role not in {"baseline", "candidate"}:
        errors.append(f"{label}.role must be 'baseline' or 'candidate'")
    path = _validate_file_ref(
        {"path": value["path"], "sha256": value["sha256"]}, label, trial_root, errors
    )
    return role, path


def _normalized_unified_diff(baseline_path: Path, candidate_path: Path) -> str:
    def normalized_lines(path: Path) -> list[str]:
        text = path.read_text(encoding="utf-8").replace("\r\n", "\n").replace("\r", "\n")
        return text.splitlines()

    lines = list(
        difflib.unified_diff(
            normalized_lines(baseline_path),
            normalized_lines(candidate_path),
            fromfile="baseline/skills/write-paper-tutor/SKILL.md",
            tofile="candidate/skills/write-paper-tutor/SKILL.md",
            lineterm="",
        )
    )
    return "\n".join(lines) + ("\n" if lines else "")


def validate_run_record(
    tasks_document: dict[str, Any],
    baseline: dict[str, Any],
    candidate: dict[str, Any],
    record: dict[str, Any],
    trial_root: str | Path | None = None,
    baseline_path: str | Path | None = None,
    candidate_path: str | Path | None = None,
) -> list[str]:
    root = Path(trial_root) if trial_root is not None else _default_trial_root()
    errors: list[str] = []
    if not _exact_keys(
        record,
        {
            "schemaVersion",
            "taskManifestSha256",
            "baselineSkillSha256",
            "candidateSkillSha256",
            "history",
            "review",
        },
        "runRecord",
        errors,
    ):
        return errors
    if record["schemaVersion"] != SCHEMA_VERSION:
        errors.append(f"runRecord.schemaVersion must be {SCHEMA_VERSION}")
    if record["taskManifestSha256"] != EXPECTED_TASK_MANIFEST_SHA256:
        errors.append("runRecord task manifest hash does not match the locked manifest")
    for field in ("baselineSkillSha256", "candidateSkillSha256"):
        _validate_sha(record[field], f"runRecord.{field}", errors)
    if isinstance(baseline.get("skillArtifact"), dict):
        if record["baselineSkillSha256"] != baseline["skillArtifact"].get("sha256"):
            errors.append("runRecord baselineSkillSha256 does not match baseline report")
    if isinstance(candidate.get("skillArtifact"), dict):
        if record["candidateSkillSha256"] != candidate["skillArtifact"].get("sha256"):
            errors.append("runRecord candidateSkillSha256 does not match candidate report")

    history = record["history"]
    if not isinstance(history, list):
        errors.append("runRecord.history must be an array")
        history = []
    stages = [event.get("stage") if isinstance(event, dict) else None for event in history]
    if stages != list(LEDGER_STAGES):
        errors.append(
            "runRecord final-test must occur after selection and before human-review; "
            f"required stage order is {list(LEDGER_STAGES)}"
        )
    previous_hash = "0" * 64
    previous_time: datetime | None = None
    bound_reports: dict[tuple[str, str], tuple[Path, dict[str, Any]]] = {}
    for position, event in enumerate(history):
        label = f"runRecord.history[{position}]"
        if not _exact_keys(
            event,
            {
                "stage",
                "timestamp",
                "skillSha256",
                "reports",
                "previousEventSha256",
                "eventSha256",
            },
            label,
            errors,
        ):
            continue
        if event["previousEventSha256"] != previous_hash:
            errors.append(f"{label}.previousEventSha256 breaks the ledger hash chain")
        _validate_sha(event["eventSha256"], f"{label}.eventSha256", errors)
        actual_hash = _event_hash(event)
        if event["eventSha256"] != actual_hash:
            errors.append(f"{label}.eventSha256 does not match event content")
        previous_hash = event["eventSha256"]
        timestamp = _parse_timestamp(event["timestamp"], f"{label}.timestamp", errors)
        if timestamp is not None and previous_time is not None and timestamp <= previous_time:
            errors.append(f"{label}.timestamp must be later than the previous event")
        if timestamp is not None:
            previous_time = timestamp
        if event["skillSha256"] != record["candidateSkillSha256"]:
            errors.append(f"{label}.skillSha256 must match the selected candidate")
        stage = event["stage"]
        if not isinstance(stage, str):
            errors.append(f"{label}.stage must be a string")
            stage_name: str | None = None
        elif stage not in LEDGER_STAGES:
            errors.append(f"{label}.stage must be one of {list(LEDGER_STAGES)}")
            stage_name = None
        else:
            stage_name = stage
        reports = event["reports"]
        expected_roles = {
            "tuning": ["candidate"],
            "selection": ["baseline", "candidate"],
            "final-test": ["candidate"],
            "human-review": [],
        }.get(stage_name, [])
        if not isinstance(reports, list):
            errors.append(f"{label}.reports must be an array")
            continue
        actual_roles = [item.get("role") if isinstance(item, dict) else None for item in reports]
        if actual_roles != expected_roles:
            errors.append(f"{label}.reports roles must be exactly {expected_roles}")
        for report_position, binding in enumerate(reports):
            binding_label = f"{label}.reports[{report_position}]"
            role, report_path = _validate_report_binding(binding, binding_label, root, errors)
            if role is None or report_path is None:
                continue
            try:
                report_document = load_json(report_path)
            except (OSError, ValueError, json.JSONDecodeError) as error:
                errors.append(f"{binding_label} could not be read: {error}")
                continue
            errors.extend(
                f"{binding_label}: {error}"
                for error in validate_report(tasks_document, report_document, root)
            )
            if stage_name is None:
                continue
            if report_document.get("stage") != stage_name:
                errors.append(f"{binding_label} stage must match ledger event {stage_name!r}")
            if report_document.get("reportKind") != role:
                errors.append(f"{binding_label} reportKind must match role {role!r}")
            skill = report_document.get("skillArtifact")
            expected_skill = (
                record["baselineSkillSha256"]
                if role == "baseline"
                else record["candidateSkillSha256"]
            )
            if not isinstance(skill, dict) or skill.get("sha256") != expected_skill:
                errors.append(f"{binding_label} evaluates the wrong skill hash")
            bound_reports[(stage_name, role)] = (report_path, report_document)

    for role, supplied, supplied_path in (
        ("baseline", baseline, baseline_path),
        ("candidate", candidate, candidate_path),
    ):
        bound = bound_reports.get(("selection", role))
        if bound is None:
            errors.append(f"selection {role} report is missing from the ledger")
            continue
        bound_path, bound_document = bound
        if bound_document != supplied:
            errors.append(f"selection {role} report content does not match the ledger")
        if supplied_path is not None and Path(supplied_path).resolve() != bound_path.resolve():
            errors.append(f"selection {role} report path does not match the ledger")

    review = record["review"]
    if _exact_keys(
        review,
        {"approved", "reviewer", "timestamp", "reviewedSkillSha256", "diff"},
        "runRecord.review",
        errors,
    ):
        if not isinstance(review["approved"], bool):
            errors.append("runRecord.review.approved must be a boolean")
        if not isinstance(review["reviewer"], str) or not review["reviewer"].strip():
            errors.append("runRecord.review.reviewer must identify the human reviewer")
        _parse_timestamp(review["timestamp"], "runRecord.review.timestamp", errors)
        if review["reviewedSkillSha256"] != record["candidateSkillSha256"]:
            errors.append("runRecord.review.reviewedSkillSha256 must match the candidate")
        if history and isinstance(history[-1], dict):
            if review["timestamp"] != history[-1].get("timestamp"):
                errors.append("runRecord.review.timestamp must match the human-review event")
        diff_path = _validate_file_ref(review["diff"], "runRecord.review.diff", root, errors)
        baseline_skill = _validate_file_ref(
            baseline.get("skillArtifact"), "baseline.skillArtifact", root, errors
        )
        candidate_skill = _validate_file_ref(
            candidate.get("skillArtifact"), "candidate.skillArtifact", root, errors
        )
        if diff_path is not None and baseline_skill is not None and candidate_skill is not None:
            actual_diff = diff_path.read_text(encoding="utf-8").replace("\r\n", "\n").replace("\r", "\n")
            if actual_diff != _normalized_unified_diff(baseline_skill, candidate_skill):
                errors.append(
                    "runRecord.review.diff does not match the normalized unified diff "
                    "between the hashed baseline and candidate skills"
                )
    return errors


def _weighted_score(row: dict[str, Any]) -> float:
    return sum(
        row["scores"][dimension] * weight / 100
        for dimension, weight in RUBRIC_WEIGHTS.items()
    )


def _aggregate(report: dict[str, Any]) -> float:
    return sum(_weighted_score(row) for row in report["rows"]) / len(report["rows"])


def _paper_aggregates(
    task_index: dict[str, dict[str, Any]], report: dict[str, Any]
) -> dict[str, float]:
    grouped: dict[str, list[float]] = {}
    for row in report["rows"]:
        paper = task_index[row["taskId"]]["paper"]
        grouped.setdefault(paper, []).append(_weighted_score(row))
    return {paper: sum(scores) / len(scores) for paper, scores in grouped.items()}


def score_threshold_reasons(
    aggregate_improvement: float, paper_deltas: dict[str, float]
) -> list[str]:
    reasons: list[str] = []
    if aggregate_improvement < MINIMUM_AGGREGATE_IMPROVEMENT:
        reasons.append(
            f"aggregate improvement {aggregate_improvement:.2f} is below the required "
            f"{MINIMUM_AGGREGATE_IMPROVEMENT:.2f}"
        )
    for paper, delta in paper_deltas.items():
        if delta < -MAXIMUM_PAPER_REGRESSION:
            reasons.append(
                f"paper {paper!r} regressed {abs(delta):.2f}, over the "
                f"{MAXIMUM_PAPER_REGRESSION:.2f} limit"
            )
    return reasons


def _report_rejection_reasons(
    label: str, report: dict[str, Any], include_flags: bool = True
) -> list[str]:
    reasons: list[str] = []
    failed_gates = [
        gate for gate, result in report["deterministicGates"].items() if not result["green"]
    ]
    if failed_gates:
        reasons.append(f"{label} deterministic gates are not green: {failed_gates}")
    if include_flags:
        for row in report["rows"]:
            for flag in row["automaticRejectionFlags"]:
                reasons.append(f"automatic rejection flag {flag!r} on {row['taskId']}")
    return reasons


def evaluate_acceptance(
    tasks_document: dict[str, Any],
    baseline: dict[str, Any],
    candidate: dict[str, Any],
    run_record: dict[str, Any],
    trial_root: str | Path | None = None,
    baseline_path: str | Path | None = None,
    candidate_path: str | Path | None = None,
) -> AcceptanceDecision:
    root = Path(trial_root) if trial_root is not None else _default_trial_root()
    validation_errors = [
        *(f"baseline: {error}" for error in validate_report(tasks_document, baseline, root)),
        *(f"candidate: {error}" for error in validate_report(tasks_document, candidate, root)),
    ]
    if validation_errors:
        return AcceptanceDecision(False, None, None, None, {}, [], validation_errors)

    reasons: list[str] = []
    if baseline["reportKind"] != "baseline":
        reasons.append("baseline reportKind must be 'baseline'")
    if candidate["reportKind"] != "candidate":
        reasons.append("candidate reportKind must be 'candidate'")
    if baseline["stage"] != "selection" or candidate["stage"] != "selection":
        reasons.append("acceptance compares baseline and candidate selection reports only")
        return AcceptanceDecision(False, None, None, None, {}, reasons, [])

    ledger_errors = validate_run_record(
        tasks_document,
        baseline,
        candidate,
        run_record,
        root,
        baseline_path,
        candidate_path,
    )
    if ledger_errors:
        return AcceptanceDecision(False, None, None, None, {}, [], ledger_errors)

    reasons.extend(_report_rejection_reasons("baseline", baseline, include_flags=False))
    reasons.extend(_report_rejection_reasons("candidate", candidate))
    if run_record["review"]["approved"] is not True:
        reasons.append("candidate human review is required")

    final_event = next(event for event in run_record["history"] if event["stage"] == "final-test")
    final_path = (root / final_event["reports"][0]["path"]).resolve()
    final_report = load_json(final_path)
    reasons.extend(_report_rejection_reasons("final-test", final_report))

    task_index, _ = _task_index(tasks_document, root.parent)
    baseline_aggregate = _aggregate(baseline)
    candidate_aggregate = _aggregate(candidate)
    improvement = candidate_aggregate - baseline_aggregate
    baseline_papers = _paper_aggregates(task_index, baseline)
    candidate_papers = _paper_aggregates(task_index, candidate)
    paper_deltas = {
        paper: candidate_papers[paper] - baseline_papers[paper]
        for paper in baseline_papers
    }
    reasons.extend(score_threshold_reasons(improvement, paper_deltas))
    return AcceptanceDecision(
        not reasons,
        baseline_aggregate,
        candidate_aggregate,
        improvement,
        paper_deltas,
        reasons,
        [],
    )


def _write_json(value: dict[str, Any]) -> None:
    print(json.dumps(value, indent=2, sort_keys=True))


def _load_or_error(path: str | Path) -> dict[str, Any]:
    try:
        return load_json(path)
    except (OSError, ValueError, json.JSONDecodeError) as error:
        raise ValueError(f"could not read {path}: {error}") from error


def _parser() -> argparse.ArgumentParser:
    root = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(
        prog="validate_skillopt",
        description="Offline policy checker; it does not run SkillOpt or a model backend.",
    )
    subcommands = parser.add_subparsers(dest="command", required=True)
    policy = subcommands.add_parser("policy", help="validate tasks.json and rubric.md")
    policy.add_argument("--tasks", type=Path, default=root / "tasks.json")
    policy.add_argument("--rubric", type=Path, default=root / "rubric.md")
    report = subcommands.add_parser("report", help="validate one scored report")
    report.add_argument("--tasks", type=Path, default=root / "tasks.json")
    report.add_argument("--rubric", type=Path, default=root / "rubric.md")
    report.add_argument("--report", type=Path, required=True)
    accept = subcommands.add_parser("accept", help="apply the completed-run acceptance gate")
    accept.add_argument("--tasks", type=Path, default=root / "tasks.json")
    accept.add_argument("--rubric", type=Path, default=root / "rubric.md")
    accept.add_argument("--baseline", type=Path, required=True)
    accept.add_argument("--candidate", type=Path, required=True)
    accept.add_argument("--run-record", type=Path, required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        tasks = _load_or_error(args.tasks)
        if args.command == "policy":
            errors = validate_policy(tasks, args.rubric)
            _write_json({"valid": not errors, "errors": errors})
            return 0 if not errors else 1
        if args.command == "report":
            errors = validate_policy(tasks, args.rubric)
            errors.extend(validate_report(tasks, _load_or_error(args.report)))
            _write_json({"valid": not errors, "errors": errors})
            return 0 if not errors else 1
        policy_errors = validate_policy(tasks, args.rubric)
        if policy_errors:
            _write_json({"accepted": False, "errors": policy_errors})
            return 1
        decision = evaluate_acceptance(
            tasks,
            _load_or_error(args.baseline),
            _load_or_error(args.candidate),
            _load_or_error(args.run_record),
            baseline_path=args.baseline,
            candidate_path=args.candidate,
        )
        _write_json(decision.to_dict())
        if decision.validation_errors:
            return 1
        return 0 if decision.accepted else 2
    except ValueError as error:
        _write_json({"valid": False, "errors": [str(error)]})
        return 1


if __name__ == "__main__":
    sys.exit(main())
