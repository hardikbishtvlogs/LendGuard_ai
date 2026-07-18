#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
API_PORT="${API_PORT:-8000}"
WEB_PORT="${WEB_PORT:-3101}"

cleanup(){ kill "${API_PID:-}" "${WEB_PID:-}" "${TUNNEL_PID:-}" 2>/dev/null || true; }
trap cleanup EXIT INT TERM

if [ ! -x "$ROOT/.venv/bin/uvicorn" ]; then
  echo "Missing Python environment. Run: python3 -m venv .venv && source .venv/bin/activate && pip install -r backend/requirements.txt"
  exit 1
fi

cd "$ROOT/frontend"
npm run build

mkdir -p "$ROOT/frontend/.next/standalone/.next"
rm -rf "$ROOT/frontend/.next/standalone/.next/static" "$ROOT/frontend/.next/standalone/public"
cp -R "$ROOT/frontend/.next/static" "$ROOT/frontend/.next/standalone/.next/static"
cp -R "$ROOT/frontend/public" "$ROOT/frontend/.next/standalone/public"

cd "$ROOT/backend"
PYTHONPATH=. "$ROOT/.venv/bin/uvicorn" app.main:app --host 127.0.0.1 --port "$API_PORT" & API_PID=$!

cd "$ROOT/frontend/.next/standalone"
HOSTNAME=0.0.0.0 PORT="$WEB_PORT" BACKEND_INTERNAL_URL="http://127.0.0.1:$API_PORT" node server.js & WEB_PID=$!

cd "$ROOT"
echo "Starting public tunnel. Share the trycloudflare.com URL printed below."
npx --yes cloudflared tunnel --url "http://127.0.0.1:$WEB_PORT" & TUNNEL_PID=$!

wait "$TUNNEL_PID"
