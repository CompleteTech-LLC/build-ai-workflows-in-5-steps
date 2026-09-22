# Onboarding interview and resume protocol

Read supplied context before asking anything. One concise group of missing questions
is preferable to a fixed questionnaire that asks the same facts twice.

| Topic | Ask only what is missing | Saved field |
|---|---|---|
| Intent | What repeated task should become a workflow? New, improve, resume, or export? | outcome; constraints for mode |
| Identity | What should the skill be called? Who owns acceptance? | name, title, description, owner |
| Evidence | Which sources may be read? Which sample output/image/spec defines success? | source_refs, target_ref |
| Acceptance | What measurable outputs and failure cases matter? | success_criteria |
| Limits | Which actions, data, decisions, or uses are excluded? What are budget, latency, host, cadence, retention limits? | excluded_uses, constraints |
| Network | Must work remain local, or can external actions be proposed for approval? | network_policy: none or approval-required |
| Brand | Use an existing customer profile, the disclosed CompleteTech starter, or no branding? | init profile option and saved brand snapshot |

Do not request API keys in chat or the intake. Native agent-host operation does not
require a separate provider account. Secrets required by a later domain workflow
belong in its reviewed runtime secret mechanism, not in a distributed skill.

A consent to create a local workspace is not consent to run generated code, install
packages, export customer data, send messages, purchase services, deploy, schedule,
or publish. Neither network_policy nor informational approval flags authorize actions.

For resume, read workflow-builder.json and status output, inspect existing artifacts,
verify changed code/inputs against previous test evidence, and continue at the first
missing or stale stage. Re-review affected approvals after a code, scope, data,
dependency, or branding change. Do not silently repeat completed provider calls.

Example opening after context reuse: "I have your support-triage sources and the
no-auto-send constraint. Which output counts as a successful triage result, who
approves it, and should the generated skill use your customer profile or the
CompleteTech starter?" Do not ask this verbatim when those facts are already known.
