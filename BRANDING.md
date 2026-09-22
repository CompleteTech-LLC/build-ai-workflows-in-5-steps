# Workflow brand handoff

## Precedence

Explicit `--brand-profile` → `<outputs>/brand-profile.json` →
`assets/brand-profile.json` (CompleteTech starter).

`--unbranded` is an explicit opt-out and cannot be combined with an explicit profile.
A present but empty, invalid, missing-explicit, or symlinked profile is an error,
not permission to substitute CompleteTech. Custom profiles are preserved without
merging provider identity, contact information, logos, or colors into them.

## Profile contract (version 1)

```json
{
  "schema_version": 1,
  "version": "1.0.0",
  "name": "Customer Business",
  "colors": {
    "accent": "#123456",
    "background": "#FFFFFF",
    "text": "#111111"
  },
  "logo": "logo.png",
  "voice": "Clear, practical, and welcoming"
}
```

Required: schema_version 1, a nonempty version/name, and a nonempty map of six-digit
hex colors. Additional profile fields are retained. `accent` controls the optional
Codex UI brand color; other tokens are carried for downstream use. A custom profile
without `accent` does not inherit CompleteTech's accent.

Omit `logo` for text-only branding. A supplied logo must be a local PNG or JPEG,
within the profile directory, no larger than 10 MiB. Absolute/remote paths,
traversal, symlinks, SVG, and missing assets are rejected. The exporter copies only
that asset and rewrites its profile path to the packaged `assets/` path. It does
not fetch assets or bundle fonts. Visual quality and rights still need human review.

The emitted profile is `assets/brand-profile.json`; the package manifest records
its version, selection source, and file hash. Existing source profiles are not
modified. The output README and agents/openai.yaml use the selected brand. The
workflow's arbitrary generated renderer is not automatically restyled; agents and
renderers must explicitly consume the profile when producing later artifacts.

## CompleteTech starter provenance

The palette and tagline follow the public
[agentic-delivery-skill renderer](https://github.com/CompleteTech-LLC/agentic-delivery-skill/blob/main/scripts/render_pdf.py),
read at blob `a1477153f9d0d9e4db5aa2f620981b5a796e22fd`:

| Token | Value |
|---|---|
| accent | `#1E3A8A` |
| accent_dark | `#0F172A` |
| accent_soft | `#EEF2FF` |
| muted | `#64748B` |
| border | `#E2E8F0` |
| zebra | `#F8FAFC` |

Tagline: **Innovation at Every Integration**. The logo is the existing
`assets/completetech_logo.jpg` in this repository, blob
`1325b5a410c5dc4c8af75fce515a188714262c25`. No replacement artwork was invented.

The starter is an example, not a statement that CompleteTech owns, authored, or
endorses a customer's outputs. Toolkit attribution and customer identity are
separate. Code licensing does not grant trademark rights. Confirm asset rights,
contrast, legibility, customer consent, and final output presentation before use.
