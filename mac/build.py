#!/usr/bin/env python3
"""Generate this Mac's private deployment files and build its PNG reader."""
import argparse
import json
import os
from pathlib import Path, PurePosixPath
import plistlib
import re
import subprocess
import sys
import tempfile
from xml.sax.saxutils import escape

SOURCE = Path(__file__).resolve().parent


def setting(name):
    value = os.environ.get(name, "")
    if not value or any(ord(ch) < 32 for ch in value):
        raise SystemExit(f"Set {name} to a nonempty, single-line value.")
    return value


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=SOURCE.parent / "build/mac")
    out = parser.parse_args().output
    host = setting("AGY_SSH_HOST")
    user = setting("AGY_SSH_USER")
    if not re.fullmatch(r"[a-zA-Z0-9][a-zA-Z0-9._:%-]*", host):
        raise SystemExit("AGY_SSH_HOST must be a hostname, address or SSH host alias.")
    if not re.fullmatch(r"[a-zA-Z0-9_][a-zA-Z0-9_.-]*", user):
        raise SystemExit("AGY_SSH_USER must be an SSH account name.")
    identity = Path(setting("AGY_SSH_KEY_PATH")).expanduser()
    remote_home = PurePosixPath(setting("AGY_VPS_HOME"))
    if not identity.is_absolute() or not remote_home.is_absolute() or ":" in str(remote_home):
        raise SystemExit("Use absolute paths for the SSH identity and the VPS home (no colon in the VPS socket path).")

    os.umask(0o077)
    out.mkdir(parents=True, exist_ok=True)
    config = {"host": host, "user": user, "identity": str(identity), "vps_home": str(remote_home)}
    lib = Path.home() / ".local/share/agy-mac"
    with tempfile.TemporaryDirectory(dir=out) as tmp:
        stage = Path(tmp)
        (stage / "connection.json").write_text(json.dumps(config, indent=2) + "\n")
        for template in (SOURCE / "launchd").glob("*.plist.in"):
            xml = template.read_text().replace("@MAC_LIB@", escape(str(lib))).replace("@PYTHON@", escape(sys.executable))
            plist = plistlib.loads(xml.encode())
            (stage / template.stem).write_bytes(plistlib.dumps(plist))
        subprocess.run(["swiftc", str(SOURCE / "service/read-png.swift"), "-o", str(stage / "read-png")], check=True)
        for artifact in stage.iterdir():
            artifact.replace(out / artifact.name)


if __name__ == "__main__":
    main()
