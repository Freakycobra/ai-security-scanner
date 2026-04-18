# AI Security Scanner

Scans source code for security vulnerabilities by layering static analysis with LLM-powered triage. Semgrep catches the patterns, GPT-4o decides what's actually exploitable — and generates a fix.

## How it works

1. **Semgrep** scans the target codebase and flags suspicious patterns
2. **Triage Agent** sends each finding + surrounding code to GPT-4o to verify exploitability
3. **Fix Generator** produces a corrected code snippet for confirmed vulnerabilities
4. **Reporter** outputs a structured security report (JSON + HTML)

## Setup

```bash
pip install -r requirements.txt
```

Install Semgrep:
```bash
pip install semgrep
```

Set your OpenAI key:
```bash
export OPENAI_API_KEY=your_key_here
```

## Usage

```bash
# Scan a directory
python main.py --target ./path/to/code

# Scan with custom semgrep config
python main.py --target ./path/to/code --config p/python

# Output report to file
python main.py --target ./path/to/code --output report.html
```

## Output

- Console summary with risk levels (Low / Medium / High / Critical)
- `security_report.json` — raw findings with LLM analysis
- `security_report.html` — human-readable report

## CI/CD

Includes a GitHub Actions workflow that runs on every push. Fails the build if any High or Critical vulnerabilities are confirmed.

## Tech Stack

- Python 3.10+
- [Semgrep](https://semgrep.dev/) — static analysis
- OpenAI GPT-4o — triage and fix generation
- GitHub Actions — CI/CD integration
