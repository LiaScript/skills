#!/usr/bin/env python3
"""Serve a LiaScript course folder with CORS (stdlib only).

  serve.py COURSE_DIR [--port 8000] [--app DIST_DIR]

Without --app: open https://liascript.github.io/course/?http://localhost:PORT/README.md
With    --app: a local LiaScript build (dist/) is served at /, the course at /course/
               -> http://localhost:PORT/?http://localhost:PORT/course/README.md
"""
import argparse, functools, http.server, os, posixpath, urllib.parse

class Handler(http.server.SimpleHTTPRequestHandler):
    course = "."
    app = None

    def end_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def translate_path(self, path):
        path = urllib.parse.unquote(urllib.parse.urlsplit(path).path)
        if self.app is None:
            root, rel = self.course, path
        elif path.startswith("/course/"):
            root, rel = self.course, path[len("/course"):]
        else:
            root, rel = self.app, path
        rel = posixpath.normpath(rel).lstrip("/")
        return os.path.join(root, *[p for p in rel.split("/") if p not in ("", ".", "..")])

    def log_message(self, *a):
        pass

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("course")
    ap.add_argument("--port", type=int, default=8000)
    ap.add_argument("--app")
    a = ap.parse_args()
    Handler.course = os.path.abspath(a.course)
    Handler.app = os.path.abspath(a.app) if a.app else None
    srv = http.server.ThreadingHTTPServer(("127.0.0.1", a.port), Handler)
    if Handler.app:
        print(f"http://localhost:{a.port}/?http://localhost:{a.port}/course/README.md")
    else:
        print(f"https://liascript.github.io/course/?http://localhost:{a.port}/README.md")
    srv.serve_forever()
