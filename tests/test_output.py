"""Tests for output helpers."""

import builtins
import io
import json

import pytest

import output


class DummyStream(io.StringIO):
    def isatty(self) -> bool:
        return False


def test_symbol_unicode_and_ascii():
    output.configure(color=False, unicode=True, quiet=False)
    assert output.symbol("success") == "✓"
    output.configure(color=False, unicode=False, quiet=False)
    assert output.symbol("success") == "[OK]"


def test_colorize_respects_disabled_color():
    output.configure(color=False, unicode=True, quiet=False)
    assert output.colorize("text", "success") == "text"


def test_json_output_v2_envelope(capsys):
    output.json_output({"foo": "bar"}, command="list", v2=True)
    payload = json.loads(capsys.readouterr().out)
    assert payload["version"] == 2
    assert payload["success"] is True
    assert payload["command"] == "list"
    assert payload["data"]["foo"] == "bar"


def test_error_with_hint(capsys):
    output.configure(color=False, unicode=False, quiet=False)
    output.error("Something went wrong", hint="Try again")
    captured = capsys.readouterr().err
    assert "Something went wrong" in captured
    assert "Try: Try again" in captured


def test_summary_formats_counts(capsys):
    output.summary({"added": 2, "skipped": 1})
    captured = capsys.readouterr().out.strip()
    assert captured == "2 added, 1 skipped"


def test_configure_quiet_suppresses_warnings(capsys):
    output.configure(color=False, unicode=False, quiet=True)
    output.warn("Quiet warning")
    output.info("Quiet info")
    captured = capsys.readouterr()
    assert captured.err == ""
    assert captured.out == ""


def test_progress_counter_non_tty():
    output.configure(color=False, unicode=False, quiet=False)
    stream = DummyStream()
    output.progress_counter(1, 3, "Working", file=stream)
    assert "[1/3] Working" in stream.getvalue()


def test_spinner_non_tty(monkeypatch, capsys):
    output.configure(color=False, unicode=False, quiet=False)
    monkeypatch.setattr(output.sys.stderr, "isatty", lambda: False)
    with output.Spinner("Working..."):
        pass
    captured = capsys.readouterr().err
    assert "Working..." in captured


def test_confirm_default_true(monkeypatch):
    monkeypatch.setattr(output.sys.stdin, "isatty", lambda: True)
    monkeypatch.setattr(builtins, "input", lambda *_: "")
    assert output.confirm("Proceed?", default=True) is True


def test_confirm_non_tty_raises(monkeypatch):
    monkeypatch.setattr(output.sys.stdin, "isatty", lambda: False)
    with pytest.raises(RuntimeError):
        output.confirm("Proceed?")


def test_require_confirmation_non_tty(monkeypatch, capsys):
    output.configure(color=False, unicode=False, quiet=False)
    monkeypatch.setattr(output.sys.stdin, "isatty", lambda: False)
    assert output.require_confirmation("Proceed?", yes_flag=False) is False
    captured = capsys.readouterr().err
    assert "Confirmation required" in captured


def test_require_confirmation_yes_flag(monkeypatch):
    monkeypatch.setattr(output.sys.stdin, "isatty", lambda: False)
    assert output.require_confirmation("Proceed?", yes_flag=True) is True


def test_symbol_ascii_mode(capsys):
    output.configure(color=False, unicode=False, quiet=False)
    output.success("Done")
    captured = capsys.readouterr().err
    assert "[OK]" in captured
