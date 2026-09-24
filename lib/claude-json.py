#!/usr/bin/env python3
"""Read and update ~/.claude.json, the file Claude Code keeps its user-level
MCP servers and per-folder trust in.

  export-mcp        print this machine's user MCP servers as JSON
  merge-mcp         merge MCP servers from stdin into this machine's
  trust PATH...     mark folders trusted so a task never stops at the trust prompt
"""
import json
import os
import sys
import tempfile

PATH = os.path.expanduser("~/.claude.json")


def load():
    try:
        with open(PATH) as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


def save(data):
    # Atomic replace: Claude rewrites this file while it runs.
    fd, tmp = tempfile.mkstemp(dir=os.path.dirname(PATH))
    with os.fdopen(fd, "w") as f:
        json.dump(data, f, indent=2)
    os.chmod(tmp, 0o600)
    os.replace(tmp, PATH)


def main(cmd, *args):
    if cmd == "export-mcp":
        json.dump(load().get("mcpServers", {}), sys.stdout)
    elif cmd == "merge-mcp":
        data = load()
        data.setdefault("mcpServers", {}).update(json.load(sys.stdin))
        save(data)
    elif cmd == "trust":
        data = load()
        projects = data.setdefault("projects", {})
        for path in args:
            projects.setdefault(path, {})["hasTrustDialogAccepted"] = True
        save(data)
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main(*(sys.argv[1:] or ["help"]))
