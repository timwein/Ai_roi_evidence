# Method, scope, and inclusion bar

This file is authoritative. The daily agent run reads it before searching.

## Purpose

Track hard evidence that ordinary, non-software corporations are getting
measurable ROI from AI spend — specifically **top-line revenue impact**.

The thesis being tested: most published AI ROI evidence is cost-side (headcount
avoidance, ticket deflection, cycle-time reduction) and comes from tech companies
or from vendors marketing to them. Revenue-side evidence from non-tech incumbents
is the scarcer and more load-bearing signal. If it is accumulating, that is a
materially different world than if it is not.

**Cost savings are not a revenue shape.** A cost story never becomes S1, S2 or
S3. Since 2026-07-30 cost evidence has its own ledger (C1–C4, below), counted
separately and never pooled with the revenue totals. The one thing that *does*
cross over: a cost collapse large enough to make a previously uneconomic segment
newly serveable is Shape 3, because the output is new demand, not a lower
expense line.

## The three shapes

Every finding is assigned exactly one.

### S1 — Velocity

AI speeds up, expands the capacity of, or raises the hit rate of a process that
produces revenue. Underwriting and policy issuance, quote-to-bind, sales
coverage, listing throughput, trial enrollment, loan origination, target
screening.

**Test:** the disclosed number is an *input* metric — time, throughput, capacity,
conversion, hit rate — not revenue itself. If revenue is attributed, reclassify
to S2 or S3.

**Standing caveat:** S1 is a leading indicator, not realized ROI. Faster issuance
only matters if bound premium actually rises. Most S1 disclosures are never
followed by a revenue number, and that silence is informative — always record
whether the company also disclosed the revenue conversion or conspicuously did
not.

### S2 — Share

Attributed incremental revenue on existing products sold into existing segments.
Personalization conversion lift, dynamic pricing, yield, attach rate, churn
reduction, cross-sell into the installed base.

**Test:** absent this AI capability, would this customer have bought something
similar from somebody? If yes → S2. A competitor lost the sale.

Real ROI for the firm and real alpha for an investor, but **zero-sum at the
industry level and GDP-neutral**. Say so in the assessment. Do not let firm-level
wins be narrated as economy-level growth.

### S3 — New TAM

**The priority bucket.** Revenue from use cases, segments, or markets not
previously served by anyone — technically impossible, economically unviable, or
unconceived. GDP-additive rather than share-shifting. Especially where it depends
on a recent frontier capability jump.

Run all four tests and record the answers in `shape_justification`:

- **(a) Counterfactual purchase.** Absent the AI, would this buyer have bought
  anything at all, from anyone?
- **(b) Prior alternative.** If buyers previously did nothing, went without, or
  used an unpaid manual workaround → S3. If they bought a competitor's product →
  reclassify to S2.
- **(c) Capability gate.** Does it require an AI capability that did not exist
  roughly 24 months ago? Frontier complexity is the tell. If 2019-era ML would
  have worked, it is probably S2 in new language.
- **(d) Newly economic.** Was the segment unserved because unit economics did not
  close, and did AI change the cost curve enough to open it?

If it looks like S3 but the source does not establish the counterfactual, use
shape `S3-CANDIDATE` and state exactly what evidence is missing. Do not promote
it.

**S3 is the most gameable bucket.** Every company claims new TAM; almost none
have it. Expect to reject most S3 claims. One honest S3 beats six inflated ones.
Misclassifying S2 as S3 is the single worst failure mode of this log, because the
whole point is measuring whether AI creates new demand or reallocates it.

Productive hunting grounds for genuine S3:

- Insurance: risk classes previously declined as uninsurable, now priced.
- Pharma/biotech: target or indication space previously unscreenable.
- Industrials: autonomy or capability sold as a **new** subscription line — a new
  product, not a better one.
- Healthcare: diagnostics or monitoring at price points that previously supported
  no service at all.
- Professional services: work never billable because delivery cost exceeded
  willingness to pay.
- Any incumbent selling an AI-enabled SKU with no predecessor in its own catalog.
- Long-tail or SMB segments served at quality levels that previously required
  enterprise pricing.

## The cost ledger — C1 to C4

Added 2026-07-30. Rationale, stated plainly so a later reader can judge it: five
consecutive runs produced almost no revenue-attributed evidence, because the
market is early and non-tech incumbents are not yet putting revenue numbers next
to AI. A log that only records absence stops being read. Cost evidence *is*
arriving regularly, and it is a real if lesser answer to "is anyone getting
anything out of this."

**The danger this creates, and the rule that contains it.** Cost evidence is
perhaps an order of magnitude more abundant than revenue evidence and is
systematically lower quality — self-reported productivity percentages,
undefined composite "value" metrics, headcount actions with several plausible
causes. If it were pooled with S1–S3 the log would look productive while losing
the ability to answer the question it exists to answer. Therefore:

- Cost entries live in a **separate ledger with separate counts.** They never
  appear in the S1/S2/S3 totals, the revenue tiles, or the "revenue findings"
  number.
- **A single disclosure is logged in exactly one ledger.** Do not double-log the
  same statement as both a revenue shape and a cost shape. Where a disclosure has
  a cost number and a speculative revenue path, log it once where the *number*
  sits and note the other reading in `shape_justification`. Worked example:
  Ategrity's "60% fewer resources" (logged 2026-07-30) is a cost figure with a
  new-TAM story attached; it is logged **once**, as S1, because the launch-capacity
  claim is what the entry is about.
- **The inclusion bar is unchanged.** Named company, a specific number or an
  explicit on-the-record executive statement of material impact, a citable dated
  source. The same tiers, the same status labels, the same skepticism rules. Cost
  being easier to find is not licence to lower the bar — it is the reason not to.

**The 2×2.** Sector × function, because the cell comparison is the whole point:

| | Non-tech | Tech |
|---|---|---|
| **Software engineering** | **C3** | **C1** |
| **Everything else** | **C4** | **C2** |

- **C1 — tech / engineering.** The easy cell. Expect the most and believe it
  least: this is where the labs and platforms have every incentive to publish.
- **C2 — tech / non-engineering.** Support, sales, marketing, G&A inside a
  technology company.
- **C3 — non-tech / engineering.** A bank's or an insurer's own developers. Real,
  but a small share of a non-tech company's cost base — a 40% coding gain on 3%
  of opex is not a margin event.
- **C4 — non-tech / non-engineering.** **The cell that matters.** Claims
  handling, call centres, back office, store and field operations — where the
  bulk of the economy's labour cost actually sits. Hardest to evidence and the
  one to weight most heavily.

**Standing traps specific to cost claims.** Record which applies in
`shape_justification`:

1. **Adoption dressed as saving.** "40% of our code is AI-generated" and "75% of
   new code" are *adoption* metrics. They say nothing about cost. Say so.
2. **Productivity that management explicitly refuses to bank.** The tell is a
   CEO volunteering that the gain is reinvested, not saved. Amex's Squeri: *"that's
   really not a savings because what that does is allows us to do more."* Log it and
   quote the disclaimer — an executive declining to claim a saving is high-value
   evidence.
3. **Composite "value" metrics.** "Economic value," "business value,"
   "productivity savings" are company-defined constructs mixing cost avoidance,
   loss avoidance and revenue. Never present one as a cost saving without saying
   what it contains, and flag when the company will not say.
4. **Headcount with many parents.** Layoffs get an AI narrative in the press
   release and a restructuring rationale in the 8-K. Ask what the company actually
   attributed. Telstra is the cleanest counter-case: real labour savings, and a CEO
   who *"could not point to a specific role that AI has directly replaced."*
5. **Cost avoidance vs realized reduction.** Hiring you did not do is not an
   expense line that fell. Both are loggable; conflating them is not.
6. **The run-cost offset.** Inference, licensing and cloud spend can eat the
   saving. Where a company raises this, capture it — it is the load-bearing
   objection to the whole cost thesis.

## Scope

Scope below governs the **revenue** log. The cost ledger deliberately admits
technology companies, since C1 and C2 exist precisely to hold them.

**In:** non-software, non-tech-platform corporations. Industrials, manufacturing,
CPG, retail, grocery, healthcare providers and payers, pharma, banks, insurers,
energy, utilities, telecom, transport, logistics, hospitality, restaurants,
agriculture, construction, real estate, media, professional services.

**Out as subjects:** software vendors, hyperscalers, AI labs, chipmakers,
consultancies selling AI services, AI-native startups. These sell the shovels;
their results describe their own sales, not adoption ROI. They may appear as
*sources* (a vendor call naming a customer's disclosed result) but the subject of
an entry must be the deploying corporation.

### The scope tension — read this

Excluding tech and AI-natives is correct for S1 and S2 but structurally
suppresses S3: incumbents mostly defend existing revenue, while genuinely new
demand is disproportionately created by entrants. Applied naively, this log would
conclude "S3 is rare" when S3 is partly just out of frame.

**Resolution:** the main log stays non-tech-only. A strong, well-evidenced
finding whose subject is out of scope gets `"scope": "appendix"` — rendered
separately, never counted in the totals. This keeps the S3 picture from being
artificially empty and keeps the incumbent-vs-entrant split visible, which is
itself one of the more interesting things this log can measure.

**The appendix accepts any shape — S3, S3-CANDIDATE, S2 or S1.** It was
originally S3-only, which threw away real signal: on 2026-07-28 an AI-native
insurance MGA disclosed a quantified S1 on a Tier A earnings call and there was
nowhere to put it, so it was discarded. That is the wrong failure. An entrant's
S1 or S2 is a legitimate comparator for the incumbent disclosures in the main
log — often the sharpest one available, because entrants quantify what
incumbents will not. Route it to the appendix rather than dropping it.

The appendix bar is the same inclusion bar as the main log. Out-of-scope is not
a lower standard, only a separate ledger. Say in `shape_justification` why the
subject is out of scope, in the subject's own words where possible.

## Inclusion bar

An entry must clear all of:

1. Named company — not "a large European retailer".
2. A specific claim with a number, **or** an explicit on-the-record executive
   statement of material revenue impact.
3. A citable primary or near-primary source with a date.

Reject: pilots or announcements with no result; "AI-influenced" or "AI-touched"
pipeline metrics; Tier D vendor case studies not independently confirmed by the
deploying company; consultant surveys reporting sentiment rather than results;
anything purely cost-side.

## Source tiers

| Tier | What it is | Why it matters |
|---|---|---|
| **A** | Earnings transcript, 10-K/20-F, annual report, investor day, formal guidance | Management is legally and reputationally exposed |
| **B** | Press release, corporate blog, exec interview, keynote | Company-issued, unaudited |
| **C** | Trade press, journalism, sell-side note | Third-party, variable rigor |
| **D** | Vendor case study, consultant survey | **Lowest.** Systematically inflated, selection-biased, often written by the party paid for the deployment. Never the sole basis for an entry |

## Status labels

- **DISCLOSED** — realized and reported.
- **ESTIMATED** — the company's own internal attribution.
- **PROJECTED** — a forward target. Still worth logging (it creates a falsifiable
  checkpoint) but never presented as realized ROI.

## Standing skepticism rules

- **Attribution laundering.** Revenue growth that would have happened anyway,
  relabeled AI-driven. Ask what the counterfactual is and whether the company
  offered one.
- **Denominator games.** "AI-influenced revenue" and "AI-touched pipeline" are
  marketing constructs, not incremental revenue.
- **Pilot-to-production gap.** A successful pilot is not ROI.
- Prefer figures a company would be embarrassed to walk back.
- **Never invent, round, or reconstruct a number from memory.** Every figure must
  trace to a source retrieved during that run. If it cannot be verified, omit it
  and say so.

## Counter-evidence

Companies walking back AI revenue claims, disappointing results, null studies —
these count as findings and are often more informative than another success
story. Set `"counter_evidence": true` and tag to the shape they contradict.

## Follow-up discipline

Claims decay. When a company already in the log reports again, check whether the
earlier claim held, was quietly dropped, or was restated. **A previously logged
claim that disappears from later disclosure is itself a finding.** Falsification
is as valuable as confirmation and much rarer in this literature — which is why
every entry carries a `falsifier` field written at the time of logging.

## Writing the day assessment

The assessment is the most-read text on the site. Write it as structured
markup, never as one paragraph: a one-line verdict callout, a bulleted pass
over the sources actually read, the pattern if one is visible across runs, the
near-misses and which specific test each failed, and the next dated catalysts.
The supported markup subset and the expected shape are documented in
[README.md](README.md#assessment-formatting). A wall of text buries the
reasoning that makes the log worth keeping.

## Daily balance between the two ledgers

The cost ledger exists to keep the log fed, not to become the log. Guidance,
not a hard cap: **the revenue hunt runs first and gets the majority of the
search effort**, S3 still weighted hardest. Cost entries are what a run
collects on the way past. A run that logs six cost entries and never searched
for S3 has inverted the point. Cost evidence also decays less — a study or a
filing from three weeks ago is still worth logging if unlogged — so there is no
reason to pad a thin cost day either.

## Empty days

If nothing clears the bar, log the day with no entries and record which search
angles were run. Do **not** pad with vendor case studies, consultant surveys,
recycled examples, or generic adoption commentary. An honest empty day is valid
output; a padded day corrupts the log. Earnings season clusters mid-Jan, mid-Apr,
mid-Jul and mid-Oct; off-weeks will be thin and that is expected.
