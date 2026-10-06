"""Build with Great Docs, normalize URL paths, stamp provenance, and validate."""

import importlib.metadata
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

import yaml

from tooling import prepare_local_tools
from validate import DISCOVERY, ROOT, authored, digest, require, validate_site

QUARTO_VERSION = "1.10.19"
SITE = ROOT / "great-docs" / "_site"


def main():
    authored()
    os.chdir(ROOT)
    prepare_local_tools()
    quarto = shutil.which("quarto")
    require(quarto is not None, "Install Quarto 1.10.19 on PATH (or extract its Windows ZIP into .tools)")
    version = subprocess.check_output([quarto, "--version"], text=True).strip()
    require(version == QUARTO_VERSION, f"Expected Quarto {QUARTO_VERSION}, found {version}")
    require(importlib.metadata.version("great-docs") == "0.17.0", "Use the committed uv.lock")
    subprocess.run([str(Path(sys.executable).parent / ("great-docs.exe" if os.name == "nt" else "great-docs")),
                    "build"], check=True)

    # 0.17.0 writes str(Path) into the legacy manifest; Windows uses backslashes.
    # Normalize only those separators. Great Docs generates/copies all publication data.
    manifest = SITE / DISCOVERY / "index.json"
    index = json.loads(manifest.read_text(encoding="utf-8"))
    for entry in index["skills"]:
        entry["files"] = [path.replace("\\", "/") for path in entry["files"]]
    manifest.write_text(json.dumps(index, indent=2) + "\n", encoding="utf-8")
    # In a docs-only build, 0.17.0 omits API-based llms files but still links
    # them in the homepage margin. Remove only links whose outputs are absent.
    homepage = SITE / "index.html"
    html = homepage.read_text(encoding="utf-8")
    for optional in ("llms.txt", "llms-full.txt"):
        if not (SITE / optional).exists():
            html = re.sub(r'<a href="' + re.escape(optional) + r'">[^<]*</a><br\s*/?>', "", html)
    homepage.write_text(html, encoding="utf-8")
    markdown = SITE / "index.md"
    if markdown.exists():
        text = markdown.read_text(encoding="utf-8")
        for optional in ("llms.txt", "llms-full.txt"):
            if not (SITE / optional).exists():
                text = text.replace(f"[{optional}]({optional})<br>", "")
        markdown.write_text(text, encoding="utf-8")
    try:
        commit = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True, stderr=subprocess.DEVNULL).strip()
        dirty = bool(subprocess.check_output(["git", "status", "--porcelain"], text=True).strip())
    except subprocess.CalledProcessError:
        commit, dirty = "uncommitted", True
    if os.environ.get("GITHUB_SHA"):
        require(commit == os.environ["GITHUB_SHA"], "Checkout differs from workflow SHA")
    config = yaml.safe_load((ROOT / "great-docs.yml").read_text(encoding="utf-8"))
    info = {
        "source_commit": commit,
        "dirty": dirty,
        "repository_url": config["repo"],
        "site_url": config["site_url"],
        "versions": {"python": sys.version.split()[0], "great_docs": "0.17.0", "quarto": version,
                     "skills": "1.7.0", "node": subprocess.check_output(["node", "--version"], text=True).strip(),
                     "uv": subprocess.check_output(["uv", "--version"], text=True).strip()},
        "skill_sha256": {f"{name}/{path}": digest(data) for name, (_, files) in authored().items()
                         for path, data in files.items()},
    }
    (SITE / "build-info.json").write_text(json.dumps(info, indent=2) + "\n", encoding="utf-8")
    validate_site(SITE)
    print(f"Build verified: {SITE}")


if __name__ == "__main__":
    main()
