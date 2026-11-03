#!/usr/bin/env python3
"""Screenshot a drawing as LiaScript itself shows it.

usage: python3 preview.py INPUT.md OUT.png [--slide N] [--nth K] [--full] [--width PX]

Unlike render.py, this runs the real LiaScript (via liascript-devserver) in
headless chromium, so "…" verbatim parts - math, links, bold, quizzes, images -
appear as they will in the course. Use it whenever a drawing contains "…".

INPUT is a course (served from its own folder, so relative images work) or a
scratch file with just the block; a file without a `#` heading gets one in a
temporary copy. The script waits until the slide and its fonts are loaded and
saves the K-th drawing on the slide with its caption.

--slide N  open slide N (1-based, default 1)
--nth K    which drawing on the slide (1-based, default 1)
--full     save the whole browser window instead of the drawing
--width    browser width in px (default 1000)

Needs liascript-devserver (npm install -g @liascript/devserver) and chromium.
Uses only the Python standard library.
"""
import base64
import json
import os
import re
import shutil
import socket
import subprocess
import sys
import tempfile
import time
import urllib.request
from pathlib import Path

READY = """(() => {
  if (document.fonts.status !== 'loaded') return null;
  const svgs = [...document.querySelectorAll('main svg, .lia-slide svg, svg')]
    .filter(s => s.getBoundingClientRect().width > 60 && s.querySelector('text, path, line'));
  if (!svgs.length) return null;
  const s = svgs[Math.min(%d, svgs.length) - 1];
  s.scrollIntoView({block: 'center'});
  const box = (s.closest('figure') || s).getBoundingClientRect();
  return [box.x, box.y, box.width, box.height];
})()"""


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


def browser():
    for name in ("chromium", "chromium-browser", "google-chrome", "chrome"):
        if shutil.which(name):
            return name
    sys.exit("chromium not found on PATH")


def main(argv):
    opts = {"--slide": "1", "--nth": "1", "--width": "1000"}
    args, full, i = [], "--full" in argv, 0
    while i < len(argv):
        if argv[i] in opts:
            opts[argv[i]] = argv[i + 1]
            i += 2
        else:
            if argv[i] != "--full":
                args.append(argv[i])
            i += 1
    if len(args) != 2 or args[0] in ("-h", "--help"):
        sys.exit(__doc__)
    if not shutil.which("liascript-devserver"):
        sys.exit("liascript-devserver not found: npm install -g @liascript/devserver")

    infile, outfile = Path(args[0]).resolve(), Path(args[1]).resolve()
    tmp = Path(tempfile.mkdtemp())
    if not re.search(r"^#{1,6} ", infile.read_text(), re.M):
        (tmp / "README.md").write_text("# Preview\n\n" + infile.read_text())
        infile = tmp / "README.md"

    lia_port, dev_port = free_port(), free_port()
    procs = [subprocess.Popen(["liascript-devserver", "-i", str(infile.parent), "-p", str(lia_port)],
                              stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)]
    try:
        base = "http://localhost:%d" % lia_port
        wait_http(base + "/")
        procs.append(subprocess.Popen(
            [browser(), "--headless=new", "--disable-gpu", "--hide-scrollbars",
             "--remote-debugging-port=%d" % dev_port, "--user-data-dir=%s" % (tmp / "profile"),
             "--window-size=%s,900" % opts["--width"], "about:blank"],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL))
        wait_http("http://localhost:%d/json/version" % dev_port)
        page = next(t for t in json.loads(wait_http("http://localhost:%d/json/list" % dev_port))
                    if t["type"] == "page")
        ws = WebSocket(page["webSocketDebuggerUrl"])

        url = "%s/liascript/index.html?%s/%s#%s" % (base, base, infile.name, opts["--slide"])
        ws.send("Page.navigate", url=url)
        box, end = None, time.time() + 30
        while time.time() < end:
            r = ws.send("Runtime.evaluate", expression=READY % int(opts["--nth"]),
                        returnByValue=True)
            box = r.get("result", {}).get("value")
            if box:
                break
            time.sleep(0.3)
        if not box:
            print("warning: no drawing found on slide %s, saving the window" % opts["--slide"],
                  file=sys.stderr)
        time.sleep(1.0)  # math and images inside the drawing settle
        if box and not full:
            box = ws.send("Runtime.evaluate", expression=READY % int(opts["--nth"]),
                          returnByValue=True)["result"]["value"]
            pad = 8
            clip = {"x": max(box[0] - pad, 0), "y": max(box[1] - pad, 0),
                    "width": box[2] + 2 * pad, "height": box[3] + 2 * pad, "scale": 1}
            shot = ws.send("Page.captureScreenshot", format="png", clip=clip)
        else:
            shot = ws.send("Page.captureScreenshot", format="png")
        outfile.write_bytes(base64.b64decode(shot["data"]))
    finally:
        for p in reversed(procs):
            p.terminate()
            p.wait()
        shutil.rmtree(tmp, ignore_errors=True)
    print(outfile)


if __name__ == "__main__":
    main(sys.argv[1:])
