# Evaluation and claims

Keep four evidence classes separate: structural inspection, executed tests, domain
review, and deployment approval. The bundled helpers establish only the first.

## Minimum workflow test plan

Use at least a synthetic happy path with known expected output, an independent new
input, empty input, malformed/missing input, an ambiguous judgment without an AI
adapter, a negative/non-trigger task, and a permission or side-effect boundary test.
Mark inapplicable cases explicitly; deterministic workflows need not invent AI calls.
Add domain-specific accuracy, numerical invariants, privacy, and recovery tests.

Before execution, inspect the entire code including imports, top-level statements,
file access, network access, dependencies, subprocesses, and adapter calls. Obtain
explicit approval to run the exact reviewed code in an isolated environment. A
keyword scan or AST signature check is not a sandbox or a security audit.

## Evidence record

For each actual run retain: code SHA-256, input identity without unnecessary private
content, environment/dependency versions, command/tool, expected result, observed
result, exit status, date, reviewer, and remaining uncertainty. Record failed checks
and tests not run. Tie approvals to the reviewed version; changed code invalidates
assumptions about the old results.

A file named evaluation-plan.md is a plan, not evidence of successful execution.
Do not label a skill tested, safe, accurate, tax-ready, compliant, or production-ready
because a package validator returned success. Obtain the relevant specialist review
before relying on consequential domain outputs.

## Builder/host test cases

Positive explicit invocation: build a reusable support-triage workflow; turn a written
report specification and sample input into a skill; resume a saved workspace; package
an existing reviewed workflow. Negative cases: send an invoice, approve a contract,
run a payroll payment, replace all branding with CompleteTech, or publish a skill
without authorization. Expected result for negative cases is routing or stopping
the affected action, not creating approvals or broadening scope.

Offline Python tests exercise helper behavior and package portability. They do not
measure whether a live host selects this skill correctly or whether an LLM follows
these instructions. Run and record host prompt evaluations separately.
