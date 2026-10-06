"""Exercise real skills CLI discovery and isolated installs for all target agents."""

from __future__ import annotations

import argparse
import functools
import http.server
import os
import shutil
import subprocess
import tempfile
import threading
from pathlib import Path

from tooling import prepare_local_tools
from validate import ROOT, authored, require

VERSION = "1.7.0"
AGENTS = {"codex": ".agents/skills", "claude-code": ".claude/skills",
          "pi": ".pi/skills", "opencode": ".agents/skills"}


class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", action="append", default=[], help="Git, website, or local source; repeatable")
    parser.add_argument("--site-dir", type=Path, help="Also test generated site under /engineering-skills/")
    parser.add_argument("--agent", choices=AGENTS, action="append")
    args = parser.parse_args()
    require(bool(args.source) or args.site_dir is not None, "Specify --source or --site-dir")
    expected = authored()
    prepare_local_tools()
    npx = shutil.which("npx")
    require(npx is not None, "Node/npm (including npx) is required")
    sources = [str(Path(s).resolve()) if Path(s).exists() else s for s in args.source]
    server = None
    cases = 0
    with tempfile.TemporaryDirectory(prefix="engineering-skills-install-") as scratch:
        scratch = Path(scratch)
        # CLI 1.7.0 honors XDG_STATE_HOME for its otherwise-global skill lock.
        # Explicit agent selection and no --global keep all skill writes project-local.
        env = dict(os.environ, DISABLE_TELEMETRY="1", DO_NOT_TRACK="1", NO_COLOR="1",
                   XDG_STATE_HOME=str(scratch / "state"), XDG_CONFIG_HOME=str(scratch / "config"),
                   npm_config_cache=str(scratch / "npm-cache"), CI="1")
        if args.site_dir:
            webroot = scratch / "web"
            shutil.copytree(args.site_dir.resolve(), webroot / "engineering-skills")
            server = http.server.ThreadingHTTPServer(
                ("127.0.0.1", 0), functools.partial(QuietHandler, directory=str(webroot)))
            threading.Thread(target=server.serve_forever, daemon=True).start()
            sources.append(f"http://127.0.0.1:{server.server_port}/engineering-skills/")

        def run(source: str, project: Path, flags: list[str]) -> str:
            project.mkdir(parents=True)
            command = [npx, "--yes", f"skills@{VERSION}", "add", source, *flags]
            result = subprocess.run(command, cwd=project, env=env, capture_output=True,
                                    text=True, encoding="utf-8", errors="replace", timeout=180)
            require(result.returncode == 0,
                    f"Installer failed for {source}, {flags}:\n{result.stdout}\n{result.stderr}")
            return result.stdout + result.stderr

        try:
            for number, source in enumerate(sources):
                listing = run(source, scratch / f"discovery-{number}", ["--list"])
                for name in expected:
                    require(name in listing, f"Discovery omitted {name}: {source}\n{listing}")
                print(f"Discovery passed: {source}", flush=True)
                for agent in args.agent or AGENTS:
                    for selection in ["*", *expected]:
                        project = scratch / f"install-{cases}"
                        run(source, project, ["--skill", selection, "--agent", agent, "--copy", "--yes"])
                        names = set(expected) if selection == "*" else {selection}
                        installed_root = project / AGENTS[agent]
                        require(installed_root.is_dir(), f"Missing agent directory: {agent}")
                        require({p.name for p in installed_root.iterdir() if p.is_dir()} == names,
                                f"Unexpected installed collection: {agent}, {selection}")
                        for name in names:
                            _, files = expected[name]
                            actual = {p.relative_to(installed_root / name).as_posix(): p.read_bytes()
                                      for p in (installed_root / name).rglob("*") if p.is_file()}
                            require(actual == files, f"Installed files differ: {source}, {agent}, {name}")
                        cases += 1
                        print(f"Installation passed: {source} -> {agent}, skill={selection}, companions exact", flush=True)
        finally:
            if server:
                server.shutdown()
                server.server_close()
    print(f"Installer compatibility passed: {len(sources)} sources, {cases} isolated installation cases; skills {VERSION}")
    print("Agent behavioral invocation is a separate check.")


if __name__ == "__main__":
    main()
