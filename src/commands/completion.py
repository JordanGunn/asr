"""Shell completion management for OASR."""

import os
import platform
import sys
from pathlib import Path

from config import load_config


def register_parser(subparsers):
    """Register the completion subcommand."""
    parser = subparsers.add_parser(
        "completion",
        help="Generate and install shell completions",
        description="Generate shell completion scripts for bash, zsh, fish, and PowerShell.",
    )

    parser.add_argument(
        "shell",
        nargs="?",
        choices=["bash", "zsh", "fish", "powershell", "install", "uninstall"],
        help="Shell type or action (install/uninstall)",
    )

    parser.add_argument(
        "--force",
        action="store_true",
        help="Force installation even if already installed",
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without doing it",
    )

    parser.add_argument(
        "--install",
        action="store_true",
        help="Install completions for the specified shell",
    )

    parser.set_defaults(func=run)


def detect_shell():
    """
    Auto-detect the user's shell based on platform and environment.

    Returns:
        str: Shell name (bash, zsh, fish, powershell)
    """
    if platform.system() == "Windows":
        shell_env = os.environ.get("SHELL", "").lower()
        if "bash" in shell_env:
            return "bash"
        # Check for PowerShell
        if "PSModulePath" in os.environ or "POWERSHELL" in os.environ.get("SHELL", "").upper():
            return "powershell"
        if "zsh" in shell_env:
            return "zsh"
        if "fish" in shell_env:
            return "fish"
        # Default to PowerShell on Windows
        return "powershell"
    else:
        # Linux/macOS
        shell = os.environ.get("SHELL", "")
        if "zsh" in shell:
            return "zsh"
        elif "fish" in shell:
            return "fish"
        else:
            # Default to bash on Unix
            return "bash"


def get_completion_script(shell):
    """
    Get the completion script content for the specified shell.

    Args:
        shell: Shell name (bash, zsh, fish, powershell)

    Returns:
        str: Completion script content
    """
    # Map shell names to completion files
    script_files = {
        "bash": "bash.sh",
        "zsh": "zsh.sh",
        "fish": "fish.fish",
        "powershell": "powershell.ps1",
    }

    if shell not in script_files:
        return ""

    # Get the path to the completion script
    completion_file = Path(__file__).parent.parent / "completions" / script_files[shell]

    if not completion_file.exists():
        return f"# {shell} completion script not found"

    return completion_file.read_text()


def get_completion_path(shell, system=False):
    """
    Get the installation path for completion script.

    Args:
        shell: Shell name
        system: If True, use system-wide path (requires root)

    Returns:
        Path: Installation path
    """
    paths = {
        "bash": {
            "user": Path.home() / ".bash_completion.d" / "oasr",
            "system": Path("/etc/bash_completion.d/oasr"),
        },
        "zsh": {
            "user": Path.home() / ".zsh" / "completion" / "_oasr",
            "system": Path("/usr/local/share/zsh/site-functions/_oasr"),
        },
        "fish": {
            "user": Path.home() / ".config" / "fish" / "completions" / "oasr.fish",
            "system": Path("/usr/share/fish/vendor_completions.d/oasr.fish"),
        },
        "powershell": {
            "user": Path.home() / ".config" / "powershell" / "oasr_completion.ps1",
            "system": Path.home() / ".config" / "powershell" / "oasr_completion.ps1",
        },
    }

    level = "system" if system else "user"
    return paths.get(shell, {}).get(level)


def print_activation_instructions(shell, path):
    """
    Print instructions for activating completions.

    Args:
        shell: Shell name
        path: Installation path
    """
    instructions = {
        "bash": f"""
✓ Completions installed for bash

To activate, add this to your ~/.bashrc:
    source {path}

Or run:
    echo 'source {path}' >> ~/.bashrc

Then restart your shell or run:
    source ~/.bashrc
""",
        "zsh": f"""
✓ Completions installed for zsh

To activate, add this to your ~/.zshrc:
    fpath=({path.parent} $fpath)
    autoload -Uz compinit && compinit

Then restart your shell or run:
    source ~/.zshrc
""",
        "fish": f"""
✓ Completions installed for fish

Completions will be active in new fish shells.
To activate now, run:
    source {path}
""",
        "powershell": f"""
✓ Completions installed for PowerShell

To activate, add this to your PowerShell profile ($PROFILE):
    . {path}

Or run:
    echo '. {path}' >> $PROFILE

Then restart PowerShell or run:
    . $PROFILE
""",
    }

    print(instructions.get(shell, ""))


def is_already_installed(shell):
    """
    Check if completions are already installed for the shell.

    Args:
        shell: Shell name

    Returns:
        bool: True if already installed
    """
    path = get_completion_path(shell)
    if not path or not path.exists():
        return False

    # Check for our signature
    with open(path) as f:
        content = f.read()
        return "# oasr completion" in content.lower()


def run_output(shell):
    """
    Output the completion script to stdout.

    Args:
        shell: Shell name

    Returns:
        int: Exit code
    """
    script = get_completion_script(shell)
    print(script)
    return 0


def run_install(args):
    """
    Install completion script.

    Args:
        args: Parsed arguments

    Returns:
        int: Exit code
    """
    shell = args.shell if args.shell != "install" else detect_shell()
    if not shell:
        print("Error: No shell specified for install", file=sys.stderr)
        return 1

    # Check config
    config = load_config()
    if not config.get("oasr", {}).get("completions", True):
        print("Completions are disabled in config (oasr.completions = false)")
        return 1

    # Check if already installed
    if is_already_installed(shell) and not args.force:
        print(f"✓ Completions already installed for {shell}")
        print("  Use --force to reinstall")
        return 0

    # Get paths
    path = get_completion_path(shell)
    if not path:
        print(f"Error: Unsupported shell: {shell}", file=sys.stderr)
        return 1

    # Dry run
    if args.dry_run:
        print(f"Would install completion to: {path}")
        print_activation_instructions(shell, path)
        return 0

    # Get script
    script = get_completion_script(shell)

    # Create directory
    path.parent.mkdir(parents=True, exist_ok=True)

    # Backup existing
    if path.exists() and not is_already_installed(shell):
        import time

        backup = path.parent / f"{path.name}.backup.{int(time.time())}"
        path.rename(backup)
        print(f"Backed up existing file to: {backup}")

    # Write script
    path.write_text(script)

    # Success message
    print_activation_instructions(shell, path)

    return 0


def run_uninstall(args):
    """
    Uninstall completion script.

    Args:
        args: Parsed arguments

    Returns:
        int: Exit code
    """
    shell = args.shell if args.shell != "uninstall" else detect_shell()
    if not shell:
        print("Error: No shell specified for uninstall", file=sys.stderr)
        return 1

    path = get_completion_path(shell)
    if not path or not path.exists():
        print(f"No completions installed for {shell}")
        return 0

    # Dry run
    if args.dry_run:
        print(f"Would remove: {path}")
        return 0

    # Remove file
    path.unlink()
    print(f"✓ Removed completions for {shell}")

    return 0


def run(args):
    """
    Execute completion command.

    Args:
        args: Parsed arguments

    Returns:
        int: Exit code
    """
    # No shell specified - show help
    if not args.shell:
        detected = detect_shell()
        print(f"Detected shell: {detected}")
        print("\nUsage:")
        print("  oasr completion bash          # Output bash completion script")
        print("  oasr completion zsh           # Output zsh completion script")
        print("  oasr completion fish          # Output fish completion script")
        print("  oasr completion powershell    # Output PowerShell completion script")
        print("  oasr completion zsh --install # Install completions for shell")
        print("  oasr completion install       # Auto-detect and install")
        print("  oasr completion uninstall     # Remove installed completions")
        return 0

    # Handle actions
    if args.shell == "install" or (args.install and args.shell in {"bash", "zsh", "fish", "powershell"}):
        return run_install(args)
    elif args.shell == "uninstall":
        return run_uninstall(args)
    else:
        # Output script to stdout
        return run_output(args.shell)
