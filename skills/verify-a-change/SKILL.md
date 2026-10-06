---
name: verify-a-change
description: Choose and run proportionate checks for an engineering change, then report evidence and gaps before declaring the change complete. Use when preparing a change handoff or checking whether a fix meets its acceptance criteria.
license: MIT
metadata:
  author: butterlyn
  status: demonstration
  version: "0.1.0"
---

# Verify a change

This is a small demonstration skill for the Engineering Skills collection.
It works with the project's available commands and tools; it requires no
particular agent, language, or test framework.

Translate the requested outcome into observable claims. For each material
claim, choose the smallest check that could expose an incorrect implementation:
a reproduction for a bug, a public-interface test for behavior, a rendered
page for a visual change, or an installation for a packaging change. Read the
project's instructions and documented commands before inventing new ones.

Run the relevant checks after the last change that could affect them. Inspect
exit status and output. A command that exits successfully without exercising
the claimed behavior is insufficient evidence. For a fix, compare the original
failure with the result after the change when a safe reproduction is available.

If a check fails, investigate and correct the cause within the user's scope,
then repeat the affected check. If a required check needs unavailable access,
an external service, or an action outside the user's authorization, describe
the missing evidence and the smallest next step. Do not treat an unavailable
check as passing or expand permissions to obtain a result.

Use [the evidence template](references/evidence-template.md) when several
claims need a compact handoff. State what changed, which claims were checked,
the commands and observed results, and any remaining uncertainty. Distinguish
structural validity, installation compatibility, and observed behavior where
those differ. Do not infer agent behavior merely from installing files.

This skill helps organize evidence. It does not replace specialist review,
the repository's required checks, or the user's judgment about deployment.
