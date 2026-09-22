# Manual distribution and registry handoff

Package the builder with scripts/package_builder_skill.py into a NEW destination.
Publish only the resulting agentic-workflow-builder-skill folder after review,
not the entire development checkout or a user's workflow workspace. The generated
ZIP has one top-level skill folder and a versioned integrity manifest.

Before a ClawHub or other registry upload: confirm explicit publication authority,
current registry rules, license and brand rights, the intended name/version, privacy,
and the exact inventory. Use that registry's current documented tool outside this
skill. No registry account, CLI install, upload, release, tag, background task, or
host registration is performed by these scripts. No registry acceptance is claimed.

The portable SKILL.md follows Agent Skills; agents/openai.yaml is optional Codex UI
metadata. Host-specific settings are not universal permission grants. Validate and
review the actual package in the intended host before sharing it with users.

For a generated child skill, review that child's separate code, branding, dependencies,
inputs, and approvals. Permission to distribute the builder is not permission to
publish a customer's workflow or data.
