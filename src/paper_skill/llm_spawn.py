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
    return subprocess.run(
        ["claude", "-p", prompt, "--max-turns", str(max_turns)],
        capture_output=True, text=True, timeout=timeout,
    ).stdout
