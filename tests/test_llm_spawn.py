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


# A batch of 30 verifier calls lost 26 of them to non-zero exits that cleared
# on the next attempt -- rate limiting, not a broken CLI. Failing the whole
# batch on a transient is as wrong as failing silently; a missing CLI still
# fails at once, since retrying that can never help.
def test_a_transient_failure_is_retried(cli_present, monkeypatch):
    attempts = []

    def flaky(argv, **kwargs):
        attempts.append(1)
        code = 1 if len(attempts) == 1 else 0
        return subprocess.CompletedProcess(argv, code, "recovered", "overloaded")

    monkeypatch.setattr("paper_skill.llm_spawn.subprocess.run", flaky)
    monkeypatch.setattr("paper_skill.llm_spawn.time.sleep", lambda _s: None)

    assert claude_spawn("hi") == "recovered"
    assert len(attempts) == 2


def test_retries_are_bounded(cli_present, monkeypatch):
    attempts = []

    def always_fails(argv, **kwargs):
        attempts.append(1)
        return subprocess.CompletedProcess(argv, 1, "", "still overloaded")

    monkeypatch.setattr("paper_skill.llm_spawn.subprocess.run", always_fails)
    monkeypatch.setattr("paper_skill.llm_spawn.time.sleep", lambda _s: None)

    with pytest.raises(LLMUnavailable):
        claude_spawn("hi")
    assert len(attempts) <= 4


def test_a_missing_cli_is_not_retried(monkeypatch):
    """Retrying a CLI that is not installed only delays the same answer."""
    calls = []
    monkeypatch.setattr("paper_skill.llm_spawn.shutil.which",
                        lambda _: calls.append(1) or None)

    with pytest.raises(LLMUnavailable):
        claude_spawn("hi")
    assert len(calls) == 1


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


# Every stage that demands "ONLY JSON" gets a ```json fence some fraction of
# the time. next_steps used a strict json.loads and rejected replies that
# concepts (which greps for the object) accepted -- same task, two answers.
@pytest.mark.parametrize("raw", [
    '{"ideas": []}',
    '```json\n{"ideas": []}\n```',
    'Here you go:\n\n{"ideas": []}\n',
    '```\n{"ideas": []}\n```\n',
])
def test_json_survives_fences_and_preamble(raw):
    from paper_skill.llm_spawn import parse_json_reply
    assert parse_json_reply(raw) == {"ideas": []}


@pytest.mark.parametrize("raw", ["", "sorry, prose not json", "[1, 2, 3]", None])
def test_non_object_replies_are_none_not_exceptions(raw):
    from paper_skill.llm_spawn import parse_json_reply
    assert parse_json_reply(raw) is None


# Windows caps a command line at ~32,767 characters, and the prompt was being
# passed as an argv argument -- so any large prompt died with WinError 206 "The
# filename or extension is too long". Hit for real by the term-definition
# stage, but latent for every stage: a paper with big sections would have taken
# P4 over the same cliff. `claude -p` reads the prompt from stdin, which has no
# such limit.
class _CaptureArgv(_FakeRun):
    def __call__(self, argv, **kwargs):
        self.argv = argv
        return super().__call__(argv, **kwargs)


def test_the_prompt_goes_by_stdin_not_argv(monkeypatch):
    fake = _CaptureArgv()
    monkeypatch.setattr(subprocess, "run", fake)
    monkeypatch.setattr("shutil.which", lambda name: "claude")

    claude_spawn("x" * 50_000)

    assert fake.kwargs["input"] == "x" * 50_000
    assert not any(len(str(a)) > 1000 for a in fake.argv), "prompt still in argv"


def test_a_prompt_far_over_the_windows_argv_limit_is_fine(monkeypatch):
    fake = _CaptureArgv()
    monkeypatch.setattr(subprocess, "run", fake)
    monkeypatch.setattr("shutil.which", lambda name: "claude")

    assert claude_spawn("y" * 200_000) == "ok"


def test_the_spawned_model_gets_no_tools(monkeypatch):
    """Every stage here is a pure text transform: the whole context is already
    inlined in the prompt and the answer comes back on stdout.

    With the default toolset the aiayn attention-visualization page did all
    three things that breaks. It explored the repo (git status, Glob) and read
    finished sibling pages -- so the page could be built from other pages
    rather than the supplied evidence, which is exactly what the contract
    forbids. It then called Write on the real pages/21_*.md, bypassing
    write_pages and therefore the pedagogy gate, which only ever sees the
    returned string. Only after all that did it hit the turn ceiling.

    Raising max_turns 3 -> 6 previously "fixed" the same failure by giving it
    more rope. The budget was never the cause.
    """
    fake = _CaptureArgv()
    monkeypatch.setattr(subprocess, "run", fake)
    monkeypatch.setattr("shutil.which", lambda name: "claude")

    claude_spawn("write me a page")

    assert "--tools" in fake.argv
    assert fake.argv[fake.argv.index("--tools") + 1] == ""


def test_a_caller_can_ask_for_a_specific_tool(monkeypatch):
    """`--tools ""` was added to stop the PAGE WRITER calling Write on the
    real artifact. It lives in claude_spawn, which P3 also uses, so a
    P4-specific guard silently removed the researcher's ability to retrieve
    anything -- while its prompt still says to work "from your own knowledge".
    That recall is why 2 of 15 cited arXiv ids resolved to the wrong paper.

    The default stays "": a stage has to ask before it can reach the network.
    """
    fake = _CaptureArgv()
    monkeypatch.setattr(subprocess, "run", fake)
    monkeypatch.setattr("shutil.which", lambda name: "claude")

    claude_spawn("research this concept", tools="WebSearch")

    assert fake.argv[fake.argv.index("--tools") + 1] == "WebSearch"


def test_the_researcher_is_the_only_stage_that_gets_a_tool(monkeypatch):
    """A seam-agreement check: the two real call sites, read from the modules
    that own them, so this cannot pass while the wiring says otherwise."""
    import inspect

    from paper_skill import p3_research, p4_write

    research = inspect.getsource(p3_research._spawn_claude)
    write = inspect.getsource(p4_write._spawn_claude)

    assert "WebSearch" in research, "P3 must be able to retrieve"
    assert "tools=" not in write, "P4 must keep the default empty toolset"


def test_a_requested_tool_is_also_permitted(monkeypatch):
    """--tools makes a tool VISIBLE, not USABLE. Granting P3 WebSearch with
    --tools alone produced, on a live run, a researcher that replied "I don't
    have permission to use WebSearch yet -- could you grant it" for 17 of 18
    concepts, every one of them recorded as `not parseable JSON`.

    The earlier probe that "confirmed" the flag asked for a url the model
    already knew, so it answered from memory and never exercised the tool.
    """
    fake = _CaptureArgv()
    monkeypatch.setattr(subprocess, "run", fake)
    monkeypatch.setattr("shutil.which", lambda name: "claude")

    claude_spawn("research this", tools="WebSearch")

    assert "--allowedTools" in fake.argv, "a visible tool is still unusable"
    assert fake.argv[fake.argv.index("--allowedTools") + 1] == "WebSearch"


def test_no_permission_is_granted_when_no_tool_is_asked_for(monkeypatch):
    """The default stays a pure text transform: nothing visible, nothing
    permitted."""
    fake = _CaptureArgv()
    monkeypatch.setattr(subprocess, "run", fake)
    monkeypatch.setattr("shutil.which", lambda name: "claude")

    claude_spawn("write a page")

    assert "--allowedTools" not in fake.argv
    assert fake.argv[fake.argv.index("--tools") + 1] == ""


# --- running a stage on a different subscription ----------------------------
# Every stage takes an injectable spawn, but run_pipeline hardwires the Claude
# one, so switching backends meant editing source. Two env vars move the whole
# pipeline to another CLI without touching a file: the prompt still goes on
# stdin and the reply still comes back on stdout, which is all any stage here
# assumes.

def test_the_backend_command_can_be_overridden(monkeypatch):
    fake = _CaptureArgv()
    monkeypatch.setattr(subprocess, "run", fake)
    monkeypatch.setattr("shutil.which", lambda name: f"/usr/bin/{name}")
    monkeypatch.setenv("KE_LLM_CMD", "gemini --yolo -p")

    claude_spawn("write a page")

    assert fake.argv[:3] == ["gemini", "--yolo", "-p"]
    assert "--max-turns" not in fake.argv, "claude flags must not leak"


def test_a_tool_stage_uses_its_own_override(monkeypatch):
    """P3 needs web search and P4 must not have it, and no two CLIs spell that
    the same way -- so the tool-enabled variant is configured separately."""
    fake = _CaptureArgv()
    monkeypatch.setattr(subprocess, "run", fake)
    monkeypatch.setattr("shutil.which", lambda name: f"/usr/bin/{name}")
    monkeypatch.setenv("KE_LLM_CMD", "gemini -p")
    monkeypatch.setenv("KE_LLM_CMD_TOOLS", "gemini --yolo -p")

    claude_spawn("research this", tools="WebSearch")

    assert fake.argv[:3] == ["gemini", "--yolo", "-p"]


def test_a_tool_stage_falls_back_to_the_plain_override(monkeypatch):
    """One variable configured, both stages still run."""
    fake = _CaptureArgv()
    monkeypatch.setattr(subprocess, "run", fake)
    monkeypatch.setattr("shutil.which", lambda name: f"/usr/bin/{name}")
    monkeypatch.setenv("KE_LLM_CMD", "codex exec")

    claude_spawn("research this", tools="WebSearch")

    assert fake.argv[:2] == ["codex", "exec"]


def test_a_missing_override_binary_names_itself(monkeypatch):
    """The not-installed message must name the CLI actually being used, or it
    sends someone to reinstall the wrong tool."""
    monkeypatch.setattr("shutil.which", lambda name: None)
    monkeypatch.setenv("KE_LLM_CMD", "gemini -p")

    with pytest.raises(LLMUnavailable) as exc:
        claude_spawn("x")

    assert "gemini" in str(exc.value)


def test_no_override_is_the_claude_path_exactly(monkeypatch):
    fake = _CaptureArgv()
    monkeypatch.setattr(subprocess, "run", fake)
    monkeypatch.setattr("shutil.which", lambda name: "claude")
    monkeypatch.delenv("KE_LLM_CMD", raising=False)
    monkeypatch.delenv("KE_LLM_CMD_TOOLS", raising=False)

    claude_spawn("x", max_turns=6)

    assert fake.argv == ["claude", "-p", "--max-turns", "6", "--tools", ""]
