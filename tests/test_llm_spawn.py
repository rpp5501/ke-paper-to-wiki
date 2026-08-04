"""claude_spawn must decode UTF-8 and must never fail quietly.

This module exists so a missing/failing model backend cannot be mistaken for an
empty result. Two ways that promise leaked:

1. subprocess.run(text=True) decodes with the *locale* encoding. On Windows
   that is cp1252, so a model emitting UTF-8 came back mojibake: the section
   anchors the page writer requires, [§sec_1], arrived as [Â§sec_1] and failed
   P5 lint downstream.
2. A non-zero exit (auth expired, rate limit) returned empty stdout, which
   callers read as "the model said nothing" rather than "the model never ran".
"""
import subprocess

import pytest

from paper_skill.llm_spawn import LLMUnavailable, claude_spawn


class _FakeRun:
    """Records kwargs and replays a canned CompletedProcess."""

    def __init__(self, stdout="ok", returncode=0, stderr=""):
        self.stdout, self.returncode, self.stderr = stdout, returncode, stderr
        self.kwargs = None

    def __call__(self, argv, **kwargs):
        self.kwargs = kwargs
        return subprocess.CompletedProcess(
            argv, self.returncode, self.stdout, self.stderr)


@pytest.fixture
def cli_present(monkeypatch):
    monkeypatch.setattr("paper_skill.llm_spawn.shutil.which", lambda _: "claude")


def test_output_is_decoded_as_utf8(cli_present, monkeypatch):
    fake = _FakeRun()
    monkeypatch.setattr("paper_skill.llm_spawn.subprocess.run", fake)

    claude_spawn("hi")

    assert fake.kwargs["encoding"] == "utf-8"


def test_undecodable_bytes_do_not_crash_a_24_page_run(cli_present, monkeypatch):
    fake = _FakeRun()
    monkeypatch.setattr("paper_skill.llm_spawn.subprocess.run", fake)

    claude_spawn("hi")

    assert fake.kwargs["errors"] == "replace"


def test_section_anchor_survives_the_round_trip(cli_present, monkeypatch):
    """The concrete regression: [§sec_1] must not become [Â§sec_1]."""
    monkeypatch.setattr("paper_skill.llm_spawn.subprocess.run",
                        _FakeRun(stdout="claim text [§sec_1] — done"))

    out = claude_spawn("write a page")

    assert "[§sec_1]" in out
    assert "Â" not in out and "â€" not in out


def test_nonzero_exit_is_loud_not_empty(cli_present, monkeypatch):
    monkeypatch.setattr(
        "paper_skill.llm_spawn.subprocess.run",
        _FakeRun(stdout="", returncode=1, stderr="Invalid API key"))

    with pytest.raises(LLMUnavailable) as e:
        claude_spawn("hi")

    # the operator needs the CLI's own reason, not just "it failed"
    assert "Invalid API key" in str(e.value)


def test_successful_exit_returns_stdout(cli_present, monkeypatch):
    monkeypatch.setattr("paper_skill.llm_spawn.subprocess.run",
                        _FakeRun(stdout="the answer"))

    assert claude_spawn("hi") == "the answer"


def test_missing_cli_still_names_the_escape_hatch(monkeypatch):
    monkeypatch.setattr("paper_skill.llm_spawn.shutil.which", lambda _: None)

    with pytest.raises(LLMUnavailable) as e:
        claude_spawn("hi")

    assert "inject" in str(e.value).lower()
