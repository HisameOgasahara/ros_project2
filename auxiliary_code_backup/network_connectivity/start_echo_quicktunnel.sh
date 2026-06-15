#!/usr/bin/env bash
set -euo pipefail

WS_PORT="${WS_PORT:-3001}"
HTTP_PORT="${HTTP_PORT:-8001}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SERVER="${SCRIPT_DIR}/ws_echo_server_jetson.py"

if ! command -v cloudflared >/dev/null 2>&1; then
  echo "cloudflared is not installed or not in PATH." >&2
  echo "Install cloudflared first, then run this script again." >&2
  exit 1
fi

cleanup() {
  if [[ -n "${SERVER_PID:-}" ]]; then
    kill "${SERVER_PID}" >/dev/null 2>&1 || true
  fi
}
trap cleanup EXIT INT TERM

echo "Starting echo debug server:"
echo "  WebSocket: ws://0.0.0.0:${WS_PORT}"
echo "  Local HTML: http://0.0.0.0:${HTTP_PORT}/phone_ws_client.html"
WS_PORT="${WS_PORT}" HTTP_PORT="${HTTP_PORT}" python3 "${SERVER}" &
SERVER_PID="$!"

sleep 2

if ! kill -0 "${SERVER_PID}" >/dev/null 2>&1; then
  echo "Echo debug server exited before tunnel startup." >&2
  exit 1
fi

echo ""
echo "Starting Cloudflare quick tunnel to local echo server."
echo "Paste the printed wss://...trycloudflare.com URL into GitHub Pages debug.html."
echo ""

cloudflared tunnel --url "http://localhost:${WS_PORT}" 2>&1 | while IFS= read -r line; do
  echo "${line}"
  if [[ "${line}" =~ https://[a-zA-Z0-9.-]+\.trycloudflare\.com ]]; then
    HTTPS_URL="${BASH_REMATCH[0]}"
    echo ""
    echo "GitHub Pages debug WebSocket URL:"
    echo "  ${HTTPS_URL/https:\/\//wss://}"
    echo ""
  fi
done
