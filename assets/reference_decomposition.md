# AI Workflow: From Financial Pack to Tax Readiness & Financial Health Scorecard

## 1. Goal
Convert a raw monthly/YTD financial pack into a repeatable AI-driven workflow that produces a dashboard with:
- estimated tax liability,
- deduction tracking by category,
- financial health ratios in plain language,
- quarterly trend comparisons,
- prioritized action items,
- a full audit trail a human can review.

## 2. Design rule
The dashboard contract was derived backward from the target end-state, but the operational workflow below runs forward from the attached source artifact.

## 3. Agent execution contract
Every workflow step must return the same envelope:

- `step_id`
- `status` = `success | needs_review | blocked`
- `confidence` = `0.00 - 1.00`
- `inputs_used`
- `evidence`
- `assumptions`
- `blockers`
- `human_review_required`
- `outputs_created`

This keeps the workflow human-readable and machine-callable.

## 4. Required inputs

| Input | Needed to start | Needed for full dashboard | Purpose | If missing |
|---|---:|---:|---|---|
| Financial pack PDF / XLSX / CSV | Yes | Yes | Base P&L / monthly financial data | Workflow cannot start |
| Entity name + fiscal year rules | Yes | Yes | Correct period labeling | Block until confirmed |
| Tax profile (entity type, jurisdiction, filing method) | No | Yes | Tax estimate and quarterly payment logic | Publish provisional tax card only, or block tax card |
| Balance sheet snapshot | No | Yes | Current ratio and debt-to-equity | Suppress those cards and raise action item |
| Headcount / employee count | No | Yes | Revenue per employee | Suppress that card and raise action item |
| Historical periods (prior quarters / 12-24 months) | No | Yes | Trend view | Show current snapshot only |
| Invoice / vendor-level expense detail | No | Strongly recommended | Better deduction classification and miscategorization detection | Lower confidence, more human review |
| Prior estimated tax payments | No | Yes | Net tax due / next payment | Show gross estimate only |
| Benchmark library by industry / size | No | Yes | Green/yellow/red status logic | Use provisional default thresholds and label as such |
| Mileage / home office evidence | No | Optional | Specific deduction opportunities | Do not create those alerts without evidence |

## 5. Final outputs

| Output | Description |
|---|---|
| `source_manifest.json` | What file was read, period detected, fiscal assumptions, parse confidence |
| `normalized_ledger.csv` | One row per account, period, amount, source reference |
| `coa_mapping.csv` | Raw account mapped to canonical dashboard bucket with confidence |
| `review_queue.json` | Low-confidence or policy-sensitive classifications |
| `metrics.json` | Revenue, COGS, opex, tax estimate, ratios, trend metrics |
| `action_items.json` | Prioritized alerts with evidence and due dates |
| `dashboard_payload.json` | UI-ready cards, labels, status colors, text explanations |
| `qa_report.md` | Tie-outs, reconciliation checks, blocked items, overrides |
| `override_log.json` | Human-approved corrections persisted for future runs |

## 6. Forward workflow in execution order

### Step 1. Intake the attachment
**Agent does**
- Read the uploaded financial pack.
- Detect entity, period end, month columns, grand totals, and document type.
- Classify the source as `monthly_ytd_financial_pack`.

**Outputs**
- `source_manifest.json`
- `document_type`
- `parse_strategy`

**Rules**
- Never assume calendar-year reporting if month headers imply a fiscal year.
- Preserve the original file hash for version control.

**Edge cases**
- If the file is scanned or unreadable, route to OCR/manual rescue.
- If multiple entities or locations appear in one file, split before continuing.
- If there are multiple tables, tag each table with a section name before merging.

---

### Step 2. Extract the table into structured rows
**Agent does**
- Convert the wide table into long-form rows with fields such as:
  - `section`
  - `parent_account`
  - `account_name`
  - `period`
  - `amount_raw`
  - `source_page`
  - `source_row_label`
  - `is_subtotal`
  - `is_grand_total`

**Outputs**
- `normalized_ledger_stage1.csv`

**Rules**
- Preserve subtotal rows for reconciliation, but do not allow them into additive metric calculations.
- Keep original text labels exactly as they appear before mapping.

**Edge cases**
- Merged cells or blank parent labels -> inherit nearest valid parent header.
- Duplicate subtotal rows -> retain one as reference, mark the rest as duplicates.
- Period headers in unusual order -> sort by detected fiscal sequence, not alphabetically.

---

### Step 3. Normalize signs, periods, and accounting semantics
**Agent does**
- Standardize date labels and fiscal periods.
- Normalize revenue and contra-revenue sign conventions for presentation.
- Keep both `amount_raw` and `amount_normalized`.
- Tag rows as one of:
  - `revenue`
  - `contra_revenue`
  - `cogs`
  - `opex`
  - `capex_candidate`
  - `non_operating`
  - `tax_adjustment_candidate`

**Outputs**
- `normalized_ledger.csv`

**Rules**
- Never discard the original sign.
- Treat refunds, discounts, and comp/meal discounts as possible contra-revenue until proven otherwise.
- Annualization is allowed only if the workflow clearly labels the estimate as annualized.

**Edge cases**
- Revenue lines use negative accounting signs -> normalize for display but preserve raw values.
- Partial-year data -> compute YTD and optional annualized views separately.
- Mixed sign usage across categories -> flag for human review.

---

### Step 4. Map raw accounts into canonical dashboard buckets
**Agent does**
- Map each raw account into a canonical chart of accounts used by the target dashboard.
- Assign:
  - `canonical_bucket`
  - `canonical_subbucket`
  - `tax_treatment`
  - `mapping_confidence`
  - `review_reason` if confidence is low

**Recommended canonical buckets**
- Revenue
- Cost of Goods Sold
- Payroll & Benefits
- Rent & Facilities
- Technology & Software
- Insurance
- Marketing & Advertising
- Professional Services
- Travel & Meals
- Miscellaneous / Review
- Capex / Fixed Assets
- Non-operating / Other

**Example mapping pattern**

| Canonical bucket | Typical raw-account behavior | Notes |
|---|---|---|
| Revenue | Sales, retail, packaging sales, refunds/discounts as contra-revenue | Net presentation matters |
| Cost of Goods Sold | Food, beverage, packaging, boxes, direct inventory purchases | Keep separate from operating expenses |
| Payroll & Benefits | Wages, salaries, payroll taxes, uniforms, bonuses | Owner pay may require special handling |
| Rent & Facilities | Rent, rates, utilities, facilities overhead | Some utilities may be broken out separately if desired |
| Technology & Software | SaaS, subscriptions, software tools | Needs vendor detail if the account label is vague |
| Insurance | Insurance expense | Usually straightforward |
| Marketing & Advertising | Advertising, promotion, campaigns | Donations should not default here |
| Professional Services | Legal, accounting, consulting, some bank/merchant fees | Commissions may need separate treatment |
| Travel & Meals | Vehicle, mileage, staff transport, meals | Personal/business split may be required |
| Miscellaneous / Review | Misc expense, cash over/short, unclear charges | Always review if material |
| Capex / Fixed Assets | Equipment purchases, depreciation | Handle through capitalization / tax depreciation policy |

**Rules**
- Use hybrid mapping: rules first, AI classification second, human override third.
- Low-confidence mappings must not silently publish as green/healthy.
- Keep a reusable mapping memory so the next run improves.

**Edge cases**
- Equipment purchases posted as expense -> move to capex review.
- Owner salary / owner draw / director compensation -> require entity-specific tax rule.
- Donations -> do not auto-classify as deductible operating expense without policy.
- Discount meals or staff meals -> determine whether they belong in contra-revenue, COGS, payroll, or meals.

---

### Step 5. Build the review queue before calculating the dashboard
**Agent does**
- Create a review queue for any row that is:
  - low confidence,
  - policy-sensitive,
  - material,
  - ambiguous,
  - missing supporting detail.

**Default review triggers**
- `mapping_confidence < 0.80`
- `miscellaneous_bucket > configurable_materiality_threshold`
- owner-related pay present
- capex candidate present
- unusually large month-over-month change
- negative expense or positive revenue in unexpected places

**Outputs**
- `review_queue.json`

**Rules**
- Review queue items should not block the whole workflow unless they affect a critical dashboard card.
- Every review item must include suggested next action.

**Edge cases**
- Too many rows hit the review queue -> downgrade the whole run confidence.
- A single material row explains most of the profit swing -> escalate priority.

---

### Step 6. Enrich missing data needed for the target dashboard
**Agent does**
- Request or ingest the supplemental data required for cards the source pack cannot provide alone:
  - balance sheet snapshot,
  - total debt and total equity,
  - current assets and current liabilities,
  - headcount / average employees,
  - tax entity type,
  - filing jurisdiction(s),
  - prior estimated tax payments,
  - prior months/quarters,
  - invoice-level expense detail,
  - mileage logs,
  - home office evidence,
  - industry benchmark configuration.

**Outputs**
- `enrichment_status.json`

**Rules**
- Missing enrichment data should not be hidden.
- For each missing input, create either:
  - a blocking status for the affected card, or
  - a degraded fallback with a visible confidence label.

**Edge cases**
- No balance sheet -> current ratio and debt-to-equity cards are marked `insufficient data`.
- No headcount -> revenue-per-employee card is suppressed.
- No historical data -> trend table becomes current-period-only.
- No invoice detail -> miscategorization insights remain high-level and lower confidence.

---

### Step 7. Compute the deduction tracker
**Agent does**
- Sum deductible amounts into dashboard buckets.
- Separate:
  - clearly deductible,
  - likely deductible but needs review,
  - non-deductible / limited-deductibility,
  - capex or depreciation items.
- Output per bucket:
  - `amount`
  - `confidence`
  - `status_color`
  - `flag_count`

**Suggested logic**
1. Start from normalized opex and COGS.
2. Exclude clear contra-revenue and non-operating items.
3. Apply tax-treatment rules:
   - ordinary business expense,
   - meals/vehicle split required,
   - limited deduction,
   - capitalization required,
   - unsupported / unclear.
4. Aggregate to the dashboard buckets.

**Rules**
- Miscellaneous must never be treated as fully safe by default.
- Capex and depreciation need a tax-policy layer, not just category mapping.
- Opportunity alerts need evidence, not guesswork.

**Edge cases**
- Large `Miscellaneous` bucket -> create action item.
- Mixed personal/business expense categories -> split or route to review.
- Only summarized P&L available -> do not fabricate detailed vendor-level deduction claims.

---

### Step 8. Compute the tax estimate
**Agent does**
- Estimate current tax liability using:
  - adjusted profit,
  - entity type,
  - filing jurisdiction,
  - allowable deductions,
  - prior estimated payments,
  - safe-harbor or forecast logic if configured.

**Suggested formula skeleton**
- `adjusted_profit = normalized_revenue - cogs - deductible_opex +/- review_adjustments`
- `taxable_income = adjusted_profit + nondeductible_addbacks - allowed_tax_adjustments`
- `estimated_tax = federal_component + state_component + local_component + entity_specific_component`
- `net_tax_due = estimated_tax - taxes_paid_to_date`

**Outputs**
- tax cards:
  - total estimated tax,
  - tax by component,
  - amount already paid,
  - next estimated payment,
  - confidence,
  - disclaimer text.

**Rules**
- If entity type or jurisdiction is unknown, do not fake precision.
- Show `directional estimate` if assumptions are incomplete.
- Payment reminders require a due date source or configured calendar.

**Edge cases**
- Unknown entity type -> publish provisional range or block tax card.
- Multi-state activity -> route to nexus review.
- Negative taxable income -> show tax benefit / no current payment, but still track filings.
- Prior tax payments missing -> show gross estimate only.

---

### Step 9. Compute the financial health ratios
**Agent does**
- Compute and explain in plain language:
  - `current_ratio = current_assets / current_liabilities`
  - `debt_to_equity = total_debt / total_equity`
  - `revenue_per_employee = annualized_revenue / average_headcount`
- Optional support metrics:
  - gross margin,
  - operating margin,
  - quick ratio.

**Outputs**
- ratio cards with:
  - value,
  - plain-English label,
  - benchmark status,
  - explanation text,
  - confidence.

**Rules**
- Benchmark thresholds must come from a configurable benchmark library, not hard-coded guesses.
- Every ratio card needs a fallback state:
  - `healthy / watch / action needed / insufficient data`

**Edge cases**
- Current liabilities = 0 -> ratio may be infinite; do not display misleadingly.
- Equity <= 0 -> debt-to-equity needs special handling and warning text.
- Headcount missing or unstable -> suppress revenue/employee or use clearly labeled average headcount if available.

---

### Step 10. Build the quarterly comparison and trend view
**Agent does**
- Convert monthly data into fiscal quarters.
- For each target metric, compute:
  - current quarter value,
  - prior quarter value,
  - change amount,
  - change direction,
  - trend label.

**Outputs**
- `quarterly_trends.json`

**Rules**
- The fiscal quarter logic must respect the detected fiscal year, not assume Jan-Mar / Apr-Jun unless configured.
- Trend labels should be plain language:
  - `Improving`
  - `Stable`
  - `Worsening`
  - `Insufficient history`

**Edge cases**
- Fewer than 2 comparable quarters -> show current period only.
- Partial current quarter -> label as `partial`.
- Backfilled data changes prior quarters -> re-run trend calculations and version the snapshot.

---

### Step 11. Generate action items
**Agent does**
- Produce prioritized, human-readable action items with:
  - `title`
  - `severity`
  - `why_it_matters`
  - `recommended_action`
  - `owner`
  - `due_date`
  - `evidence`
  - `confidence`

**Trigger examples**
- Miscellaneous bucket exceeds threshold
- Low-confidence mapping on material expense
- Tax payment due within configured time window
- Ratio falls outside configured industry range
- Two consecutive quarters worsen
- Missing critical input prevents full dashboard
- Capex likely misbooked as expense
- Vehicle/meals/home office opportunities supported by evidence

**Rules**
- Suppress speculative alerts.
- Every alert needs evidence and a recommended next step.
- Low-confidence alerts must say they require review.

**Edge cases**
- Evidence is weak -> demote to `review suggestion`.
- Conflicting signals -> prefer neutral language and human review.
- Too many alerts -> rank by materiality and due date.

---

### Step 12. QA, reconciliation, and human approval
**Agent does**
- Tie extracted totals back to the source.
- Verify:
  - month sums match source totals,
  - subtotals are not double-counted,
  - normalized revenue and COGS are internally consistent,
  - source percentages are approximately reproducible where possible,
  - dashboard totals trace to mapped ledger rows.
- Route material variances or low-confidence cards to human review.

**Outputs**
- `qa_report.md`
- approval status

**Rules**
- No dashboard card should publish without lineage.
- Any material variance must be visible in the QA report.
- Human overrides must be logged and reusable in future runs.

**Edge cases**
- Source totals do not tie out -> block publish.
- Mapping changes alter prior results -> version both runs and explain delta.
- Reconciliation fails only for non-critical cards -> publish partial dashboard with visible warnings.

---

### Step 13. Publish and schedule refresh
**Agent does**
- Build the final dashboard payload.
- Render cards, trend tables, status colors, and action items.
- Store:
  - current snapshot,
  - prior snapshot,
  - audit trail,
  - overrides,
  - unresolved review items.
- Schedule reruns:
  - on monthly close,
  - on new invoice batch,
  - on balance-sheet upload,
  - on manual override.

**Outputs**
- `dashboard_payload.json`
- `dashboard_snapshot`
- `audit_bundle`

**Rules**
- Preserve historical snapshots for quarter-over-quarter comparison.
- Do not overwrite human overrides without review.
- Every rerun must retain change history.

---

## 7. Edge-case playbook

| Edge case | Detection | System response | Severity |
|---|---|---|---|
| Scanned / unreadable PDF | Low parse confidence | OCR or manual extraction queue | High |
| Revenue sign inversion | Revenue mostly negative in raw data | Normalize for presentation, preserve raw sign | Medium |
| Subtotals double-counted | Rows contain `Total` / `Grand Total` | Exclude from additive calculations | High |
| Only summarized P&L available | No invoice-level detail | Publish high-level deduction tracker only; lower confidence | Medium |
| Balance sheet missing | No current assets/liabilities or debt/equity | Suppress those ratio cards; add action item | High |
| Headcount missing | No employee count | Suppress revenue/employee card | Medium |
| Unknown tax entity or jurisdiction | No tax profile | Publish provisional tax estimate or block tax card | High |
| Partial-year data only | Less than 12 months or incomplete quarter | Separate YTD from annualized results; label clearly | Medium |
| No historical periods | Fewer than 2 quarters | Show snapshot-only trend state | Medium |
| Multi-entity data mixed together | Multiple entities / locations detected | Split before mapping and benchmarking | High |
| Capex mixed into opex | Equipment/depreciation signals | Move to review queue | High |
| Owner compensation ambiguity | Owner pay or director draw present | Require entity-specific human rule | High |
| Miscellaneous bucket too large | Bucket exceeds materiality threshold | Raise review item and confidence warning | Medium |
| Negative equity or zero liabilities | Ratio denominator invalid | Special ratio handling and warning text | Medium |
| Refunds / discounts misread as expenses | Contra-revenue patterns detected | Reclassify before margin/tax calculations | High |
| Currency or fiscal calendar mismatch | Mixed periods or currencies | Block publish until normalized | High |

## 8. Minimum publish criteria
The workflow is considered complete only if all of the following are true:

1. Source totals reconcile to extracted data.
2. Every dashboard card is either:
   - populated with confidence and evidence, or
   - explicitly marked `insufficient data`.
3. No material low-confidence classification is silently published.
4. Every action item includes evidence and a next step.
5. Human overrides are saved for the next run.
6. The final dashboard payload can be regenerated from the audit trail.

## 9. Practical implementation note
For this specific source type, the smartest implementation is:

1. Start with the uploaded financial pack.
2. Parse and normalize it into a canonical ledger.
3. Map accounts into dashboard buckets.
4. Add enrichment gates for tax profile, balance sheet, headcount, and history.
5. Compute only the cards supported by current evidence.
6. Use action items to request whatever is still missing.
7. Re-run automatically when new data arrives.

That avoids fake precision while still moving steadily from a static financial pack toward the dynamic dashboard in the target end-state.