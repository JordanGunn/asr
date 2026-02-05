"""Centralized output formatting for OASR CLI."""

from __future__ import annotations

import json as _json
import sys
import threading
import time
from typing import TextIO

_use_color: bool = True
_use_unicode: bool = True
_quiet: bool = False

EXIT_SUCCESS = 0
EXIT_FAILURE = 1
EXIT_USAGE = 2
EXIT_UNEXPECTED = 3
EXIT_INTERRUPT = 130


def configure(*, color: bool = True, unicode: bool = True, quiet: bool = False) -> None:
    """Configure output settings. Called once from cli.py."""
    global _use_color, _use_unicode, _quiet
    _use_color = color and sys.stderr.isatty()
    _use_unicode = unicode
    _quiet = quiet


def is_interactive() -> bool:
    """Return True when stdin/stdout are TTY (safe for interactive prompts)."""
    return sys.stdin.isatty() and sys.stdout.isatty()


def json_enabled(value: object) -> bool:
    """Return True when JSON output is requested."""
    return bool(value)


def json_v2(value: object) -> bool:
    """Return True when JSON v2 output is requested."""
    return value == "v2"


def json_v1(value: object) -> bool:
    """Return True when JSON v1 output is requested."""
    return bool(value) and value != "v2"


def unicode_enabled() -> bool:
    """Return True when unicode output is enabled."""
    return _use_unicode


SYMBOLS_UNICODE = {
    "success": "✓",
    "warning": "⚠",
    "error": "✗",
    "checking": "↓",
    "updating": "↻",
    "unknown": "?",
    "bullet": "•",
    "arrow": "→",
}

SYMBOLS_ASCII = {
    "success": "[OK]",
    "warning": "[!]",
    "error": "[X]",
    "checking": "[v]",
    "updating": "[~]",
    "unknown": "[?]",
    "bullet": "*",
    "arrow": "->",
}


def symbol(key: str) -> str:
    """Return the symbol for key, respecting unicode mode."""
    symbols = SYMBOLS_UNICODE if _use_unicode else SYMBOLS_ASCII
    return symbols.get(key, key)


COLORS = {
    "success": "\033[32m",
    "warning": "\033[33m",
    "error": "\033[31m",
    "info": "\033[36m",
    "dim": "\033[90m",
    "bold": "\033[1m",
    "reset": "\033[0m",
}


def colorize(text: str, color_key: str) -> str:
    """Apply ANSI color if enabled."""
    if not _use_color:
        return text
    color = COLORS.get(color_key)
    if not color:
        return text
    reset = COLORS["reset"]
    return f"{color}{text}{reset}"


def success(message: str, *, file: TextIO | None = None) -> None:
    """Print a success message."""
    if file is None:
        file = sys.stderr
    sym = colorize(symbol("success"), "success")
    print(f"{sym} {message}", file=file)


def error(message: str, *, hint: str | None = None, file: TextIO | None = None) -> None:
    """Print an error message with an optional hint."""
    if file is None:
        file = sys.stderr
    sym = colorize(symbol("error"), "error")
    label = colorize("Error:", "error")
    print(f"{sym} {label} {message}", file=file)
    if hint:
        print(f"\n  Try: {hint}", file=file)


def warn(message: str, *, file: TextIO | None = None) -> None:
    """Print a warning message (suppressed in quiet mode)."""
    if _quiet:
        return
    if file is None:
        file = sys.stderr
    sym = colorize(symbol("warning"), "warning")
    label = colorize("Warning:", "warning")
    print(f"{sym} {label} {message}", file=file)


def info(message: str, *, file: TextIO | None = None) -> None:
    """Print an informational message (suppressed in quiet mode)."""
    if _quiet:
        return
    if file is None:
        file = sys.stderr
    print(message, file=file)


def progress(message: str, *, file: TextIO | None = None) -> None:
    """Print a progress message (suppressed in quiet mode)."""
    if _quiet:
        return
    if file is None:
        file = sys.stderr
    sym = colorize(symbol("checking"), "dim")
    print(f"  {sym} {message}", file=file, flush=True)


def status_line(status_key: str, name: str, detail: str = "", *, file: TextIO | None = None) -> None:
    """Print a status line with a symbol and status word."""
    if file is None:
        file = sys.stderr
    color_map = {
        "success": "success",
        "warning": "warning",
        "error": "error",
        "checking": "dim",
        "updating": "dim",
    }
    sym = colorize(symbol(status_key), color_map.get(status_key, ""))
    status_word = {
        "success": "OK",
        "warning": "warning",
        "error": "error",
        "checking": "checking",
        "updating": "updating",
    }.get(status_key, "")
    if detail:
        print(f"{sym} {name}: {status_word} - {detail}", file=file)
    else:
        print(f"{sym} {name}: {status_word}", file=file)


def summary(counts: dict[str, int], *, file: TextIO | None = None) -> None:
    """Print a summary line from ordered counts."""
    if file is None:
        file = sys.stdout
    parts = [f"{count} {label}" for label, count in counts.items()]
    print(", ".join(parts), file=file)


def header(title: str, *, file: TextIO | None = None) -> None:
    """Print a section header."""
    if file is None:
        file = sys.stdout
    print(f"\n{colorize(title, 'bold')}\n", file=file)


INDENT = "  "


def indent(text: str, level: int = 1) -> str:
    """Indent a block of text."""
    prefix = INDENT * level
    return prefix + text.replace("\n", f"\n{prefix}")


def confirm(prompt: str, *, default: bool = False) -> bool:
    """Prompt for confirmation. Raises RuntimeError if not interactive."""
    if not sys.stdin.isatty():
        raise RuntimeError("Confirmation required but running in non-interactive mode")
    suffix = "[Y/n]" if default else "[y/N]"
    response = input(f"{prompt} {suffix}: ").strip().lower()
    if not response:
        return default
    return response in ("y", "yes")


def require_confirmation(prompt: str, *, yes_flag: bool, default: bool = False) -> bool:
    """Require confirmation unless --yes is passed."""
    if yes_flag:
        return True
    if not sys.stdin.isatty():
        error("Confirmation required in non-interactive mode", hint="Use --yes flag to skip confirmation")
        return False
    return confirm(prompt, default=default)


class Spinner:
    """Threaded spinner for long operations."""

    FRAMES_UNICODE = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
    FRAMES_ASCII = ["-", "\\", "|", "/"]

    def __init__(self, message: str) -> None:
        self.message = message
        self._stop_event = threading.Event()
        self._thread: threading.Thread | None = None

    def _spin(self) -> None:
        frames = self.FRAMES_UNICODE if _use_unicode else self.FRAMES_ASCII
        i = 0
        while not self._stop_event.is_set():
            frame = frames[i % len(frames)]
            sys.stderr.write(f"\r{colorize(frame, 'dim')} {self.message}\033[K")
            sys.stderr.flush()
            i += 1
            time.sleep(0.1)
        sys.stderr.write("\r\033[K")
        sys.stderr.flush()

    def __enter__(self) -> Spinner:
        if _quiet:
            return self
        if not sys.stderr.isatty():
            print(f"  {self.message}", file=sys.stderr)
            return self
        self._thread = threading.Thread(target=self._spin, daemon=True)
        self._thread.start()
        return self

    def __exit__(self, *args) -> None:
        if self._thread is not None:
            self._stop_event.set()
            self._thread.join(timeout=0.5)


def progress_counter(current: int, total: int, message: str, *, file: TextIO | None = None) -> None:
    """Print a progress counter."""
    if _quiet:
        return
    if file is None:
        file = sys.stderr
    counter = f"[{current}/{total}]"
    counter_colored = colorize(counter, "dim")
    if file.isatty():
        file.write(f"\r{counter_colored} {message}\033[K")
        file.flush()
        if current == total:
            file.write("\n")
    else:
        print(f"{counter} {message}", file=file)


def progress_done(message: str, *, file: TextIO | None = None) -> None:
    """Clear progress line and print completion message."""
    if file is None:
        file = sys.stderr
    if file.isatty():
        file.write("\r\033[K")
    success(message, file=file)


def json_output(
    data: dict | list | None,
    *,
    command: str,
    success: bool = True,
    error_message: str | None = None,
    error_hint: str | None = None,
    v2: bool = False,
    file: TextIO | None = None,
) -> None:
    """Print JSON output with optional v2 envelope."""
    if file is None:
        file = sys.stdout
    if v2:
        envelope = {
            "version": 2,
            "success": success,
            "command": command,
            "data": data,
            "error": None
            if success
            else {
                "message": error_message,
                "hint": error_hint,
            },
        }
        print(_json.dumps(envelope, indent=2), file=file)
    else:
        print(_json.dumps(data, indent=2), file=file)
