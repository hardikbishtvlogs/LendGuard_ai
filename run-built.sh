#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
WEB_PORT="${WEB_PORT:-3100}"
API_PORT="${API_PORT:-8000}"
API_URL="${NEXT_PUBLIC_API_URL:-http://localhost:$API_PORT}"

cleanup(){ kill "${API_PID:-}" "${WEB_PID:-}" 2>/dev/null || true; }
trap cleanup EXIT INT TERM

if [ ! -x "$ROOT/.venv/bin/uvicorn" ]; then
  echo "Missing Python environment. Run: python3 -m venv .venv && source .venv/bin/activate && pip install -r backend/requirements.txt"
  exit 1
fi

if [ ! -d "$ROOT/frontend/.next/standalone" ]; then
  echo "Production build not found. Run: cd frontend && npm run build"
  exit 1
fi

if [ ! -d "$ROOT/frontend/.next/static" ]; then
  echo "Next static assets not found. Run: cd frontend && npm run build"
  exit 1
fi

mkdir -p "$ROOT/frontend/.next/standalone/.next"
rm -rf "$ROOT/frontend/.next/standalone/.next/static"
cp -R "$ROOT/frontend/.next/static" "$ROOT/frontend/.next/standalone/.next/static"
rm -rf "$ROOT/frontend/.next/standalone/public"
cp -R "$ROOT/frontend/public" "$ROOT/frontend/.next/standalone/public"

cd "$ROOT/backend"
PYTHONPATH=. "$ROOT/.venv/bin/uvicorn" app.main:app --host 127.0.0.1 --port "$API_PORT" & API_PID=$!

cd "$ROOT/frontend/.next/standalone"
HOSTNAME=0.0.0.0 PORT="$WEB_PORT" NEXT_PUBLIC_API_URL="$API_URL" node server.js & WEB_PID=$!

echo "LendGuard AI production build is running: http://localhost:$WEB_PORT (API docs: http://localhost:$API_PORT/docs)"
echo "Press Ctrl+C to stop both services."
wait
