# CompleteTech library handoff

The orchestrator owns shared lifecycle state. This builder owns technical design
and the resulting workflow skill. Preserve the orchestrator's existing project_state
fields and supply a proposed update rather than overwriting unrelated tracks.

```yaml
project_state:
  workflow_type: user-selected-domain
  client: verified-client-or-TBD
  workflow: workflow-name
  stage: current-verified-stage
  owner: verified-owner-or-TBD
  source_artifacts: []
  artifact_versions:
    - artifact: workflow-skill
      path: verified-export-path
      version: actual-version
      status: draft
      source_artifacts: []
  known_facts: {}
  assumptions: []
  missing_info: []
  dependencies: []
  blockers: []
  approvals: {}
  next_decision_needed: review-generated-code-and-tests
  next_skill: appropriate-owner-or-TBD
  downstream_handoff:
    skill_key: actual-child-skill-name
    workspace: verified-workspace-path
    source_sha256: {}
    brand_profile: verified-profile-path
    brand_origin: custom-or-completetech-starter-or-unbranded
    executed_tests: []
    untested_behavior: []
    structural_validation: actual-observation
```

This is an illustrative handoff shape, not proof of approval or an executable
orchestrator adapter. Use actual artifact versions/hashes and observed checks.
Do not copy raw source contents or credentials. Leave unknown facts unresolved.

Route commercial discovery to agentic-discovery-skill; approved execution artifacts
to agentic-delivery-skill; material security risks to agentic-security-review-skill.
Proposal, contract, invoice, customer-success, case-study, email, envelope, and
certificate skills remain responsible for their own artifacts and approval gates.
Measured usage can go to ai-usage-ledger-skill; do not invent cost savings.

A new workflow-builder skill is not automatically registered in another repo's
routing table. Offer or perform that separate change only when authorized, and
verify the actual owning repository rather than assuming it was updated.
