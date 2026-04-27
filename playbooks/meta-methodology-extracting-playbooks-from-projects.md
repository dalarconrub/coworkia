# Meta-methodology — How to extract a reusable playbook from a research project

**Date:** 2026-04-17
**Purpose:** document the META-PROCESS by which methodological lessons from a completed (or in-progress) research project are abstracted, consolidated, and transformed into a discipline-agnostic playbook applicable to future projects in any scientific field.

**Trigger:** this document describes how to do what we just did — transform 6 weeks of RH research into a 1500-line methodology usable for economics, sports science, biology, sociology, etc.

**Meta-level:** this is a methodology ABOUT methodology extraction. It can itself be refined by applying it to the extraction process.

---

## 0. Why do this at all

Most research projects produce specific results. Few produce METHODOLOGICAL outputs.

But the methodological layer often has MORE transfer value than the specific results:

- Our RH project did not solve RH. But the methodology used (falsification-first, A/B/C routes, multi-agent review, retraction workflow) transfers to any hard scientific problem.
- A failed biology experiment may still teach lessons about experimental design, data management, peer review organization — applicable to all biology, or even beyond.
- A PhD thesis produces specific domain knowledge AND tacit methodological know-how. The methodological layer is what the PhD student actually learned; the thesis is just its specific instantiation.

**The extraction process documented here makes the methodological layer EXPLICIT, REUSABLE, and TRANSFERABLE.**

---

## 1. When to perform extraction

### 1.1 Appropriate triggers

Do this at:

1. **End of a major project phase** — after each significant milestone (not just at the end)
2. **After a near-miss** — when you avoided a disaster by a specific practice, capture it
3. **After a retraction or significant error** — the lessons are expensive; make them reusable
4. **Before starting a new project in a different field** — ensures you bring forward what transfers
5. **When onboarding a new collaborator** — forces articulation of implicit practices
6. **Once per year at minimum** for long-running programs

### 1.2 Inappropriate triggers

Do NOT do this:

- Mid-sprint (disrupts flow, premature synthesis)
- When the project is stalled but alive (confounds "stuck" with "done")
- When lessons are too raw (wait 1-2 weeks for perspective)

### 1.3 Ideal conditions

- Project phase has a clear end (deliverable shipped, paper submitted, milestone reached)
- At least 4-6 weeks of substantive work to mine
- Multiple artifacts (notes, commits, papers, logs) — the raw material
- Enough distance to identify patterns but enough recency to remember context

---

## 2. Prerequisites

Before starting extraction, ensure:

### 2.1 Artifact completeness

- All notes timestamped and committed
- All decisions recorded in memos (not just chats)
- Error episodes documented (both the error and the fix)
- Pivot moments labeled (why we changed direction)

If you don't have these, first spend a session backfilling the record. You cannot extract from what isn't written.

### 2.2 Multi-source material

Better extraction comes from multiple independent records:

- Your own notes
- Reviewer agent's critiques (e.g., Codex's feedback)
- Commit history
- Paper drafts and their revision cycles
- Retraction memos
- Correspondence with collaborators

Having 2-3 sources triangulates lessons and prevents single-perspective bias.

### 2.3 Availability of a reviewer agent

The extraction itself benefits from multi-agent review. Have:

- An **extractor agent** (reads raw material, produces candidate lessons)
- A **reviewer agent** (challenges overgeneralization, identifies domain-specificity vs universality)
- **Human judgment** (makes final calls on what's transferable)

---

## 3. The 7-step extraction pipeline

### Step 1 — Inventory the raw material (1-2 hours)

Produce a list of ALL project artifacts:

```
- `notes/*.md` files (count, date range)
- commit history (`git log --oneline`)
- paper drafts (each version)
- review cycles (prompts + responses)
- retraction memos
- data files / JSON outputs
- scripts
```

Don't read yet; just inventory. This calibrates scope for later work.

### Step 2 — Surface-level survey (half day)

Read HEADERS / ABSTRACTS only:

- Titles of notes and their opening paragraphs
- Commit messages (no diffs)
- Abstracts of papers
- First and last line of each review response

Produce a timeline of the project:

```
2026-03-13: project start, initial dataset
2026-03-18: first round of 6 approaches attempted
2026-03-20: major pivot (measure before compute)
2026-04-07: normalization error discovered
...
```

Result: `project-timeline.md` with narrative arc.

### Step 3 — Deep mining by category (1-2 days)

For each category below, go through artifacts extracting EXAMPLES and LESSONS.

**Categories to mine** (adapt to project; this is the default list):

1. **Error moments** — what errors occurred, how discovered, what propagated
2. **Breakthrough moments** — what unblocked progress, what pattern preceded it
3. **Dead ends** — what didn't work, structural reasons
4. **Pivots** — when direction changed significantly
5. **Sprint patterns** — intensive vs distributed work comparison
6. **Review cycles** — what reviewer feedback was most valuable
7. **Data quality events** — remeasurements, outliers, validation
8. **Paper architecture evolution** — how organization changed
9. **Anti-patterns** — things that wasted time
10. **Strategic wins** — practices that produced disproportionate value
11. **Collaboration patterns** — how human-AI interaction evolved
12. **Decision gates** — binary choice points and how resolved

**For each item in each category, record:**

- **What happened** (concrete example with date)
- **Why it mattered** (cost saved / value produced, quantified if possible)
- **Generalizable lesson** (stripped of domain specifics)

**Tool:** delegate this step to an agent with this exact structure. In our case, we used the Agent tool with a prompt:

> "Read FILE. Extract lessons in CATEGORIES. For each: what, why, generalizable."

This is one of the few cases where a general-purpose agent is strictly better than human reading, because it applies uniform structure.

### Step 4 — First synthesis pass (half day)

From the raw lesson list, identify PATTERNS:

- Multiple examples of the same lesson? Merge into one stronger rule.
- Lesson appears domain-specific? Try to strip the domain.
- Lesson contradicts another? Resolve explicitly (maybe both are true in different contexts).
- Lesson is an instance of a known rule? Reference the known rule.

**Output:** `candidate-lessons.md` with ~20-50 distilled lessons, organized by category.

### Step 5 — Domain-universality audit (half day)

For each candidate lesson, ask:

1. **Is this domain-specific?** (e.g., "always verify mpmath precision" is math/CS specific)
2. **Is this universally applicable?** (e.g., "falsify cheaply before investing deeply" applies everywhere)
3. **Is this a SPECIFIC INSTANCE of a universal rule?** (if so, identify the universal rule AND the specific instance)

Classify lessons into:

- **Universal principles** (work in any field)
- **Multi-field patterns** (applicable with translation)
- **Field-specific practices** (keep as reference but not core playbook)

### Step 6 — Integration into structured document (1-2 days)

Write the playbook with this structure:

1. **Core philosophy** (3-5 principles)
2. **Architecture** (repo / workflow / role separation)
3. **Phases of work** (problem framing → literature → hypothesis → test → write → integrate)
4. **Specific systems** (documentation, version control, review cycles)
5. **Patterns and procedures** (falsification sprints, decision gates, etc.)
6. **Common pitfalls** (with concrete examples from source project)
7. **Templates** (kickoff, decision gate, submission, session close)
8. **Field adaptations** (how translations work for different disciplines)
9. **Meta-lessons** (10 highest-level principles)
10. **Minimum viable workflow** (if you remember nothing else)

### Step 7 — Universalization pass (half day)

Read the completed playbook as if you were in a COMPLETELY DIFFERENT FIELD (e.g., if written from a math project, read as if you were a sociologist).

For each section, ask:

- Does this work for my hypothetical other field?
- What concept translations are needed?
- Any vocabulary that's too specific?

Add a "universal vocabulary translation table" with columns for 5-10 different fields. Add field-specific protocols as examples.

Commit. Iterate.

---

## 4. Sources to mine systematically

### 4.1 Primary sources

| Source | What to extract |
|---|---|
| Commit history | Decision points, frequency of work, topic shifts |
| Session-close notes | End-of-day summaries, pending items, context |
| Paper drafts and revisions | Architectural decisions, framing changes |
| Review cycles (Codex prompts + responses) | Specific critique patterns that repeated |
| Retraction memos | Error-discovery patterns, what triggered the catch |
| Pivot memos | Why direction changed, cost of the pivot |

### 4.2 Secondary sources

| Source | What to extract |
|---|---|
| Failed scripts / aborted computations | Infrastructure lessons, overhead patterns |
| Todo lists (completed) | Estimation accuracy (did tasks take as long as planned?) |
| Email / chat threads | Communication patterns, handoff failures |
| Literature reading notes | How you triaged, what bridges worked |

### 4.3 Meta-sources

| Source | What to extract |
|---|---|
| Your own after-action retrospectives | Reflexive observations |
| Collaborator feedback | External view of the process |
| Field-specific methodological literature | Prior playbooks for this domain |

---

## 5. Concepts to extract (the 12-category taxonomy)

When mining a project, the following 12 categories cover most methodological ground:

| # | Category | Example in our project |
|---|---|---|
| 1 | **Breakthrough moments** | Measure-to-theory pivot 2026-03-20 |
| 2 | **Error moments** | Normalization error 2026-04-07 |
| 3 | **Dead ends** | 29 failed perturbative approaches |
| 4 | **Pivot moments** | Route δ → NB/BD |
| 5 | **Sprint patterns** | Intensive 3-day blocks vs distributed |
| 6 | **Collaboration patterns** | Claude-Codex role separation |
| 7 | **Data quality events** | 6.14M zero re-measurement |
| 8 | **Architecture evolution** | A-J → I-V → I-IV-new (with retractions) |
| 9 | **Anti-patterns** | Accumulator testing, scope creep |
| 10 | **Strategic wins** | 1-day falsification saving weeks |
| 11 | **Decision gates** | "Does d(N) decay polynomially?" |
| 12 | **Retrospective synthesis** | Obstruction layer enumeration |

For each project, adapt this list. Some categories may not apply; others may need to be added (e.g., "ethical dilemmas" for human subjects research, "access problems" for field work).

---

## 6. Integration patterns

### 6.1 The "three sources into one" pattern

Our best methodology document came from integrating:

- Claude's own methodology notes
- Codex's parallel playbook
- Historical research log (5085 lines)

Each source had blind spots the others filled. The integration produced a stronger synthesis than any source alone.

**Rule:** always merge ≥ 2 independent perspectives. If only one source exists, delay integration until a second is produced.

### 6.2 The "preserve provenance" pattern

The final document has a "Provenance" section naming its sources. This allows:

- Future readers to understand WHERE each insight came from
- Returning to original sources for more depth
- Distinguishing Claude-contributed ideas from Codex-contributed ideas from empirical observations

Always include a provenance block. It's tempting to erase authorship in the final synthesis; resist this.

### 6.3 The "layered redundancy" pattern

Some lessons appear in multiple sections (e.g., "falsification-first" might appear in core principles, in experimental design, AND in meta-lessons).

**This is a feature, not a bug.** Different readers arrive at different sections. A truly important lesson should be reachable from multiple entry points.

But: if a lesson appears in 5+ sections identically, it's been over-emphasized. Consolidate.

### 6.4 The "concrete example" pattern

Every general principle should have at least ONE concrete example. Abstract principles don't transfer; concrete-plus-abstract does.

**Bad:** "Always document assumptions."

**Good:** "Always document assumptions. Example: in our project, α_BC = 236 was stated as universal but secretly depended on P_max = 5M. When one approach required P_max = T, α_BC diverged as log²(T)/2. Three weeks of false confidence resulted. The fix: every numerical result tagged with `@requires(P_max=5M)` and `@invalidates(if P_max changes)`."

The concrete example makes the abstract rule land.

---

## 7. Universalization techniques

### 7.1 Vocabulary substitution

Make a table of vocabulary used in your project and equivalents in other fields:

| Your field | Other field #1 | Other field #2 | ... |
|---|---|---|---|

In our case: "Route" (math) ↔ "Design" (experimental science) ↔ "Paradigm" (qualitative) ↔ "Framework" (theory).

Once the table exists, a reader from any field can translate.

### 7.2 Strip domain-specific assumptions

For each lesson, ask: "Does this lesson mention specific theorems, datasets, instruments, or concepts?"

If yes, can the lesson be restated without them?

- **Before:** "When computing ⟨ρ_a, ρ_b⟩ inner products, use Vasyunin's formula for speed."
- **After:** "When performing numerical computations with known closed forms, prefer the closed form over numerical quadrature."

The stripped version applies to economics, biology, physics — anywhere numerical computation with analytical structure exists.

### 7.3 Add field-specific instantiations

After stripping, ADD back field-specific examples for multiple fields:

- "In mathematics: [example]"
- "In economics: [example]"
- "In biology: [example]"
- etc.

This way, a reader in any field sees the abstraction AND a concrete example from their own field.

### 7.4 Identify hard constraints that break the methodology

Not every methodology adapts cleanly. Document specific adaptations needed:

- Hard iteration limits (astronomy, clinical trials)
- Qualitative vs quantitative epistemology differences
- Human subjects / IRB considerations
- Industrial / commercial constraints (IP, trade secrets)

For each hard constraint, specify which parts of the methodology need modification.

---

## 8. Templates for the extraction process itself

### 8.1 Agent prompt for lesson extraction

```markdown
# Lesson Extraction — [PROJECT NAME / PHASE]

## Context
[1-paragraph summary of what the project is about and the phase being mined]

## Raw material
- [list of files to read]

## Task
Read all listed files. Extract methodological lessons — not domain knowledge.

## Categories to cover
1. Breakthrough moments
2. Error moments
3. Dead ends
4. Pivots
5. Sprint patterns
6. Collaboration patterns
7. Data quality events
8. Architecture evolution
9. Anti-patterns
10. Strategic wins
11. Decision gates
12. Retrospective synthesis

## For each lesson, provide:
- **What happened:** concrete example with date if possible
- **Why it mattered:** cost saved / value produced (quantified where possible)
- **Generalizable lesson:** stripped of domain specifics

## Scope
Target: 2000-3000 words, organized by category.
Focus on actionable insights, not narrative history.

## Output
Structured markdown with category headers and lesson entries.
```

### 8.2 Review prompt for a candidate playbook

```markdown
# Review — [PLAYBOOK DRAFT]

## Context
This is a draft playbook extracted from [PROJECT].
Intended to be applied to research in any scientific field.

## Please audit for:

1. **Over-generalization:** any lesson claimed as universal but actually specific?
2. **Under-generalization:** any lesson presented as specific but actually universal?
3. **Domain-vocabulary pollution:** any terms that won't make sense to non-domain readers?
4. **Missing principles:** any important lessons you'd expect but don't see?
5. **Internal consistency:** contradictory advice within the document?
6. **Practical feasibility:** any recommendation too expensive or unrealistic?

## Expected output
- Section-by-section assessment
- Specific rewrites for problematic claims
- Missing-principle candidates
- Binary: ready / needs revision
```

### 8.3 Template for the final playbook structure

```markdown
# [Methodology name]

**Date:** [date]
**Source:** distilled from [project]
**Purpose:** [transferable methodology for X]
**Applicability:** [list of fields]

## 0. Philosophy and core principles
[3-5 principles]

## 1. Architecture
[Repo, workflow, roles]

## 2. Roles and division of labor
[Multi-agent structure]

## 3. The right unit of work
[Artifacts not chats]

## 4. Problem formulation
[5-question gate]

## 5. Literature workflow
[5 layers]

## 6. Knowledge organization
[Epistemic status labels]

## 7. Route management
[A/B/C tagging]

## 8. Decision gates and stop criteria

## 9. Experimental design

## 10. Numerical / empirical evidence

## 11. Synthesis

## 12. Writing

## 13. Internal review

## 14. Venue discipline

## 15. AI roles

## 16. Inter-agent communication

## 17. Managing invalidated ideas

## 18. Reproducibility

## 19. Using AI without losing rigor

## 20. Phases of investigation (complete workflow)

## 21. Common pitfalls

## 22. Templates

## 23. Meta-lessons (10 principles that matter most)

## 24. Adaptation to other fields
[Tables and field-specific protocols]

## 25. What the methodology does NOT do

## 26. Minimum viable workflow

## 27. Final takeaway

## 28. Closing note

## Provenance
[Explicit list of sources integrated]
```

Adapt section count to project; 20-30 sections is typical.

---

## 9. Anti-patterns (what NOT to do when extracting)

### 9.1 Over-abstraction

**Symptom:** lessons so general they say nothing. "Be disciplined." "Think carefully."

**Fix:** concrete example required for EVERY lesson.

### 9.2 Narrative retelling

**Symptom:** the playbook becomes a history of the project instead of extracted lessons.

**Fix:** if you're writing dates and names, you're retelling not abstracting. Every paragraph should be phrased as a rule + example, not as story.

### 9.3 Single-perspective bias

**Symptom:** the playbook reflects only one person's experience.

**Fix:** integrate reviewer agent's independent observations. If no reviewer existed, delay integration until you have one.

### 9.4 Field lock-in

**Symptom:** the playbook uses only your domain's vocabulary and examples.

**Fix:** universalization pass (Step 7). Force yourself to read as a stranger from another field.

### 9.5 Premature integration

**Symptom:** extracting lessons while the project is still active. Creates retroactive justifications.

**Fix:** wait for a natural endpoint. Milestones, paper submissions, retraction completions.

### 9.6 Over-complete capture

**Symptom:** trying to record EVERY possible lesson. Document becomes unnavigable.

**Fix:** prioritize. Top 30-50 lessons. The rest are details that apprentices will discover themselves.

### 9.7 Single-source extraction

**Symptom:** only one person / agent does the extraction. Misses what they couldn't see.

**Fix:** mandatory multi-agent extraction. Even for the extraction process itself, apply the methodology's own multi-agent principle.

### 9.8 Skipping the universalization pass

**Symptom:** playbook is useful within your field but not transferable.

**Fix:** Step 7 is non-optional. Read as if you were in a different field. Add translation tables.

### 9.9 Treating the playbook as immutable

**Symptom:** playbook is extracted once and never updated.

**Fix:** playbooks are LIVING documents. Re-extraction after each subsequent project. Merge lessons from multiple projects over time.

---

## 10. Maintenance and evolution

### 10.1 Versioning

Playbooks should be versioned:

- v1.0: initial extraction from project 1
- v1.1: minor refinements based on project 2
- v2.0: major restructuring based on cross-field applications
- etc.

### 10.2 Feedback loops

After applying the playbook to a new project:

- Did any sections not apply?
- Did any missing principles emerge?
- Did any templates need modification for the new field?

Feed these back into the playbook as v(N+1).

### 10.3 Cross-project synthesis

After ≥ 3 projects have used the playbook:

- Which lessons held universally?
- Which needed significant adaptation?
- Which were specific to the original extraction project?

Refine the playbook to strengthen universal lessons and weaken project-specific framing.

### 10.4 Retirement of outdated principles

Some lessons become obsolete (new tools, changed conventions). Mark explicitly:

- "This principle applied when LLMs had small context windows (2022-2024). With 1M context (2026+), this adapts to..."

Don't silently remove. Mark as deprecated and explain.

---

## 11. Time budget for extraction

For a 6-week research project:

| Step | Time |
|---|---|
| 1. Inventory | 1-2 hours |
| 2. Surface survey | 4 hours |
| 3. Deep mining (delegated to agent) | 1-2 days clock time (mostly agent runtime) |
| 4. First synthesis | 4 hours |
| 5. Universality audit | 4 hours |
| 6. Integration | 1-2 days |
| 7. Universalization pass | 4 hours |
| **Total** | **3-4 days focused work** |

For smaller projects (1-2 weeks): scale down proportionally, but don't skip Step 7.

For larger programs (> 6 months): multiple extraction rounds, one per phase, then cross-phase synthesis.

---

## 12. Outputs of the extraction

A successful extraction produces at least:

1. **The playbook** (main deliverable, 20-30 sections, 1000-2000 lines)
2. **Provenance document** (what sources were integrated, in what order)
3. **Candidate-lessons raw file** (intermediate output, preserved for future reference)
4. **Translation tables** (vocabulary, tools, constraints per field)
5. **Templates** (reusable in future projects)

Store these together in a dedicated subdirectory (e.g., `methodology/`) that can be forked into new projects.

---

## 13. A concrete extraction recipe (copy-paste ready)

```bash
# 1. In your source project repo:
mkdir -p methodology/
cd methodology/

# 2. Inventory
git log --oneline > project-timeline.txt
ls notes/ > notes-inventory.txt
ls papers/ > papers-inventory.txt

# 3. Extract with agent (this is pseudo; actual invocation depends on your stack)
# Use the lesson extraction prompt template from §8.1
# Output: raw-lessons.md

# 4. Synthesize
# Write candidate-lessons.md by merging/refining raw-lessons.md

# 5. Universality audit
# Edit candidate-lessons.md, tagging each as universal / multi-field / specific

# 6. Integrate into final playbook
# Use template from §8.3 as starting structure
# Output: playbook-vN.N.md

# 7. Universalization pass
# Read playbook as a stranger from another field
# Add translation tables and field examples
# Output: playbook-vN.N.md (updated)

# 8. Commit
git add methodology/
git commit -m "Extract methodology playbook v1.0 from [project]"
```

---

## 14. Final principle

> **The methodology a project produces is often more valuable than the specific results.**

Most projects leave the methodology implicit. This is a waste of hard-won experience.

The extraction process documented here makes it explicit. Once explicit, it transfers. Once transferred, the next project starts further along.

If you do this across 3-5 projects, you build a meta-playbook that makes you ~2× more efficient at starting any new scientific investigation. This compounds across a career.

---

## 15. Meta-meta-note

This document itself was produced by applying the process it describes to the meta-question "how did we extract the main methodology playbook?"

Steps:
1. Inventory: the main methodology playbook + its sources
2. Surface survey: the process by which we created it
3. Deep mining: identify steps taken, patterns used
4. Synthesis: abstract the steps into a reusable pipeline
5. Universality audit: confirm it applies across fields
6. Integration: structure into 15 sections
7. Universalization pass: ensure the meta-process itself is field-agnostic

Result: you're reading it.

**This is the recursion:** the methodology applies to itself. Any good methodology must survive self-application.

---

## Provenance

- **Source:** the process of extracting the main methodology playbook (itself integrating Claude + Codex + CLAUDE_HISTORICO sources)
- **Generated:** 2026-04-17, concurrent with the main playbook's universalization pass
- **Reusability:** can be applied to any future project to produce its own methodology playbook
