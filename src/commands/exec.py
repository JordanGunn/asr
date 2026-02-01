"""Execute a skill from the registry using an agent CLI."""

import argparse
import sys
from pathlib import Path

from agents.registry import detect_available_agents, get_driver
from config import load_config
from registry import load_registry


def register(subparsers):
    """Register the exec command."""
    setup_parser(subparsers)


def setup_parser(subparsers):
    """Set up the exec command parser."""
    parser = subparsers.add_parser(
        "exec",
        help="Execute a skill from the registry",
        description="Execute a skill from the registry using an agent CLI. "
        "The skill is executed in the current working directory.",
    )
    parser.add_argument(
        "skill_name",
        help="Name of the skill to execute from the registry",
    )
    parser.add_argument(
        "-p",
        "--prompt",
        help="Inline prompt/instructions for the agent",
    )
    parser.add_argument(
        "-i",
        "--instructions",
        metavar="FILE",
        help="Read prompt/instructions from a file",
    )
    parser.add_argument(
        "-a",
        "--agent",
        help="Override the default agent (codex, copilot, claude, opencode)",
    )
    parser.set_defaults(func=run)


def run(args: argparse.Namespace) -> int:
    """Execute a skill from the registry."""
    # Load registry to find the skill
    entries = load_registry()
    entry_map = {e.name: e for e in entries}
    skill_name = args.skill_name

    if skill_name not in entry_map:
        print(f"Error: Skill '{skill_name}' not found in registry", file=sys.stderr)
        print("\nUse 'oasr registry list' to see available skills.", file=sys.stderr)
        return 1

    skill_entry = entry_map[skill_name]
    skill_source = skill_entry.path

    if not skill_source:
        print(f"Error: Skill '{skill_name}' has no source configured", file=sys.stderr)
        return 1

    # Get the skill content - look for SKILL.md in the skill directory
    skill_dir = Path(skill_source)
    skill_path = skill_dir / "SKILL.md"

    if not skill_path.exists():
        print(f"Error: Skill file not found: {skill_path}", file=sys.stderr)
        print("\nTry running 'oasr sync' to update your skills.", file=sys.stderr)
        return 1

    try:
        skill_content = skill_path.read_text(encoding="utf-8")
    except Exception as e:
        print(f"Error reading skill file: {e}", file=sys.stderr)
        return 1

    # Get the user prompt from various sources
    user_prompt = _get_user_prompt(args)
    if user_prompt is None:
        # Error already printed by _get_user_prompt
        return 1

    # Determine which agent to use
    agent_name = _get_agent_name(args)
    if agent_name is None:
        # Error already printed by _get_agent_name
        return 1

    # Get the agent driver
    try:
        driver = get_driver(agent_name)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    # Execute the skill
    print(f"Executing skill '{skill_name}' with {agent_name}...", file=sys.stderr)
    print("━" * 60, file=sys.stderr)

    try:
        result = driver.execute(skill_content, user_prompt)
        # CompletedProcess has returncode attribute (0 = success)
        # Output was already streamed to stdout since capture_output=False
        return result.returncode
    except Exception as e:
        print(f"\nUnexpected error: {e}", file=sys.stderr)
        return 1


def _get_user_prompt(args: argparse.Namespace) -> str | None:
    """Get the user prompt from CLI args or stdin.

    Returns None if there's an error, with error message printed to stderr.
    """
    # Check for conflicting options
    if args.prompt and args.instructions:
        print(
            "Error: Cannot use both --prompt and --instructions at the same time",
            file=sys.stderr,
        )
        return None

    # Option 1: Inline prompt via -p/--prompt
    if args.prompt:
        return args.prompt

    # Option 2: File-based instructions via -i/--instructions
    if args.instructions:
        instructions_path = Path(args.instructions)
        if not instructions_path.exists():
            print(f"Error: Instructions file not found: {args.instructions}", file=sys.stderr)
            return None

        try:
            return instructions_path.read_text(encoding="utf-8")
        except Exception as e:
            print(f"Error reading instructions file: {e}", file=sys.stderr)
            return None

    # Option 3: Read from stdin
    if not sys.stdin.isatty():
        try:
            return sys.stdin.read()
        except Exception as e:
            print(f"Error reading from stdin: {e}", file=sys.stderr)
            return None

    # No prompt provided
    print("Error: No prompt provided", file=sys.stderr)
    print("\nProvide a prompt using one of:", file=sys.stderr)
    print("  -p/--prompt 'Your prompt here'", file=sys.stderr)
    print("  -i/--instructions path/to/file.txt", file=sys.stderr)
    print("  echo 'Your prompt' | oasr exec <skill>", file=sys.stderr)
    return None


def _get_agent_name(args: argparse.Namespace) -> str | None:
    """Get the agent name from CLI flag or config.

    Returns None if there's an error, with error message printed to stderr.
    """
    # Option 1: Explicit --agent flag
    if args.agent:
        agent_name = args.agent.lower()
        # Validate it's a known and available agent
        available = detect_available_agents()
        if agent_name not in available or not available[agent_name]:
            print(f"Error: Agent '{agent_name}' is not available", file=sys.stderr)
            print("\nAvailable agents:", file=sys.stderr)
            for name in sorted(available.keys()):
                status = "✓" if available[name] else "✗"
                print(f"  {status} {name}", file=sys.stderr)
            return None
        return agent_name

    # Option 2: Default from config
    config = load_config()
    default_agent = config.get("agent", {}).get("default")

    if default_agent:
        return default_agent

    # No agent configured
    print("Error: No agent configured", file=sys.stderr)
    print("\nConfigure a default agent with:", file=sys.stderr)
    print("  oasr config set agent <agent-name>", file=sys.stderr)
    print("\nOr specify an agent for this command:", file=sys.stderr)
    print("  oasr exec --agent <agent-name> <skill>", file=sys.stderr)
    print("\nAvailable agents:", file=sys.stderr)
    available = detect_available_agents()
    for name in sorted(available.keys()):
        status = "✓" if available[name] else "✗"
        print(f"  {status} {name}", file=sys.stderr)
    return None
