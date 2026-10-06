# Combined collection curation

This is a human maintenance record, **not a native Pack configuration file**.
Only authored content under `skills/` is published by this repository and site.
No Matt Pocock skill is copied, forked, or served here.

Selection status: **provisional, awaiting the owner's choice**.
Pack status: **not created; Vercel access and authorization are still required**.

Proposed Pack name: **Engineering workflow essentials**.
Proposed description: **butterlyn's authored change-evidence workflow with a small upstream engineering subset**.

## Sources and selection

Authored source: [butterlyn/engineering-skills](https://github.com/butterlyn/engineering-skills).
Include `verify-a-change` and its `references/evidence-template.md` and `LICENSE`.

Third-party source: [mattpocock/skills](https://github.com/mattpocock/skills).
Reviewed upstream commit on 2026-10-06:
[`6fd947921b935b7e1e69293a200400f0fdd5c15f`](https://github.com/mattpocock/skills/tree/6fd947921b935b7e1e69293a200400f0fdd5c15f).

| Skill | Exact upstream directory | Purpose/status | Required companions or support |
|---|---|---|---|
| `tdd` | [skills/engineering/tdd](https://github.com/mattpocock/skills/tree/main/skills/engineering/tdd) | Proposed primary: behavior-focused test-first work | `tests.md`, `mocking.md`; `codebase-design` for interface/seam questions; `code-review` for the review stage |
| `codebase-design` | [skills/engineering/codebase-design](https://github.com/mattpocock/skills/tree/main/skills/engineering/codebase-design) | Proposed primary: shared module/interface vocabulary | `DEEPENING.md`, `DESIGN-IT-TWICE.md`; alternative designs use subagents |
| `code-review` | [skills/engineering/code-review](https://github.com/mattpocock/skills/tree/main/skills/engineering/code-review) | Proposed support for TDD's review stage | Parallel subagents; repo standards/spec; `docs/agents/issue-tracker.md`, configured by the setup skill |
| `setup-matt-pocock-skills` | [skills/engineering/setup-matt-pocock-skills](https://github.com/mattpocock/skills/tree/main/skills/engineering/setup-matt-pocock-skills) | Proposed setup support | Keep its `domain.md`, issue-tracker templates, and `triage-labels.md`; triage setup is conditional on installing `triage` (outside this proposal) |

Preserve upstream `agents/openai.yaml` where present. Run the upstream setup
skill in each consumer repository with that repository owner's approval. It
creates repository-local tracker/domain instructions; this publication task
does not run it or change issue settings. TDD asks the user to agree test seams.
Agent installation support does not establish that upstream subagent or Skill
tool assumptions work in every target agent.

## Native Pack setup remaining

1. Confirm the proposed two primary skills and their two support skills, or
   supply a replacement subset and review its dependencies.
2. The owner signs in at [Create pack](https://www.skills.sh/packs/create) with
   Vercel and chooses the intended team. GitHub CLI authentication is separate.
3. Enter the proposed name/description. Use the native **skills.sh** source
   picker to add the exact public Matt Pocock skill entries. Verify source,
   name, and companions; avoid importing his whole repository.
4. Add the authored collection using the public source picker if indexed. If
   importing from GitHub requires a connection, the owner must authorize that
   connection separately. Select only this repository's authored skills. A
   local folder/ZIP upload is another native option; it is a snapshot.
5. Review the final list and file contents in the builder, then create the
   Pack only after authorized access is available. Record its returned URL
   and exact native install command here, and test it in disposable projects.

Native [Pack documentation](https://www.skills.sh/docs/packs) describes sharing
by unlisted link, which is not an access-control boundary. Files need valid
skill metadata; binary and oversized individual files are filtered. Inspect
the result for companions after any upload/import.

## Maintenance and update limits

The documented consumer flow is `npx skills update`, including a named-skill
update, after Pack contents change. New installations use the current Pack
contents. Automatic upstream-to-Pack refresh frequency, commit pinning, and
editable source replacement are **not verified**. Confirm these in the native
UI when creating the Pack; uploads need explicit refresh unless the service
demonstrates otherwise. Re-review upstream skill references and setup behavior
when updating. Record the reviewed commit, selection, returned Pack URL, and
date of the isolated installation check here.
