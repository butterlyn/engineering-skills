"""Validate authored skills, Great Docs output, and the actual Pages tar artifact."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import tarfile
from html.parser import HTMLParser
from pathlib import Path, PurePosixPath
from urllib.parse import unquote, urljoin, urlsplit

import yaml

ROOT = Path(__file__).resolve().parents[1]
DISCOVERY = ".well-known/agent-skills"
LINK = re.compile(r"\[[^\]]*\]\(<?([^\s)>]+)>?(?:\s+[^)]*)?\)")
NAME = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def frontmatter(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    parts = re.split(r"^---\s*$", text, maxsplit=2, flags=re.MULTILINE)
    require(len(parts) == 3 and not parts[0].strip(), f"Missing frontmatter: {path}")
    metadata = yaml.safe_load(parts[1])
    require(isinstance(metadata, dict), f"Invalid frontmatter: {path}")
    return metadata


def skill_files(directory: Path) -> dict[str, bytes]:
    result = {}
    for path in sorted(directory.rglob("*")):
        require(not path.is_symlink(), f"Skill symlink is not portable: {path}")
        if path.is_file():
            relative = path.relative_to(directory).as_posix()
            require(not any(p.startswith(".") for p in path.relative_to(directory).parts),
                    f"Unexpected hidden skill content: {path}")
            result[relative] = path.read_bytes()
    return result


def validate_skill(directory: Path) -> tuple[dict, dict[str, bytes]]:
    entry = directory / "SKILL.md"
    require(entry.is_file(), f"Missing {entry}")
    metadata = frontmatter(entry)
    name = metadata.get("name")
    require(isinstance(name, str) and len(name) <= 64 and NAME.fullmatch(name) is not None,
            f"Invalid skill name: {entry}")
    require(name == directory.name, f"Name differs from directory: {entry}")
    description = metadata.get("description")
    require(isinstance(description, str) and 0 < len(description.strip()) <= 1024,
            f"Missing/invalid description: {entry}")
    files = skill_files(directory)
    for relative, data in files.items():
        if not relative.endswith(".md"):
            continue
        text = data.decode("utf-8")
        for target in LINK.findall(text):
            parsed = urlsplit(target)
            if parsed.scheme in ("https", "http", "mailto") or target.startswith("#"):
                continue
            require(not parsed.scheme and not parsed.netloc,
                    f"Unsupported reference scheme in {relative}: {target}")
            local = unquote(parsed.path)
            require(not Path(local).is_absolute() and not local.startswith("/"),
                    f"Absolute local reference in {relative}: {target}")
            resolved = (directory / relative).parent.joinpath(local).resolve()
            require(resolved.is_relative_to(directory.resolve()),
                    f"Reference escapes skill directory in {relative}: {target}")
            require(resolved.exists(), f"Missing reference in {relative}: {target}")
    return metadata, files


def authored(root: Path = ROOT) -> dict[str, tuple[dict, dict[str, bytes]]]:
    config = yaml.safe_load((root / "great-docs.yml").read_text(encoding="utf-8"))
    require(config.get("reference") is False, "Documentation-only project needs reference: false")
    for key in ("cli", "go_cli", "rust_cli", "mcp", "changelog"):
        require(config.get(key, {}).get("enabled") is False, f"Disable irrelevant {key} generation")
    require(config.get("pypi") is False and config.get("package_info_page") is False,
            "Disable library-specific pages/links")
    skill_config = config.get("skill", {})
    require(skill_config.get("enabled") is True and skill_config.get("well_known") is True,
            "Enable skill publication and discovery")
    configured = skill_config.get("skills", [])
    require(bool(configured), "Explicitly list authored skills for publication")
    result = {}
    for item in configured:
        name = item.get("name")
        require(name not in result, f"Duplicate publication entry: {name}")
        require(item.get("file") == f"skills/{name}/SKILL.md", f"Unexpected skill source: {item}")
        result[name] = validate_skill(root / "skills" / name)
    found = {p.parent.relative_to(root / "skills").as_posix()
             for p in (root / "skills").rglob("SKILL.md")}
    require(found == set(result), "Authored skill directories and publication allowlist differ")
    return result


def validate_manifest(index: dict, expected: dict, read_file) -> None:
    entries = index.get("skills")
    require(isinstance(entries, list), "Manifest must have a skills array")
    require(len(entries) == len(expected), "Manifest skill count differs")
    require({e.get("name") for e in entries} == set(expected), "Manifest skill names differ")
    for item in entries:
        name = item["name"]
        metadata, files = expected[name]
        require(item.get("description") == metadata["description"].strip(),
                f"Manifest description differs: {name}")
        published = item.get("files")
        require(isinstance(published, list) and len(published) == len(set(published)),
                f"Invalid or duplicate manifest files: {name}")
        require(set(published) == set(files), f"Manifest omits/adds companion files: {name}")
        for relative, data in files.items():
            require(read_file(f"{DISCOVERY}/{name}/{relative}") == data,
                    f"Published content differs: {name}/{relative}")


class PageLinks(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links: list[tuple[str, str, dict]] = []

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        for attribute in ("src", "href"):
            if attribute in values:
                self.links.append((tag, values[attribute], values))


def validate_site(site: Path, root: Path = ROOT) -> None:
    expected = authored(root)
    read_file = lambda path: (site / path).read_bytes()
    index = json.loads(read_file(f"{DISCOVERY}/index.json"))
    validate_manifest(index, expected, read_file)
    require(read_file("skill.md") == next(iter(expected.values()))[1]["SKILL.md"],
            "Primary convenience skill differs")
    info = json.loads(read_file("build-info.json"))
    hashes = {f"{name}/{path}": digest(data) for name, (_, files) in expected.items()
              for path, data in files.items()}
    require(info.get("skill_sha256") == hashes, "Build stamp skill hashes differ")
    base = yaml.safe_load((root / "great-docs.yml").read_text(encoding="utf-8"))["site_url"]
    require(info.get("site_url") == base, "Build stamp site URL differs")
    base_parts = urlsplit(base)
    canonical_found = False
    for page in site.rglob("*.html"):
        parser = PageLinks()
        parser.feed(page.read_text(encoding="utf-8"))
        page_url = urljoin(base, page.relative_to(site).as_posix())
        for tag, target, attrs in parser.links:
            if attrs.get("rel") == "canonical" and page == site / "index.html":
                require(target.rstrip("/") == base.rstrip("/"), "Homepage canonical URL differs")
                canonical_found = True
            parts = urlsplit(urljoin(page_url, target))
            if parts.scheme not in ("https", "http") or parts.netloc != base_parts.netloc:
                continue
            require(parts.path.startswith(base_parts.path), f"URL escapes project subpath: {target}")
            relative = unquote(parts.path[len(base_parts.path):]) or "index.html"
            local = site / relative
            if local.is_dir():
                local = local / "index.html"
            require(local.is_file(), f"Broken local link in {page.name}: {target}")
    require(canonical_found, "Homepage lacks the configured canonical URL")
    print(f"Site validation passed: {len(expected)} skill(s), companions byte-identical, project URLs valid")


def validate_archive(archive: Path, site: Path, root: Path = ROOT) -> None:
    with tarfile.open(archive) as tar:
        actual = {}
        for member in tar.getmembers():
            relative = member.name.removeprefix("./")
            parts = PurePosixPath(relative).parts
            require(not member.issym() and not member.islnk(), f"Artifact link: {relative}")
            require(not relative.startswith("/") and ".." not in parts, f"Unsafe artifact path: {relative}")
            require(not ({".git", ".github"} & set(parts)), f"Repository internals in artifact: {relative}")
            if member.isfile():
                require(relative not in actual, f"Duplicate artifact file: {relative}")
                actual[relative] = tar.extractfile(member).read()
    source = {p.relative_to(site).as_posix(): p.read_bytes() for p in site.rglob("*") if p.is_file()}
    require(actual == source, "Uploaded artifact differs from generated static-site directory")
    validate_manifest(json.loads(actual[f"{DISCOVERY}/index.json"]), authored(root), actual.__getitem__)
    print(f"Pages artifact validation passed: {len(actual)} files, including .well-known and every companion")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--site", type=Path)
    parser.add_argument("--archive", type=Path)
    args = parser.parse_args()
    expected = authored()
    print(f"Structural validation passed: {len(expected)} self-contained authored skill(s)")
    if args.site:
        validate_site(args.site)
    if args.archive:
        require(args.site is not None, "--archive requires --site for exact artifact comparison")
        validate_archive(args.archive, args.site)


if __name__ == "__main__":
    main()
