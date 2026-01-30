"""Remote skill fetching from GitHub and GitLab.

Provides low-level operations for parsing URLs, fetching from APIs,
and managing remote skill content.
"""

import json
import os
import re
import shutil
import tempfile
from pathlib import Path
from urllib import error as urlerror
from urllib import parse as urlparse
from urllib import request


# Custom exceptions
class RemoteSkillError(Exception):
    """Base exception for remote skill operations."""

    pass


class RemoteSkillNotFoundError(RemoteSkillError):
    """Remote skill or repository not found."""

    pass


class RemoteRateLimitError(RemoteSkillError):
    """API rate limit exceeded."""

    pass


class RemoteNetworkError(RemoteSkillError):
    """Network error during remote operation."""

    pass


class InvalidRemoteUrlError(RemoteSkillError):
    """Invalid remote URL format."""

    pass


# URL patterns
GITHUB_PATTERN = re.compile(r"^https?://github\.com/([^/]+)/([^/]+)(?:/(?:tree|blob)/([^/]+)/(.+))?/?$")
GITLAB_PATTERN = re.compile(r"^https?://gitlab\.com/([^/]+)/([^/]+)(?:/(?:-/)?tree/([^/]+)/(.+))?/?$")


def parse_github_url(url: str) -> dict | None:
    """Parse a GitHub URL into components.

    Args:
        url: GitHub URL (e.g., https://github.com/user/repo/tree/main/path)

    Returns:
        Dictionary with 'owner', 'repo', 'ref', 'path' keys, or None if invalid
    """
    match = GITHUB_PATTERN.match(url)
    if not match:
        return None

    owner, repo, ref, path = match.groups()

    return {
        "owner": owner,
        "repo": repo,
        "ref": ref or "main",  # Default to main branch
        "path": path or "",
    }


def parse_gitlab_url(url: str) -> dict | None:
    """Parse a GitLab URL into components.

    Args:
        url: GitLab URL (e.g., https://gitlab.com/user/project/tree/main/path)

    Returns:
        Dictionary with 'owner', 'repo', 'ref', 'path' keys, or None if invalid
    """
    match = GITLAB_PATTERN.match(url)
    if not match:
        return None

    owner, repo, ref, path = match.groups()

    return {
        "owner": owner,
        "repo": repo,
        "ref": ref or "main",
        "path": path or "",
    }


def derive_skill_name(url: str) -> str:
    """Derive a skill name from a remote URL.

    Extracts repo name and skill path to create a kebab-case name.
    Format: {repo}-{skill-identifier}

    Args:
        url: Remote URL

    Returns:
        Derived skill name in kebab-case

    Raises:
        InvalidRemoteUrlError: If URL cannot be parsed
    """
    parsed = parse_github_url(url) or parse_gitlab_url(url)

    if not parsed:
        raise InvalidRemoteUrlError(f"Cannot parse URL: {url}")

    repo = parsed["repo"]
    path = parsed["path"]

    # Get last component of path as skill identifier
    if path:
        skill_id = Path(path).name
    else:
        skill_id = ""

    # Combine repo and skill identifier
    if skill_id:
        name = f"{repo}-{skill_id}"
    else:
        name = repo

    # Ensure kebab-case (lowercase with hyphens)
    name = name.lower().replace("_", "-")

    return name


def validate_remote_url(url: str) -> tuple[bool, str]:
    """Validate a remote URL format.

    Args:
        url: URL to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not url:
        return False, "URL is empty"

    if not (url.startswith("http://") or url.startswith("https://")):
        return False, "URL must start with http:// or https://"

    if parse_github_url(url):
        return True, ""

    if parse_gitlab_url(url):
        return True, ""

    return False, "URL must be a valid GitHub or GitLab repository URL"


def _get_auth_token(platform: str) -> str | None:
    """Get authentication token from environment.

    Args:
        platform: 'github' or 'gitlab'

    Returns:
        Token string or None
    """
    if platform == "github":
        return os.environ.get("GITHUB_TOKEN")
    elif platform == "gitlab":
        return os.environ.get("GITLAB_TOKEN")
    return None


def fetch_github_directory(
    owner: str,
    repo: str,
    path: str,
    ref: str = "main",
    token: str | None = None,
) -> list[dict]:
    """Fetch directory contents from GitHub API.

    Args:
        owner: Repository owner
        repo: Repository name
        path: Path within repository
        ref: Branch/tag/commit reference
        token: Optional authentication token

    Returns:
        List of file/directory entries

    Raises:
        RemoteSkillNotFoundError: If repository or path not found
        RemoteRateLimitError: If rate limit exceeded
        RemoteNetworkError: On network errors
    """
    api_url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"
    if ref:
        api_url += f"?ref={ref}"

    headers = {"Accept": "application/vnd.github.v3+json"}
    if token:
        headers["Authorization"] = f"token {token}"

    req = request.Request(api_url, headers=headers)

    try:
        with request.urlopen(req) as response:
            data = json.loads(response.read().decode("utf-8"))
            return data if isinstance(data, list) else [data]
    except urlerror.HTTPError as e:
        if e.code == 404:
            raise RemoteSkillNotFoundError(f"Not found: {owner}/{repo}/{path}")
        elif e.code == 403:
            raise RemoteRateLimitError("GitHub API rate limit exceeded. Set GITHUB_TOKEN environment variable.")
        else:
            raise RemoteNetworkError(f"HTTP error {e.code}: {e.reason}")
    except urlerror.URLError as e:
        raise RemoteNetworkError(f"Network error: {e.reason}")


def fetch_gitlab_directory(
    owner: str,
    repo: str,
    path: str,
    ref: str = "main",
    token: str | None = None,
) -> list[dict]:
    """Fetch directory contents from GitLab API.

    Args:
        owner: Project owner/group
        repo: Repository name
        path: Path within repository
        ref: Branch/tag/commit reference
        token: Optional authentication token

    Returns:
        List of file/directory entries

    Raises:
        RemoteSkillNotFoundError: If repository or path not found
        RemoteRateLimitError: If rate limit exceeded
        RemoteNetworkError: On network errors
    """
    project_id = f"{owner}%2F{repo}"
    api_url = f"https://gitlab.com/api/v4/projects/{project_id}/repository/tree"
    params = {"ref": ref, "path": path, "recursive": "false"}
    full_url = f"{api_url}?{urlparse.urlencode(params)}"

    headers = {}
    if token:
        headers["PRIVATE-TOKEN"] = token

    req = request.Request(full_url, headers=headers)

    try:
        with request.urlopen(req) as response:
            data = json.loads(response.read().decode("utf-8"))
            return data if isinstance(data, list) else []
    except urlerror.HTTPError as e:
        if e.code == 404:
            raise RemoteSkillNotFoundError(f"Not found: {owner}/{repo}/{path}")
        elif e.code == 429:
            raise RemoteRateLimitError("GitLab API rate limit exceeded. Set GITLAB_TOKEN environment variable.")
        else:
            raise RemoteNetworkError(f"HTTP error {e.code}: {e.reason}")
    except urlerror.URLError as e:
        raise RemoteNetworkError(f"Network error: {e.reason}")


def _download_file(url: str, dest: Path, token: str | None = None, platform: str = "github"):
    """Download a file from URL to destination.

    Args:
        url: File download URL
        dest: Destination file path
        token: Optional authentication token
        platform: 'github' or 'gitlab'
    """
    headers = {}
    if token:
        if platform == "github":
            headers["Authorization"] = f"token {token}"
        elif platform == "gitlab":
            headers["PRIVATE-TOKEN"] = token

    req = request.Request(url, headers=headers)

    dest.parent.mkdir(parents=True, exist_ok=True)

    with request.urlopen(req) as response:
        dest.write_bytes(response.read())


def _fetch_github_recursive(
    owner: str,
    repo: str,
    path: str,
    ref: str,
    dest_dir: Path,
    token: str | None = None,
):
    """Recursively fetch GitHub directory structure.

    Args:
        owner: Repository owner
        repo: Repository name
        path: Path within repository
        ref: Branch/tag/commit reference
        dest_dir: Destination directory
        token: Optional authentication token
    """
    entries = fetch_github_directory(owner, repo, path, ref, token)

    for entry in entries:
        entry_path = entry["path"]
        entry_name = entry["name"]
        entry_type = entry["type"]

        if entry_type == "file":
            download_url = entry["download_url"]
            dest_file = dest_dir / entry_name
            _download_file(download_url, dest_file, token, "github")
        elif entry_type == "dir":
            subdir = dest_dir / entry_name
            subdir.mkdir(parents=True, exist_ok=True)
            _fetch_github_recursive(owner, repo, entry_path, ref, subdir, token)


def _fetch_gitlab_recursive(
    owner: str,
    repo: str,
    path: str,
    ref: str,
    dest_dir: Path,
    token: str | None = None,
):
    """Recursively fetch GitLab directory structure.

    Args:
        owner: Project owner/group
        repo: Repository name
        path: Path within repository
        ref: Branch/tag/commit reference
        dest_dir: Destination directory
        token: Optional authentication token
    """
    entries = fetch_gitlab_directory(owner, repo, path, ref, token)

    for entry in entries:
        entry_path = entry["path"]
        entry["name"]
        entry_type = entry["type"]

        if entry_type == "blob":  # File
            # Construct raw file URL
            project_id = f"{owner}%2F{repo}"
            file_path_encoded = urlparse.quote(entry_path, safe="")
            download_url = (
                f"https://gitlab.com/api/v4/projects/{project_id}/repository/files/{file_path_encoded}/raw?ref={ref}"
            )

            # Calculate relative path from base path
            rel_path = Path(entry_path).relative_to(path) if path else Path(entry_path)
            dest_file = dest_dir / rel_path
            _download_file(download_url, dest_file, token, "gitlab")
        elif entry_type == "tree":  # Directory
            rel_path = Path(entry_path).relative_to(path) if path else Path(entry_path)
            subdir = dest_dir / rel_path
            subdir.mkdir(parents=True, exist_ok=True)
            _fetch_gitlab_recursive(owner, repo, entry_path, ref, subdir, token)


def fetch_remote_to_temp(url: str) -> Path:
    """Fetch a remote skill to a temporary directory.

    Args:
        url: Remote skill URL

    Returns:
        Path to temporary directory containing fetched skill

    Raises:
        InvalidRemoteUrlError: If URL is invalid
        RemoteSkillNotFoundError: If skill not found
        RemoteNetworkError: On network errors
    """
    # Parse URL
    github_parsed = parse_github_url(url)
    gitlab_parsed = parse_gitlab_url(url)

    if github_parsed:
        parsed = github_parsed
        platform = "github"
    elif gitlab_parsed:
        parsed = gitlab_parsed
        platform = "gitlab"
    else:
        raise InvalidRemoteUrlError(f"Invalid URL: {url}")

    owner = parsed["owner"]
    repo = parsed["repo"]
    ref = parsed["ref"]
    path = parsed["path"]
    token = _get_auth_token(platform)

    # Create temporary directory
    temp_dir = Path(tempfile.mkdtemp(prefix="asr-remote-"))

    try:
        if platform == "github":
            _fetch_github_recursive(owner, repo, path, ref, temp_dir, token)
        elif platform == "gitlab":
            _fetch_gitlab_recursive(owner, repo, path, ref, temp_dir, token)

        return temp_dir
    except Exception:
        # Clean up on error
        shutil.rmtree(temp_dir, ignore_errors=True)
        raise


def check_remote_reachability(url: str) -> tuple[bool, int, str]:
    """Check if a remote URL is reachable.

    Args:
        url: Remote URL to check

    Returns:
        Tuple of (is_reachable, status_code, message)
    """
    # Parse URL to get API endpoint for the specific path
    github_parsed = parse_github_url(url)
    gitlab_parsed = parse_gitlab_url(url)

    if github_parsed:
        parsed = github_parsed
        # Check the specific path, not just the repo
        path = parsed["path"] or ""
        api_url = f"https://api.github.com/repos/{parsed['owner']}/{parsed['repo']}/contents/{path}"
        if parsed["ref"]:
            api_url += f"?ref={parsed['ref']}"
        token = _get_auth_token("github")
        headers = {}
        if token:
            headers["Authorization"] = f"token {token}"
    elif gitlab_parsed:
        parsed = gitlab_parsed
        project_id = f"{parsed['owner']}%2F{parsed['repo']}"
        path = parsed["path"] or ""
        # Check the specific path, not just the project
        api_url = f"https://gitlab.com/api/v4/projects/{project_id}/repository/tree?path={path}"
        if parsed["ref"]:
            api_url += f"&ref={parsed['ref']}"
        token = _get_auth_token("gitlab")
        headers = {}
        if token:
            headers["PRIVATE-TOKEN"] = token
    else:
        return False, 0, "Invalid URL format"

    req = request.Request(api_url, headers=headers, method="HEAD")

    try:
        with request.urlopen(req) as response:
            return True, response.status, "Reachable"
    except urlerror.HTTPError as e:
        if e.code in (404, 410):
            return False, e.code, f"Not found (HTTP {e.code})"
        else:
            return False, e.code, f"HTTP error: {e.reason}"
    except urlerror.URLError as e:
        return False, 0, f"Network error: {e.reason}"
