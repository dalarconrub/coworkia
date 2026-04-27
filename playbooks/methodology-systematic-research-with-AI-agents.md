# Methodology — Systematic scientific research with AI agents (unified)

**Date:** 2026-04-17 (unified version integrating Claude's methodology note + Codex's AI-systematic-research playbook)
**Source:** distilled from the Berry-Keating / Riemann Hypothesis project (2026-03 to 2026-04)
**Purpose:** provide a transferable methodology for using AI agents (Claude + Codex + human)
to systematically investigate open problems in any scientific field.

**Applicability:** physics, mathematics, biology, computer science, engineering, social
sciences, humanities — any field where evidence accumulates, theories compete, and
conclusions must be defensible.

---

## 0. Core principle and philosophy

### 0.1 The single most important framing

The main lesson, stated in one sentence:

> **Do not use AI as a source of answers. Use AI as a structured research workforce inside a controlled epistemic process.**

This distinction changes everything.

**If AI is treated as an oracle:**
- shallow pattern matching
- overclaiming
- unstable conjectures
- untracked assumptions
- low-grade hallucinated coherence

**If AI is treated as a workforce inside a disciplined process:**
- rapid literature triage
- technical extraction from papers
- formalization proposals
- test generation
- consistency checking
- paper writing and revision
- project continuity across iterations

The system only works if the human keeps control of:
- problem framing
- epistemic status
- final claims
- stopping rules
- publication standards

### 0.2 Four principles that govern everything

1. **Honesty over optimism.** Every claim tagged: proved / empirical / heuristic / pipeline-dependent / speculation / invalidated. Probabilities explicit, never summed. Inflated confidence corrupts later decisions.

2. **Falsification before investment.** Before committing weeks to a route, run the cheapest serious test that could REFUTE it. One day of negative clarity is often worth more than a month of vague forward motion.

3. **Work by artifacts, not chats.** Every meaningful step leaves one durable artifact (memo, note, script, JSON, paper, review). Research-by-chat is the dominant failure mode; it produces interesting ideas without continuity.

4. **Multi-agent role separation.** One agent executes, another reviews independently, a human decides. No single agent both produces and validates its own work.

### 0.3 Three category separation (critical)

Routes must be classified and NEVER conflated:

- **A — Direct-attack routes:** if they work, they solve the main problem or an equivalent criterion
- **B — Partial-result routes:** publishable progress that does not itself solve the main problem
- **C — Long-term programs:** fertile research directions not on the critical path

Many strategic errors come from presenting a B-route as if it were an A-route. Always tag.

### 0.4 The research-by-chat antipattern

**Bad flow (what happens without discipline):**
```
interesting idea -> local excitement -> no artifact -> loss of continuity
```

**Good flow (what discipline produces):**
```
idea -> note -> test -> verdict -> paper or archive -> next branch
```

Every step produces a durable, timestamped artifact.

---

## 1. Project architecture

A large AI-assisted scientific project needs explicit architecture:

1. **Shared repository** with persistent notes, scripts, outputs, papers.
2. **Strict separation** between:
   - raw exploration
   - intermediate synthesis
   - submit-ready writing
3. **Named routes / branches** of inquiry.
4. **Persistent note system** recording:
   - what was tried
   - why it failed
   - what remains open
   - what the next decision gate is
5. **Companion papers** that isolate distinct claims (never one giant unsubmittable document).
6. **Role-separated agents** (§2).

Without this architecture, research becomes a memory game and continuity breaks.

---

## 2. Roles and division of labor

### 2.1 Three-agent structure

| Role | Who | Responsibilities |
|---|---|---|
| **Coordinator / Executor** | Claude (or equivalent) | Read PDFs, produce memos, run computations, draft papers, manage repos, first-pass deliverables |
| **Critical Reviewer** | Codex (or equivalent) | Audit deliverables, calibrate probabilities, identify overclaims, emit verdicts at decision gates, may provide targeted rewrite specs |
| **Principal Investigator** | Human | Strategic decisions, authorize actions, resolve agent disagreements, own the project |

The same agent should NOT be the only producer and validator of a major claim.

### 2.2 AI role types (more granular)

Within the Coordinator/Reviewer split, four functional roles emerge:

- **Explorer:** scan notes, find files, extract formulas, identify missing references, answer bounded codebase questions.
- **Worker:** implement scripts, run extensions, update notes, prepare tables, tighten drafts.
- **Referee:** identify overclaims, surface venue mismatch, check proof-vs-observation framing, force explicit fixes.
- **Synthesizer:** produce route maps, continuity plans, memos, cross-document integration.

The human decides which role is needed. Asking one agent to do all four at once usually degrades quality.

### 2.3 Workflow per deliverable

```
1. Coordinator produces first-pass (memo, paper edit, analysis)
2. Coordinator commits to repo with descriptive message
3. Coordinator notifies PI
4. PI passes to Reviewer
5. Reviewer emits verdict (approve / revise / reject)
6. If revise: Coordinator iterates with feedback
7. If reject: Coordinator produces alternative or documents obstruction
8. PI has final say
```

### 2.4 Decision gates

At specific phase boundaries, both agents produce verdicts independently:
- If verdicts coincide: PI confirms, proceed
- If verdicts differ: explicit discussion, PI decides

This prevents single-agent drift.

### 2.5 Why this structure is necessary

A single AI agent producing and validating its own work falls into predictable failure modes:
- Probability inflation (own work looks better than it is)
- Confirmation bias (missing flaws in own reasoning)
- Narrative lock-in (committing to a framing early)

Two independent AI agents + human decision-maker break these modes. In our project, Codex's "is this overclaimed?" question caught errors Claude couldn't see, and vice versa.

---

## 3. The right unit of work

The correct unit of research work is **not** "a chat." It is one of these:

- a note with a concrete claim
- a script with a clearly defined computation
- a verdict memo
- a review prompt
- a paper draft
- a referee response
- a roadmap update

Every meaningful step leaves one durable artifact. Good artifact types:

| Type | Purpose | Example |
|---|---|---|
| `plan-*.md` | Route or experiment plan | `plan-route-delta.md` |
| `results-*.md` | What was computed and what it means | `results-gram-matrix-N100.md` |
| `memo-*.md` | Synthesis for another agent or future self | `memo-paper-E-bridge.md` |
| `request-*.md` | Bounded task for another agent | `request-codex-review-IVnew.md` |
| `reply-*.md` | Response to another agent's request | `reply-codex-phase2.md` |
| `paper-*/main.tex` | Public-facing narrative | companion papers |
| `output/*.json` | Machine-readable results | reproducible outputs |
| `notebooks/run_*.py` | Reproducible computation | scripts |

This turns research into a traceable system rather than a memory game.

---

## 4. Problem formulation (the 5-question gate)

The first stage is not "solve X." It is:

> **define the object, the obstruction, the measurable quantity, and the failure mode.**

Before launching ANY major computation or writing effort, answer 5 explicit questions:

1. **What is the exact target statement?** (Theorem? Measurement? Bound?)
2. **What object would witness progress?** (How will we know it's right?)
3. **What is already known to obstruct the naive version?** (What's the most likely failure mode?)
4. **What is the cheapest serious falsification?** (30-minute to 1-day test that could refute)
5. **What is the stop criterion if the route stalls or becomes ambiguous?**

If you cannot answer all 5, **the route is not ready**. Define them first.

A good early test is not "can we prove it?" but:

> **is the target object analytically well-defined and operationally measurable?**

If not, freeze the route early. Many bad routes are not false — they are ill-posed.

---

## 5. Literature workflow (5 layers)

### 5.1 Identification (broad)

Start broad, but classify immediately:
- foundational papers
- technical bridge papers
- recent updates (2020-2026)
- computational papers
- speculative papers
- papers only useful for bibliography hygiene

**Not all papers deserve equal depth.** Identify 20-50 in initial sweep.

### 5.2 Triage (minutes per paper)

For each paper, answer:
- What does it actually prove?
- What are the main tools?
- Which hypotheses are used?
- What exact object overlaps with our project?
- Is it directly actionable, context only, or misleadingly adjacent?

**Most papers should stop here.** A 1-paragraph note and a classification tag are enough.

### 5.3 Deep read (only a few papers)

A paper is worth full reading when:
- it contains the exact criterion or operator we may use
- it defines the Gram matrix / kernel / transform we must compute
- it is the main cited source behind a route
- it is the standard paper a referee will expect us to know

### 5.4 Extraction (technical, not prose)

Do not "summarize the paper" in vague prose. Extract:
- theorems (exact statements)
- definitions
- formulas
- proof skeletons
- constants
- assumptions
- computational handles

Output should be closer to a technical memo than to a book review.

### 5.5 Bridge verdict (essential)

After reading, issue a verdict:
- `no bridge`
- `weak bridge`
- `partial technical bridge`
- `strong technical bridge`

**Without a verdict, literature reading becomes passive consumption.**

### 5.6 Always include classical reformulations

In hard problems, old equivalent criteria often matter more than new speculative breakthroughs. In our project, Nyman-Beurling (1950) / Báez-Duarte (2003) was more useful than any 2024-2026 breakthrough. Phase 1 literature search must include classical reformulations, not just recent results.

### 5.7 Tools

- **Consensus MCP** (if available; rate-limited, ~30 free searches/month)
- **WebSearch** (broad, unstructured)
- **Agent tool with general-purpose subagent** for parallel multi-paper surveys
- **Local PDF collection** (`references/` directory) + `INDEX.md`
- **Standardized `.bib` files** per paper with `author_year_shortkey` convention

---

## 6. Knowledge organization by epistemic status

Research with agents collapses unless information is organized by epistemic status.

### 6.1 The seven status labels

Every substantive claim should be tagged with one of:

- **proved** (rigorous theorem)
- **empirical but stable** (measurement consistent across tests)
- **heuristic** (plausible but not proved, not rigorously measured)
- **pipeline-dependent** (result depends on specific pipeline / numerical method)
- **frozen** (route deferred; triggers documented for reactivation)
- **open** (in active investigation)
- **invalidated** (error found; retracted with explanation)

### 6.2 Good status phrasing

- `route frozen`
- `target ambiguous`
- `empirical law on tested range only`
- `not a theorem`
- `proof sketch only`
- `submit-ready`
- `pipeline artifact`
- `finite-N diagnostic relation`

### 6.3 Why this matters

Prevents contamination between:
- what was measured
- what was inferred
- what was actually proved

Researchers (including AI agents) drift from "measurement" to "proof" silently. The status label prevents this.

---

## 7. Route-based research management

### 7.1 Named routes

A large project should be decomposed into named routes. Each route has:
- short name
- target
- stop condition
- success condition
- current status
- classification (A / B / C)

### 7.2 Route statuses

- `active` — current execution
- `exploratory` — preliminary reading and triage
- `monitor only` — literature watch, no execution
- `frozen` — stopped pending specific trigger
- `closed negative` — proven or strongly evidenced to not work
- `submit-ready` — output ready for peer review

### 7.3 The A/B/C tag (critical for communication)

Every route gets exactly one:
- **A:** direct leverage on the main problem (equivalent criterion or full solution)
- **B:** partial but publishable progress (bound, verification, negative result)
- **C:** long-horizon autonomous program (not on critical path)

This single label prevents enormous internal confusion.

### 7.4 Negative results are assets

> **Negative results are not noise; they are route-closure assets.**

In our project, papers like "structural blindness of spacing statistics" became the most impactful precisely because they cleanly closed an entire family of approaches. Closed routes properly documented prevent rediscovering dead ends.

### 7.5 Rational time allocation

With explicit statuses, time allocation becomes decidable:
- `active` routes get primary time
- `exploratory` gets scheduled reading
- `monitor only` gets quarterly 30-min reviews
- `frozen` gets zero time unless trigger fires
- `closed negative` goes to the archive

---

## 8. Decision gates and stop criteria

### 8.1 Why stop criteria matter

> **A research project without stop criteria becomes a sunk-cost engine.**

For each route, define ahead of time:
- what result would KILL it
- what result would WEAKEN it
- what result would UPGRADE it
- what would justify a PAPER
- what would justify a PAUSE

### 8.2 Example good stop criteria

- target object turns out pipeline-dependent
- asymptotic claim appears pre-asymptotic on tested range
- simplified analytic proxy does not match extracted quantity
- the observable is structurally blind (provable)
- numerical sensitivity is far below detectability threshold
- the route depends on a literature result already known to close it
- entry cost is incompatible with available bandwidth

This prevents "one more experiment" drift.

### 8.3 Decision gate template

```markdown
# Decision gate: [SPECIFIC QUESTION]

## Input artifacts
- [list]

## Binary output
- OPTION A: [criteria for choosing A]
- OPTION B: [criteria for choosing B]

## Coordinator verdict
- [A or B or needs more input]
- Justification: [1-3 paragraphs]

## Reviewer verdict
- [A or B or disagree]
- Justification: [1-3 paragraphs]

## Resolution
- PI decision: [A or B]
- Rationale: [why]
```

---

## 9. Experimental design with agents

### 9.1 The fundamental rule

> **Never run a computation without already knowing what verdicts the result could trigger.**

Each experiment answers a yes/no or scale/comparison question.

**Bad experiment:** large scan with no decision consequence.

**Good experiment:** "If quantity scales like 1/N^p, route stays alive; if O(1), freeze route."

### 9.2 The falsification sprint pattern

1. Pose one binary question.
2. Design the cheapest test that could kill the route.
3. Time-box aggressively (days, not weeks).
4. Issue a verdict immediately on completion.
5. Either escalate to deep work or freeze the route.

### 9.3 The standard experimental cycle

1. Define the mathematical object.
2. Derive the expected scaling or signature.
3. Implement a small reproducible script.
4. Save machine-readable outputs.
5. Write a results note immediately.
6. Update the route verdict.

### 9.4 Falsification-first = highest ROI pattern

In our project, the single highest-ROI pattern was running 1-day falsification sprints before committing to 4-week deep dives. Multiple times this saved weeks of misdirected work:

- Hybrid CUE_N hypothesis: refuted in 1 day vs 4-week sprint
- α=0.6 from halo derivative: refuted with Step 1 in days vs months
- Paper III-new target ambiguity: identified in 2-3 day audit

**The cheapest 1-day test is worth 10× the value of any "let's just start computing"** approach.

### 9.5 Infrastructure for long computations

- High-precision arithmetic (mpmath, Arb, mpfr)
- Reproducible scripts (explicit parameters, fixed seeds, output JSON)
- Cloud compute for long runs (Lightning Studio, Google Colab Pro, HPC)
- Local compute for iterative development
- `nohup` + log files for long-running jobs
- **Always use `flush=True`** on progress output (nohup buffers by default → appears frozen)
- **Always cap loops with explicit maxima** (infinite-loop bugs waste hours silently)
- **Always estimate runtime before launch** and include checkpointing

### 9.6 Obstruction layer enumeration (before pursuing many approaches)

**Pattern discovered from 29-route historical record:** before attempting 20+ approaches to a hard problem, identify the minimal set of structural obstructions. In our project, 29 failed approaches clustered into 4 obstruction layers:

1. **First-order vanishing** (sinc(1)=0 type): ~7 routes
2. **Wrong sign at higher order**: ~6 routes
3. **Required cancellation not achieved** (O(√T) type): ~8 routes
4. **Output type invalidity** (non-DPP, non-positive, etc.): ~8 routes

**Implication:** spend 1-2 days identifying obstruction layers BEFORE attempting routes. Enumerate what COULD block any approach in this family. Then approaches can be classified in advance ("this would fail in layer 2, same as route #6"). Reduces wasted effort from weeks to days.

**Template:** a single table
```
| Route # | Name | Expected obstruction layer | Observed result | Cost |
```
maintained across all attempts turns failures into a taxonomy, not a frustration.

### 9.7 Re-measurement protocols

Establish EXPLICIT thresholds for data quality escalation BEFORE collecting data:

- **Outlier beyond Bonferroni (p < 0.01/N):** auto-remeasure at highest resolution
- **Remeasure shifts > 1σ:** flag for scope review (original right? new right? bounds wrong?)
- **All remeasurements logged** in separate audit trail, not merged into main dataset

In our project: the single outlier re-measurement (logT=20.2003, 6.14M zeros, 8h compute + 2h analysis) saved 6 weeks of false confidence in a theoretical constant that turned out to be non-universal. Re-measurement cost: ~10h. Value: ~6 weeks. ROI: 30×.

---

## 10. The right use of numerical evidence

Numerics can do exactly four jobs:

1. **Falsify** a route (cheapest, highest-value use)
2. **Calibrate** a conjecture (which is the dominant reduced variable?)
3. **Reveal** the correct reduced variable or structure
4. **Support** a working empirical law on a tested range

Numerics must **NOT** be silently used as:
- proof substitute
- asymptotic guarantee
- hidden parameter tuning device

### 10.1 Always state which role

When writing, always declare which role the computation is serving. Good phrasing:

- "empirical on the tested range"
- "finite-N diagnostic relation"
- "working numerical observation"
- "not established asymptotically"
- "pipeline-specific effective law, not abstract asymptotic"

---

## 11. Deep reflection and conceptual synthesis

Computations alone do not advance a project. Periodic synthesis rounds must ask:

> **What have we actually learned about the structure of the problem?**

### 11.1 Synthesis round outputs

- route viability maps
- obstruction maps
- continuity plans
- cross-paper synthesis notes

### 11.2 When to synthesize

- After each phase completes
- After any binary decision gate
- When route-register gets >10 active routes
- Before publication
- On PI's explicit request

### 11.3 Who leads

**The human should lead most strongly** in synthesis rounds. Agents help by assembling facts, but the synthesis judgment must be deliberate.

---

## 12. Writing papers as modular outputs

### 12.1 Do not wait for the grand theorem

> **Do not wait for the grand theorem.**

Instead, write modular papers that isolate:
- a positive measurement
- a solver
- a structural theorem
- an obstruction map
- a rigorous kernel lemma
- a negative result that closes a route

### 12.2 Benefits of modular papers

- publishes real progress incrementally
- forces clearer scope per paper
- creates referee-grade artifacts along the way
- prevents one giant unsubmittable document
- compounds citations across the series

### 12.3 One dominant claim per paper

Each paper should have **one** dominant claim. If a draft has too many claims of different epistemic status, split it.

### 12.4 Paper types that emerged

Our project produced:
- **Empirical measurement paper** (Paper I-new: c = 1.245)
- **Computational tool paper** (Paper II-new: Tracy-Widom solver)
- **Phi-observable paper** (Paper III-new: 3 rigorous results + open gap)
- **Structural blindness theorem** (Paper IV-new: negative result)
- **Verification paper** (Paper VII: CCM numerical confirmation)

Each with one dominant claim, different venue-fits, different review trajectories.

### 12.5 Publication path independence

**Identify at project start: which papers are path-independent?**

Path-independent papers can be published REGARDLESS of whether the grand theorem is solved. They depend only on completed prior work (data collection, measurement, infrastructure).

Path-dependent papers require downstream unsolved pieces.

In our project:
- Papers I-II (empirical + mechanism): PATH-INDEPENDENT — publishable after data collection alone
- Paper IV (negative result / obstruction map): PATH-INDEPENDENT — always publishable
- Paper III (Φ-observable): PARTIALLY PATH-DEPENDENT — core result rigorous, full RH connection open
- Paper VII (CCM verification): PATH-INDEPENDENT — verification of another group's framework

**Why this matters:**

Without path-independence mapping, researchers fall into "we have results but they're incomplete, so we can't publish" — the grand-theorem trap. By explicitly tagging papers, some go to submit while others remain in development.

**Decomposition instead of solution:**

When the grand theorem is blocked, pivot to:

> "Decompose the grand theorem into {solvable components} + {non-solvable components}. Publish the solvable. Document the non-solvable."

In our project: c = 7% (PNT-analytic, proven) + 26% (Born bound, proven) + 67% (non-perturbative, open). This reframing made 33% of the grand result publishable immediately, instead of blocking on 100%.

---

## 13. Referee-mode review as part of the process

### 13.1 Every serious draft gets internal review

A good internal referee prompt asks:
- Is the theorem actually proved?
- Is the empirical claim overstated?
- Are the constants justified?
- Is the benchmark sufficient?
- Are there missing references?
- Is the venue right?
- What would block acceptance?

### 13.2 The three-round review pattern

For papers and major documents:

- **Round 1:** expect "major revision." Receive numbered actionable items.
- **Round 2:** apply targeted fixes, expect "minor revision." Some items still open.
- **Round 3:** final framing and submission gate. Expect "accept" or minor wording.

Allocate 1-2 weeks per round. **Submitting after round 1 is usually premature.**

### 13.3 Pattern worked repeatedly

```
draft -> referee review -> targeted edits -> second-round review -> submit gate
```

This was the single most reliable path to strong papers in our project.

---

## 14. Venue discipline

Choose the venue based on the paper's **actual dominant content**, not the project's ambition.

### 14.1 Rough heuristic

| Content type | Suitable venue tier |
|---|---|
| Rigorous theorem + strong proof | Annals / Duke / Inventiones |
| Rigorous theorem + synthesis | IMRN / Journal of Number Theory |
| Numerical verification + empirical law | Experimental Mathematics / Math Comp |
| Synthesis + theorem + conceptual map | IMRN / mid-tier theory journal |
| Tool paper | Math Comp / specialized tool journals |

### 14.2 Realistic fallback tiers

Always define:
- **First choice** (aspirational but plausible)
- **Fallback 1** (realistic, expected success probability > 50%)
- **Fallback 2** (safe baseline)

Never make strategy suppose the first-choice venue.

### 14.3 Common mis-aim

- A paper that is 70% numerical should not be written as if it belongs in a pure theorem journal
- Conversely, if a paper is theorem-led, empirical observations must be clearly subordinate

Mis-aimed venues force wrong rhetoric and waste review cycles.

---

## 15. AI role choice (Explorer / Worker / Referee / Synthesizer)

### 15.1 Choose the role deliberately

See §2.2. When delegating to an agent, name the role:

- **Explorer role** for: searching notes, finding files, extracting formulas
- **Worker role** for: implementing scripts, running computations, drafting tables
- **Referee role** for: identifying overclaims, checking framing, venue fit
- **Synthesizer role** for: route maps, memos, cross-document integration

### 15.2 Avoid role conflation

Asking one agent to do all four in one session degrades quality. Better: separate sessions, explicit role labels in prompts.

### 15.3 When to switch

Switch from Worker to Referee when:
- First draft is complete
- A major decision is imminent
- The PI suspects the result is too optimistic

Switch from Explorer to Synthesizer when:
- Enough facts are gathered
- A map is needed for decision-making

---

## 16. Communication between agents

### 16.1 Bad pattern
```
"continue from before"
```

### 16.2 Good pattern

Stable artifact-mediated handoffs:
- `request-*.md`
- `reply-*.md`
- `memo-for-*.md`
- precise question list
- explicit attachments

### 16.3 Each handoff specifies

- exact task
- exact files
- exact verdict format
- what decision depends on the answer

This prevents conversational drift and hidden assumptions.

---

## 17. Managing invalidated ideas

### 17.1 An invalidated idea has value if

- it is named
- it is documented
- it is connected to a structural reason for failure

Do not just stop using an idea. Write:
- what was hypothesized
- what was tested
- what failed
- whether the failure is numerical, conceptual, or structural

This creates reusable no-go knowledge and prevents rediscovering dead ends.

### 17.2 Error-chain audit (when a foundational error is found)

1. Identify the precise error (exact formula / line of code / assumption)
2. List all papers using this error DIRECTLY
3. List all papers depending on the first list TRANSITIVELY
4. Decide which artifacts are retracted, revised, or preserved
5. Document the chain explicitly (retraction memo)
6. Clean citations and route maps accordingly

In our project: 8 papers retracted via this procedure, 6 active papers audited, 0 valid content lost (all absorbed into other papers).

### 17.3 Retraction as quality control

> **Retraction, done properly, is not embarrassment management. It is quality control.**

Negative synthesis papers can emerge from invalidated routes — in our project, the "structural blindness" theorem was implicit in the invalidated chain and became a rigorous positive result when extracted.

### 17.4 Scope assumption auditing

Every numerical or theoretical result carries HIDDEN ASSUMPTIONS about scope (computational bounds, truncation levels, regime of validity). These must be made explicit.

**Example from our project:** the constant α_BC = 236 was computed with prime truncation P_max = 5M and held firm for ~3 weeks as a "universal constant." When one approach required P_max = T (physical infinity), α_BC diverged as log²(T)/2. The universality was an artifact of the truncation, not a property of the underlying object.

**Protocol:** for each numerical result claimed, document:
- **Assumptions:** "This holds if P_max = 5M, sigma_floor = 0.00020, logT ∈ [14,24]"
- **Invalidation triggers:** "If P_max changes, recompute these 23 notebooks"
- **Cross-result dependencies:** which claims depend on which assumptions

**Invalidation rules in practice:**
```
@requires(P_max = 5M)  # result depends on this bound
@invalidates(if P_max != 5M)  # downstream claims to revisit
alpha_BC = 236 +/- 4
```

Without this, scope drift goes unnoticed until a downstream calculation fails. In our project: 3 weeks of false confidence. With the rule: same bug caught in hours.

---

## 18. Reproducibility standards

Every substantial claim should have:
- script path
- output artifact
- parameter set
- precision or runtime context

If a table in a paper comes from code, the path should be findable in under a minute.

If the code lives in another repo, pin the commit hash.

**Reproducibility should be designed early, not added after drafting.**

### 18.1 Concrete reproducibility checklist

- [ ] All parameters in the script file (not hardcoded magic numbers)
- [ ] Output saved as JSON with full metadata
- [ ] Random seeds fixed and recorded
- [ ] Runtime and precision documented in output
- [ ] Script committed before running
- [ ] Results committed with reference to script commit

---

## 19. How to use AI without losing rigor

Practical rules derived from our project:

1. **Never let an agent silently convert an empirical pattern into an asymptotic statement.**
2. **Never let a theorem-style label remain on an unproved statement.**
3. **Always mark pipeline-dependent quantities as such.**
4. **Always distinguish** exact theorem, proof sketch, numerical observation, heuristic, conjecture.
5. **If two agent outputs disagree, do not average them.** Create a test or a clarifying note.
6. **If a claim matters for a paper**, read the primary source yourself or have an agent produce a technical extraction from it.
7. **If a route depends on a quantity whose definition is unstable, freeze it.**
8. **Flag any single-word claim that could carry heavy load** ("obviously", "clearly", "it follows that") — these often hide gaps.

---

## 20. Phases of investigation (complete workflow)

### Phase 0 — Problem framing (days 1-3)

Define the object, measurable quantity, success criteria, failure modes. Use 5-question gate. Produce `problem-statement.md`.

### Phase 1 — Literature landscape (weeks 1-2)

5-layer workflow (§5). Identify 20-50 papers; triage; deep-read a few; extract technically; issue bridge verdicts. Produce `literature-landscape.md` + `references.bib`.

### Phase 2 — Hypothesis generation and triage (weeks 2-4)

Enumerate 5-15 routes. Classify A/B/C. Rank by expected value (probability × inverse timeline). Multi-agent triage. Produce `route-map.md`.

### Phase 3 — Falsification sprints (days, not weeks)

For top routes: frame binary question, run cheapest decisive test, issue verdict. Do NOT commit long work without this step.

### Phase 4 — Deep computation / analysis (weeks to months)

Survivors from Phase 3. Structured progress logging. Weekly Reviewer audit. Explicit stop criteria. Document obstructions.

### Phase 5 — Writing and peer review (weeks)

Outline before text. Rigorous parts first. Three rounds internal review. Submission checklist.

### Phase 6 — Integration and next steps (continuous)

Archive invalidated work. Cross-reference audit. Update route map. Schedule quarterly literature monitoring.

### Operational monthly cadence

- One synthesis memo
- One route-map update
- One literature refresh
- One internal referee review on any serious draft
- One explicit freeze / continue / close decision on each active route

---

## 21. Common pitfalls and fixes

| Pitfall | Symptom | Fix |
|---|---|---|
| Probability inflation | "Combined probability 60-70%" from summed 20% routes | State outcome-specific. Never sum. |
| Category confusion | B-route presented as A | Always tag A/B/C. Review for drift. |
| Narrative lock-in | Committing to framing early | Falsification sprints. Articulate refutation. |
| Stale documentation | Plan files no longer match reality | Top-of-file "state block" updated each session |
| Single-agent drift | All decisions by one agent | Mandatory Reviewer verdict at gates |
| Infinite loops | Long run with no output | Cap loops, use `flush=True`, estimate runtime |
| Overlooking classics | Only 2020+ papers | Phase 1 must include classical reformulations |
| Research-by-chat | Many sessions, no artifact | Every step must produce a file |
| Epistemic slippage | Empirical becomes "asymptotic" | Explicit status labels |
| Venue mis-aim | Theorem-paper to Exp Math | Match content to venue type |
| Skipped review rounds | Submit after round 1 | Mandatory 3-round internal review |

---

## 22. Templates for reuse

### 22.1 Project kickoff checklist

```markdown
# Project: [NAME]

## Problem statement
[precise formulation]

## Success criteria
- Full: [what it means to solve]
- Partial: [what counts as useful progress]

## Initial inventory
- [ ] Literature landscape complete (20+ papers)
- [ ] Tools inventory
- [ ] Route enumeration (5+ routes)
- [ ] A/B/C classification
- [ ] Initial roadmap (90 days)

## Agents
- Coordinator: [who]
- Reviewer: [who]
- PI: [who]
```

### 22.2 Route plan template

```markdown
# Route [SHORTNAME]

## Target
[specific output]

## Classification
[A / B / C]

## Current status
[active / exploratory / frozen / closed negative / submit-ready]

## Success condition
[what means it worked]

## Stop condition
[what means we abandon]

## Reactivation trigger (if frozen)
[what would revive]

## Current deliverables
- [list with statuses]
```

### 22.3 Paper submission checklist

```markdown
# Paper SUBMISSION_CHECKLIST

## Files ready
- [ ] main.pdf compiled cleanly
- [ ] main.tex with all cross-refs resolved
- [ ] references.bib with no broken entries
- [ ] cover_letter.tex drafted
- [ ] supplementary materials if needed

## Metadata
- [ ] Title finalized
- [ ] Abstract (word count target)
- [ ] MSC / PACS codes / keywords
- [ ] Author ORCID
- [ ] Affiliation

## Venue
- First choice: [journal]
- Fallback 1: [journal]
- Fallback 2: [journal]

## Pre-submission checks
- [ ] Spell check
- [ ] All references verified
- [ ] No citations to retracted papers
- [ ] Repo public (if code cited)
- [ ] No mentions of invalidated prior claims
```

### 22.4 Reviewer-agent prompt template

```markdown
# Review — [DELIVERABLE]

## Context (1-2 paragraphs)
[What this is and why it matters]

## Specific changes since last round
1. [edit 1]
2. [edit 2]
...

## Questions
A. [Question 1]
B. [Question 2]
...

## Expected output
- Per-question verdict
- Binary: approve / revise / reject
- Any concern we missed
```

### 22.5 Session close template

```markdown
# Session close — [DATE]

## What changed today
- [major deliverables]

## Repo state
- [repo]: [HEAD, status]

## Pending for next session
- [ ] [item 1]
- [ ] [item 2]

## Key commits
[list with 1-line descriptions]

## Review status
- Codex: [rounds this session, verdicts]
- PI: [decisions made]

## Open questions
- [question 1]
- [question 2]
```

### 22.6 Concrete operating template (new project)

Starting a new scientific topic with AI agents:

1. Create repo with directories:
   - `notes/`
   - `papers/`
   - `code/`
   - `output/`
   - `references/`

2. Write:
   - `project-map.md`
   - `route-register.md`
   - `initial-literature-triage.md`

3. For each route:
   - `plan-route-X.md`
   - `results-route-X-*.md`
   - stop criteria

4. For each important paper: technical extraction note.

5. For each major draft: at least one referee-style review cycle.

6. Weekly: continuity memo (closed / alive / test-next / freeze).

7. For strategy-affecting drafts: reviewer-agent pass before treating as stable.

8. For any foundational correction: retraction / error-propagation memo before resuming forward work.

---

## 23. Meta-lessons (10 principles that matter most)

1. **Work by artifacts, not chats.**
2. **Separate proof, numerics, and heuristics aggressively.**
3. **Freeze ambiguous targets early.** Do not try to compute your way through a target whose definition is unstable.
4. **Use internal referee review before external submission.** Saves review cycles.
5. **Treat negative results as first-class outputs.** They close routes cleanly and often publish.
6. **Prefer route maps over idea accumulation.** Ideas without classification drift.
7. **Let AI accelerate structure, not replace judgment.** Human owns epistemic commitments.
8. **Use cheap falsification to protect deep-work time.** Highest-ROI pattern in the project.
9. **Separate direct attacks, partial results, and long-term programs.** A/B/C always tagged.
10. **Treat review and retraction as core research operations, not cleanup.**

### 23.1 Additional lessons

11. **Iteration beats planning.** Good 90-day plan revised 5 times > perfect plan revised never.
12. **Two AI agents > one AI agent + smart human.** Breaks confirmation bias.
13. **Classical results matter.** Foundational 1950s papers often more useful than 2024 breakthroughs.
14. **Explicit stop criteria defined in advance.** Researchers convince themselves progress is happening when it isn't.
15. **Honest probability is harder than optimistic probability** — but necessary.

---

## 24. Adaptation to other scientific fields

The methodology is DOMAIN-AGNOSTIC. Only the concrete instantiations of each concept change. This section provides specific translations for a wide range of fields.

### 24.1 Universal vocabulary translations

| Methodology concept | Math/Physics | Statistics | CS/Engineering | Biology | Economics | Psychology | Sociology | Sports/Exercise | Qualitative |
|---|---|---|---|---|---|---|---|---|---|
| **Route** | Proof strategy / ansatz | Modeling approach | Algorithm / architecture | Experimental design | Identification strategy | Theoretical framework | Sampling / analytical approach | Intervention protocol | Theoretical lens / coding frame |
| **Falsification sprint** | Toy computation | Simulation on toy data | Small-scale prototype | Single-condition experiment | Identification check on reduced sample | Pilot study with small N | Exploratory interviews | Pilot intervention on N=5-10 | Early reflexive memo / code saturation check |
| **Decision gate** | First provable lemma | Power analysis / preregistration milestone | MVP / alpha release | Preliminary results milestone | Pre-analysis plan checkpoint | Pilot → full study decision | Saturation check | Safety & efficacy pre-check | Theoretical sufficiency assessment |
| **Obstruction layer** | Kernel singularity / sign constraint | Endogeneity / selection bias / identifiability | Complexity wall / halting / correctness | Confounders / reverse causation / ecological validity | Omitted variable / weak instruments | Construct validity / measurement invariance | Selection bias / reflexivity | Floor/ceiling effects / regression to mean | Reactivity / researcher effect |
| **Error-chain audit** | If theorem wrong, which corollaries fail? | If p-hacking in source, which meta-analyses contaminated? | If library bug, which downstream systems? | If foundational paper retracted, which follow-ons? | If identification assumption wrong, which policy inferences fail? | If measure invalid, which findings affected? | If source data biased, which theories affected? | If protocol flawed, which clinical recommendations? | If key informant unreliable, which themes contaminated? |
| **Epistemic label** | proved / conjectured / empirical | significant / exploratory / spurious | verified / tested / prototype | replicated / single-study / pilot | identified / suggestive / descriptive | confirmed / replicated / exploratory | theorized / grounded / speculative | evidence-based / exploratory / case-study | thick description / grounded / interpretive |

### 24.2 Field-specific protocols

#### Mathematics / Pure theory

- **Route types:** proof strategies, ansätze, reductions to known problems
- **Falsification sprint:** compute a toy case at low precision; check if the claim survives
- **Literature:** identify classical equivalent criteria (often more useful than recent breakthroughs)
- **Multi-agent:** one agent develops proof, other audits for gaps
- **Artifact types:** `.tex` files with theorem-proof structure, verified computations in mpmath/SageMath

#### Statistics / Quantitative methods

- **Route types:** modeling approaches, estimation strategies, inference frameworks
- **Falsification sprint:** simulation study with synthetic data where ground truth is known
- **Literature:** prior methodological papers + applied examples
- **Multi-agent:** one runs analysis, other does robustness checks (different specifications, bootstrap, bayesian vs frequentist)
- **Specific anti-patterns:** p-hacking, garden of forking paths, HARKing (Hypothesizing After Results are Known)
- **Epistemic discipline:** preregistration vs exploratory analysis; confirmatory vs generative

#### Computer science / Software engineering

- **Route types:** algorithmic approaches, architectural choices, implementation strategies
- **Falsification sprint:** small-scale prototype with toy input before full implementation
- **Literature:** prior art in key venues (NeurIPS, ICML, POPL, OSDI, SOSP, CHI)
- **Multi-agent:** independent code review + independent test writing + independent benchmarking
- **Error chain:** if library bug, which downstream systems affected?
- **Reproducibility:** version pins, container images, seed controls, compute resource declarations

#### Physics (theoretical + experimental)

- **Route types:** theoretical frameworks, experimental protocols, simulation strategies
- **Falsification sprint:** toy model / simpler simulation before production run
- **Literature:** review of experimental status (e.g., PDG for particle physics) + theoretical landscape
- **Decision gate:** after preliminary data, commit to full experiment
- **Specific:** systematic errors must be classified separately from statistical; beam time / accelerator access is a hard constraint on iteration speed

#### Biology (cellular, molecular, organismal, ecological)

- **Route types:** mechanistic hypotheses, experimental designs, model systems
- **Falsification sprint:** single-condition experiment before multi-factorial design
- **Literature:** evolutionary + biochemical + clinical (depending on scope)
- **Error chain:** foundational paper retracted → cascade through citing papers (e.g., replication crisis in psychology has biology analogs)
- **Specific:** n (biological vs technical replicates), power analysis, strain/batch effects, microbiome/environmental confounds
- **Ethics:** IACUC / IRB approvals must be part of the artifact trail

#### Economics / Quantitative social science

- **Route types:** identification strategies (IV, RDD, DiD, RCT), theoretical models, structural vs reduced-form
- **Falsification sprint:** identification diagnostic on small sample (e.g., balance tests, first-stage F-statistics) before full analysis
- **Literature:** seminal papers + recent empirical + current methodological debates (AER, QJE, Econometrica)
- **Obstruction layers:** weak instruments, selection bias, non-compliance, spillovers, SUTVA violations
- **Path independence:** descriptive papers are path-independent; causal papers depend on identification working
- **Decomposition:** decompose causal effect into channels (income, substitution, information); publish per-channel even if aggregate estimate is uncertain

#### Psychology (cognitive, social, clinical, developmental)

- **Route types:** experimental paradigms, theoretical accounts, measurement approaches
- **Falsification sprint:** small-N pilot before full study with power analysis for main effect
- **Literature:** prior findings + Open Science Framework preregistrations + replication reports
- **Obstruction layers:** construct validity (am I measuring what I think?), demand characteristics, measurement invariance, ceiling/floor effects, WEIRD samples
- **Specific:** preregistration mandatory for confirmatory studies; exploratory analyses clearly labeled
- **Replication crisis context:** treat single-study findings as preliminary; require multi-lab or meta-analytic support for strong claims
- **Error chain:** if measure (e.g., implicit association test) turns out unreliable, which literatures contaminated?

#### Sociology (quantitative and qualitative)

- **Route types:** theoretical frameworks (e.g., Bourdieu, Foucault, rational choice), methodological approaches (ethnography, survey, comparative-historical, computational)
- **Falsification sprint:** exploratory interviews or small-scale survey pilot; coding 10% of data to check interpretive frame
- **Literature:** theory + prior empirical + current methodological debates
- **Qualitative-specific obstructions:** reflexivity (researcher influence), access (who will talk to you?), ethics (consent, anonymity), generalizability vs depth trade-off
- **Mixed methods:** keep quantitative and qualitative analyses separate until integration phase; document sequence (QUAN→QUAL, QUAL→QUAN, concurrent)
- **Path independence:** descriptive ethnography path-independent; causal claims depend on additional data

#### Sports sciences / Exercise physiology / Sports medicine

- **Route types:** training protocols, intervention designs, measurement approaches (VO2max, lactate, wearables)
- **Falsification sprint:** small-N pilot (N=5-10 athletes) before full RCT; athletes as their own controls
- **Literature:** sport-specific + general physiology + statistical methods (mixed models for repeated measures, individual response analysis)
- **Obstruction layers:** regression to mean, Hawthorne effect, placebo, individual response variability (what works on average may not work per-athlete), seasonal / training-status confounds
- **Specific:** ethics (injury risk), practical constraints (elite athlete availability), ecological validity (lab vs field), publication bias toward positive effects
- **Modular papers:** methodological paper (new measurement) + intervention paper (effect) + mechanism paper (physiology)
- **Epistemic discipline:** effect sizes over p-values, confidence intervals, magnitude-based inference

#### Qualitative research (ethnography, grounded theory, phenomenology, narrative, discourse analysis)

- **Route types:** theoretical lens, methodological approach, sampling strategy
- **Falsification sprint:** early reflexive memo; check if preliminary themes survive additional data
- **Literature:** theoretical sources + methodological exemplars + domain-specific prior studies
- **Obstruction layers:** reactivity, researcher bias, saturation (am I actually at saturation or just tired?), negative cases (am I ignoring disconfirming evidence?)
- **Artifact types:** field notes, transcripts, codebook, memos, thick descriptions, final analysis
- **Credibility instead of validity:** triangulation, member checking, peer debriefing, reflexivity statements
- **Multi-agent analog:** one agent as primary coder, other as independent coder for intercoder agreement; a third for audit trail review
- **Decision gate:** theoretical sufficiency (further data wouldn't change conclusions), not statistical power
- **Publication:** thick description is path-independent; theoretical contribution depends on analytic engagement

#### Mixed methods research

- **Route types:** integration strategies (sequential QUAN→QUAL, QUAL→QUAN, concurrent, nested)
- **Falsification sprint:** pilot both quantitative measurement AND qualitative coding before full integration
- **Literature:** mixed-methods methodology + domain-specific integration examples
- **Specific challenges:** different epistemic standards, integration is harder than running two separate studies
- **Artifacts:** parallel tracks of QUAN and QUAL until explicit integration document
- **Path independence:** QUAN and QUAL components can often be path-independent from each other

#### Humanities (history, literature, philosophy, cultural studies)

- **Route types:** interpretive frameworks, source selection, methodological schools
- **Falsification sprint:** close reading of 1-2 key texts/sources to test interpretive frame
- **Literature:** historiography / critical landscape / prior interpretations
- **Error chain:** if foundational text is mistranslated or misread, which scholarship fails?
- **Artifacts:** source archives, close-reading notes, argumentative drafts
- **Specific:** archival access, language skills, historical context accuracy

### 24.3 Cross-field commonalities

Regardless of field, these patterns ALWAYS apply:

1. **Work by artifacts, not conversations.** A 90-minute brainstorming chat that doesn't produce a memo is wasted.

2. **Classify every claim by epistemic status.** The labels differ by field (`proved` in math, `replicated` in psychology, `saturated` in grounded theory) but the discipline is the same.

3. **Falsify cheaply before investing deeply.** Every field has its version of the 1-day test that could kill a route.

4. **Route map with A/B/C classification.** A direct answer, B partial result, C long-term program. Never confuse them.

5. **Multi-agent review.** Whether it's peer reviewer, coder check, robustness audit, or mathematical peer — independent validation is non-negotiable.

6. **Decomposition over blocking.** When the grand claim is stuck, decompose into publishable components.

7. **Path independence mapping.** Identify which deliverables can ship without waiting for the grand solution.

8. **Scope assumption auditing.** Every numerical/empirical/interpretive result carries scope. Document it. Re-audit when scope changes.

9. **Dead-end taxonomy.** After N failed approaches, synthesize a reusable taxonomy. Pays off exponentially.

10. **Retraction as quality control.** When errors are found, retract explicitly. Extract valid content into active work.

### 24.4 Field-specific tool stacks

| Field | Typical tools | AI agent role |
|---|---|---|
| Math / Physics theory | LaTeX, mpmath, SageMath, Mathematica | Executor: computations; Reviewer: proof gaps |
| Physics experimental | ROOT, Geant4, MATLAB, Python | Executor: data reduction; Reviewer: systematic error audit |
| Statistics | R, Stan, Python (statsmodels), SAS | Executor: models; Reviewer: robustness / specification |
| CS / ML | Python (PyTorch/JAX), Rust, Go | Executor: prototypes; Reviewer: tests, benchmarks, security |
| Biology | R (Bioconductor), Python (scanpy), GraphPad, ImageJ | Executor: pipeline; Reviewer: experimental design, batch effects |
| Economics | Stata, R, Python, Matlab | Executor: estimation; Reviewer: identification, robustness |
| Psychology | R, JASP, jamovi, Qualtrics | Executor: analysis; Reviewer: preregistration compliance, effect size |
| Sociology (quant) | R, SPSS, Stata, Python | Executor: models; Reviewer: specification, robustness |
| Sociology (qual) | NVivo, Atlas.ti, Dedoose, Taguette | Executor: coding; Reviewer: intercoder reliability, reflexivity |
| Sports science | R, Python, kinematic analysis (Vicon, Xsens), wearables (Garmin, Polar) | Executor: time-series + training models; Reviewer: ecological validity, individual response |
| Qualitative | NVivo, Atlas.ti, MAXQDA | Executor: transcription, coding; Reviewer: reflexivity audit |
| Humanities | Zotero, text-analysis tools (spaCy for computational), archives | Executor: research synthesis; Reviewer: interpretive argument |

### 24.5 When the methodology needs adaptation

Some fields have specific constraints that require modification:

**Fields with hard iteration limits** (astronomy with telescope time, particle physics with beam time, clinical trials with regulatory cycles):
- Falsification sprints become MORE important (can't afford wasted iterations)
- Pre-analysis plans and preregistrations are mandatory
- Decision gates must be set before data collection, not after

**Fields with strong qualitative traditions** (ethnography, phenomenology, certain humanities):
- "Falsification" concept adapts to theoretical sufficiency / negative case analysis
- Multi-agent peer debriefing replaces independent statistical audit
- Artifact types shift toward thick description and reflexive memos

**Fields with human subjects** (psychology, medicine, sociology, sports science):
- IRB / ethics approval becomes part of the artifact chain
- Consent, data privacy, re-identification risks enter error-chain audits
- Publication delays and embargoes affect timeline planning

**Fields with industrial / commercial constraints** (applied ML, industrial engineering, product research):
- Path independence includes patent considerations
- Publication decisions involve trade secrets
- Multi-agent review includes legal / IP audit

### 24.6 Universal applicability statement

This methodology has been successfully used in mathematics (RH project). Its core patterns — **artifact-based work, falsification-first, A/B/C routes, multi-agent review, epistemic labels, decision gates, stop criteria, error-chain audits, decomposition, path independence, retraction as quality control** — are discipline-agnostic.

What changes across fields:
- Vocabulary (route → design / paradigm / framework / protocol)
- Tools (LaTeX → Stata → NVivo → etc.)
- Epistemic standards (proof → replication → saturation)
- Hard constraints (compute → beam time → IRB → field access)

What stays invariant:
- The DISCIPLINE of working by artifacts, classifying epistemically, falsifying cheaply, splitting direct/partial/long-term, reviewing independently, auditing scope, decomposing when blocked, documenting retractions.

**Any project where AI agents collaborate with humans to produce defensible scientific outputs benefits from this discipline.** Economics PhD dissertations, sports-science RCTs, sociology ethnographies, biology single-cell analyses, CS systems papers, statistics methodological notes — all benefit.

The project you're reading this from was in number theory. The method works wherever defensible inquiry is the goal.

---

## 25. What this methodology does NOT do

- **Does not guarantee solving the problem.** Most research projects produce partial results, not full solutions.
- **Does not replace deep expertise.** AI amplifies expertise; doesn't replace it.
- **Does not work on trivially simple problems.** If solvable in a day, don't impose 6 phases.
- **Does not remove need for community engagement.** Peer review, correspondence, conferences — these require human relationships and judgment.

---

## 26. Minimum viable workflow

If you remember nothing else:

1. **Two AI agents with separated roles** (executor + reviewer), plus human PI.
2. **Phases:** frame → literature → hypothesis → falsify → deep work → write → review.
3. **A/B/C classification** of routes. Never conflate.
4. **Cheap falsification before expensive work.**
5. **Honest documentation** with timestamps, commits, retraction memos.
6. **Decision gates with pre-specified stop criteria.**
7. **Iteration over planning:** revise the plan monthly.
8. **Work by artifacts, not chats.**

Everything else is refinement.

---

## 27. Final takeaway

The strongest meta-result of this project is not a theorem about RH. It is a method:

> **AI can make a research program faster and broader only if the project is run as a disciplined system of routes, artifacts, verdicts, and reviews. Without that system, AI amplifies confusion. With that system, AI becomes a serious research instrument.**

---

## 28. Closing note

This methodology emerged from working on a hard open problem (Riemann Hypothesis-adjacent) over several months with Claude (Anthropic) and Codex (OpenAI via ChatGPT-like interface) as AI agents. The human PI (David Alarcón) drove strategic decisions and provided domain expertise.

The project produced:
- 11 active papers (I-IV-new, VII, A, B, B1, E, J, PHYS, RC)
- 8 retracted papers (C, C1, D, D1, F, G, H, MAIN)
- 1 submit-ready flagship (Paper IV-new → IMRN)
- ~25 memos and notes
- ~5 rounds of internal review per flagship paper
- 1 90-day roadmap with 4 phases, 6 stop criteria, explicit probabilities
- 1 equivalent-criterion route (Nyman-Beurling / Báez-Duarte) currently under Gram-matrix test

It did **not** solve the Riemann Hypothesis. It mapped what works, what doesn't, and what remains viable. The methodology above is what survived.

**Adapt it; don't blindly apply it. The structure is more important than the specific tools. Good luck.**

---

## 29. Rhythms, pivots, and prompt evolution (lessons from 6-week intensive phase)

Analysis of 5085-line historical research log (CLAUDE_HISTORICO.md, March 2026) reveals temporal patterns not captured in the abstract methodology above.

### 29.1 Sprint rhythm: intensive blocks > distributed work

**Pattern observed:** days 2-3 of a single intensive sprint produced 3× better diagnostics per hour than day 1 (onboarding overhead).

**Quantitative:**
- **Intensive sprints (3-4 consecutive days):** ~2 new approaches + 1 diagnostic per day. High velocity, low finish rate. Best for exploration.
- **Distributed sessions (1-2 notebooks per day):** ~1 approach + systematic closure per day. Lower velocity, higher quality closure. Best for finalization.

**Most valuable outputs** (major discoveries, constant identification, scope corrections) all occurred in dedicated multi-day blocks where context remained hot.

**Rule:**
- Reserve 2-3 day blocks with NO context-switching for exploratory research
- Reserve distributed days for closure, writing, review
- Efficiency drops ~40% when switching between 5+ simultaneous notebooks

### 29.2 Measure-to-theory pivot

**When theoretical approaches plateau, pivot to measurement-driven diagnostics.**

In our project: after 12 failed theoretical approaches, a single day of measurement (2026-03-20) produced:
1. Analytical confirmation of δb₂_PNT(τ) = -τ
2. Detection that p₂ Janossy formula was wrong (missing Schur complement term)
3. Decomposition of c into 7% PNT + 26% Born + 67% non-perturbative

More value in one measurement day than in 12 preceding theoretical days.

**Rule:** when stuck, **measure before computing next**. Regression to empirical basics often reveals framework errors invisible in abstract approaches.

### 29.3 Batch similar approaches

**Observed anti-pattern ("accumulator testing"):** executing 3-4 approaches back-to-back without intermediate diagnosis.

**Example:** 2026-03-18 ran Caminos D', E, F (second-order kernel, factorization, Yakaboylu) — all failed for IDENTICAL reasons (sign error, non-GUE base). Cost: 2 days wasted on repeats.

**Rule:** after each approach, measure prevalence of blockage type. Is this a new obstruction or a repeat? **Batch repeats; diagnose before next batch.** Five approaches blocked by sinc(1)=0 can be diagnosed once, not five times.

### 29.4 Scope creep protection (2-day branching rule)

**Observed anti-pattern:** a single approach (e.g., Painlevé V linealization) started as 2-day task, expanded to 5 days as sub-questions arose. Context lost; unclear output.

**Rule:**
- Set a 2-day limit per approach
- If questions remain after 2 days, BRANCH to sub-notebooks with explicit dependencies
- Never expand the original task; create new ones

This forces decomposition and prevents "one more experiment" drift.

### 29.5 Prompt evolution (compute → diagnose → scope)

**Observed progression in effective agent usage:**

- **Early sessions (early weeks):** "compute X" prompts. Single-question, straightforward.
- **Mid sessions (after ~10 failed approaches):** "why did approaches 1-12 fail in the same way?" Diagnostic queries.
- **Late sessions (near publication):** "which results are publishable without solving c?" Scope/strategy queries.

**Pattern:** the most valuable AI agent outputs shifted from numerical results to:
1. Unified obstruction identification (4 layers across 17 approaches)
2. Decomposition proposals (7% / 26% / 67%)
3. Scope validation (what's publishable in current state)

**Rule:** when a project has 20+ failed approaches, STOP asking "compute approach #21." Instead ask:
1. "What blockers do approaches 1-20 share?" (diagnostic)
2. "Which fraction of the target is solvable vs non-perturbative?" (decomposition)
3. "What's publishable without the remaining unsolved piece?" (scope)

**Methodology should codify WHEN to use each type of prompt.**

### 29.6 Multi-agent scaling threshold

**Observation:** single-agent efficient for 6-week projects. For 12+ weeks or 200+ notebooks, multi-agent architecture pays off.

Specifically:
- **Diagnostic agent** (architectural decisions, cross-notebook reviews, scope management)
- **Compute agent** (execution, notebook scaffolding, unit tests, reporting)

Without split: ~30% of diagnostic agent time spent on bookkeeping instead of diagnosis.

**Rule:** at project scope > 200 notebooks or > 8 weeks of single-agent time, introduce multi-agent architecture with weekly sync.

### 29.7 Dead-end taxonomy as reusable asset

**Single most productive synthesis activity:** creating a unified obstruction table mid-project.

**Our project:** after 17 failed approaches, 1-hour synthesis produced:

```
| # | Route name | Numerical result | Obstruction layer | Cost |
|---|---|---|---|---|
| 1 | Sine kernel first order | -1.6 (sign error) | Layer 2 | 3h |
| 2 | Cosine kernel | +0 identically | Layer 1 (sinc=0) | 5h |
...
```

**Value produced:** 5 subsequent approaches designed to explicitly avoid layers 1-3. They still failed but failed FASTER (~1 day each vs ~3 days each). Cost of table: 1 hour. Savings: ~2 weeks.

**Rule:** mid-project synthesis of failures into a reusable taxonomy pays off exponentially. Schedule it after every ~10 approaches.

### 29.8 Strategic retractions enable forward progress

**When a foundational error is discovered, strategic retraction can enable rather than halt forward progress.**

Our project: 8 papers retracted in 1 session after identifying the 2026-04-07 normalization error. This sounds catastrophic but:

- Valid content (empirical c = 1.245, blindness theorem, Born ceiling, eigenvalue sharpening) extracted INTO other papers
- The 8 retracted papers contained NO unique valid content after extraction
- Retraction FREED the project from defending unsound claims
- Strengthened remaining papers by eliminating self-contradictions

**Rule:** when retracting, simultaneously audit for what can be preserved in active papers. Retraction is extraction + archival, not deletion.

---

## Provenance

This document integrates:
- **Claude's methodology note** (original version, 12 sections): philosophy, phases, templates, pitfalls, adaptation.
- **Codex's AI-systematic-research playbook** (23 sections): core principle framing, artifact-centric unit of work, 5-layer literature workflow, epistemic status labels, 4 AI role types, agent-to-agent communication patterns, retraction procedures, 10 "what mattered most" principles.
- **CLAUDE_HISTORICO.md analysis** (5085-line research log, March 2026, §29): sprint rhythms, measure-to-theory pivot, batching, scope creep protection, prompt evolution, multi-agent scaling, dead-end taxonomy, strategic retractions.

The unified version preserves strongest framings from each source, removes redundancy, and provides a single authoritative reference.

Last update: 2026-04-17.
