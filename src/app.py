import json
import os
import socket
from http.server import BaseHTTPRequestHandler, HTTPServer

PORT = int(os.environ.get("PORT", "8080"))

BUILD = {
    "service": os.environ.get("SERVICE_NAME", "deploy-pilot"),
    "environment": os.environ.get("ENVIRONMENT", "local"),
    "branch": os.environ.get("GIT_BRANCH", "unknown"),
    "commit": os.environ.get("GIT_SHA", "unknown"),
    "built_at": os.environ.get("BUILD_TIME", "unknown"),
    "host": socket.gethostname(),
}

PAGE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Deploy Pilot</title>
<style>
  :root {{
    --bg: #f6f7f9; --card: #ffffff; --fg: #15181d; --muted: #5c6672;
    --line: #e3e6ea; --accent: #2f6df6;
  }}
  @media (prefers-color-scheme: dark) {{
    :root:not([data-theme="light"]) {{
      --bg: #0f1115; --card: #171a21; --fg: #e8eaed; --muted: #9aa3af;
      --line: #262b34; --accent: #6f9bff;
    }}
  }}
  * {{ box-sizing: border-box; }}
  body {{
    margin: 0; min-height: 100vh; background: var(--bg); color: var(--fg);
    font: 15px/1.5 ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, sans-serif;
    display: grid; place-items: center; padding: 16px;
  }}
  .card {{
    width: 100%; max-width: 480px; background: var(--card);
    border: 1px solid var(--line); border-radius: 14px; padding: 28px;
  }}
  h1 {{ margin: 0 0 4px; font-size: 20px; letter-spacing: -0.01em; }}
  .sub {{ color: var(--muted); font-size: 13px; margin-bottom: 22px; }}
  dl {{ margin: 0; display: grid; grid-template-columns: auto 1fr; gap: 10px 18px; }}
  dt {{ color: var(--muted); font-size: 13px; }}
  dd {{ margin: 0; font-family: ui-monospace, SFMono-Regular, Menlo, monospace; font-size: 13px; word-break: break-all; }}
  .pill {{
    display: inline-block; padding: 2px 10px; border-radius: 999px;
    background: var(--accent); color: #fff; font-size: 12px; font-weight: 600;
  }}
</style>
</head>
<body>
  <main class="card">
    <h1>{service}</h1>
    <div class="sub">CI/CD pipeline smoke test</div>
    <dl>
      <dt>Environment</dt><dd><span class="pill">{environment}</span></dd>
      <dt>Branch</dt><dd>{branch}</dd>
      <dt>Commit</dt><dd>{commit}</dd>
      <dt>Built at</dt><dd>{built_at}</dd>
      <dt>Host</dt><dd>{host}</dd>
    </dl>
  </main>
</body>
</html>
"""


class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def _send(self, status, body, content_type):
        payload = body.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def do_GET(self):
        if self.path == "/healthz":
            self._send(200, "ok", "text/plain; charset=utf-8")
        elif self.path == "/version":
            self._send(200, json.dumps(BUILD, indent=2), "application/json")
        elif self.path == "/":
            self._send(200, PAGE.format(**BUILD), "text/html; charset=utf-8")
        else:
            self._send(404, "not found", "text/plain; charset=utf-8")

    def log_message(self, fmt, *args):
        print(f"{self.address_string()} {fmt % args}", flush=True)


if __name__ == "__main__":
    print(f"listening on :{PORT} {json.dumps(BUILD)}", flush=True)
    HTTPServer(("0.0.0.0", PORT), Handler).serve_forever()
