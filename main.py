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


def main():
    args = parse_args()

    if not OPENAI_API_KEY:
        print("Error: OPENAI_API_KEY environment variable is not set.", file=sys.stderr)
        sys.exit(1)

    print(f"[1/4] Running Semgrep on {args.target} (config: {args.config})...")
    try:
        findings = run_semgrep(args.target, config=args.config)
    except (FileNotFoundError, RuntimeError) as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    if not findings:
        print("Semgrep found no issues. All clear.")
        sys.exit(0)

    print(f"       {len(findings)} raw finding(s) from Semgrep")

    print(f"[2/4] Triaging findings with LLM...")
    triaged = triage_all(findings, verbose=args.verbose)

    confirmed_count = sum(1 for f in triaged if not f.get("is_false_positive"))
    fp_count = len(triaged) - confirmed_count
    print(f"       {confirmed_count} confirmed, {fp_count} false positive(s)")

    if not args.no_fix and confirmed_count > 0:
        print(f"[3/4] Generating fixes for confirmed vulnerabilities...")
        triaged = generate_fixes(triaged, verbose=args.verbose)
    else:
        print(f"[3/4] Skipping fix generation")

    print(f"[4/4] Building report...")
    report = build_report(triaged, target=args.target)

    json_path = save_json_report(report, args.json_output)
    html_path = save_html_report(report, args.output)

    print_summary(report)

    print(f"Reports saved:")
    print(f"  HTML: {html_path}")
    print(f"  JSON: {json_path}")

    if args.fail_on_findings and has_high_or_critical(triaged):
        sys.exit(1)


if __name__ == "__main__":
    main()
