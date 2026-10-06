# Engineering Skills

A personal collection of engineering and agent-workflow skills by **butterlyn**.
The MVP contains one small, clearly labelled demonstration skill,
**verify-a-change**, with its evidence template and license.

- Source of truth: [butterlyn/engineering-skills](https://github.com/butterlyn/engineering-skills)
- Owner: `butterlyn` · visibility: **public** · default branch: **main**
- Great Docs project site: [Engineering Skills](https://butterlyn.github.io/engineering-skills/)
- Discovery: [project manifest](https://butterlyn.github.io/engineering-skills/.well-known/agent-skills/index.json)
- Deployment evidence and behavioral limits: [VERIFICATION.md](VERIFICATION.md)
- Combined skills.sh Pack: **pending**; see [CURATION.md](CURATION.md)

The initial deployment and live Git/website installer checks succeeded in
[Actions run 37482305387](https://github.com/butterlyn/engineering-skills/actions/runs/37482305387).
[Live build provenance](https://butterlyn.github.io/engineering-skills/build-info.json)
identifies the currently published commit; subsequent pushes run the same checks.
Actual agent behavior remains unverified for the reasons in `VERIFICATION.md`.

The repository and documentation site publish the same authored skills. The
separate Pack will curate upstream Matt Pocock skills; his content is neither
vendored nor republished here.

## Install

From the consumer project, with Node 22.20.0+ and Git available:

```bash
# Discover either source.
npx skills@1.7.0 add butterlyn/engineering-skills --list
npx skills@1.7.0 add https://butterlyn.github.io/engineering-skills/ --list

# Install one skill. Pick either source.
npx skills@1.7.0 add butterlyn/engineering-skills --skill verify-a-change --agent codex --copy --yes
npx skills@1.7.0 add https://butterlyn.github.io/engineering-skills/ --skill verify-a-change --agent codex --copy --yes

# Install the authored collection into all four target agents.
npx skills@1.7.0 add butterlyn/engineering-skills --skill '*' --agent codex claude-code pi opencode --copy --yes
npx skills@1.7.0 add https://butterlyn.github.io/engineering-skills/ --skill '*' --agent codex claude-code pi opencode --copy --yes
```

The CLI identifier for **pi-coding-agent is `pi`**. Project installs go to
`.agents/skills/` for Codex/OpenCode, `.claude/skills/` for Claude Code, and
`.pi/skills/` for pi. `--copy` avoids symlink requirements; omit it to use the
installer's default symlink method. No `--global` flag is used here.

The full project-site URL matters. Do not replace it with the domain root or
the primary `skill.md` download: the latter does not package companion files.
Review updates before `npx skills update`; keep the Git route as a fallback.
Unversioned `npx skills` uses the current release; `1.7.0` is the tested version.

## Local tooling, validation, build, and preview

Tested/pinned tooling: Python **3.12.7**, uv **0.9.16**, Great Docs **0.17.0**,
Quarto **1.10.19**, Node **24.21.0** in CI, skills **1.7.0**. The Python
documentation environment uses `uv.lock` and `[tool.uv] package = false`.
There is no Python library to install or API to document.

Install uv, the pinned Python/Node versions, and Quarto 1.10.19. Put Quarto on
PATH. On Windows, alternatively extract the official Quarto 1.10.19 ZIP into
`.tools/`, so `.tools/bin/quarto.cmd` exists; the build helper finds it.
Verify downloads against the release checksums. `.tools/` is ignored.
The official Node Windows ZIP can likewise live at
`.tools/node-v24.21.0-win-x64/`; build and smoke helpers use it without changing
global PATH. Windows Node 25.2.1 exhibited a libuv shutdown assertion in the
website CLI discovery check; use the pinned Node 24 release for these checks.

```bash
uv sync --frozen
uv run --frozen python scripts/validate.py
uv run --frozen python -m unittest discover -s tests -v
uv run --frozen python scripts/build_site.py
uv run --frozen python scripts/validate.py --site great-docs/_site
uv run --frozen python scripts/smoke_install.py --source ./skills --site-dir great-docs/_site
uv run --frozen python -m http.server 8000 --bind 127.0.0.1 --directory great-docs/_site
```

Open `http://127.0.0.1:8000/` for the built static preview; stop it with Ctrl+C.
The installer smoke script also serves the build under `/engineering-skills/`
in a temporary server to exercise project-subpath discovery. All installs,
the CLI lock/state (`XDG_STATE_HOME`), and npm test cache use disposable
directories. It never changes a real project's or global agent's skill files.
Use `./skills` for local discovery: generated, ignored Great Docs output can
otherwise be mistaken for another local skill source by the installer.

To verify publication of the current local commit, use this PowerShell command
after its Actions run succeeds. The commit comparison detects stale deployments:

```powershell
uv run --frozen python scripts/check_live.py --url https://butterlyn.github.io/engineering-skills/ --commit (git rev-parse HEAD)
uv run --frozen python scripts/smoke_install.py --source https://github.com/butterlyn/engineering-skills --source https://butterlyn.github.io/engineering-skills/
```

## Add or edit a skill

Keep the procedure in `skills/<name>/SKILL.md`. Place its required references,
assets, and license inside that same directory. Add the directory's name and
entrypoint to the explicit `skill.skills` list in `great-docs.yml`. Add a page
under `docs/` that explains usage, setup, examples, and limits, linking to the
skill rather than duplicating its procedure. The validator rejects missing
references, paths outside the skill, duplicate names, and publication mismatch.

Run the local checks above, then commit and push to `main`. GitHub Actions
rebuilds and publishes; no manual HTML build/upload is needed. A PR runs checks
and the build without publishing. See [CONTRIBUTING.md](CONTRIBUTING.md).

## Publishing and maintenance

[Validate and publish](.github/workflows/pages.yml) installs every required
tool explicitly and uses frozen Python dependencies. Its build job has only
read access. Main runs upload **only `great-docs/_site`** with hidden files
enabled, download and compare the actual artifact, then deploy with GitHub's
native Pages actions and the workflow token. Only the deployment job has Pages
write/OIDC permissions. The `github-pages` environment is restricted to `main`.
Main runs are serialized through post-deployment checks. Manual dispatch on
other branches is skipped. No PR content is published.

The workflow checks live JSON discovery, homepage/assets, source commit, and
byte-identical skills/companions. `build-info.json` records the revision and
tool versions to expose stale deployments. CI also exercises single-skill and
whole-collection installation for every target agent.

Great Docs 0.17.0's supported `project_type: []` declares no library ecosystem,
so build-time Python requirements are not presented as skill requirements.
`reference: false` disables Python API generation;
CLI/MCP/changelog, package-info, and PyPI features are also disabled. This
release uses **root `great-docs.yml` → `great-docs/_site`**. Newer online docs
describe a different layout. Explicit multi-skill mode copies all companion
files. On Windows it emits backslash paths in the manifest; our narrow build
helper normalizes those URL paths before validation. Generated output is ignored.
The release also injects homepage links to API-derived `llms` files even when
API generation is disabled; the helper removes these links when the files are
absent. It does not generate a substitute API or change skill instructions.

Upgrade the lockfile deliberately (`uv lock --upgrade-package great-docs`,
after choosing a supported version constraint), verify new configuration keys,
and repeat build/artifact/installer checks. Review pinned action SHAs and
tool versions when updating. Keep Pack maintenance separate in `CURATION.md`.

## Official capability references

- [Great Docs skills publication](https://posit-dev.github.io/great-docs/user-guide/agent-skills.html)
  and the [tested 0.17.0 implementation](https://github.com/posit-dev/great-docs/tree/v0.17.0/great_docs)
- [skills CLI 1.7.0](https://github.com/vercel-labs/skills/tree/v1.7.0), including
  [agent identifiers](https://github.com/vercel-labs/skills/blob/v1.7.0/src/agents.ts)
  and [path-relative website discovery](https://github.com/vercel-labs/skills/blob/v1.7.0/src/providers/wellknown.ts)
- [GitHub native Pages workflows](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages)
- [Native skills.sh Packs](https://www.skills.sh/docs/packs)
