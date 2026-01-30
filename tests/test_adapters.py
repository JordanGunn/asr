"""Tests for Copilot and Claude adapters."""


class TestCopilotAdapter:
    """Tests for the Copilot adapter."""

    def test_copilot_generates_prompt_files(self, sample_skills, tmp_output_dir):
        """Copilot adapter creates prompt files in .github/prompts/."""
        from adapters.copilot import CopilotAdapter

        adapter = CopilotAdapter()
        generated, removed = adapter.generate_all(sample_skills, tmp_output_dir)

        prompts_dir = tmp_output_dir / ".github" / "prompts"
        assert prompts_dir.exists()

        # Should have one prompt file per skill plus instructions file
        prompt_files = list(prompts_dir.glob("*.prompt.md"))
        assert len(prompt_files) == len(sample_skills)

    def test_copilot_creates_instructions_index(self, sample_skills, tmp_output_dir):
        """Copilot adapter creates copilot-instructions.md with skill index."""
        from adapters.copilot import CopilotAdapter

        adapter = CopilotAdapter()
        adapter.generate_all(sample_skills, tmp_output_dir)

        instructions_file = tmp_output_dir / ".github" / "copilot-instructions.md"
        assert instructions_file.exists()

        content = instructions_file.read_text()

        # Check markers present
        assert "<!-- ASR-MANAGED-SKILLS -->" in content
        assert "<!-- /ASR-MANAGED-SKILLS -->" in content

        # Check all skills listed with /name format
        for skill in sample_skills:
            assert f"/{skill.name}" in content

    def test_copilot_preserves_user_content(self, sample_skills, tmp_output_dir):
        """Copilot adapter preserves content outside managed markers."""
        from adapters.copilot import CopilotAdapter

        # Create existing file with user content
        github_dir = tmp_output_dir / ".github"
        github_dir.mkdir(parents=True)
        output_file = github_dir / "copilot-instructions.md"

        user_content = "# My Custom Instructions\n\nDo not delete this.\n"
        output_file.write_text(user_content)

        adapter = CopilotAdapter()
        adapter.generate_all(sample_skills, tmp_output_dir)

        content = output_file.read_text()

        # User content should still be there
        assert "My Custom Instructions" in content
        assert "Do not delete this" in content
        # Skills should be added
        assert "git-commit" in content


class TestClaudeAdapter:
    """Tests for the Claude adapter."""

    def test_claude_generates_per_skill_files(self, sample_skills, tmp_output_dir):
        """Claude adapter creates one file per skill."""
        from adapters.claude import ClaudeAdapter

        adapter = ClaudeAdapter()
        generated, removed = adapter.generate_all(sample_skills, tmp_output_dir)

        assert len(generated) == len(sample_skills)

        commands_dir = tmp_output_dir / ".claude" / "commands"
        assert commands_dir.exists()

        for skill in sample_skills:
            assert (commands_dir / f"{skill.name}.md").exists()

    def test_claude_cleanup_removes_stale_files(self, sample_skills, tmp_output_dir):
        """Claude adapter removes orphaned generated files."""
        from adapters.claude import ClaudeAdapter

        adapter = ClaudeAdapter()

        # First generate all
        adapter.generate_all(sample_skills, tmp_output_dir)

        # Now generate with only some skills (simulating removal)
        partial_skills = sample_skills[:2]
        generated, removed = adapter.generate_all(partial_skills, tmp_output_dir)

        # Should have removed the other files
        assert len(removed) == len(sample_skills) - 2

        commands_dir = tmp_output_dir / ".claude" / "commands"
        remaining_files = list(commands_dir.glob("*.md"))
        assert len(remaining_files) == 2


class TestAdapterCopyFlag:
    """Tests for the --copy flag functionality."""

    def test_copy_flag_copies_skills_locally(self, sample_skills, tmp_output_dir):
        """--copy flag copies skill directories to local skills folder."""
        from adapters.cursor import CursorAdapter

        adapter = CursorAdapter()
        adapter.generate_all(sample_skills, tmp_output_dir, copy=True)

        skills_dir = tmp_output_dir / ".cursor" / "skills"
        assert skills_dir.exists()

        for skill in sample_skills:
            assert (skills_dir / skill.name).exists()
            assert (skills_dir / skill.name / "SKILL.md").exists()

    def test_copy_flag_uses_relative_paths(self, sample_skills, tmp_output_dir):
        """--copy flag generates adapter files with relative paths."""
        from adapters.windsurf import WindsurfAdapter

        adapter = WindsurfAdapter()
        adapter.generate_all(sample_skills, tmp_output_dir, copy=True)

        workflow_file = tmp_output_dir / ".windsurf" / "workflows" / f"{sample_skills[0].name}.md"
        content = workflow_file.read_text()

        # Should contain relative path, not absolute
        assert "../skills/" in content
        assert sample_skills[0].path not in content


class TestAdapterCommand:
    """Tests for the adapter CLI command."""

    def test_adapter_command_includes_copilot_claude(self, cli_runner, tmp_skills_dir):
        """CLI adapter command recognizes copilot and claude targets."""
        # Just check help includes the new targets
        exit_code, stdout, stderr = cli_runner(["help", "adapter"])

        assert exit_code == 0
        # The adapter subcommands should be visible
        assert "copilot" in stdout.lower() or "claude" in stdout.lower()
