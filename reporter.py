import json
from datetime import datetime
from pathlib import Path
from jinja2 import Template


REPORT_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Security Scan Report</title>
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: #0f1117; color: #e2e8f0; }
  .header { background: #1a1d27; border-bottom: 1px solid #2d3748; padding: 24px 40px; }
  .header h1 { font-size: 22px; font-weight: 600; }
  .header .meta { font-size: 13px; color: #718096; margin-top: 4px; }
  .summary { display: flex; gap: 16px; padding: 24px 40px; background: #13151f; border-bottom: 1px solid #2d3748; flex-wrap: wrap; }
  .badge { padding: 8px 16px; border-radius: 6px; font-size: 13px; font-weight: 600; }
  .badge.critical { background: #4a1010; color: #fc8181; border: 1px solid #9b1c1c; }
  .badge.high     { background: #3d1f08; color: #f6ad55; border: 1px solid #9c4221; }
  .badge.medium   { background: #3d3108; color: #faf089; border: 1px solid #975a16; }
  .badge.low      { background: #0f2a1a; color: #68d391; border: 1px solid #276749; }
  .badge.fp       { background: #1a1d27; color: #718096; border: 1px solid #4a5568; }
  .content { padding: 24px 40px; }
  .section-title { font-size: 16px; font-weight: 600; margin-bottom: 16px; color: #a0aec0; text-transform: uppercase; letter-spacing: 0.05em; font-size: 12px; }
  .finding { background: #1a1d27; border: 1px solid #2d3748; border-radius: 8px; margin-bottom: 16px; overflow: hidden; }
  .finding.critical { border-left: 4px solid #fc8181; }
  .finding.high     { border-left: 4px solid #f6ad55; }
  .finding.medium   { border-left: 4px solid #faf089; }
  .finding.low      { border-left: 4px solid #68d391; }
  .finding.false_positive { border-left: 4px solid #4a5568; opacity: 0.6; }
  .finding-header { padding: 14px 18px; display: flex; justify-content: space-between; align-items: flex-start; gap: 12px; }
  .finding-title { font-size: 14px; font-weight: 600; }
  .finding-loc { font-size: 12px; color: #718096; margin-top: 3px; font-family: monospace; }
  .risk-tag { font-size: 11px; font-weight: 700; padding: 3px 8px; border-radius: 4px; text-transform: uppercase; white-space: nowrap; }
  .risk-tag.critical { background: #9b1c1c; color: #fed7d7; }
  .risk-tag.high     { background: #9c4221; color: #feebc8; }
  .risk-tag.medium   { background: #975a16; color: #fefcbf; }
  .risk-tag.low      { background: #276749; color: #c6f6d5; }
  .risk-tag.fp       { background: #2d3748; color: #a0aec0; }
  .finding-body { padding: 0 18px 16px; }
  .explanation { font-size: 13px; color: #cbd5e0; line-height: 1.6; margin-bottom: 10px; }
  .attack-scenario { font-size: 13px; color: #fc8181; background: #1f1010; border: 1px solid #9b1c1c; border-radius: 4px; padding: 10px 12px; margin-bottom: 10px; }
  .attack-scenario strong { display: block; margin-bottom: 4px; color: #fc8181; font-size: 11px; text-transform: uppercase; letter-spacing: 0.05em; }
  details { margin-top: 8px; }
  summary { font-size: 12px; color: #718096; cursor: pointer; user-select: none; padding: 4px 0; }
  summary:hover { color: #a0aec0; }
  pre { background: #0d0f16; border: 1px solid #2d3748; border-radius: 4px; padding: 12px; font-size: 12px; overflow-x: auto; margin-top: 8px; color: #e2e8f0; line-height: 1.5; white-space: pre; }
  .fix-code { background: #0a1a10; border-color: #276749; color: #c6f6d5; }
  .no-findings { text-align: center; padding: 60px; color: #718096; }
</style>
</head>
<body>
<div class="header">
  <h1>Security Scan Report</h1>
  <div class="meta">Target: {{ target }} &nbsp;|&nbsp; {{ scan_time }} &nbsp;|&nbsp; {{ total }} finding(s) from Semgrep, {{ confirmed }} confirmed by LLM triage</div>
</div>

<div class="summary">
  {% if counts.critical %}<div class="badge critical">{{ counts.critical }} Critical</div>{% endif %}
  {% if counts.high %}<div class="badge high">{{ counts.high }} High</div>{% endif %}
  {% if counts.medium %}<div class="badge medium">{{ counts.medium }} Medium</div>{% endif %}
  {% if counts.low %}<div class="badge low">{{ counts.low }} Low</div>{% endif %}
  {% if counts.false_positive %}<div class="badge fp">{{ counts.false_positive }} False Positive</div>{% endif %}
  {% if not counts.critical and not counts.high and not counts.medium and not counts.low %}
    <div class="badge low">No confirmed vulnerabilities</div>
  {% endif %}
</div>

<div class="content">

{% if confirmed_findings %}
<div class="section-title">Confirmed Vulnerabilities</div>
{% for f in confirmed_findings %}
<div class="finding {{ f.risk_level }}">
  <div class="finding-header">
    <div>
      <div class="finding-title">{{ f.rule_id.split('.')[-1] | replace('-', ' ') | title }}</div>
      <div class="finding-loc">{{ f.file }}:{{ f.line_start }}</div>
    </div>
    <span class="risk-tag {{ f.risk_level }}">{{ f.risk_level }}</span>
  </div>
  <div class="finding-body">
    <div class="explanation">{{ f.explanation }}</div>
    {% if f.attack_scenario %}
    <div class="attack-scenario">
      <strong>Attack scenario</strong>
      {{ f.attack_scenario }}
    </div>
    {% endif %}
    {% if f.context %}
    <details>
      <summary>View code context</summary>
      <pre>{{ f.context | e }}</pre>
    </details>
    {% endif %}
    {% if f.fix %}
    <details>
      <summary>View suggested fix</summary>
      <pre class="fix-code">{{ f.fix | e }}</pre>
    </details>
    {% endif %}
  </div>
</div>
{% endfor %}
{% endif %}

{% if fp_findings %}
<div class="section-title" style="margin-top: 32px;">False Positives</div>
{% for f in fp_findings %}
<div class="finding false_positive">
  <div class="finding-header">
    <div>
      <div class="finding-title">{{ f.rule_id.split('.')[-1] | replace('-', ' ') | title }}</div>
      <div class="finding-loc">{{ f.file }}:{{ f.line_start }}</div>
    </div>
    <span class="risk-tag fp">False Positive</span>
  </div>
  <div class="finding-body">
    <div class="explanation" style="color: #718096;">{{ f.explanation }}</div>
  </div>
</div>
{% endfor %}
{% endif %}

{% if not confirmed_findings and not fp_findings %}
<div class="no-findings">No findings to display.</div>
{% endif %}

</div>
</body>
</html>
"""


def build_report(findings: list[dict], target: str) -> dict:
    """Build a structured report dict from triaged + fixed findings."""
    confirmed = [f for f in findings if not f.get("is_false_positive", False)]
    false_positives = [f for f in findings if f.get("is_false_positive", False)]

    risk_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    confirmed.sort(key=lambda x: risk_order.get(x.get("risk_level", "low"), 4))

    counts = {"critical": 0, "high": 0, "medium": 0, "low": 0, "false_positive": len(false_positives)}
    for f in confirmed:
        level = f.get("risk_level", "low")
        if level in counts:
            counts[level] += 1

    return {
        "target": target,
        "scan_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "total": len(findings),
        "confirmed": len(confirmed),
        "counts": counts,
        "confirmed_findings": confirmed,
        "fp_findings": false_positives,
    }


def save_json_report(report: dict, path: str = "security_report.json"):
    with open(path, "w") as f:
        json.dump(report, f, indent=2)
    return path


def save_html_report(report: dict, path: str = "security_report.html"):
    tmpl = Template(REPORT_TEMPLATE)
    html = tmpl.render(**report)
    with open(path, "w", encoding="utf-8") as f:
        f.write(html)
    return path


def print_summary(report: dict):
    from rich.console import Console
    from rich.table import Table
    from rich import box

    console = Console()
    c = report["counts"]

    console.print(f"\n[bold]Scan complete[/bold] — {report['total']} findings, {report['confirmed']} confirmed\n")

    if not report["confirmed_findings"]:
        console.print("[green]No confirmed vulnerabilities.[/green]\n")
        return

    table = Table(box=box.SIMPLE, show_header=True, header_style="bold dim")
    table.add_column("Risk", width=10)
    table.add_column("File", width=50)
    table.add_column("Line", width=6)
    table.add_column("Rule", width=40)

    colors = {"critical": "red", "high": "yellow", "medium": "bright_yellow", "low": "green"}

    for f in report["confirmed_findings"]:
        lvl = f.get("risk_level", "low")
        color = colors.get(lvl, "white")
        table.add_row(
            f"[{color}]{lvl.upper()}[/{color}]",
            f["file"],
            str(f["line_start"]),
            f["rule_id"].split(".")[-1],
        )

    console.print(table)

    if c["critical"] or c["high"]:
        console.print(f"[red bold]FAILED[/red bold] — {c['critical']} critical, {c['high']} high severity issues found.\n")
    else:
        console.print(f"[green]PASSED[/green] — no high/critical issues.\n")
