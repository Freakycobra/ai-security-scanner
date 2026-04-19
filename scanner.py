import subprocess
import json
import os
import shutil
import sys
from pathlib import Path
from config import DEFAULT_SEMGREP_CONFIG, CONTEXT_LINES


def _find_semgrep() -> str:
    """Locate the semgrep executable, handles venv and Windows edge cases."""
    # Check PATH first
    found = shutil.which("semgrep")
    if found:
        return found
    # Fallback: look next to the current Python executable (same venv)
    venv_bin = Path(sys.executable).parent
    for name in ("semgrep", "semgrep.exe", "semgrep.cmd"):
        candidate = venv_bin / name
        if candidate.exists():
            return str(candidate)
    raise FileNotFoundError(
        "semgrep not found. Install it with: pip install semgrep"
    )


def run_semgrep(target_path: str, config: str = DEFAULT_SEMGREP_CONFIG) -> list[dict]:
    """Run semgrep against target_path and return parsed findings."""
    target = Path(target_path).resolve()
    if not target.exists():
        raise FileNotFoundError(f"Target path does not exist: {target}")

    semgrep_bin = _find_semgrep()

    cmd = [
        semgrep_bin,
        "scan",
        f"--config={config}",
        "--json",
        "--quiet",
        str(target),
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode not in (0, 1):
        raise RuntimeError(f"Semgrep failed:\n{result.stderr}")

    try:
        data = json.loads(result.stdout)
    except json.JSONDecodeError:
        raise RuntimeError(f"Could not parse semgrep output:\n{result.stdout[:500]}")

    return _parse_findings(data, str(target))


def _parse_findings(semgrep_output: dict, target_root: str) -> list[dict]:
    """Extract relevant fields from raw semgrep output."""
    findings = []
    for r in semgrep_output.get("results", []):
        file_path = r.get("path", "")
        start_line = r.get("start", {}).get("line", 0)
        end_line = r.get("end", {}).get("line", start_line)
        rule_id = r.get("check_id", "unknown")
        message = r.get("extra", {}).get("message", "")
        severity = r.get("extra", {}).get("severity", "WARNING").lower()
        code_snippet = r.get("extra", {}).get("lines", "")

        context = _get_code_context(file_path, start_line, end_line)

        findings.append({
            "file": file_path,
            "line_start": start_line,
            "line_end": end_line,
            "rule_id": rule_id,
            "message": message,
            "severity": severity,
            "code_snippet": code_snippet,
            "context": context,
        })

    return findings


def _get_code_context(file_path: str, start_line: int, end_line: int) -> str:
    """Read CONTEXT_LINES before and after the finding from the source file."""
    try:
        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            lines = f.readlines()

        context_start = max(0, start_line - CONTEXT_LINES - 1)
        context_end = min(len(lines), end_line + CONTEXT_LINES)

        numbered = []
        for i, line in enumerate(lines[context_start:context_end], start=context_start + 1):
            marker = ">>>" if start_line <= i <= end_line else "   "
            numbered.append(f"{marker} {i:4d} | {line.rstrip()}")

        return "\n".join(numbered)
    except (OSError, IOError):
        return ""


def save_raw_results(findings: list[dict], output_path: str = "semgrep_results.json"):
    with open(output_path, "w") as f:
        json.dump(findings, f, indent=2)
