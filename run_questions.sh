#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 1 ]]; then
  echo "Usage: $0 /path/to/book.txt [options]"
  echo "Example: $0 /path/to/book.txt --question-type all --format json"
  exit 1
fi

BOOK_PATH="$1"
shift

python3 "$(dirname "$0")/main.py" "$BOOK_PATH" "$@"
