"""Local server for site/, the way a host with clean URLs serves it (no trailing slash), plus the research machine's private files.

  uv run python tools/serve_local.py [--port 8796] [--public]

/reconstruction/3d serves 3d.html and /reconstruction/ redirects to /reconstruction. /_local/ is not a folder of site/: it exposes research/layers (working copies of the layers),
research/overlays (the georeferenced plan S01), research/raw/photos (research-only copies) and research/raw/buildings (the full building pages) to the map and the 3D view. --public turns
/_local/ off, which is what a visitor gets. Pages find out whether /_local/ is there from the X-Palace-Local header on any answer, so on a plain static server (the preview on :8790, a host) they never ask for it. Binds to 127.0.0.1 only. Sends no-cache headers.
"""

import argparse
import functools
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / "site"
LOCAL = {
    "/_local/layers/": ROOT / "research/layers",
    "/_local/overlays/": ROOT / "research/overlays",  # the plan S01, georeferenced; never public
    "/_local/photos/": ROOT / "research/raw/photos",  # research-only copies; never public
    "/_local/buildings/": ROOT / "research/raw/buildings",  # full building pages; never public
    "/_local/plancrops/": ROOT / "research/raw/plancrops",  # the plan S01 round each object; never public
}


class Handler(SimpleHTTPRequestHandler):
    private = True
    extensions_map = {**SimpleHTTPRequestHandler.extensions_map, ".geojson": "application/json", ".i16": "application/octet-stream", ".bin": "application/octet-stream", ".woff2": "font/woff2", ".webp": "image/webp"}

    def translate_path(self, path):
        clean = path.split("?", 1)[0].split("#", 1)[0]
        for prefix, folder in LOCAL.items():
            if clean.startswith(prefix):
                target = (folder / clean[len(prefix):]).resolve()
                return str(target) if self.private and folder.resolve() in target.parents else str(SITE / "_missing")
        target = SITE / clean.lstrip("/")
        if not target.exists() and target.with_suffix(".html").exists():
            target = target.with_suffix(".html")
        elif target.is_dir() and (target / "index.html").exists():
            target = target / "index.html"
        return str(target)

    def do_GET(self):
        path, _, query = self.path.partition("?")
        if path.endswith("/") and path != "/":  # no trailing slash
            self.send_response(308)
            self.send_header("Location", path.rstrip("/") + ("?" + query if query else ""))
            self.end_headers()
            return
        super().do_GET()

    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        if self.private:
            self.send_header("X-Palace-Local", "1")
        super().end_headers()

    def log_message(self, fmt, *args):
        pass


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=8796)
    ap.add_argument("--public", action="store_true")
    args = ap.parse_args()
    Handler.private = not args.public
    handler = functools.partial(Handler, directory=str(SITE))
    print(f"http://localhost:{args.port}/ ({'public files only' if args.public else 'with the private layers under /_local/'})")
    ThreadingHTTPServer(("127.0.0.1", args.port), handler).serve_forever()


if __name__ == "__main__":
    main()
