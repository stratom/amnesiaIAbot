#!/usr/bin/env bash
# Telegram-only launcher for CachyOS / Arch Linux.
set -euo pipefail
cd "$(dirname "$0")"

if ! command -v python >/dev/null 2>&1; then
  echo "Python is missing. On CachyOS run: sudo pacman -Syu python python-pip"
  exit 1
fi

if [ ! -d ".venv" ]; then
  python -m venv .venv
fi

source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python app.py
