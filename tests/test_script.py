import json
import shutil
import time
from pathlib import Path

def test_clone_manifest_lifecycle(tmp_path, monkeypatch):
    """
    Integration-like test for src/clones.py using pytest fixtures.

    This test performs the following steps in an isolated temporary workspace:
    - Prepares a sample source skill directory with files.
    - Computes its hash via `compute_skill_hash`.
    - Simulates `asr use` by copying the skill into a project location and calling
      `add_or_update_clone_entry`.
    - Modifies the source, runs `update_clone_skill` to propagate changes to the
      recorded clone, and checks that the cloned copy and manifest get updated.
    - Removes the clone entry and then the entire clone manifest, verifying behavior.
    """
    # Ensure imports resolve to the repository's `src` directory.
    repo_root = Path(__file__).resolve().parent.parent
    src_dir = repo_root / "src"
    monkeypatch.syspath_prepend(str(src_dir))

    # Run operations inside the temporary directory so manifests and files are local.
    monkeypatch.chdir(tmp_path)

    # Import the functions under test after adjusting sys.path
    from clones import (
        compute_skill_hash,
        add_or_update_clone_entry,
        load_clone_manifest,
        update_clone_skill,
        remove_clone_manifest,
        get_manifest_path,
        check_clone_manifest,
        remove_clone_entry,
    )

    # 1) Create a sample source skill
    source = tmp_path / "source_skill"
    source.mkdir()
    (source / "README.md").write_text("# Example Skill\n\nInitial content\n")
    (source / "action.py").write_text("print('action v1')\n")

    # 2) Compute initial hash
    h1 = compute_skill_hash(source)
    assert h1 and h1.startswith("sha256:"), "initial hash should be a sha256: string"

    # 3) Simulate copying the skill into a project destination and register clone
    project_root = tmp_path / "project"
    project_root.mkdir()
    dest = project_root / "example_skill"
    if dest.exists():
        shutil.rmtree(dest)
    shutil.copytree(source, dest)

    add_or_update_clone_entry("example_skill", dest)

    # Manifest should exist and record the clone
    manifest_path = get_manifest_path("example_skill")
    assert manifest_path.exists(), f"expected manifest at {manifest_path}"
    manifest = load_clone_manifest("example_skill")
    assert manifest is not None
    assert manifest.name == "example_skill"
    assert len(manifest.clones) == 1
    assert manifest.clones[0].clone == str(dest)
    assert manifest.clones[0].hash == h1

    # check_clone_manifest should report True when comparing manifest vs source
    assert check_clone_manifest(manifest, source) is True

    # 4) Modify the source to emulate an upstream change
    (source / "CHANGELOG.md").write_text("Changelog entry\n")
    (source / "action.py").write_text("print('action v2')\n")
    # ensure the filesystem registers new content/time
    time.sleep(0.01)

    h2 = compute_skill_hash(source)
    assert h2 != h1, "hash should change after source modification"

    # 5) Propagate the change to the recorded clone(s)
    update_clone_skill("example_skill", source)

    # Confirm destination files updated (action.py now contains v2)
    dest_action = (dest / "action.py")
    assert dest_action.exists()
    assert "action v2" in dest_action.read_text()

    # Manifest should have been updated with the new hash
    manifest_updated = load_clone_manifest("example_skill")
    assert manifest_updated is not None
    assert manifest_updated.clones[0].hash == h2

    # 6) Remove the clone entry pointing to dest
    remove_clone_entry("example_skill", dest)

    # After removal, manifest no longer exists (we remove manifest when no clones remain)
    assert load_clone_manifest("example_skill") is None

    # 7) Re-add clone entry and then remove entire clone manifest
    add_or_update_clone_entry("example_skill", dest)
    assert load_clone_manifest("example_skill") is not None
    remove_clone_manifest("example_skill")
    assert load_clone_manifest("example_skill") is None