"""Validation module for skill structure and frontmatter."""

import re
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

from discovery import parse_frontmatter

KEBAB_CASE_PATTERN = re.compile(r"^[a-z]+(-[a-z]+)*$")


class Severity(Enum):
    """Validation message severity."""

    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


@dataclass
class ValidationMessage:
    """A validation message."""

    code: str
    severity: Severity
    message: str
    file: str | None = None

    def __str__(self) -> str:
        prefix = {
            Severity.ERROR: "✗",
            Severity.WARNING: "⚠",
            Severity.INFO: "ℹ",
        }[self.severity]

        if self.file:
            return f"{prefix} {self.code}: {self.message} ({self.file})"
        return f"{prefix} {self.code}: {self.message}"


@dataclass
class ValidationResult:
    """Result of validating a skill."""

    name: str
    path: str
    valid: bool
    errors: list[ValidationMessage] = field(default_factory=list)
    warnings: list[ValidationMessage] = field(default_factory=list)
    info: list[ValidationMessage] = field(default_factory=list)

    @property
    def all_messages(self) -> list[ValidationMessage]:
        """All messages sorted by severity."""
        return self.errors + self.warnings + self.info

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON output."""
        return {
            "name": self.name,
            "path": self.path,
            "valid": self.valid,
            "errors": [{"code": m.code, "message": m.message, "file": m.file} for m in self.errors],
            "warnings": [{"code": m.code, "message": m.message, "file": m.file} for m in self.warnings],
            "info": [{"code": m.code, "message": m.message, "file": m.file} for m in self.info],
        }


def validate_skill(
    path: Path,
    reference_max_lines: int = 500,
    check_exists: bool = True,
    skip_name_match: bool = False,
) -> ValidationResult:
    """Validate a skill directory.

    Args:
        path: Path to skill directory.
        reference_max_lines: Maximum lines for reference files (W007).
        check_exists: If True, check if path exists (for I001).
        skip_name_match: If True, skip W002 directory name check (for remote skills).

    Returns:
        ValidationResult with all messages.
    """
    path = path.resolve()
    result = ValidationResult(
        name=path.name,
        path=str(path),
        valid=True,
    )

    if check_exists and not path.exists():
        result.info.append(
            ValidationMessage(
                code="I001",
                severity=Severity.INFO,
                message="Registered skill path no longer exists",
            )
        )
        result.valid = False
        return result

    if not path.is_dir():
        result.errors.append(
            ValidationMessage(
                code="E001",
                severity=Severity.ERROR,
                message="Path is not a directory",
            )
        )
        result.valid = False
        return result

    skill_md = path / "SKILL.md"

    if not skill_md.exists():
        result.errors.append(
            ValidationMessage(
                code="E001",
                severity=Severity.ERROR,
                message="Missing SKILL.md file",
            )
        )
        result.valid = False
        return result

    try:
        content = skill_md.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as e:
        result.errors.append(
            ValidationMessage(
                code="E002",
                severity=Severity.ERROR,
                message=f"Cannot read SKILL.md: {e}",
            )
        )
        result.valid = False
        return result

    frontmatter = parse_frontmatter(content)

    if frontmatter is None:
        result.errors.append(
            ValidationMessage(
                code="E002",
                severity=Severity.ERROR,
                message="Malformed or missing YAML frontmatter in SKILL.md",
            )
        )
        result.valid = False
        return result

    name = frontmatter.get("name")
    if not name:
        result.errors.append(
            ValidationMessage(
                code="E003",
                severity=Severity.ERROR,
                message="Missing frontmatter field: name",
            )
        )
        result.valid = False
    elif not isinstance(name, str):
        result.errors.append(
            ValidationMessage(
                code="E003",
                severity=Severity.ERROR,
                message="Frontmatter field 'name' must be a string",
            )
        )
        result.valid = False
    else:
        result.name = name

        if not KEBAB_CASE_PATTERN.match(name):
            result.errors.append(
                ValidationMessage(
                    code="E005",
                    severity=Severity.ERROR,
                    message=f"Name '{name}' violates kebab-case format (must match ^[a-z]+(-[a-z]+)*$)",
                )
            )
            result.valid = False

        if not skip_name_match and name != path.name:
            result.warnings.append(
                ValidationMessage(
                    code="W002",
                    severity=Severity.WARNING,
                    message=f"Directory name '{path.name}' doesn't match frontmatter name '{name}'",
                )
            )

    description = frontmatter.get("description")
    if description is None:
        result.errors.append(
            ValidationMessage(
                code="E004",
                severity=Severity.ERROR,
                message="Missing frontmatter field: description",
            )
        )
        result.valid = False
    elif not isinstance(description, str):
        result.errors.append(
            ValidationMessage(
                code="E004",
                severity=Severity.ERROR,
                message="Frontmatter field 'description' must be a string",
            )
        )
        result.valid = False
    elif not description.strip():
        result.warnings.append(
            ValidationMessage(
                code="W001",
                severity=Severity.WARNING,
                message="Description is empty or whitespace-only",
            )
        )

    if " " in str(path) or any(c in str(path) for c in ["'", '"', "&", "|", ";", "$"]):
        result.warnings.append(
            ValidationMessage(
                code="W003",
                severity=Severity.WARNING,
                message="Skill path contains spaces or special characters",
            )
        )

    _check_directory_structure(path, result)
    _check_script_portability(path, result)
    _check_empty_files(path, result)
    _check_reference_lengths(path, result, reference_max_lines)

    return result


def _check_directory_structure(path: Path, result: ValidationResult) -> None:
    """Check if skill has only scripts/ directory."""
    subdirs = [d for d in path.iterdir() if d.is_dir()]
    subdir_names = {d.name for d in subdirs}

    if subdir_names == {"scripts"}:
        result.warnings.append(
            ValidationMessage(
                code="W004",
                severity=Severity.WARNING,
                message="Skill contains only scripts/ directory - consider using scripts-only utility",
            )
        )


def _check_script_portability(path: Path, result: ValidationResult) -> None:
    """Check for .sh without .ps1 and vice versa."""
    scripts_dir = path / "scripts"
    if not scripts_dir.is_dir():
        return

    sh_files = {f.stem for f in scripts_dir.glob("*.sh")}
    ps1_files = {f.stem for f in scripts_dir.glob("*.ps1")}

    sh_only = sh_files - ps1_files
    ps1_only = ps1_files - sh_files

    for name in sh_only:
        result.warnings.append(
            ValidationMessage(
                code="W006",
                severity=Severity.WARNING,
                message=f"scripts/{name}.sh has no accompanying {name}.ps1",
                file=f"scripts/{name}.sh",
            )
        )

    for name in ps1_only:
        result.warnings.append(
            ValidationMessage(
                code="W006",
                severity=Severity.WARNING,
                message=f"scripts/{name}.ps1 has no accompanying {name}.sh",
                file=f"scripts/{name}.ps1",
            )
        )


def _check_empty_files(path: Path, result: ValidationResult) -> None:
    """Check for empty files in references/, assets/, scripts/."""
    for dirname in ["references", "assets", "scripts"]:
        dir_path = path / dirname
        if not dir_path.is_dir():
            continue

        for file in dir_path.iterdir():
            if file.is_file():
                try:
                    if file.stat().st_size == 0:
                        result.warnings.append(
                            ValidationMessage(
                                code="W005",
                                severity=Severity.WARNING,
                                message=f"Empty file: {dirname}/{file.name}",
                                file=f"{dirname}/{file.name}",
                            )
                        )
                except OSError:
                    pass


def _check_reference_lengths(path: Path, result: ValidationResult, max_lines: int) -> None:
    """Check if reference files exceed line threshold."""
    refs_dir = path / "references"
    if not refs_dir.is_dir():
        return

    for file in refs_dir.iterdir():
        if not file.is_file() or not file.suffix == ".md":
            continue

        try:
            content = file.read_text(encoding="utf-8")
            line_count = content.count("\n") + 1

            if line_count > max_lines:
                result.warnings.append(
                    ValidationMessage(
                        code="W007",
                        severity=Severity.WARNING,
                        message=f"references/{file.name} exceeds {max_lines} lines ({line_count} lines)",
                        file=f"references/{file.name}",
                    )
                )
        except (OSError, UnicodeDecodeError):
            pass


def validate_all(
    entries: list,
    reference_max_lines: int = 500,
) -> list[ValidationResult]:
    """Validate all registered skills.

    Args:
        entries: List of SkillEntry objects.
        reference_max_lines: Maximum lines for reference files.

    Returns:
        List of validation results.
    """
    results = []

    for entry in entries:
        result = validate_skill(
            Path(entry.path),
            reference_max_lines=reference_max_lines,
            check_exists=True,
        )
        results.append(result)

    return results
