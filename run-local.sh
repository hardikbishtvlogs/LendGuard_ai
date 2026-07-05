#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
WEB_PORT="${WEB_PORT:-3100}"
cleanup(){ kill "${API_PID:-}" "${WEB_PID:-}" 2>/dev/null || true; }
trap cleanup EXIT INT TERM

if [ ! -x "$ROOT/.venv/bin/uvicorn" ]; then
  echo "Missing Python environment. Run: python3 -m venv .venv && source .venv/bin/activate && pip install -r backend/requirements.txt"
  exit 1
fi

if [ ! -d "$ROOT/frontend/node_modules" ]; then
  echo "Missing frontend dependencies. Run: cd frontend && npm install"
  exit 1
fi

cd "$ROOT/backend"
PYTHONPATH=. "$ROOT/.venv/bin/uvicorn" app.main:app --reload --port 8000 & API_PID=$!
cd "$ROOT/frontend"
PORT="$WEB_PORT" npm run dev & WEB_PID=$!
echo "LendGuard AI is starting: http://localhost:$WEB_PORT (API docs: http://localhost:8000/docs)"
wait
