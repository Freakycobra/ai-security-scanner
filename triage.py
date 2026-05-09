import concurrent.futures
from openai import OpenAI
from config import OPENAI_API_KEY, OPENAI_MODEL

client = OpenAI(api_key=OPENAI_API_KEY)

RISK_LEVELS = ("low", "medium", "high", "critical")

TRIAGE_SYSTEM_PROMPT = """You are a senior application security engineer doing code review.
Your job is to analyze static analysis findings and determine if they are real, exploitable vulnerabilities or false positives.
Think like a penetration tester — consider the actual data flow, not just the pattern.
Be concise and precise. Do not be alarmist, but do not dismiss real risks."""

TRIAGE_USER_TEMPLATE = """Semgrep flagged a potential vulnerability in this code.

Rule: {rule_id}
File: {file}:{line_start}
Semgrep message: {message}

Code context (>>> marks the flagged lines):
{context}

Answer the following in this exact JSON format:
{{
  "is_false_positive": true/false,
  "risk_level": "low|medium|high|critical",
  "explanation": "1-3 sentence explanation of why this is or isn't exploitable in this specific context",
  "attack_scenario": "If real: describe exactly how an attacker would exploit this. If false positive: leave empty string."
}}

Only output valid JSON, nothing else."""


def triage_finding(finding: dict) -> dict:
    """Send a single finding to the LLM for triage. Returns enriched finding dict."""
    prompt = TRIAGE_USER_TEMPLATE.format(
        rule_id=finding["rule_id"],
        file=finding["file"],
        line_start=finding["line_start"],
        message=finding["message"],
        context=finding["context"] or finding["code_snippet"],
    )

    try:
        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": TRIAGE_SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            temperature=0.1,
            response_format={"type": "json_object"},
        )

        import json
        result = json.loads(response.choices[0].message.content)

        return {
            **finding,
            "is_false_positive": result.get("is_false_positive", False),
            "risk_level": result.get("risk_level", "medium").lower(),
            "explanation": result.get("explanation", ""),
            "attack_scenario": result.get("attack_scenario", ""),
            "triage_status": "false_positive" if result.get("is_false_positive") else "confirmed",
        }

    except Exception as e:
        return {
            **finding,
            "is_false_positive": False,
            "risk_level": "medium",
            "explanation": f"Triage failed: {str(e)}",
            "attack_scenario": "",
            "triage_status": "error",
        }


def triage_all(findings: list[dict], verbose: bool = False) -> list[dict]:
    """Triage all findings in parallel. Returns list with triage results attached."""
    triaged = [None] * len(findings)
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_index = {
            executor.submit(triage_finding, finding): i
            for i, finding in enumerate(findings)
        }

        completed = 0
        for future in concurrent.futures.as_completed(future_to_index):
            i = future_to_index[future]
            completed += 1
            if verbose:
                finding = findings[i]
                print(f"  triaged [{completed}/{len(findings)}]: {finding['file']}:{finding['line_start']}")
            triaged[i] = future.result()

    return triaged


def filter_confirmed(findings: list[dict]) -> list[dict]:
    """Return only non-false-positive findings."""
    return [f for f in findings if not f.get("is_false_positive", False)]


def has_high_or_critical(findings: list[dict]) -> bool:
    """Check if any confirmed finding is high or critical severity."""
    from config import FAILING_RISK_LEVELS
    confirmed = filter_confirmed(findings)
    return any(f.get("risk_level", "").lower() in FAILING_RISK_LEVELS for f in confirmed)
