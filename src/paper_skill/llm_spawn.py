"""Shared LLM spawn: the single place the pipeline shells out to a model.

Historically each stage (concepts, p3_research, p4_write) had its own
``_spawn_claude`` that ran ``claude -p``. When the ``claude`` CLI is not on the
machine that call raised an opaque ``FileNotFoundError``, which upstream
orchestration swallowed and quietly fell back to a table-of-contents graph --
producing an empty-looking dashboard with no visible cause. This module makes
that failure loud and names the escape hatch: inject your own ``spawn``.
"""
import json
import re
import shutil
import subprocess
import time

# A batch of 30 verifier calls lost 26 to non-zero exits that cleared on the
# next attempt: rate limiting, not a broken CLI. Failing a whole batch on a
# transient is as wrong as failing silently.
MAX_ATTEMPTS = 3
BACKOFF_SECONDS = 2.0

_JSON_BLOCK = re.compile(r"\{.*\}", re.S)


class LLMUnavailable(RuntimeError):
    """Raised when no model backend is reachable for a required LLM stage."""


def parse_json_reply(raw: str) -> dict | None:
    """Pull the JSON object out of a model reply, or None.

    Every stage that asks for "ONLY JSON" gets a markdown ```json fence or a
    line of preamble some fraction of the time. One tolerant reader lives here
    so stages cannot disagree about it -- next_steps used a strict json.loads
    and reported "not parseable JSON" on replies concepts would have accepted.
    """
    match = _JSON_BLOCK.search(raw or "")
    if not match:
        return None
    try:
        parsed = json.loads(match.group(0))
    except json.JSONDecodeError:
        return None
    return parsed if isinstance(parsed, dict) else None


def claude_spawn(prompt: str, max_turns: int = 3, timeout: int = 600,
                 tools: str = "") -> str:
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
    for attempt in range(MAX_ATTEMPTS):
        # The prompt goes on stdin, not in argv: Windows caps a command line at
        # ~32,767 characters, so a large prompt died with WinError 206 "The
        # filename or extension is too long" before the model was ever reached.
        # --tools "" because every stage here is a pure text transform: the
        # context is inlined in the prompt and the answer comes back on stdout.
        # Left with the default toolset, the page writer explored the repo and
        # read finished sibling pages (so a page could be built from other
        # pages instead of the supplied evidence), then called Write on the
        # real artifact -- bypassing write_pages and the pedagogy gate, which
        # only ever inspects the returned string. The turn ceiling it hit
        # afterwards was the symptom, not the cause.
        proc = subprocess.run(
            ["claude", "-p", "--max-turns", str(max_turns), "--tools", tools]
            # --tools makes a tool visible; it does not make it usable.
            # With --tools alone the researcher answered "I don't have
            # permission to use WebSearch yet -- could you grant it" for
            # 17 of 18 concepts, each logged as `not parseable JSON`.
            + (["--allowedTools", tools] if tools else []),
            input=prompt,
            capture_output=True, text=True, encoding="utf-8", errors="replace",
            timeout=timeout,
        )
        if proc.returncode == 0:
            return proc.stdout
        # A non-zero exit here is usually transient (rate limit, overload); the
        # not-installed case already returned above and retrying it could only
        # delay the same answer.
        if attempt < MAX_ATTEMPTS - 1:
            time.sleep(BACKOFF_SECONDS * (2 ** attempt))

    # Same contract as a missing CLI: "the model never ran" must not reach
    # callers as "the model returned nothing".
    raise LLMUnavailable(
        f"`claude -p` exited {proc.returncode} on {MAX_ATTEMPTS} attempts, so "
        f"this LLM stage did not run. Do NOT treat this as an empty result. "
        f"CLI said: {(proc.stderr or proc.stdout or '').strip()[:500]}"
    )
