# Verification record

Checks performed on **2026-10-06**. Installation compatibility is established;
actual agent behavior remains unverified for the explicit reasons below.

## Publication

- Repository: [butterlyn/engineering-skills](https://github.com/butterlyn/engineering-skills),
  personal owner `butterlyn`, **public**, default branch **main**.
- Confirmed site: [Engineering Skills](https://butterlyn.github.io/engineering-skills/).
- First successful deployment: [Actions run 37482305387](https://github.com/butterlyn/engineering-skills/actions/runs/37482305387),
  commit [`592002f63646467ed7e12f247415943e5ad2672a`](https://github.com/butterlyn/engineering-skills/commit/592002f63646467ed7e12f247415943e5ad2672a).
  The `build`, `deploy`, and `verify-live` jobs all succeeded.
- [Live build provenance](https://butterlyn.github.io/engineering-skills/build-info.json)
  identifies the currently published revision and versions. Subsequent pushes
  update it; the workflow rejects a stale revision during post-deployment checks.
- GitHub API verified Pages `build_type: workflow`, no custom domain, and the
  `github-pages` environment's `main` branch policy. Repository homepage is the
  confirmed live project URL.

## Structural validation

Passed: one independently installable authored demonstration skill, metadata,
explicit publication allowlist, required companions, and relative references
that remain within the installed skill directory.

Five unit checks passed: valid standalone companion; rejection of a missing
companion, repository-level reference, omitted manifest companion, and changed
published bytes. The frozen uv environment built the complete Great Docs site.
All same-origin navigation/assets stayed under `/engineering-skills/` and
resolved to generated files; the homepage canonical URL matched the project.

A separate disposable documentation-only fixture with **two explicitly authored
skills** also built successfully. Its manifest listed both skills and every
companion matched its source. No Python library was created; the extra skill
was used only for this check and was never committed or published.

The actual `github-pages` artifact was downloaded during CI and its tar members
compared byte-for-byte with `great-docs/_site`. The check included `.well-known/`
and every skill companion, rejected links/unsafe paths, and excluded repository
internals. Generated output and installer test projects are outside source control.

## Installation compatibility

With **skills 1.7.0**, discovery and installation passed for all four identifiers:

| Target | CLI identifier | Installed project directory | Collection + individual skill |
|---|---|---|---|
| Codex | `codex` | `.agents/skills/` | Passed for each source |
| Claude Code | `claude-code` | `.claude/skills/` | Passed for each source |
| pi-coding-agent | `pi` | `.pi/skills/` | Passed for each source |
| OpenCode | `opencode` | `.agents/skills/` | Passed for each source |

Sources actually exercised:

- Local authored `./skills` directory and a temporary HTTP server mounting the
  generated site at `/engineering-skills/`: **16 installation cases**.
- Actual GitHub repository: **8 installation cases** locally.
- Actual Pages project URL: **8 installation cases** locally.
- CI repeated the local/subpath matrix and then **16 live installation cases**
  from the intended commit's Git URL and the Pages project URL.

Each source also passed `--list` discovery. Both `--skill '*'` and
`--skill verify-a-change` used `--copy`; installed `SKILL.md`,
`references/evidence-template.md`, and `LICENSE` matched authored bytes exactly.
No symlink-mode or global installations were exercised. Projects, npm cache,
and installer state (`XDG_STATE_HOME`) were isolated in disposable directories.

Live checks parsed the project-path discovery manifest as JSON, compared every
published skill/companion with the checkout, fetched homepage JavaScript/CSS,
and matched `build-info.json` against the intended commit with `dirty: false`.
There was **no project-subpath discovery limitation** with this tested CLI/runtime.
Browser navigation from the homepage to the installation page also succeeded.

## Actual behavioral compatibility

Native CLI probes used a disposable calculator fixture with a deliberate
`add(2, 3)` defect. The direct baseline check failed as expected. Each probe
received the installed demonstration skill, a read/check request, and a
restriction against editing the fixture. Fixture files remained unchanged.
These probes do **not** establish successful skill execution:

| Agent/runtime | Executed result | Smallest next action |
|---|---|---|
| Codex CLI 0.160.0 | Invocation returned an honest blocked report; its child execution policy rejected reading the skill/template and running the check | Retry the same disposable read-only probe in a session whose policy permits local reads/checks |
| Claude Code 2.1.283 | Invocation stopped at the existing account session limit | Retry after the reported session reset (11:40pm Australia/Perth on the test date) |
| OpenCode 1.0.134 | Configured `sonar-reasoning-pro` was rejected as unsupported (HTTP 400) | Select a supported model in the owner's OpenCode configuration, then retry |
| pi-coding-agent | Native CLI absent; invocation unexecuted | Install/configure pi independently, then run the disposable probe |

No quota, account, provider, or global agent settings were changed. Installer
compatibility alone does not prove that an agent follows the skill, reads the
template automatically, or produces a correct assessment.

## Tested versions and pipeline limits

Python **3.12.7**; uv **0.9.16**; Great Docs **0.17.0**; Quarto **1.10.19**;
Node **24.21.0**; skills **1.7.0**. GitHub CLI **2.83.1**, Git
**2.52.0.windows.1** were used for setup. Windows portable Node/Quarto downloads
were verified against their official release checksums. CI uses Ubuntu 24.04
and action releases pinned to reviewed commit SHAs in the workflow.

The actual `push: main` pipeline was executed end-to-end. PR and manual-dispatch
conditions were reviewed in the workflow, but no artificial PR or manual run
was created. PRs cannot upload/deploy; manual runs outside `main` skip the build;
only the deployment job receives Pages/OIDC permissions.

Great Docs 0.17.0 uses root `great-docs.yml` and `great-docs/_site`, differing
from newer online examples. `project_type: []` and `reference: false` support
this documentation-only project. A narrow build helper normalizes Windows
manifest separators and removes links to absent API-derived `llms` files.
Windows Node 25.2.1 produced a libuv shutdown assertion during website discovery;
the pinned Node 24.21.0 completed every case. Local installer discovery should
use `./skills` to avoid mistaking ignored generated output for another skill.

## Pack

**Not created.** The proposed Matt Pocock subset remains provisional, and no
Vercel login or GitHub connection has been authorized for skills.sh. Exact
sources, supporting skills, setup requirements, native builder steps, and
privacy/update uncertainties are in [CURATION.md](CURATION.md). Matt's files
are never included in this repository's authored publication.
