#!/usr/bin/env python3
import argparse
import sys
import os

from scanner import run_semgrep
from triage import triage_all, has_high_or_critical
from fix_generator import generate_fixes
from reporter import build_report, save_json_report, save_html_report, print_summary
from config import OPENAI_API_KEY, DEFAULT_SEMGREP_CONFIG


def parse_args():
    parser = argparse.ArgumentParser(
        description="Scan source code for vulnerabilities using Semgrep + GPT-4o triage",
    )
    parser.add_argument(
        "--target", "-t",
        required=True,
        help="Path to the directory or file to scan",
    )
    parser.add_argument(
        "--config", "-c",
        default=DEFAULT_SEMGREP_CONFIG,
        help=f"Semgrep ruleset config (default: {DEFAULT_SEMGREP_CONFIG})",
    )
    parser.add_argument(
        "--output", "-o",
        default="security_report.html",
        help="Output path for the HTML report (default: security_report.html)",
    )
    parser.add_argument(
        "--no-fix",
        action="store_true",
        help="Skip fix generation (faster, saves API tokens)",
    )
    parser.add_argument(
        "--json-output",
        default="security_report.json",
        help="Output path for the JSON report",
    )
    parser.add_argument(
        "--fail-on-findings",
        action="store_true",
        help="Exit with code 1 if high/critical vulnerabilities are found (for CI use)",
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Show progress during triage and fix generation",
    )
    return parser.parse_args()


def _run_scan(target, config):
    print(f"[1/4] Running Semgrep on {target} (config: {config})...")
    try:
        findings = run_semgrep(target, config=config)
    except (FileNotFoundError, RuntimeError) as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    if not findings:
        print("Semgrep found no issues. All clear.")
        sys.exit(0)

    print(f"       {len(findings)} raw finding(s) from Semgrep")
    return findings


def _run_triage(findings, verbose):
    print(f"[2/4] Triaging findings with LLM...")
    triaged = triage_all(findings, verbose=verbose)

    confirmed_count = sum(1 for f in triaged if not f.get("is_false_positive"))
    fp_count = len(triaged) - confirmed_count
    print(f"       {confirmed_count} confirmed, {fp_count} false positive(s)")

    return triaged, confirmed_count


def _run_fix(triaged, confirmed_count, no_fix, verbose):
    if not no_fix and confirmed_count > 0:
        print(f"[3/4] Generating fixes for confirmed vulnerabilities...")
        triaged = generate_fixes(triaged, verbose=verbose)
    else:
        print(f"[3/4] Skipping fix generation")

    return triaged


def _run_report(triaged, target, json_output, output, fail_on_findings):
    print(f"[4/4] Building report...")
    report = build_report(triaged, target=target)

    json_path = save_json_report(report, json_output)
    html_path = save_html_report(report, output)

    print_summary(report)

    print(f"Reports saved:")
    print(f"  HTML: {html_path}")
    print(f"  JSON: {json_path}")

    if fail_on_findings and has_high_or_critical(triaged):
        sys.exit(1)


def main():
    args = parse_args()

    if not OPENAI_API_KEY:
        print("Error: OPENAI_API_KEY environment variable is not set.", file=sys.stderr)
        sys.exit(1)

    findings = _run_scan(args.target, args.config)
    triaged, confirmed_count = _run_triage(findings, args.verbose)
    triaged = _run_fix(triaged, confirmed_count, args.no_fix, args.verbose)
    _run_report(triaged, args.target, args.json_output, args.output, args.fail_on_findings)


if __name__ == "__main__":
    main()
