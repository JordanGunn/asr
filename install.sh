#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
install.sh — install ASR CLI for the current user.

Default behavior:
- Creates an isolated venv under ~/.local/share/asr/venv
- Installs this project in editable mode
- Symlinks `oasr` and `skills` into ~/.local/bin
- Optionally adds ~/.local/bin to PATH (can be disabled)

Usage:
  ./install.sh [--prefix DIR] [--venv DIR] [--no-modify-path] [--dry-run]

Options:
  --prefix DIR         Install shims into DIR/bin (default: ~/.local)
  --venv DIR           Virtual environment directory (default: ~/.local/share/asr/venv)
  --no-modify-path     Do not modify shell profile to add prefix/bin to PATH
  --dry-run            Print actions without making changes
  -h, --help           Show this help
EOF
}

die() {
  echo "error: $*" >&2
  exit 1
}

DRY_RUN=0
MODIFY_PATH=1
PREFIX="${HOME}/.local"
VENV_DIR="${HOME}/.local/share/asr/venv"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --prefix)
      PREFIX="${2:-}"; shift 2 ;;
    --venv)
      VENV_DIR="${2:-}"; shift 2 ;;
    --no-modify-path)
      MODIFY_PATH=0; shift ;;
    --dry-run)
      DRY_RUN=1; shift ;;
    -h|--help)
      usage; exit 0 ;;
    *)
      die "unknown argument: $1" ;;
  esac
done

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
BIN_DIR="${PREFIX}/bin"

run() {
  if [[ "$DRY_RUN" -eq 1 ]]; then
    printf 'dry-run: %q ' "$@"
    echo
    return 0
  fi
  "$@"
}

ensure_path() {
  local path_entry="$1"

  if [[ ":${PATH}:" == *":${path_entry}:"* ]]; then
    return 0
  fi

  if [[ "$MODIFY_PATH" -eq 0 ]]; then
    cat >&2 <<EOF
warning: ${path_entry} is not on PATH.
Add it to your shell profile, for example:
  export PATH="${path_entry}:\$PATH"
EOF
    return 0
  fi

  local shell_name profile
  shell_name="$(basename "${SHELL:-sh}")"
  case "$shell_name" in
    zsh) profile="${HOME}/.zprofile" ;;
    bash) profile="${HOME}/.bash_profile" ;;
    *) profile="${HOME}/.profile" ;;
  esac

  if [[ -f "$profile" ]]; then
    if command -v rg >/dev/null 2>&1; then
      if rg -q --fixed-strings "${path_entry}:" "$profile" 2>/dev/null; then
        return 0
      fi
      if rg -q --fixed-strings "${path_entry}\"" "$profile" 2>/dev/null; then
        return 0
      fi
    else
      if grep -Fq "${path_entry}:" "$profile" 2>/dev/null; then
        return 0
      fi
      if grep -Fq "${path_entry}\"" "$profile" 2>/dev/null; then
        return 0
      fi
    fi
  fi

  run mkdir -p "$(dirname "$profile")"
  cat <<EOF
Adding ${path_entry} to PATH via ${profile}
EOF
  if [[ "$DRY_RUN" -eq 1 ]]; then
    return 0
  fi

  {
    echo
    echo "# Added by oasr/install.sh"
    echo "export PATH=\"${path_entry}:\$PATH\""
  } >>"$profile"

  export PATH="${path_entry}:${PATH}"
}

create_venv() {
  if [[ "$DRY_RUN" -eq 1 ]]; then
    return 0
  fi

  if [[ -x "${VENV_DIR}/bin/python" ]]; then
    return 0
  fi

  if command -v uv >/dev/null 2>&1; then
    run uv venv "${VENV_DIR}"
    return 0
  fi

  if command -v python3 >/dev/null 2>&1; then
    run python3 -m venv "${VENV_DIR}"
    return 0
  fi

  if command -v python >/dev/null 2>&1; then
    run python -m venv "${VENV_DIR}"
    return 0
  fi

  die "python3/python not found (install Python or uv)"
}

install_project() {
  if [[ "$DRY_RUN" -eq 1 ]]; then
    return 0
  fi

  local vpy="${VENV_DIR}/bin/python"
  [[ -x "$vpy" ]] || die "venv python not found at ${vpy}"

  # Some environments (including certain uv configurations) may create a venv
  # without pip. Ensure pip is present before attempting installs.
  if ! "$vpy" -c "import pip" >/dev/null 2>&1; then
    if "$vpy" -m ensurepip --upgrade >/dev/null 2>&1; then
      :
    fi
  fi
  if ! "$vpy" -c "import pip" >/dev/null 2>&1; then
    die "pip is missing in venv at ${VENV_DIR}. Try installing python with ensurepip enabled, or install pip/venv tooling."
  fi

  run "$vpy" -m pip install --upgrade pip
  run "$vpy" -m pip install -e "${SCRIPT_DIR}"
}

install_shims() {
  if [[ "$DRY_RUN" -eq 1 ]]; then
    return 0
  fi

  run mkdir -p "${BIN_DIR}"

  local src_oasr="${VENV_DIR}/bin/oasr"
  local src_skills="${VENV_DIR}/bin/skills"

  [[ -x "$src_oasr" ]] || die "expected CLI at ${src_oasr} (install may have failed)"

  run ln -sf "$src_oasr" "${BIN_DIR}/oasr"
  if [[ -x "$src_skills" ]]; then
    run ln -sf "$src_skills" "${BIN_DIR}/skills"
  fi
}

migrate_data() {
  # Safely migrate from ~/.skills/ to ~/.oasr/
  # Only moves oasr-managed files: manifests/, registry.toml, config.toml
  
  local old_dir="${HOME}/.skills"
  local new_dir="${HOME}/.oasr"
  
  # If new directory already exists and has data, skip migration
  if [[ -d "${new_dir}" ]] && [[ -f "${new_dir}/registry.toml" ]]; then
    return 0
  fi
  
  # If old directory doesn't exist, nothing to migrate
  if [[ ! -d "${old_dir}" ]]; then
    return 0
  fi
  
  # Check if there's anything to migrate
  local has_oasr_data=0
  [[ -d "${old_dir}/manifests" ]] && has_oasr_data=1
  [[ -f "${old_dir}/registry.toml" ]] && has_oasr_data=1
  [[ -f "${old_dir}/config.toml" ]] && has_oasr_data=1
  
  if [[ "$has_oasr_data" -eq 0 ]]; then
    return 0
  fi
  
  echo "Migrating oasr data from ~/.skills/ to ~/.oasr/ ..."
  
  if [[ "$DRY_RUN" -eq 1 ]]; then
    echo "dry-run: would migrate oasr files from ${old_dir} to ${new_dir}"
    return 0
  fi
  
  # Create new directory
  mkdir -p "${new_dir}"
  
  # Move only oasr-managed files
  if [[ -d "${old_dir}/manifests" ]]; then
    echo "  Moving manifests/ ..."
    mv "${old_dir}/manifests" "${new_dir}/"
  fi
  
  if [[ -f "${old_dir}/registry.toml" ]]; then
    echo "  Moving registry.toml ..."
    mv "${old_dir}/registry.toml" "${new_dir}/"
  fi
  
  if [[ -f "${old_dir}/config.toml" ]]; then
    echo "  Moving config.toml ..."
    mv "${old_dir}/config.toml" "${new_dir}/"
  fi
  
  echo "  ✓ Migration complete"
  echo "  Note: ~/.skills/ directory preserved (may contain other files)"
}

echo "Installing ASR from: ${SCRIPT_DIR}"
echo "Venv: ${VENV_DIR}"
echo "Shims: ${BIN_DIR}"

create_venv
install_project
install_shims
migrate_data
ensure_path "${BIN_DIR}"

cat <<EOF
Done.

Try:
  oasr --version
  oasr --help
EOF
