"""Use optional, project-local Windows tools without changing global settings."""

import os

from validate import ROOT


def prepare_local_tools():
    version = (ROOT / ".node-version").read_text().strip()
    candidates = [ROOT / ".tools" / f"node-v{version}-win-x64", ROOT / ".tools" / "bin"]
    paths = [str(path) for path in candidates if path.is_dir()]
    if paths:
        os.environ["PATH"] = os.pathsep.join([*paths, os.environ["PATH"]])
