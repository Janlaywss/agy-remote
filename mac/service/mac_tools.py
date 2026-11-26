import json
import os
from pathlib import Path
import signal
import socketserver
import subprocess
import tempfile

BASE = Path.home() / "Codex"
SOCKET = Path(__file__).parent / "tools.sock"
TOOL = {
    "name": "mac_shell",
    "description": "Run zsh on the user's Mac for shell commands and all filesystem operations. Omit cwd to use the Mac directory selected at launch. To discover it, run pwd without cwd.",
    "inputSchema": {"type": "object", "properties": {
        "command": {"type": "string"},
        "cwd": {"type": "string", "description": "Absolute Mac directory or path relative to the session starting directory"},
        "timeout": {"type": "integer", "minimum": 1, "maximum": 3600}
    }, "required": ["command"]},
}

def shell(args):
    directory = BASE / Path(args.get("cwd", ".")).expanduser()
    with tempfile.TemporaryFile() as output:
        proc = subprocess.Popen(["/bin/zsh", "-lc", args["command"]], cwd=directory,
                                stdin=subprocess.DEVNULL, stdout=output, stderr=subprocess.STDOUT,
                                start_new_session=True)
        try:
            proc.wait(timeout=max(1, min(3600, args.get("timeout", 120))))
        except subprocess.TimeoutExpired:
            os.killpg(proc.pid, signal.SIGKILL)
            proc.wait()
            output.write(b"\nCommand timed out\n")
        output.seek(0)
        data = output.read(100001)
        result = data[:100000].decode(errors="replace")
        if len(data) > 100000:
            result += "\n[output truncated]"
    return {"content": [{"type": "text", "text": f"Exit {proc.returncode}\n{result}"}], "isError": proc.returncode != 0}

class Session(socketserver.StreamRequestHandler):
    def handle(self):
        for line in self.rfile:
            request = json.loads(line)
            if "id" not in request:
                continue
            reply = {"jsonrpc": "2.0", "id": request["id"]}
            method, params = request["method"], request.get("params", {})
            try:
                if method == "initialize":
                    version = params.get("protocolVersion")
                    reply["result"] = {"protocolVersion": version if version in ("2024-11-05","2025-03-26","2025-06-18","2025-11-25") else "2025-06-18",
                        "capabilities": {"tools": {}}, "serverInfo": {"name": "agy-mac", "version": "1.0"}}
                elif method == "tools/list":
                    reply["result"] = {"tools": [TOOL]}
                elif method == "tools/call" and params.get("name") == TOOL["name"]:
                    reply["result"] = shell(params["arguments"])
                elif method == "ping":
                    reply["result"] = {}
                else:
                    reply["error"] = {"code": -32601, "message": "Unknown method"}
            except Exception as exc:
                reply["error"] = {"code": -32603, "message": str(exc)}
            self.wfile.write(json.dumps(reply).encode() + b"\n")

os.umask(0o077)
SOCKET.unlink(missing_ok=True)
with socketserver.ThreadingUnixStreamServer(str(SOCKET), Session) as server:
    server.serve_forever()
