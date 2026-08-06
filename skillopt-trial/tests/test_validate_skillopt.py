"""Offline contract tests for the paper-tutor SkillOpt validation gate."""

from __future__ import annotations

import json
import hashlib
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


TRIAL_ROOT = Path(__file__).resolve().parents[1]
VALIDATION_DIR = TRIAL_ROOT / "validation"
FIXTURES = VALIDATION_DIR / "fixtures"
sys.path.insert(0, str(VALIDATION_DIR))

import validate_skillopt as gate  # noqa: E402


class SkillOptValidationGateTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tasks = gate.load_json(VALIDATION_DIR / "tasks.json")
        self.baseline = gate.load_json(FIXTURES / "baseline-selection.json")
        self.candidate = gate.load_json(FIXTURES / "candidate-accepted-selection.json")
        self.final_test = gate.load_json(FIXTURES / "candidate-final-test.json")
        self.run_record = gate.load_json(FIXTURES / "accepted-run-record.json")

    def _run_cli(self, *arguments: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(VALIDATION_DIR / "validate_skillopt.py"), *arguments],
            check=False,
            capture_output=True,
            text=True,
        )

    def _accept_cli(
        self, baseline_path: Path, candidate_path: Path, run_record_path: Path
    ) -> subprocess.CompletedProcess[str]:
        return self._run_cli(
            "accept",
            "--tasks",
            str(VALIDATION_DIR / "tasks.json"),
            "--rubric",
            str(VALIDATION_DIR / "rubric.md"),
            "--baseline",
            str(baseline_path),
            "--candidate",
            str(candidate_path),
            "--run-record",
            str(run_record_path),
        )

    def _bind_selection_report(
        self, record: dict[str, object], role: str, report_path: Path
    ) -> None:
        selection = next(
            event for event in record["history"] if event["stage"] == "selection"
        )
        binding = next(item for item in selection["reports"] if item["role"] == role)
        binding["path"] = report_path.relative_to(TRIAL_ROOT).as_posix()
        binding["sha256"] = hashlib.sha256(report_path.read_bytes()).hexdigest()
        previous = "0" * 64
        for event in record["history"]:
            event["previousEventSha256"] = previous
            payload = {key: value for key, value in event.items() if key != "eventSha256"}
            event["eventSha256"] = hashlib.sha256(
                json.dumps(
                    payload,
                    sort_keys=True,
                    separators=(",", ":"),
                    ensure_ascii=False,
                ).encode("utf-8")
            ).hexdigest()
            previous = event["eventSha256"]

    def test_current_policy_locks_manifest_split_weights_flags_and_artifacts(self) -> None:
        """Changing a benchmark input must break policy validation."""
        self.assertEqual(
            gate.validate_policy(self.tasks, VALIDATION_DIR / "rubric.md"),
            [],
        )

    def test_policy_rejects_manifest_prompt_or_artifact_tampering(self) -> None:
        """Prompts and paper-to-artifact mappings are cryptographically fixed."""
        tampered = json.loads(json.dumps(self.tasks))
        tampered["tasks"][0]["prompt"] += " hidden tuning hint"
        tampered["tasks"][1]["artifactDir"] = "artifacts/aiayn-live"

        errors = gate.validate_policy(tampered, VALIDATION_DIR / "rubric.md")

        joined = " ".join(errors)
        self.assertIn("manifest hash", joined)
        self.assertIn("artifactDir", joined)

    def test_report_command_cannot_bypass_the_locked_manifest(self) -> None:
        """Every CLI path must enforce the manifest, not only the policy command."""
        tampered = json.loads(json.dumps(self.tasks))
        tampered["tasks"][0]["prompt"] += " post-lock edit"
        with tempfile.TemporaryDirectory() as temporary_directory:
            tasks_path = Path(temporary_directory) / "tasks.json"
            tasks_path.write_text(json.dumps(tampered), encoding="utf-8")
            completed = self._run_cli(
                "report",
                "--tasks",
                str(tasks_path),
                "--report",
                str(FIXTURES / "candidate-final-test.json"),
            )

        self.assertEqual(completed.returncode, 1)
        self.assertIn("manifest hash", completed.stdout)

    def test_policy_rejects_a_displayed_weight_that_disagrees_with_policy(self) -> None:
        """A misleading percentage cannot pass beside the machine policy."""
        rubric_text = (VALIDATION_DIR / "rubric.md").read_text(encoding="utf-8")
        altered = rubric_text.replace(
            "| Factual and evidence accuracy | 15% |",
            "| Factual and evidence accuracy | 14% |",
            1,
        )
        with tempfile.TemporaryDirectory() as temporary_directory:
            rubric_path = Path(temporary_directory) / "rubric.md"
            rubric_path.write_text(altered, encoding="utf-8")
            errors = gate.validate_policy(self.tasks, rubric_path)

        self.assertTrue(any("human-readable rubric weights" in error for error in errors), errors)

    def test_valid_selection_and_final_test_reports_verify_local_evidence(self) -> None:
        """Every fixture reference and SHA-256 must resolve before use."""
        self.assertEqual(gate.validate_report(self.tasks, self.baseline), [])
        self.assertEqual(gate.validate_report(self.tasks, self.candidate), [])
        self.assertEqual(gate.validate_report(self.tasks, self.final_test), [])

    def test_report_rejects_raw_output_hash_tampering(self) -> None:
        """Replacing a scored raw output must invalidate its report."""
        candidate = json.loads(json.dumps(self.candidate))
        with tempfile.TemporaryDirectory(dir=TRIAL_ROOT) as temporary_directory:
            temporary_path = Path(temporary_directory)
            tampered_output = temporary_path / "tampered-output.txt"
            tampered_output.write_text("changed after scoring", encoding="utf-8")
            candidate["rows"][0]["rawOutput"]["path"] = tampered_output.relative_to(
                TRIAL_ROOT
            ).as_posix()
            report_path = temporary_path / "candidate.json"
            report_path.write_text(json.dumps(candidate), encoding="utf-8")
            completed = self._run_cli("report", "--report", str(report_path))

        self.assertEqual(completed.returncode, 1)
        self.assertIn("hash mismatch", completed.stdout)

    def test_report_rejects_deterministic_gate_evidence_tampering(self) -> None:
        """A green gate without matching evidence cannot validate."""
        candidate = json.loads(json.dumps(self.candidate))
        with tempfile.TemporaryDirectory(dir=TRIAL_ROOT) as temporary_directory:
            temporary_path = Path(temporary_directory)
            tampered_evidence = temporary_path / "tampered-gate.txt"
            tampered_evidence.write_text("not the recorded gate run", encoding="utf-8")
            candidate["deterministicGates"]["correctness"]["evidence"]["path"] = (
                tampered_evidence.relative_to(TRIAL_ROOT).as_posix()
            )
            report_path = temporary_path / "candidate.json"
            report_path.write_text(json.dumps(candidate), encoding="utf-8")
            completed = self._run_cli("report", "--report", str(report_path))

        self.assertEqual(completed.returncode, 1)
        self.assertIn("hash mismatch", completed.stdout)

    def test_tuning_report_rejects_final_test_row_with_exit_one(self) -> None:
        """A privacy final-test row can never become tuning input."""
        completed = self._run_cli(
            "report",
            "--report",
            str(FIXTURES / "tuning-with-privacy-row.json"),
        )

        self.assertEqual(completed.returncode, 1)
        payload = json.loads(completed.stdout)
        self.assertFalse(payload["valid"])
        self.assertTrue(any("final-test task" in error for error in payload["errors"]))

    def test_run_record_requires_selection_before_final_test_and_review(self) -> None:
        """Reordering final-test ahead of selection invalidates ledger history."""
        record = json.loads(json.dumps(self.run_record))
        record["history"][1], record["history"][2] = record["history"][2], record["history"][1]
        with tempfile.TemporaryDirectory() as temporary_directory:
            record_path = Path(temporary_directory) / "run-record.json"
            record_path.write_text(json.dumps(record), encoding="utf-8")
            completed = self._accept_cli(
                FIXTURES / "baseline-selection.json",
                FIXTURES / "candidate-accepted-selection.json",
                record_path,
            )

        self.assertEqual(completed.returncode, 1)
        self.assertIn("final-test must occur after selection", completed.stdout)

    def test_accepted_candidate_earns_its_margin_on_visual_explanation(self) -> None:
        """The accepted fixture passes only with the complete evidence ledger.

        Its margin is deliberately the diagram gap: baseline scores 40 on
        visual_explanation (contract v1 never mentioned diagrams), candidate 85.
        Strip that dimension and the remaining improvement is 2.55, below the
        +3 gate -- which is the point of adding the dimension.
        """
        completed = self._accept_cli(
            FIXTURES / "baseline-selection.json",
            FIXTURES / "candidate-accepted-selection.json",
            FIXTURES / "accepted-run-record.json",
        )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        payload = json.loads(completed.stdout)
        self.assertTrue(payload["accepted"])
        self.assertAlmostEqual(payload["aggregate_improvement"], 9.3, places=6)

    def test_inclusive_three_point_boundary_is_accepted(self) -> None:
        """+3 exactly still passes; the gate is inclusive."""
        candidate = json.loads(json.dumps(self.candidate))
        # Weights sum to 100, so subtracting c from every dimension of every
        # row lowers the aggregate by exactly c. 9.3 - 6.3 lands on the bound.
        for row in candidate["rows"]:
            for dimension in row["scores"]:
                row["scores"][dimension] -= 6.3
        record = json.loads(json.dumps(self.run_record))
        with tempfile.TemporaryDirectory(dir=TRIAL_ROOT) as temporary_directory:
            candidate_path = Path(temporary_directory) / "candidate.json"
            candidate_path.write_text(json.dumps(candidate), encoding="utf-8")
            self._bind_selection_report(record, "candidate", candidate_path)
            record_path = Path(temporary_directory) / "record.json"
            record_path.write_text(json.dumps(record), encoding="utf-8")
            completed = self._accept_cli(
                FIXTURES / "baseline-selection.json", candidate_path, record_path)

        payload = json.loads(completed.stdout)
        self.assertAlmostEqual(payload["aggregate_improvement"], 3.0, places=6)
        self.assertTrue(payload["accepted"], payload)

    def test_improvement_below_three_is_a_valid_exit_two_rejection(self) -> None:
        """An otherwise valid +2.9 candidate is rejected, not treated as malformed."""
        candidate = json.loads(json.dumps(self.candidate))
        # Same arithmetic as the boundary test: 9.3 - 6.4 = 2.9, just under.
        for row in candidate["rows"]:
            for dimension in row["scores"]:
                row["scores"][dimension] -= 6.4
        record = json.loads(json.dumps(self.run_record))
        with tempfile.TemporaryDirectory(dir=TRIAL_ROOT) as temporary_directory:
            candidate_path = Path(temporary_directory) / "candidate.json"
            candidate_path.write_text(json.dumps(candidate), encoding="utf-8")
            self._bind_selection_report(record, "candidate", candidate_path)
            record_path = Path(temporary_directory) / "record.json"
            record_path.write_text(json.dumps(record), encoding="utf-8")
            completed = self._accept_cli(
                FIXTURES / "baseline-selection.json",
                candidate_path,
                record_path,
            )

        self.assertEqual(completed.returncode, 2, completed.stderr)
        self.assertTrue(completed.stdout, completed.stderr)
        payload = json.loads(completed.stdout)
        self.assertFalse(payload["accepted"])
        self.assertTrue(any("below the required" in reason for reason in payload["reasons"]))

    def test_paper_regression_boundary_is_generic_and_inclusive(self) -> None:
        """Exactly -2 passes while a worse paper delta rejects."""
        self.assertTrue(hasattr(gate, "score_threshold_reasons"))
        check = gate.score_threshold_reasons
        self.assertEqual(check(3.0, {"paper-a": -2.0}), [])
        self.assertTrue(any("paper-a" in reason for reason in check(3.0, {"paper-a": -2.01})))

    def test_stage_mismatch_is_a_structured_exit_two_rejection(self) -> None:
        """A valid tuning baseline must not crash selection acceptance."""
        tuning_baseline = json.loads(json.dumps(self.baseline))
        tuning_baseline["stage"] = "tuning"
        tuning_baseline["rows"] = []
        for task in self.tasks["tasks"]:
            if task["split"] == "train":
                row = json.loads(json.dumps(self.baseline["rows"][0]))
                row["taskId"] = task["id"]
                tuning_baseline["rows"].append(row)

        with tempfile.TemporaryDirectory() as temporary_directory:
            baseline_path = Path(temporary_directory) / "tuning-baseline.json"
            baseline_path.write_text(json.dumps(tuning_baseline), encoding="utf-8")
            completed = self._accept_cli(
                baseline_path,
                FIXTURES / "candidate-accepted-selection.json",
                FIXTURES / "accepted-run-record.json",
            )

        self.assertEqual(completed.returncode, 2, completed.stderr)
        self.assertTrue(completed.stdout, completed.stderr)
        payload = json.loads(completed.stdout)
        self.assertFalse(payload["accepted"])
        self.assertTrue(any("selection reports only" in reason for reason in payload["reasons"]))

    def test_acceptance_requires_flags_green_gates_and_audited_human_review(self) -> None:
        """Automatic rejection, failed evidence gate, and rejected review all remain fatal."""
        candidate = json.loads(json.dumps(self.candidate))
        candidate["rows"][0]["automaticRejectionFlags"] = ["invented_formula"]
        candidate["deterministicGates"]["evidence_citation"]["green"] = False
        record = json.loads(json.dumps(self.run_record))
        record["review"]["approved"] = False
        with tempfile.TemporaryDirectory(dir=TRIAL_ROOT) as temporary_directory:
            temporary_path = Path(temporary_directory)
            candidate_path = temporary_path / "candidate.json"
            record_path = temporary_path / "record.json"
            candidate_path.write_text(json.dumps(candidate), encoding="utf-8")
            self._bind_selection_report(record, "candidate", candidate_path)
            record_path.write_text(json.dumps(record), encoding="utf-8")
            completed = self._accept_cli(
                FIXTURES / "baseline-selection.json", candidate_path, record_path
            )

        self.assertEqual(completed.returncode, 2, completed.stderr)
        self.assertTrue(completed.stdout, completed.stderr)
        reasons = " ".join(json.loads(completed.stdout)["reasons"])
        self.assertIn("automatic rejection", reasons)
        self.assertIn("deterministic gates", reasons)
        self.assertIn("human review", reasons)

    def test_selection_report_bytes_are_bound_by_the_run_ledger(self) -> None:
        """Changing candidate selection scores without a ledger update is malformed."""
        candidate = json.loads(json.dumps(self.candidate))
        candidate["rows"][0]["scores"]["conceptual_depth"] += 1
        with tempfile.TemporaryDirectory() as temporary_directory:
            candidate_path = Path(temporary_directory) / "changed-candidate.json"
            candidate_path.write_text(json.dumps(candidate), encoding="utf-8")
            completed = self._accept_cli(
                FIXTURES / "baseline-selection.json",
                candidate_path,
                FIXTURES / "accepted-run-record.json",
            )

        self.assertEqual(completed.returncode, 1, completed.stderr)
        self.assertIn("selection candidate report", completed.stdout)

    def test_ledger_tuning_event_binds_train_only_report_without_final_rows(self) -> None:
        """The tuning event must point to a hashed train-only report."""
        tuning_event = self.run_record["history"][0]
        self.assertIsInstance(tuning_event.get("reports"), list)
        tuning_ref = tuning_event["reports"][0]
        tuning_report = gate.load_json(TRIAL_ROOT / tuning_ref["path"])
        self.assertEqual(tuning_report["stage"], "tuning")
        task_ids = {row["taskId"] for row in tuning_report["rows"]}
        final_ids = {
            task["id"] for task in self.tasks["tasks"] if task["split"] == "final-test"
        }
        self.assertTrue(task_ids)
        self.assertTrue(task_ids.isdisjoint(final_ids))

    def test_review_diff_must_match_exact_normalized_skill_diff(self) -> None:
        """A hashed placeholder diff cannot stand in for the reviewed skill change."""
        record = json.loads(json.dumps(self.run_record))
        with tempfile.TemporaryDirectory(dir=TRIAL_ROOT) as temporary_directory:
            temporary_path = Path(temporary_directory)
            fake_diff = temporary_path / "fake.diff"
            fake_diff.write_text("--- fake\n+++ fake\n", encoding="utf-8")
            record["review"]["diff"] = {
                "path": fake_diff.relative_to(TRIAL_ROOT).as_posix(),
                "sha256": hashlib.sha256(fake_diff.read_bytes()).hexdigest(),
            }
            record_path = temporary_path / "record.json"
            record_path.write_text(json.dumps(record), encoding="utf-8")
            completed = self._accept_cli(
                FIXTURES / "baseline-selection.json",
                FIXTURES / "candidate-accepted-selection.json",
                record_path,
            )

        self.assertEqual(completed.returncode, 1, completed.stderr)
        self.assertIn("normalized unified diff", completed.stdout)

    def test_baseline_rejection_flags_do_not_reject_candidate(self) -> None:
        """Baseline flags remain recorded data; only candidate flags reject."""
        baseline = json.loads(json.dumps(self.baseline))
        baseline["rows"][0]["automaticRejectionFlags"] = ["invented_formula"]

        record = json.loads(json.dumps(self.run_record))
        with tempfile.TemporaryDirectory(dir=TRIAL_ROOT) as temporary_directory:
            temporary_path = Path(temporary_directory)
            baseline_path = temporary_path / "baseline.json"
            record_path = temporary_path / "record.json"
            baseline_path.write_text(json.dumps(baseline), encoding="utf-8")
            self._bind_selection_report(record, "baseline", baseline_path)
            record_path.write_text(json.dumps(record), encoding="utf-8")
            completed = self._accept_cli(
                baseline_path,
                FIXTURES / "candidate-accepted-selection.json",
                record_path,
            )

        self.assertEqual(completed.returncode, 0, completed.stdout)
        self.assertTrue(json.loads(completed.stdout)["accepted"])

    def test_direct_ledger_validation_rejects_non_string_stage_and_role_values(self) -> None:
        """Lists, objects, and null must become validation errors, never TypeError."""
        for field, value in (
            ("stage", []),
            ("stage", {}),
            ("stage", None),
            ("role", []),
            ("role", {}),
            ("role", None),
        ):
            with self.subTest(field=field, value=value):
                record = json.loads(json.dumps(self.run_record))
                if field == "stage":
                    record["history"][0]["stage"] = value
                else:
                    record["history"][0]["reports"][0]["role"] = value
                try:
                    errors = gate.validate_run_record(
                        self.tasks, self.baseline, self.candidate, record
                    )
                except Exception as error:  # pragma: no cover - failure assertion below
                    self.fail(f"malformed {field} raised {type(error).__name__}: {error}")
                self.assertTrue(any(f".{field}" in error for error in errors), errors)

    def test_cli_ledger_validation_returns_exit_one_for_non_string_stage_and_role(self) -> None:
        """The CLI must emit structured JSON for every malformed discriminator type."""
        for field, value in (
            ("stage", []),
            ("stage", {}),
            ("stage", None),
            ("role", []),
            ("role", {}),
            ("role", None),
        ):
            with self.subTest(field=field, value=value):
                record = json.loads(json.dumps(self.run_record))
                if field == "stage":
                    record["history"][0]["stage"] = value
                else:
                    record["history"][0]["reports"][0]["role"] = value
                with tempfile.TemporaryDirectory() as temporary_directory:
                    record_path = Path(temporary_directory) / "record.json"
                    record_path.write_text(json.dumps(record), encoding="utf-8")
                    completed = self._accept_cli(
                        FIXTURES / "baseline-selection.json",
                        FIXTURES / "candidate-accepted-selection.json",
                        record_path,
                    )
                self.assertEqual(completed.returncode, 1, completed.stderr)
                self.assertTrue(completed.stdout, completed.stderr)
                payload = json.loads(completed.stdout)
                self.assertFalse(payload["accepted"])
                self.assertTrue(payload["validation_errors"])


if __name__ == "__main__":
    unittest.main()
