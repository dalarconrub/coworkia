# Iterative multi-agent review — portable playbook

**Date:** 2026-04-28
**Source:** distilled from the L1 RECONEX+ grant memory review cycle (executor: Claude; reviewer: Codex; director: human), 3 iterations over 48 h on a 25-page proposal with hard external deadline.
**Purpose:** transferable methodology for producing high-stakes deliverables under deadline using a director + executor + reviewer pattern with two AI agents.
**Applicability:** any deliverable that benefits from independent critical review before submission — research grants, manuscripts, business plans, RFPs, technical documentation, policy drafts, legal contracts, UX designs, strategic reports, master/PhD theses, product specs, public-policy memos, marketing campaigns, code modules under PR review.

---

## 0. Philosophy and core principles

1. **Two agents independent of each other beat one agent ever-iterating with itself.** A reviewer with no memory of the executor's reasoning catches structural blindspots that the executor cannot see. The cost of running a second agent is small compared to the value of independent critique.
2. **The human director never delegates judgment** on strategic decisions (scope, area, deadline, irreversible tradeoffs). The director delegates execution and review, not direction.
3. **Every review round must be self-contained.** A reviewer with no context about prior rounds must be able to do its job from a single prompt. This forces clarity and prevents context drift.
4. **Critique must be specific and quantified.** Generic feedback ("improve coherence") is rejected. Quantified critique ("criterion 2 sits at 16/30 against threshold 15; needs +4-7 points via X, Y") is accepted.
5. **Append-only history.** Each version of the deliverable is preserved. Each review is preserved. Each prompt to the reviewer is preserved. The trail is auditable end-to-end.
6. **Stop when the deliverable is presentable, not when it is perfect.** Iteration must converge. A clear definition of "presentable" set at the start prevents infinite loops.

---

## 1. When to apply this playbook

### 1.1 Appropriate triggers

- **High-stakes one-shot submissions** with no second chance (grant proposals, RFP responses, legal filings, regulatory submissions).
- **Documents evaluated by an independent third party** with their own scoring rubric (peer review, awards, certifications).
- **Internal documents requiring buy-in** from senior stakeholders before circulation (board memos, strategic plans, public policy drafts).
- **Code changes in critical paths** where an independent reviewer adds disproportionate value (security, financial, infrastructure code).
- **Long-form deliverables** (>10 pages or >500 LOC) where a single agent's coherence drift is real risk.
- **Hard external deadlines** that force convergence with limited time for free-form iteration.

### 1.2 Inappropriate triggers

- Throw-away artifacts (ad-hoc scripts, exploratory notes, draft brainstorms).
- Deliverables with very short latency (<2 h) — overhead of two agents exceeds the benefit.
- Single-author opinion pieces where critique would dilute voice.
- Agile sprints where iteration latency is intentional.

### 1.3 Ideal preconditions

- Deliverable definition is stable (the *what*) but content is open (the *how*).
- A clear external rubric or implicit acceptance criteria exists.
- The director has at least 30 minutes per round to validate decisions.
- Two AI agents available with persistent identity files (CLAUDE.md, AGENTS.md or equivalent), or at minimum two distinct sessions/tools with clear role separation.
- A version-controlled repo or equivalent storage for the deliverable.

---

## 2. Roles and division of labor

Three actors, never collapsed:

| Role | Identity | Function | Owns |
| --- | --- | --- | --- |
| **Director** | Human | Defines scope, deadlines, and acceptance criteria. Validates strategic decisions. Accepts or rejects reviewer recommendations. Triggers rounds. | The deliverable's *purpose* and the *go/no-go* decisions. |
| **Executor** | AI agent A (e.g. Claude) | Drafts and revises the deliverable. Applies director-approved recommendations. Handles operational logistics (file edits, version bumps, structural changes). | The deliverable's *content* (subject to director approval). |
| **Reviewer** | AI agent B (e.g. Codex) | Reads the deliverable cold (no memory of executor's reasoning). Audits against the rubric. Produces structured critique with quantified impact. | The *independent assessment*. |

### 2.1 Why the executor and reviewer must be different agents

- **Memory separation**: the reviewer should not remember the executor's compromises and rationalizations. Cold reading is the source of value.
- **Style separation**: a different prompt heritage, different conversation history, different identity file. Two distinct *minds* produce divergent failure modes that catch each other.
- **Accountability separation**: when one agent both writes and reviews, "I think this is fine" is not a review. It's a self-affirmation.

### 2.2 What the director never delegates

- The choice of *what* to deliver (scope).
- The choice of *who* sees it (audience).
- The hard tradeoffs the reviewer surfaces (resource allocation, accepting risk, pivoting strategy).
- The final *go/no-go* before submission.

The director can delegate to the executor or reviewer the *exposition* of options and the *quantification* of tradeoffs, but never the *decision*.

---

## 3. Architecture of files and version control

### 3.1 Standard naming pattern

```
<workspace>/
  <deliverable-namespace>/
    DELIVERABLE_v0.1.md         <-- Executor's first draft
    DELIVERABLE_v0.2.md         <-- Second iteration (post-review-1)
    DELIVERABLE_v0.3.md         <-- Third iteration (post-review-2)
    REVIEW_PROMPT_<reviewer>_DELIVERABLE_v0.1.md   <-- What the director sent the reviewer to evaluate v0.1
    REVIEW_<reviewer>_DELIVERABLE_v0.1.md          <-- The reviewer's output for v0.1
    REVIEW_PROMPT_<reviewer>_DELIVERABLE_v0.2.md
    REVIEW_<reviewer>_DELIVERABLE_v0.2.md
    REVIEW_PROMPT_<reviewer>_DELIVERABLE_v0.3.md
    REVIEW_<reviewer>_DELIVERABLE_v0.3.md
```

Each round produces **two** review artifacts: the *prompt* (what was asked) and the *output* (what was answered). Both are preserved.

### 3.2 The "operational annex" pattern inside the deliverable

When the deliverable has a fixed external format (e.g. a 25-page PDF), the iteration metadata cannot live in the deliverable's body. Solution: append an **operational annex** at the bottom of the working file, marked explicitly to exclude from the final export.

```markdown
<!-- ============================================================
  OPERATIONAL ANNEX — METADATA AND INTERNAL CHANGELOG
  DO NOT INCLUDE IN THE FINAL PRESENTATION
  This block is excluded from the page count and from the final exported document.
  Used only for traceability between working versions and review by agents/director.
============================================================ -->

# Operational Annex — change history

> This annex is NOT part of the document submitted to the audience. Strip it (or keep a separate `_workdoc.md`) before generating the final version.

**Closed decisions (date)**:
- D1 (date): ...
- D2 (date): ...

**v0.1 (date)**: initial draft.

**v0.2 (date)**: applied recommendations from REVIEW_v0.1:
- (a) ...
- (b) ...

**v0.3 (date)**: applied recommendations from REVIEW_v0.2:
- ...

**Residual pending items in v0.X (require director or third-party input)**:
- ...
```

This pattern keeps the executor honest (every change is logged, attributed to a specific recommendation) and gives the reviewer a clean diff to audit.

### 3.3 Append-only logs at the project level

Independent of the deliverable, the project keeps:

- **Daily chat log** (`chats/chat_YYYY-MM-DD.md`): conversation thread between director and agents. Append-only.
- **Devlog** (`devlog/DEVLOG.md` or equivalent): feature-level milestones, append-only.
- **Memory snapshot** (e.g. `memory/SNAPSHOT.md`): aggregated stable agreements, regenerated automatically.

These are project-level, not deliverable-level. They survive across deliverables.

---

## 4. The N-round review cycle

### 4.1 The canonical 3-round shape

| Round | Trigger | Executor produces | Reviewer produces | Director decides |
| --- | --- | --- | --- | --- |
| **0** | Director defines scope, audience, deadline, acceptance criteria | — | — | What is "done", what is "presentable", what is the rubric |
| **1** | Director triggers v0.1 draft | DELIVERABLE_v0.1 | — | Whether v0.1 is structurally sound enough to send to review (sanity check) |
| **2** | Director writes review prompt; sends to reviewer | — | REVIEW_v0.1 | Which CRITICAL/HIGH recommendations to apply (typically all CRITICAL, most HIGH); which to defer or reject (typically MEDIUM/LOW) |
| **3** | Director instructs executor to apply approved recommendations → DELIVERABLE_v0.2 | DELIVERABLE_v0.2 | — | Whether v0.2 needs another review round |
| **4** | Director writes second review prompt; sends to reviewer | — | REVIEW_v0.2 | Same triage |
| **5** | Executor produces v0.3 | DELIVERABLE_v0.3 | — | Whether to ship v0.3, do a third review, or pivot |
| **6** | Optional third review | — | REVIEW_v0.3 | Final pre-submission decision |
| **7** | Submission / publication | Final version | — | Sign-off |

Three review rounds is typical for high-stakes deliverables under tight deadline. One review round is often insufficient (catches CRITICALs but not new risks introduced by their fix); five+ rounds usually means the deliverable scope is unstable.

### 4.2 The cost-of-iteration heuristic

After each review:
- If the reviewer raises **new CRITICAL issues** that did not exist in the previous round → one more review needed.
- If the reviewer raises **only MEDIUM/LOW** new issues → the deliverable is converging; one more *quick* review may add value or may be skipped.
- If the reviewer raises **no new issues** (only confirms previous fixes) → ship.

### 4.3 The convergence indicator

Track a single quantitative metric across rounds (score, probability, defect count). The shape of its trajectory tells you when to stop:

- **Steeply rising** (e.g. v1 = 70 → v2 = 77 → v3 = 84): converging, one more round may push to peak.
- **Flat** (v1 = 80 → v2 = 82 → v3 = 82): converged. Ship.
- **Oscillating or declining**: iteration is hurting more than helping. Stop and ship the best previous version.

In our reference project: v0.1 = 69 → v0.2 = 77 → v0.3 = TBD. If v0.3 > 80, ship. If v0.3 = 78 with new risks, one final tightening pass.

---

## 5. The review prompt as a self-contained artifact

### 5.1 Why self-contained

The reviewer should be able to do its job by reading **only the review prompt + the deliverable + the linked source materials**. No prior chat memory, no context handoff, no "as we discussed".

This forces the director to articulate the rubric explicitly. It also makes the prompt reusable for the next round (just update the version number and the diff summary).

### 5.2 Standard structure of a review prompt

```markdown
# Review prompt — <DELIVERABLE> v0.X

> **Version under review**: path to DELIVERABLE_v0.X
>
> **Type of review**: Nth round — comparison against REVIEW_v0.(X-1) and validation of changes applied since.
>
> **Hard deadline**: <date>. **Internal deadline**: <date>.
>
> **Operational constraints**:
> - Append-only on logs.
> - DO NOT modify the deliverable or the previous reviews.
> - Deliver output at: <path/REVIEW_v0.X.md>
> - Cite literally when issuing a negative judgment, referencing the exact line.
> - Recommendations must be actionable (not generic).

## Context and changes since v0.(X-1)

[Diff summary: what changed structurally, what was added, what was removed, what is still pending. This is the only place where prior context is reintroduced — kept tight, factual, no rationalization.]

## Files to read in order

1. `<deliverable>_v0.X.md` — the document under review
2. `REVIEW_<reviewer>_<deliverable>_v0.(X-1).md` — previous review that originated current changes
3. `<deliverable>_v0.(X-1).md` — previous version (for diff)
4. ... (rubric documents, base regulations, source files, logs)

## Evaluation to produce

[A list of N "Dimensions" — each is a section the reviewer must produce in the output. Common dimensions:]

### Dimension 1 — Compliance with previous review
For each recommendation in the previous review, verdict: APPLIED FULLY / APPLIED PARTIALLY / NOT APPLIED — JUSTIFIED / NOT APPLIED — UNJUSTIFIED. Cite the line of the new version that confirms.

### Dimension 2 — Formal compliance with rubric
[E.g. page count, format, mandatory sections, hard validators...]

### Dimension 3 — Score recalculation per criterion
| Criterion | v0.(X-1) | v0.X | Δ | Justification |

### Dimension 4 — Probability of success / acceptance
[Quantitative range with cumulative and cualitative justification.]

### Dimension 5 — New risks introduced by v0.X
[Regressions, side-effects, contradictions, things the fix broke.]

### Dimension 6 — Internal coherence
[Cross-references, mappings, dependencies between sections.]

### Dimension 7 — Prioritized list of changes for v0.(X+1)
| Priority | Type | Section | Change required | Effort | Expected impact |

### Dimension 8 — Open administrative or operational risks
[Things outside the executor's control: third-party approvals, missing data, etc.]

### Dimension 9 — Conclusion and recommended next step
[Is the deliverable ready to ship if pending items are resolved? What minimal changes are still needed? Time estimate.]

## Output format
Single markdown file at <path/REVIEW_v0.X.md>.

## Closing operations for the reviewer
1. Append summary entry to daily chat log.
2. Add devlog entry tagged DOCS / REVIEW.
3. Run project close routines.
4. Commit and push.
```

### 5.3 What makes a review prompt good vs bad

| Good review prompt | Bad review prompt |
| --- | --- |
| Lists every file to read, in order. | "Look at the relevant files." |
| Specifies output path explicitly. | "Send me your thoughts." |
| Defines exactly the dimensions to cover. | "Critique it freely." |
| Asks for quantitative impact per recommendation. | "Tell me what's wrong." |
| Asks for literal citations on negative judgments. | "Be specific." |
| States hard deadlines and constraints. | Implicit constraints. |
| Mentions previous-round diff explicitly. | Pretends prior rounds didn't exist. |
| Requests recommendations sorted by priority. | Unranked list. |

---

## 6. The review output as a structured artifact

### 6.1 Required sections in the reviewer's output

Mirroring the prompt's dimensions exactly. No additions, no omissions. The reviewer's output is auditable: each section maps to a section asked for. This rigid mirroring is the source of cross-round comparability.

### 6.2 Required form of every recommendation

Each recommendation must include:

- **Priority**: CRITICAL / HIGH / MEDIUM / LOW.
- **Section** of the deliverable affected.
- **What's wrong**: the specific defect, with literal citation if the judgment is negative.
- **What to do**: the actionable fix.
- **Effort estimate**: hours-person.
- **Impact estimate**: points on the rubric, probability delta, defect class avoided.

Recommendations that lack any of these fields are reflexes, not recommendations.

### 6.3 Mandatory categorization of unmet recommendations

When a recommendation from the previous round was not applied:

- **JUSTIFIED**: depends on third-party input (data, signature, approval, oracle decision). Effort to apply is locked. Expected when ready.
- **UNJUSTIFIED**: should have been applied. Flagged as risk.

The director uses this distinction to decide where to push and where to wait.

---

## 7. Director-level decisions: when to intervene

The director makes decisions at exactly four moments per round:

### 7.1 Before round 1 — Acceptance criteria and rubric

The director writes down (or imports) the rubric, the audience, the hard deadline, and the definition of "presentable". This is the **fixed point** the reviewer will measure against. If this drifts, all reviews lose meaning.

### 7.2 After each review — Triage

Standard triage policy:

- **CRITICAL**: apply unless physically impossible. Document why if not applied.
- **HIGH**: apply unless trades off against another HIGH or CRITICAL. Justify trade-offs explicitly.
- **MEDIUM**: apply if cheap; defer with note if costly.
- **LOW**: usually defer.

The director writes a one-line triage decision per recommendation. The executor applies. Both records are preserved.

### 7.3 At any point — Strategic pivot

If the reviewer surfaces a recommendation that is structurally larger than a routine fix (e.g. "change target audience", "switch evaluation track", "rescope deliverable"), the director must engage personally. Examples from our reference project:

- Switching evaluation area (SEJ → HUM) because of administrative coherence with the executor's affiliation: director-level decision; took 30 minutes of dialogue and one explicit confirmation.
- Extending duration (30 → 36 months) because it allowed all 5 outputs to be sent within the project: director-level decision; took 15 minutes.

These decisions should never be made by the executor alone, even if the reviewer recommends them.

### 7.4 Before submission — Final go/no-go

The director reads the final version cold (or has a third reviewer do it) and signs off. This is the only decision that has no review.

---

## 8. Quantitative tracking across rounds

A single, well-chosen metric tracked across rounds is worth more than a thousand qualitative remarks. Choose one (or two) that the rubric provides naturally:

| Project type | Tracked metric |
| --- | --- |
| Grant proposal | Estimated total score / 100 against rubric; estimated probability of success in range |
| Manuscript | Number of major comments expected from peer review; reviewer quality score |
| Code module | Defect density; test coverage; cyclomatic complexity |
| Business plan | Probability of investment / round close |
| RFP response | Estimated win probability vs known competitors |
| Policy document | Stakeholder approval probability; clarity score |

Plot the metric across rounds. The trajectory tells you whether iteration is converging.

In our reference project: criterion scores (1.1 / 1.2 / 2 / 3 / 4) tracked separately, total tracked separately, probability of grant award tracked as a range. Each round, the reviewer recalculated all six metrics with delta vs previous round. The trajectory was monotonically rising, signaling convergence.

---

## 9. When to stop iterating (definition of "presentable")

Stop conditions, any of which is sufficient:

1. **Quantitative threshold reached**: the tracked metric crosses the predefined "presentable" floor.
2. **No new CRITICAL issues** in the latest review.
3. **All CRITICAL/HIGH recommendations applied or justified**, only MEDIUM/LOW remain.
4. **Hard deadline within 24 hours**: stop and ship the best version on hand.
5. **Marginal cost > marginal value**: the next round's expected improvement is smaller than the cost of running it (rare but real for very mature deliverables).

In all cases, document the stop reason. The next project's playbook draws from these.

---

## 10. Common anti-patterns

### 10.1 Single-agent review

**Symptom**: the same agent that wrote the deliverable also "reviews" it. Self-affirmation cosplaying as critique.

**Fix**: enforce hard role separation. Different identity files. Different sessions. Different prompt heritage.

### 10.2 Reviewer with full chat history

**Symptom**: the reviewer is invoked in the same conversation as the executor and reads the executor's reasoning before reviewing. The reviewer is contaminated.

**Fix**: a fresh session for the reviewer. The review prompt is the only context.

### 10.3 Fuzzy critique

**Symptom**: review output reads like "improve clarity", "consider strengthening section 3", "the introduction could be more compelling".

**Fix**: prompt the reviewer for literal citations on every negative judgment, quantified impact, and actionable rewrites. Reject reviews that don't meet this bar.

### 10.4 Triage drift

**Symptom**: the director marks everything CRITICAL or everything LOW. Triage adds no information.

**Fix**: enforce the priority distribution. In any given review, expect ~20-30% CRITICAL/HIGH and ~70-80% MEDIUM/LOW. If the distribution is skewed, the rubric is misspecified.

### 10.5 Executor over-applies

**Symptom**: the executor applies all recommendations including LOW ones, sometimes inventing scope. The deliverable bloats.

**Fix**: the director's triage line is the only mandate. The executor cannot apply un-triaged recommendations.

### 10.6 Reviewer flatters

**Symptom**: the second review says "v0.2 is much improved, score 92" without identifying remaining issues.

**Fix**: the prompt must require Dimension 5 (new risks) and Dimension 7 (prioritized list for v0.X+1). If both come back empty, one of two things is true: the deliverable is genuinely done (then stop), or the reviewer is flattering (re-run with a stricter prompt).

### 10.7 Endless iteration

**Symptom**: rounds 4, 5, 6 happen because each review surfaces new things. The deliverable never ships.

**Fix**: hard stop conditions in §9. After round 3, the director must justify any further round in writing.

### 10.8 Lossy version control

**Symptom**: v0.2 overwrites v0.1; the diff is lost. Reviewer cannot audit changes; trail is broken.

**Fix**: never overwrite. Each version is a new file or a clearly tagged commit. The operational annex (§3.2) preserves the changelog.

### 10.9 Reviewer not given the rubric

**Symptom**: the reviewer scores the deliverable against an internal aesthetic rather than against the actual evaluation criteria the audience will use.

**Fix**: the review prompt explicitly references the rubric document(s) and instructs the reviewer to score by criterion.

### 10.10 Deliverable diverges from external constraint

**Symptom**: through iteration, the deliverable becomes longer than allowed, more expensive than allowed, late by deadline.

**Fix**: the rubric in §7.1 must list every hard constraint (page count, budget cap, deadline, format). The reviewer audits against these in every round (Dimension 2).

---

## 11. Templates (copy-paste ready)

### 11.1 Director's intake template (round 0)

```markdown
# Deliverable intake — <NAME>

**Audience:** [who reads it; who decides on it]
**Hard deadline:** [date and time]
**Internal deadline:** [date and time]
**Format constraints:** [page count, file type, format, sections required]
**Rubric:** [link / paste of evaluation criteria with weights]
**Definition of "presentable":** [quantitative or qualitative threshold]
**Out of scope:** [explicit exclusions to prevent scope creep]
**Stakeholders requiring sign-off:** [list]
**Closed decisions before drafting:** [D1, D2, D3...]
**Open decisions to be resolved during drafting:** [D4, D5...]
**Executor agent:** [identity]
**Reviewer agent:** [identity, must be different]
**Number of review rounds expected:** [typically 2-3]
```

### 11.2 Round invocation template (rounds 2, 4, 6...)

```markdown
# Review round <N> — <DELIVERABLE>

The executor has produced <DELIVERABLE>_v0.X based on the previous review's recommendations.

Reviewer: please execute the prompt at <path/REVIEW_PROMPT_v0.X.md>.

Constraints:
- Self-contained: read only the linked files.
- Deliver at <path/REVIEW_v0.X.md>.
- Do not modify the deliverable or any prior file.
- Cite literally for negative judgments.
- Quantify impact per recommendation.

When done:
1. Summary entry in chat log.
2. Devlog entry.
3. Project close routines.
4. Commit + push.
```

### 11.3 Triage decision log template

```markdown
# Triage of REVIEW_v0.X — <DELIVERABLE>
Director: [name]
Date: [date]

| Recommendation | Priority | Decision | Rationale |
| --- | --- | --- | --- |
| (a) ... | CRITICAL | APPLY | — |
| (b) ... | HIGH | APPLY | — |
| (c) ... | HIGH | DEFER (depends on third-party data) | wait until <date> |
| (d) ... | MEDIUM | APPLY | cheap |
| (e) ... | MEDIUM | REJECT | trades off against (a) |
| (f) ... | LOW | DEFER | post-submission |
```

### 11.4 Stop-condition checklist

```markdown
# Stop-condition check — <DELIVERABLE> after round <N>

[ ] Quantitative metric at or above "presentable" floor
[ ] No new CRITICAL issues in latest review
[ ] All CRITICAL/HIGH recommendations applied or justified
[ ] All format constraints validated (page count, file type, etc.)
[ ] All third-party dependencies resolved or have a fallback path
[ ] Director has read the final version cold
[ ] Hard deadline > 12 hours away (if not, stop regardless)

If all checked: SHIP.
If 1-2 unchecked: one more focused round.
If >2 unchecked: pause; reassess scope.
```

---

## 12. Adaptation across project types

### 12.1 Vocabulary translation table

| Concept | Grant proposal | Manuscript | Business plan | RFP response | Policy doc | Code PR |
| --- | --- | --- | --- | --- | --- | --- |
| **Deliverable** | Memory + Annex I | Manuscript | Pitch deck + business plan | Proposal document | Policy memo | Pull request |
| **Audience** | Funding agency reviewers | Journal peer reviewers | Investors / VCs | Procurement committee | Policymakers / committee | Tech lead + maintainers |
| **Rubric** | Funding rubric (criteria + weights) | Journal scope + reviewer guidelines | Investor's IC criteria | RFP evaluation matrix | Policy white-paper standards | Style guide + CI checks |
| **Hard deadline** | Submission window close | Editor's response deadline | Pitch date | RFP submission deadline | Committee meeting date | Sprint end / release cut |
| **Format constraints** | Page count, font, margins | Word count, figures cap, format | Slide count, format | Page count, mandatory sections | Length, structure | LOC, test coverage, lint |
| **Tracked metric** | Score / probability of award | Reviewer rating prediction | Probability of investment | Win probability | Adoption probability | Defect density / pass rate |
| **CRITICAL recommendation** | Causes exclusion | Causes desk rejection | Causes investor pass | Causes proposal disqualification | Causes legal challenge | Breaks build / security |
| **Reviewer agent suitable** | Codex (analytical) | Codex (analytical) | Claude (narrative) | Codex (compliance) | Claude (clarity) | Codex (code review) |

### 12.2 Field-specific adaptations

#### Research grant (the reference project for this playbook)
- Rubric is published with the call. Map every criterion to a section of the deliverable.
- Hard format constraints (page count, font, margin, language) are not subsanable. Reviewer must validate format every round.
- Reviewer scores criterion-by-criterion with quantified impact per change.
- Stop condition: total score above the historical award cutoff with margin for evaluator subjectivity (typically 5-10 points above floor).

#### Scientific manuscript
- Rubric is the journal's scope + the typical structure peer reviewers use.
- Reviewer roleplays as a hostile referee. Prompts emphasize "what would cause a desk rejection" and "what would trigger a major revision".
- Tracked metric: a per-section score plus a binary "ready for submission" verdict.
- Stop condition: no major revision triggers, all minor concerns addressed or noted as limitations.

#### Business plan / pitch
- Rubric is the investor's IC framework (market, team, traction, model, risk).
- Reviewer roleplays as a skeptical IC member. Asks "what would I challenge in 5 minutes of Q&A".
- Tracked metric: probability of investment, broken down by IC question.
- Stop condition: every IC concern has a defensible answer in the deck.

#### RFP response
- Rubric is the RFP's evaluation matrix (technical, commercial, references, methodology, etc.).
- Reviewer scores against each matrix item and flags missed mandatory sections.
- Tracked metric: score per matrix line + win probability vs known competitors.
- Stop condition: no missed mandatory sections, score above competitor mean by margin.

#### Public policy memo
- Rubric is the audience's policy framework (stakeholder impact, legal feasibility, fiscal impact, political viability).
- Reviewer challenges from each stakeholder's perspective in turn.
- Tracked metric: stakeholder support probability per group.
- Stop condition: at least one stakeholder group is convinced; no group is mortally opposed.

#### Code PR
- Rubric is the project's style guide + CI checks + maintainer expectations.
- Reviewer agent runs through static analysis, security scan, test coverage, semantics.
- Tracked metric: defect density, test pass rate, code review feedback per LOC.
- Stop condition: CI green, no maintainer-blocking comments, test coverage above project floor.

### 12.3 Hard constraints that need adaptation

- **Confidentiality / IP**: if the deliverable cannot be shared with cloud agents, both executor and reviewer must run locally. The methodology is the same; the agents change.
- **Real-time deadlines (<2 h)**: the 3-round structure is too expensive. Compress to 1 round with a tight prompt; accept higher residual risk.
- **Multilingual deliverables**: agents may have asymmetric language quality. The reviewer should be tested in the target language before relying on its critique.
- **Highly tacit domains** (e.g. legal contracts in unusual jurisdictions): a third human reviewer may be required after round 3. The agents handle 80%; the human handles the last 20%.

---

## 13. Meta-lessons (the 10 highest-level principles)

1. **Independence is the source of value.** Two cooperating agents that never argue produce only consensus drift. Two independent agents with different identities catch what neither alone can see.
2. **The rubric is non-negotiable.** Every iteration measures against the same fixed rubric. If the rubric changes, every prior round becomes unreliable.
3. **Citation is the currency of critique.** "This is wrong" without a line citation is wind. "Line 273 says X, but the rubric requires Y" is steel.
4. **Quantification is the currency of impact.** "This will help" is nothing. "+2 points in criterion 4, lifting the total from 77 to 79" is something. "Effort 0.5 h, impact +5%" is everything.
5. **Append-only is the only way to audit.** When you overwrite, you destroy the trail. The trail is what makes the methodology defensible.
6. **The director never delegates strategy.** Tactics: yes. Wording: yes. Reorganization: yes. Scope, audience, deadline, irreversible tradeoffs: never.
7. **Stop conditions must be defined before round 1.** Otherwise iteration becomes its own goal and the deadline arrives unmet.
8. **Self-containment of the review prompt is the proof of methodology integrity.** If you cannot explain what to evaluate without prior chat memory, the methodology is leaking.
9. **Convergence is observable.** Plot the tracked metric across rounds. If it rises and flattens, ship. If it oscillates, your rubric is wrong. If it falls, you are over-iterating.
10. **The methodology survives self-application.** The first time you use this playbook, you will discover gaps. Apply the meta-methodology (extract-playbooks-from-projects) to itself: produce v0.2 of this playbook from your first use.

---

## 14. Minimum viable workflow (if you remember nothing else)

You have 24 hours, one deliverable, two AI agents and one decision-maker. Run this:

1. Write down the rubric and the hard deadline. (15 min, director)
2. Executor produces v0.1. (3-6 h)
3. Director writes a self-contained review prompt referencing the rubric. (30 min)
4. Reviewer produces REVIEW_v0.1. (1-2 h)
5. Director triages: which CRITICAL/HIGH to apply. (15 min)
6. Executor produces v0.2. (1-3 h)
7. Director reads v0.2 cold. If it crosses the "presentable" floor, ship. If not, one more round (steps 3-6 again, faster).
8. Director signs off. Submit.

Total: 8-15 h of human + agent work. Two review rounds. One deliverable shipped.

---

## 15. What this playbook does NOT do

- Does not replace domain expertise. The agents and director must understand the subject. The methodology multiplies expertise; it does not create it.
- Does not work for adversarial deliverables (e.g. sales copy where the audience is hostile and rubric is implicit). For those, the reviewer needs different prompts (red-team mode).
- Does not handle agile cadence. This is for one-shot deliverables. For continuous work, embed the pattern inside sprints, not over them.
- Does not replace human review for legally-binding artifacts. The agents flag and structure; a human signs.

---

## 16. Closing note

The pattern documented here is not new. Peer review, code review, editorial cycles all use a director + executor + reviewer separation. What is new is the operational discipline of running it with two AI agents under deadline, with full append-only traceability, and with rigid self-containment of every artifact.

Once you run it once, the second time is cheap. The third time, the templates are reusable verbatim. By the fifth deliverable, the cost is dominated by domain reasoning, not by methodology overhead.

That is the test of any methodology: it should disappear into the work.

---

## Provenance

- **Source**: the L1 RECONEX+ grant memory review cycle (Junta de Andalucía 2026 call), 2026-04-27 to 2026-04-28. Three rounds: v0.1 → REVIEW_v0.1 → v0.2 → REVIEW_v0.2 → v0.3 → REVIEW_v0.3 (in progress at time of extraction).
- **Executor agent**: Claude (Anthropic, identity in `CLAUDE.md`).
- **Reviewer agent**: Codex (OpenAI, identity in `AGENTS.md`).
- **Director**: human (D. Alarcón, repository owner).
- **Tracked metrics**: criterion scores per Apéndice II (Andalusian L1 grant rubric); estimated total / 100; estimated probability of award in range.
- **Trajectory observed**: v0.1 = 69/100 with P(award) 25-40% → v0.2 = 77/100 with P(award) 35-50% → v0.3 = pending.
- **Time budget**: ~36 hours of director-time + ~20 hours of executor-time + ~6 hours of reviewer-time over 48 hours of wall-clock.
- **Underlying meta-methodology**: `playbooks/meta-methodology-extracting-playbooks-from-projects.md` (self-applied to extract this playbook).
- **Extraction date**: 2026-04-28.
- **Extraction method**: applied the 7-step pipeline (inventory, surface survey, deep mining, first synthesis, universalization audit, integration, universalization pass) to the conversation thread and the artifacts of the source project.
