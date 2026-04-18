import os

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

# how many lines of context to send around each finding
CONTEXT_LINES = 10

# semgrep default ruleset
DEFAULT_SEMGREP_CONFIG = "auto"

# risk levels that should fail CI
FAILING_RISK_LEVELS = {"high", "critical"}
