"""Shared test fixtures for ASR CLI tests."""

import sys
from pathlib import Path
from dataclasses import dataclass

import pytest

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


@dataclass
class MockSkillEntry:
    """Mock skill entry for testing."""
    path: str
    name: str
    description: str


@pytest.fixture
def tmp_skills_dir(tmp_path, monkeypatch):
    """Create a temporary skills directory and patch config to use it."""
    skills_dir = tmp_path / ".skills"
    skills_dir.mkdir()
    
    # Patch the config module
    import config
    monkeypatch.setattr(config, "SKILLS_DIR", skills_dir)
    
    # Patch registry module
    import registry
    monkeypatch.setattr(registry, "REGISTRY_FILE", skills_dir / "registry.toml")
    
    return skills_dir


@pytest.fixture
def tmp_output_dir(tmp_path):
    """Create a temporary output directory for adapter tests."""
    output_dir = tmp_path / "project"
    output_dir.mkdir()
    return output_dir


@pytest.fixture
def sample_skills(tmp_path):
    """Create sample skill directories with SKILL.md manifests."""
    skills = []
    
    skill_data = [
        ("git-commit", "Generate conventional commit messages"),
        ("git-review", "Perform code reviews for git changes"),
        ("code-format", "Format code according to style guides"),
        ("test-writer", "Generate unit tests for functions"),
        ("doc-generator", "Generate documentation from code"),
    ]
    
    for name, description in skill_data:
        skill_dir = tmp_path / "skills" / name
        skill_dir.mkdir(parents=True)
        
        manifest = skill_dir / "SKILL.md"
        manifest.write_text(f"""---
name: {name}
description: {description}
---

# {name}

{description}
""")
        
        skills.append(MockSkillEntry(
            path=str(skill_dir),
            name=name,
            description=description,
        ))
    
    return skills


@pytest.fixture
def sample_registry(tmp_skills_dir, sample_skills, monkeypatch):
    """Create a pre-populated registry with sample skills."""
    import registry
    
    # Disable manifest creation for tests
    monkeypatch.setattr(registry, "create_manifest", lambda **kw: None)
    monkeypatch.setattr(registry, "save_manifest", lambda m: None)
    monkeypatch.setattr(registry, "delete_manifest", lambda n: None)
    
    entries = [
        registry.SkillEntry(
            path=s.path,
            name=s.name,
            description=s.description,
        )
        for s in sample_skills
    ]
    
    registry.save_registry(entries)
    
    return entries


@pytest.fixture
def cli_runner(monkeypatch, capsys):
    """Helper to run CLI commands and capture output."""
    def run(argv):
        import cli
        try:
            exit_code = cli.main(argv)
        except SystemExit as e:
            exit_code = e.code if e.code is not None else 0
        
        captured = capsys.readouterr()
        return exit_code, captured.out, captured.err
    
    return run
