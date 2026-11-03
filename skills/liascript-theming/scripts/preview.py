#!/usr/bin/env python3
"""Screenshot a themed LiaScript course in light and dark mode.

usage: python3 preview.py COURSE.md OUTDIR [--slides 1,2] [--modes light,dark]
                          [--views textbook,presentation] [--size 1280x900] [--app DIST]

Serves the course folder (with CORS) from this process, opens it in headless
chromium on https://liascript.github.io/course/ (the current release), sets the
reader settings for every combination, waits until LiaScript and its fonts are
loaded and the requested mode is active, and saves OUTDIR/<view>-<mode>-<slide>.png.

--slides  slide numbers, 1-based (default 1)
--modes   light, dark or both (default light,dark)
--views   textbook, presentation, slides (default textbook)
--size    browser window (default 1280x900)
--app     a local LiaScript build (dist/) instead of liascript.github.io

Needs chromium and, without --app, internet access. Python standard library only.
"""
import base64
import functools
import http.server
import json
import os
import re
import shutil
import socket
import subprocess
import sys
import tempfile
import threading
import time
import urllib.request
from pathlib import Path

STATE = """(() => {
  const r = document.documentElement.classList, c = document.querySelector('.lia-canvas');
  if (!c || !document.querySelector('.lia-slide__content')) return null;
  if (document.fonts.status !== 'loaded') return null;
  const mode = ['textbook', 'presentation', 'slides'].find(m => c.classList.contains('lia-mode--' + m));
  return {dark: r.contains('lia-variant-dark'), view: mode || ''};
})()"""

SETTINGS = """(() => {
  const s = JSON.parse(localStorage.getItem('settings') || '{}');
  Object.assign(s, %s);
  localStorage.setItem('settings', JSON.stringify(s));
  return true;
})()"""


class CorsHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def log_message(self, *a):
        pass


def serve(folder):
    httpd = http.server.ThreadingHTTPServer(
        ("localhost", 0), functools.partial(CorsHandler, directory=str(folder)))
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    return httpd


def free_port():
    with socket.socket() as s:
        s.bind(("localhost", 0))
        return s.getsockname()[1]


def wait_http(url, seconds=15):
    end = time.time() + seconds
    while time.time() < end:
        try:
            return urllib.request.urlopen(url, timeout=1).read()
        except OSError:
            time.sleep(0.1)
    sys.exit("no answer from " + url)


class WebSocket:
    """Just enough of RFC 6455 to talk to the Chrome DevTools protocol."""

    def __init__(self, url):
        host, port, path = re.match(r"ws://([^:/]+):(\d+)(/.*)", url).groups()
        self.sock = socket.create_connection((host, int(port)))
        key = base64.b64encode(os.urandom(16)).decode()
        self.sock.sendall(("GET %s HTTP/1.1\r\nHost: %s:%s\r\nUpgrade: websocket\r\n"
                           "Connection: Upgrade\r\nSec-WebSocket-Key: %s\r\n"
                           "Sec-WebSocket-Version: 13\r\n\r\n" % (path, host, port, key)).encode())
        head = b""
        while b"\r\n\r\n" not in head:
            head += self.sock.recv(1)
        self.next_id = 0

    def _read(self, n):
        data = b""
        while len(data) < n:
            chunk = self.sock.recv(n - len(data))
            if not chunk:
                raise ConnectionError("devtools connection closed")
            data += chunk
        return data

    def send(self, method, **params):
        self.next_id += 1
        payload = json.dumps({"id": self.next_id, "method": method, "params": params}).encode()
        n = len(payload)
        head = bytes([0x81])
        if n < 126:
            head += bytes([0x80 | n])
        elif n < 65536:
            head += bytes([0x80 | 126]) + n.to_bytes(2, "big")
        else:
            head += bytes([0x80 | 127]) + n.to_bytes(8, "big")
        mask = os.urandom(4)
        self.sock.sendall(head + mask + bytes(b ^ mask[i % 4] for i, b in enumerate(payload)))
        while True:
            msg = json.loads(self._message())
            if msg.get("id") == self.next_id:
                if "error" in msg:
                    sys.exit("devtools: %s" % msg["error"])
                return msg.get("result", {})

    def _message(self):
        data = b""
        while True:
            b1, b2 = self._read(2)
            n = b2 & 0x7F
            if n == 126:
                n = int.from_bytes(self._read(2), "big")
            elif n == 127:
                n = int.from_bytes(self._read(8), "big")
            data += self._read(n)
            if b1 & 0x80:
                return data

    def eval(self, js):
        return self.send("Runtime.evaluate", expression=js, returnByValue=True) \
            .get("result", {}).get("value")


def browser():
    for name in ("chromium", "chromium-browser", "google-chrome", "chrome"):
        if shutil.which(name):
            return name
    sys.exit("chromium not found on PATH")


def wait_state(ws, seconds=30):
    end = time.time() + seconds
    while time.time() < end:
        state = ws.eval(STATE)
        if state:
            return state
        time.sleep(0.3)
    return None


def main(argv):
    opts = {"--slides": "1", "--modes": "light,dark", "--views": "textbook",
            "--size": "1280x900", "--app": None}
    args, i = [], 0
    while i < len(argv):
        if argv[i] in opts:
            opts[argv[i]] = argv[i + 1]
            i += 2
        else:
            args.append(argv[i])
            i += 1
    if len(args) != 2 or args[0] in ("-h", "--help"):
        sys.exit(__doc__)
    course, outdir = Path(args[0]).resolve(), Path(args[1]).resolve()
    if course.is_dir():
        course = course / "README.md"
    outdir.mkdir(parents=True, exist_ok=True)

    course_srv = serve(course.parent)
    course_url = "http://localhost:%d/%s" % (course_srv.server_port, course.name)
    if opts["--app"]:
        app_srv = serve(Path(opts["--app"]).resolve())
        app_url = "http://localhost:%d/" % app_srv.server_port
    else:
        app_srv, app_url = None, "https://liascript.github.io/course/"

    tmp = Path(tempfile.mkdtemp())
    port = free_port()
    proc = subprocess.Popen(
        [browser(), "--headless=new", "--disable-gpu", "--hide-scrollbars",
         # liascript.github.io may fetch the course from localhost
         "--disable-features=PrivateNetworkAccessChecks,BlockInsecurePrivateNetworkRequests,"
         "LocalNetworkAccessChecks",
         "--remote-debugging-port=%d" % port, "--user-data-dir=%s" % tmp,
         "--window-size=%s" % opts["--size"].replace("x", ","), "about:blank"],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    written, problems = [], []
    try:
        wait_http("http://localhost:%d/json/version" % port)
        page = next(t for t in json.loads(wait_http("http://localhost:%d/json/list" % port))
                    if t["type"] == "page")
        ws = WebSocket(page["webSocketDebuggerUrl"])
        ws.send("Page.navigate", url="%s?%s" % (app_url, course_url))
        if not wait_state(ws, 60):
            sys.exit("LiaScript did not load %s" % course_url)

        for view in opts["--views"].split(","):
            for mode in opts["--modes"].split(","):
                settings = {"theme": "default", "light": mode == "light",
                            "mode": view.capitalize()}
                ws.eval(SETTINGS % json.dumps(settings))
                ws.send("Page.reload")
                state = wait_state(ws)
                if state and (state["dark"] != (mode == "dark") or state["view"] != view):
                    # the app may write its own settings back: use the buttons instead
                    if state["dark"] != (mode == "dark"):
                        ws.eval("document.getElementById('lia-btn-light-mode')?.click()")
                    if state["view"] != view:
                        ws.eval("document.getElementById('lia-mode-%s')?.click()" % view)
                    time.sleep(1.0)
                    state = wait_state(ws)
                for slide in opts["--slides"].split(","):
                    # after a reload LiaScript returns to the last visited slide,
                    # so switch slides inside the running app
                    ws.eval("location.hash = '#%s'" % slide)
                    end = time.time() + 10
                    while time.time() < end and ws.eval("location.hash") != "#" + slide:
                        time.sleep(0.2)
                    name = "%s-%s-%s.png" % (view, mode, slide)
                    if ws.eval("location.hash") != "#" + slide:
                        problems.append("%s: slide %s not reached" % (name, slide))
                    state = wait_state(ws)
                    if not state or state["dark"] != (mode == "dark") or state["view"] != view:
                        problems.append("%s: got %s" % (name, state))
                    time.sleep(0.8)  # transitions and lazy content settle
                    shot = ws.send("Page.captureScreenshot", format="png")
                    (outdir / name).write_bytes(base64.b64decode(shot["data"]))
                    written.append(outdir / name)
    finally:
        proc.terminate()
        proc.wait()
        course_srv.shutdown()
        if app_srv:
            app_srv.shutdown()
        shutil.rmtree(tmp, ignore_errors=True)
    for f in written:
        print(f)
    for p in problems:
        print("warning: mode not reached, " + p, file=sys.stderr)


if __name__ == "__main__":
    main(sys.argv[1:])
