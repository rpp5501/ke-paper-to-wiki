"""Shared LLM spawn: the single place the pipeline shells out to a model.

Historically each stage (concepts, p3_research, p4_write) had its own
``_spawn_claude`` that ran ``claude -p``. When the ``claude`` CLI is not on the
machine that call raised an opaque ``FileNotFoundError``, which upstream
orchestration swallowed and quietly fell back to a table-of-contents graph --
producing an empty-looking dashboard with no visible cause. This module makes
that failure loud and names the escape hatch: inject your own ``spawn``.
"""
import shutil
import subprocess


class LLMUnavailable(RuntimeError):
    """Raised when no model backend is reachable for a required LLM stage."""


def claude_spawn(prompt: str, max_turns: int = 3, timeout: int = 600) -> str:
    """Run one prompt through the ``claude`` CLI, or fail with guidance.

    Raises ``LLMUnavailable`` (never a bare ``FileNotFoundError``) when the CLI
    is absent so callers cannot mistake "no model" for "empty result".
    """
    if shutil.which("claude") is None:
        raise LLMUnavailable(
            "the `claude` CLI is not on PATH, so this LLM stage cannot run. "
            "Do NOT fall back to a table-of-contents graph. Either install the "
            "CLI, or inject a working `spawn(prompt)->str` into "
            "extract_concepts / write_pages (e.g. via a subagent)."
        )
    # encoding is explicit: text=True alone decodes with the *locale* encoding
    # (cp1252 on Windows), which turned every [§sec_N] anchor the page writer
    # emits into [Â§sec_N] and broke P5 lint. errors="replace" keeps one odd
    # byte from killing a 24-page run.
    proc = subprocess.run(
        ["claude", "-p", prompt, "--max-turns", str(max_turns)],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        timeout=timeout,
    )
    if proc.returncode != 0:
        # Same contract as a missing CLI: "the model never ran" must not reach
        # callers as "the model returned nothing".
        raise LLMUnavailable(
            f"`claude -p` exited {proc.returncode}, so this LLM stage did not "
            f"run. Do NOT treat this as an empty result. CLI said: "
            f"{(proc.stderr or proc.stdout or '').strip()[:500]}"
        )
    return proc.stdout
