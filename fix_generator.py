from openai import OpenAI
from config import OPENAI_API_KEY, OPENAI_MODEL

client = OpenAI(api_key=OPENAI_API_KEY)

FIX_SYSTEM_PROMPT = """You are a senior security engineer.
Your job is to fix security vulnerabilities in code.
Write clean, idiomatic fixes using security best practices.
Return only the fixed code snippet — no explanations, no markdown fences, no extra text."""

FIX_USER_TEMPLATE = """Fix this security vulnerability:

Vulnerability: {rule_id}
Risk: {risk_level}
Issue: {explanation}

Original code:
{context}

Return only the corrected code snippet that fixes the vulnerability."""


def generate_fix(finding: dict) -> dict:
    """Generate a code fix for a confirmed vulnerability. Returns finding with fix attached."""
    if finding.get("is_false_positive"):
        return {**finding, "fix": None}

    prompt = FIX_USER_TEMPLATE.format(
        rule_id=finding["rule_id"],
        risk_level=finding.get("risk_level", "unknown"),
        explanation=finding.get("explanation", finding["message"]),
        context=finding.get("context") or finding.get("code_snippet", ""),
    )

    try:
        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": FIX_SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            temperature=0.1,
        )
        fix = response.choices[0].message.content.strip()
        # strip accidental markdown code fences if the model adds them
        if fix.startswith("```"):
            lines = fix.split("\n")
            fix = "\n".join(lines[1:-1]) if lines[-1].strip() == "```" else "\n".join(lines[1:])

        return {**finding, "fix": fix}

    except Exception as e:
        return {**finding, "fix": f"Fix generation failed: {str(e)}"}


def generate_fixes(findings: list[dict], verbose: bool = False) -> list[dict]:
    """Generate fixes for all confirmed (non-false-positive) findings."""
    result = []
    confirmed = [f for f in findings if not f.get("is_false_positive", False)]
    skipped = [f for f in findings if f.get("is_false_positive", False)]

    for i, finding in enumerate(confirmed, 1):
        if verbose:
            print(f"  generating fix [{i}/{len(confirmed)}]: {finding['file']}:{finding['line_start']}")
        result.append(generate_fix(finding))

    # false positives pass through without a fix
    result.extend(skipped)
    return result
