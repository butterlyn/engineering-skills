# Contributing and maintenance

Make small changes to authored skills and their human-facing docs together.
Only redistribute content you authored or have explicit rights to publish.
Third-party curation belongs in `CURATION.md`; do not add Matt Pocock's skills
under `skills/` or expose them through this site's manifest.

Each `skills/<name>/` directory must be installable alone. Keep required files
inside it, link local references relatively, and include the applicable
license. Keep metadata names unique and matched to the directory. Add every
authored skill to `skill.skills` in the root `great-docs.yml`; leaving a new
skill out of publication fails validation. Add setup/examples/limitations in
`docs/` without reproducing the skill procedure.

Before pushing, run the README's structural checks, build, and isolated
installer smoke checks. Do not commit `.venv`, `.tools`, `great-docs`, credentials,
private examples, or test installations. Review `git diff --cached`.

PRs to `main` validate without deployment privileges. A successful main build
publishes through Actions. For a manual deployment, choose **main** in the
workflow dispatcher; other refs are skipped. Inspect the run's build, deploy,
and live-verification jobs before declaring a publication successful.

For dependency upgrades, change explicit version constraints/pins, regenerate
`uv.lock` intentionally, and repeat checks. CI uses `--frozen` and cannot
silently update the lockfile. Behavior checks using live agents are separate
from metadata, build, and installer tests; record omissions honestly.
