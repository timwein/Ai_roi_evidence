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

**Pure cost-savings stories are out of scope.** Do not log them. The only
exception: a cost collapse large enough to make a previously uneconomic segment
newly serveable — that is Shape 3, not a cost story.

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

## Scope

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

**Resolution:** the main log stays non-tech-only. A strong, well-evidenced S3
whose subject is out of scope gets `"scope": "appendix"` — rendered separately,
never counted in the totals. This keeps the S3 picture from being artificially
empty and keeps the incumbent-vs-entrant split visible, which is itself one of
the more interesting things this log can measure.

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

## Empty days

If nothing clears the bar, log the day with no entries and record which search
angles were run. Do **not** pad with vendor case studies, consultant surveys,
recycled examples, or generic adoption commentary. An honest empty day is valid
output; a padded day corrupts the log. Earnings season clusters mid-Jan, mid-Apr,
mid-Jul and mid-Oct; off-weeks will be thin and that is expected.
