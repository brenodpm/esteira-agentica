import subprocess
import time

AGENT_ROLES: list[str] = [
    "product",
    "requirements",
    "architecture",
    "engineering",
    "quality",
    "operations",
]


def run(
    role: str,
    context_files: list[str],
    prompt: str,
    timeout_s: int = 300,
) -> dict:
    cmd = ["kiro", "chat", "--agent", role]
    for path in context_files:
        cmd += ["--context", path]

    start = time.monotonic()
    try:
        result = subprocess.run(
            cmd,
            input=prompt,
            capture_output=True,
            text=True,
            timeout=timeout_s,
            check=True,
        )
    except subprocess.TimeoutExpired:
        raise TimeoutError(f"Agent '{role}' exceeded timeout of {timeout_s}s")
    except subprocess.CalledProcessError as exc:
        raise RuntimeError(exc.stderr)

    duration_s = time.monotonic() - start
    output = result.stdout

    tokens_in = _extract_tokens(result.stdout, result.stderr, "tokens_in")
    tokens_out = _extract_tokens(result.stdout, result.stderr, "tokens_out")

    return {
        "output": output,
        "tokens_in": tokens_in,
        "tokens_out": tokens_out,
        "duration_s": duration_s,
    }


def _extract_tokens(stdout: str, stderr: str, key: str) -> int | None:
    """Try to parse token counts from CLI output. Returns None if not found."""
    import re
    pattern = rf"{key}[=:\s]+(\d+)"
    for text in (stdout, stderr):
        m = re.search(pattern, text, re.IGNORECASE)
        if m:
            return int(m.group(1))
    return None
