# Format and library sources

Reviewed for this conversion on 2026-09-22. Host behavior and installation paths can
change; verify the current official documentation when adapting distribution.

## Primary format/host references

- [Agent Skills specification](https://agentskills.io/specification): scoped name/description, YAML frontmatter, progressive references, scripts, and a matching installed directory.
- [OpenAI Codex skills](https://developers.openai.com/codex/skills/): local skill discovery, explicit invocation, agents/openai.yaml, and implicit-invocation policy.
- [Claude Code skills](https://code.claude.com/docs/en/skills): project skill directories, slash-command invocation, host-specific permissions and visibility controls.

The frontmatter uses the shared specification; optional Codex UI policy is separate.
No broad allowed-tools permission is granted. Other hosts may handle invocation
differently. Structural tests are not live-host compatibility certification.

## CompleteTech examples actually inspected

- [agentic-discovery-skill SKILL.md](https://github.com/CompleteTech-LLC/agentic-discovery-skill/blob/main/SKILL.md), blob 576e0c711198722f5e3172391d376000b3f6ed9a: purpose, boundaries, resource guide, artifact selection, verified facts, specialist handoffs.
- [agentic-contract-skill README](https://github.com/CompleteTech-LLC/agentic-contract-skill/blob/main/README.md), blob 6c8bf8816ea1b22fe5facb6fd610d94ebda81c07: explicit configuration/overrides, branded examples, runtime and licensing boundaries.
- [agentic-services-orchestrator-skill](https://github.com/CompleteTech-LLC/agentic-services-orchestrator-skill): workflow state, approval/risk triage, artifact versions, and specialist ownership.
- [ai-usage-ledger-skill](https://github.com/CompleteTech-LLC/ai-usage-ledger-skill): onboarding disclosure, persistent preferences, resumable operation, and opt-in boundaries.
- [agentic-delivery-skill renderer](https://github.com/CompleteTech-LLC/agentic-delivery-skill/blob/main/scripts/render_pdf.py), blob a1477153f9d0d9e4db5aa2f620981b5a796e22fd: starter palette and tagline; see ../BRANDING.md for exact tokens.

The library examples informed structure and boundaries; they are not bundled runtime
dependencies. This change does not claim to have audited every listed repository
or to have changed their routing tables. Brand identity is not copied into customer
facts. The six-step method and existing child exporter remain the repository's own
teaching implementation; Agent Skills is an external open format.
