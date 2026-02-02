"""Execution policy system for OASR.

Enforces host-level security boundaries for skill execution by defining what
agents can and cannot do. Policy profiles are user-defined in config.toml and
enforced at runtime before agent invocation.

Usage:
    import policy

    # Load profile from config
    profile = policy.load(config, "safe")

    # Assess risk
    needs_confirm, reasons = policy.assess_risk(
        profile,
        stdin_used=True,
        instructions_file_used=False
    )

    # Get confirmation if needed
    if needs_confirm:
        summary = policy.summarize(profile, skill_name, agent_name)
        if not policy.prompt_confirmation(summary, reasons):
            return 1  # aborted

This module does NOT:
- Detect prompt injection via NLP
- Rewrite or sanitize prompts
- Validate skill correctness
- Implement agent-specific permissions

It DOES:
- Load and validate policy profiles from config
- Assess execution risk based on context
- Require explicit confirmation for risky operations
- Fail closed with conservative defaults
"""

from policy.defaults import SAFE as SAFE_DEFAULTS
from policy.enforcement import assess_risk, prompt_confirmation
from policy.profile import Profile, load, summarize

__all__ = [
    "Profile",
    "load",
    "summarize",
    "assess_risk",
    "prompt_confirmation",
    "SAFE_DEFAULTS",
]
