"""Policy enforcement logic - risk assessment and confirmation prompts.

Determines when execution requires user confirmation and handles the
confirmation flow.
"""

from __future__ import annotations

import sys

from policy.profile import Profile


def assess_risk(
    profile: Profile,
    stdin_used: bool,
    instructions_file_used: bool,
    force_confirm: bool = False,
) -> tuple[bool, list[str]]:
    """Determine if execution requires user confirmation based on risk triggers.

    Risk triggers:
    1. Input from stdin (non-interactive) or file
    2. Profile is not "safe"
    3. Environment exposure enabled
    4. Network enabled
    5. Shell execution allowed
    6. Force confirmation flag set

    Args:
        profile: Policy profile being used
        stdin_used: True if stdin is non-tty (piped input)
        instructions_file_used: True if prompt read from file
        force_confirm: Force confirmation even if otherwise safe

    Returns:
        Tuple of (requires_confirmation, reasons)
        where reasons is list of human-readable trigger descriptions
    """
    reasons = []

    if force_confirm:
        reasons.append("Explicit confirmation requested (--confirm)")

    if stdin_used:
        reasons.append("Input from stdin (non-interactive)")

    if instructions_file_used:
        reasons.append("Prompt loaded from file")

    if profile.name != "safe":
        reasons.append(f"Non-safe profile '{profile.name}' in use")

    if profile.allow_env:
        reasons.append("Environment variable access enabled")

    if profile.network:
        reasons.append("Network access enabled")

    if not profile.deny_shell:
        reasons.append("Shell execution allowed")

    return (len(reasons) > 0, reasons)


def prompt_confirmation(
    policy_summary: str,
    reasons: list[str],
) -> bool:
    """Display policy summary and prompt for user confirmation.

    Args:
        policy_summary: Formatted policy summary from profile.summarize()
        reasons: List of risk trigger reasons

    Returns:
        True if user confirms, False otherwise

    Notes:
        - Writes to stderr (not stdout)
        - Handles Ctrl+C gracefully (returns False)
        - Default answer is No (safe)
    """
    print(policy_summary, file=sys.stderr)
    print(file=sys.stderr)

    if reasons:
        print("⚠  This execution requires confirmation due to:", file=sys.stderr)
        for reason in reasons:
            print(f"   - {reason}", file=sys.stderr)
        print(file=sys.stderr)

    try:
        response = input("Proceed? [y/N] ").strip().lower()
        return response in ("y", "yes")
    except (EOFError, KeyboardInterrupt):
        print("\nAborted.", file=sys.stderr)
        return False
