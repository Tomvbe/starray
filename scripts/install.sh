#!/usr/bin/env bash
set -euo pipefail

PACKAGE_NAME="starray"
PYTHON_VERSION="3.13.12"

if ! command -v python3 >/dev/null 2>&1; then
  echo "python3 is required." >&2
  exit 1
fi

CURRENT_PYTHON="$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:3])))')"
if [[ "$CURRENT_PYTHON" != "$PYTHON_VERSION" ]]; then
  echo "Warning: detected Python $CURRENT_PYTHON; recommended $PYTHON_VERSION for this project."
fi

if ! command -v pipx >/dev/null 2>&1; then
  echo "pipx not found; installing with python3 -m pip --user pipx"
  python3 -m pip install --user pipx
  python3 -m pipx ensurepath
  echo "Restart your shell if 'pipx' is still not available."
fi

if pipx list 2>/dev/null | grep -q "$PACKAGE_NAME"; then
  echo "Upgrading $PACKAGE_NAME..."
  pipx upgrade "$PACKAGE_NAME"
else
  echo "Installing $PACKAGE_NAME..."
  pipx install "$PACKAGE_NAME"
fi

echo "Run: starray --version"
