"""Check a deployed project site, provenance, JSON discovery, skills, and assets."""

import argparse
import json
import time
import urllib.error
import urllib.request
from urllib.parse import urljoin, urlsplit

from validate import DISCOVERY, PageLinks, authored, digest, require, validate_manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", required=True)
    parser.add_argument("--commit", required=True, help="Expected deployed source commit")
    args = parser.parse_args()
    base = args.url.rstrip("/") + "/"

    def fetch(path: str) -> bytes:
        url = urljoin(base, path)
        request = urllib.request.Request(url, headers={"User-Agent": "engineering-skills-verification",
                                                      "Cache-Control": "no-cache"})
        for attempt in range(4):
            try:
                with urllib.request.urlopen(request, timeout=20) as response:
                    require(response.status == 200, f"Unexpected HTTP status: {url}")
                    return response.read()
            except (urllib.error.URLError, TimeoutError):
                if attempt == 3:
                    raise
                time.sleep(5)

    # Retry a stale deployment as well as network failures, with a bounded wait.
    for attempt in range(6):
        info = json.loads(fetch("build-info.json"))
        if info.get("source_commit") == args.commit:
            break
        if attempt == 5:
            raise ValueError(f"Stale deployment: expected {args.commit}, received {info.get('source_commit')}")
        time.sleep(5)
    require(info.get("dirty") is False, "Live deployment came from a dirty source tree")
    require(info.get("site_url") == base, "Live stamp has a different site URL")
    homepage = fetch("").decode("utf-8")
    require("Engineering Skills" in homepage, "Unexpected homepage")
    links = PageLinks()
    links.feed(homepage)
    require(any(attrs.get("rel") == "canonical" and target.rstrip("/") == base.rstrip("/")
                for _, target, attrs in links.links), "Live canonical URL differs")
    assets = {}
    origin = urlsplit(base).netloc
    for tag, target, attrs in links.links:
        absolute = urljoin(base, target)
        if urlsplit(absolute).netloc != origin:
            continue
        if tag == "script" and target.endswith(".js"):
            assets.setdefault("javascript", absolute)
        if tag == "link" and attrs.get("rel") == "stylesheet":
            assets.setdefault("stylesheet", absolute)
    require(len(assets) == 2, "Missing representative homepage assets")
    for kind, url in assets.items():
        require(url.startswith(base), f"Asset escapes project subpath: {url}")
        require(len(fetch(url)) > 0, f"Empty {kind} asset")
        print(f"Live {kind} passed: {url}")
    expected = authored()
    index = json.loads(fetch(f"{DISCOVERY}/index.json"))
    validate_manifest(index, expected, fetch)
    hashes = {f"{name}/{path}": digest(data) for name, (_, files) in expected.items()
              for path, data in files.items()}
    require(info.get("skill_sha256") == hashes, "Live stamp hashes differ from intended authored content")
    print(f"Live publication passed: homepage, assets, JSON manifest, exact skill/companion bytes; commit {args.commit}")
    print("Published tool versions: " + json.dumps(info["versions"], sort_keys=True))


if __name__ == "__main__":
    main()
