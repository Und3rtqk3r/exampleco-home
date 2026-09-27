"""Local dev server that mimics the production nginx try_files fallback.
Serves real files when they exist; otherwise falls back to index.html so
clean URLs like /kontakt and /ki-agenten work on reload. Dev-only helper.
"""
import os
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

PORT = 8002


class FallbackHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        raw = self.path.split("?")[0]
        fs = self.translate_path(self.path)
        # 1) real file → serve it
        if os.path.isfile(fs):
            return super().do_GET()
        # 2) try $uri.html (clean URLs like /ki-agenten-systeme → ki-agenten-systeme.html)
        html_rel = raw.rstrip("/") + ".html"
        if os.path.isfile(self.translate_path(html_rel)):
            self.path = html_rel
            return super().do_GET()
        # 3) directory with index.html → serve it
        if os.path.isdir(fs) and os.path.isfile(os.path.join(fs, "index.html")):
            return super().do_GET()
        # 4) extensionless route → SPA fallback to index.html
        if "." not in os.path.basename(raw):
            self.path = "/index.html"
        return super().do_GET()


if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    print(f"Dev server with SPA fallback running on http://localhost:{PORT}")
    ThreadingHTTPServer(("", PORT), FallbackHandler).serve_forever()
