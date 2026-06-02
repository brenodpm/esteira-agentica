import subprocess
import time


def run(
    role: str,
    context_files: list[str],
    prompt: str,
    timeout_s: int = 300,
) -> dict:
    cmd = ["kiro-cli", "chat", "--agent", role, "--no-interactive"]
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


def build_prompt(role: str, issue: dict, rework: bool = False, acao: str | None = None) -> str:
    """Build a structured prompt from a GitHub issue for a specific agent role."""
    number = issue.get("number", "?")
    title = issue.get("title", "")
    body = issue.get("body") or ""

    rework_note = "\n\n> ⚠️ REWORK: esta etapa foi rejeitada. Revise o artefato anterior antes de produzir a nova versão." if rework else ""
    acao_note = f"\n\nAção: {acao}" if acao else ""

    return (
        f"Etapa: {role}\n"
        f"Issue: #{number} — {title}\n"
        f"{acao_note}{rework_note}\n\n"
        f"{body}\n\n"
        f"---\n"
        f"IMPORTANTE: Salve todos os artefatos produzidos em disco usando as ferramentas disponíveis (fs_write). "
        f"Não responda apenas com texto — persista os arquivos conforme descrito no seu papel."
    ).strip()


def _extract_tokens(stdout: str, stderr: str, key: str) -> int | None:
    """Try to parse token counts from CLI output. Returns None if not found."""
    import re
    pattern = rf"{key}[=:\s]+(\d+)"
    for text in (stdout, stderr):
        m = re.search(pattern, text, re.IGNORECASE)
        if m:
            return int(m.group(1))
    return None
