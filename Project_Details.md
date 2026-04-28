# Epistemic Dialectic Engine — Project Details

**Version:** 0.1 (Prototype)
**Last updated:** 28 April 2026
**Author:** Prof. Viktoria Dalko and Krishil Parmar

---

## 1. What This Project Is

The Epistemic Dialectic Engine (EDE) is an AI-powered advisory system designed for executive doctoral education. It reads a user's business dilemma, diagnoses the mindset the user is operating from, and then responds in a way that gently elevates their thinking toward a more sophisticated frame — while protecting them from the risks that come with that shift.

The core idea: most people, when facing a business decision, default to a narrow frame. Someone worried about layoffs thinks only about protecting their own job. Someone dealing with a difficult partner thinks only about getting a fair deal. These are valid starting points, but they limit the quality of the decision. The EDE identifies where the user is, decides where they could productively move to, and crafts advice that models the elevated frame rather than lecturing about it.

This is not a general-purpose chatbot. It is a structured pedagogical tool that follows a specific framework and set of rules.

---

## 2. The Mindset Elevation Framework

### 2.1. The Two Axes

The framework classifies every user query along two independent dimensions:

**Interaction Mode** — How the user relates to other parties in the situation:

| Level | Name            | What it sounds like                                                                                                                                                       |
| ----- | --------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1     | Transactional   | "What do I get out of this?" — Exchange-based thinking. The relationship has a defined endpoint. Trust is verified through contracts and deliverables.                   |
| 2     | Reciprocal      | "They helped me before, so I should help them now." — Long-term balance. Past favors are remembered. Fairness is measured across time, not within a single transaction.  |
| 3     | Collaborative   | "We need to figure this out together." — Joint creation. Neither party can produce the outcome alone. The output is something new that emerges from working together.    |
| 4     | Co-Evolutionary | "This changes how we both operate going forward." — Mutual transformation. Both parties and the broader system they work within are reshaped. Strategic, not altruistic. |

**Scope** — How wide the user's circle of concern extends:

| Level | Name       | What it sounds like                                                                                                                                                     |
| ----- | ---------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1     | Individual | "How do I protect myself?" — Focus is entirely on the user's own outcomes. Other people are mentioned only as instruments or obstacles.                                |
| 2     | Relational | "What does success look like for both of us?" — Named counterparties whose outcomes the user genuinely considers. My team, my partner, my co-founder.                  |
| 3     | Systemic   | "What precedent does this set for the whole company?" — The user evaluates decisions against effects on a broader system: a department, company, industry, or market.  |
| 4     | Universal  | "What kind of leader do I want to be remembered as?" — Principles, future generations, society-wide impact. Rare in operational queries and classified conservatively. |

### 2.2. The 16 Cells

Combining these two axes produces a 4x4 grid of 16 possible mindset states. Every user query is mapped to one cell. For example:

- **"How do I convince my startup to pay me a stipend?"** maps to **(Transactional, Individual)** — exchange-based thinking focused on the user's own outcome.
- **"My partner isn't pulling their weight. What should I do?"** maps to **(Transactional, Relational)** — still exchange-based thinking, but the user is engaging with a named counterparty as a person.
- **"How do I get our engineering and product teams to work as one unit?"** maps to **(Reciprocal, Systemic)** — the user is thinking about long-term organisational dynamics.

A critical principle: **cells are not personality types.** They describe the mindset expressed in a specific query at a specific moment. The same person can be in different cells across different questions. The cell is a diagnostic anchor for the current situation, not a label for the person.

### 2.3. How Cells Are Distinguished

When a query sits on the boundary between two cells, the system uses conservative disambiguation rules:

- **Transactional vs Reciprocal:** If the user expects any future interaction with the same person beyond the current task, it is Reciprocal. If the relationship ends at delivery, Transactional.
- **Reciprocal vs Collaborative:** If each party could in principle produce the output alone (just better together), Reciprocal. If the output is genuinely joint and neither party could produce it alone, Collaborative.
- **Individual vs Relational:** If the user mentions other people only to describe the situation but does not articulate what success looks like for them, Individual. If they articulate the other party's interests, Relational.
- **Systemic vs Universal:** If the system the user references is bounded (a company, an industry), Systemic. If unbounded (humanity, future generations, domain-spanning principles), Universal.

When in doubt, the system classifies into the lower cell. This is deliberate — over-classifying someone's mindset leads to advice that feels disconnected from where they actually are.

---

## 3. How the Engine Makes Decisions

The engine processes every query through four sequential stages. Each stage has a specific purpose and produces a specific output that feeds into the next.

### Stage 1: Classification — "Where is the user right now?"

The system reads the user's query and determines which of the 16 cells it best represents. It produces:

- **Top cell**: The single best-fit cell, e.g., (Transactional, Individual).
- **Confidence score**: 0.0 to 1.0. How certain the system is about the classification.
- **Justification**: A brief explanation of why this cell was chosen, grounded in the language of the query.
- **Context signals**: Whether the situation involves hostile behaviour, fraud, safety threats, power imbalances, or legal exposure (explained in Section 4).

**If confidence is below 60%**, the system does not proceed. Instead, it asks the user a targeted clarification question to gather more information. For example, if someone submits "Things have gotten weird with my co-founder," the system recognises this is too vague to classify and asks: "Can you tell me more about what 'weird' means in this context? Are you concerned about how work is getting done, the future of your partnership, or something else?"

### Stage 2: Policy Decision — "Where should the user move to?"

Once the current cell is known, the system consults a policy table to decide what to do. There are four possible decisions:

| Decision             | When it applies                               | What it means                                                                                                                                                                  |
| -------------------- | --------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **Elevate**    | The default for most queries                  | Move the user one step up on both axes. If they are at (Transactional, Individual), the target becomes (Reciprocal, Relational).                                               |
| **Stay**       | When elevation would be harmful               | Hold the user at their current cell. This is critical for hostile, fraudulent, or safety-critical contexts (see Section 4).                                                    |
| **Deepen**     | When the user is already at the highest level | The user is already at (Co-Evolutionary, Universal) or another high cell. Instead of trying to elevate further, the system reinforces and stress-tests their current position. |
| **Horizontal** | Reserved for Phase 2                          | Move on one axis but not the other. Not yet implemented — requires observed cohort data to know which transitions are most valuable.                                          |

**The default elevation rule is "+1 on each axis, capped at level 4."** This is a placeholder. It is deliberately simple because the correct policy depends on observing how real cohort members use the system, which has not happened yet. Refining this rule is one of the most important Phase 2 tasks.

### Stage 3: Response Generation — "Craft the advice"

Armed with the current cell, target cell, and decision type, the system generates a response. The response is not just good advice — it is advice that **models the target cell's way of thinking.** If the target is (Reciprocal, Relational), the response frames the situation in terms of ongoing relationships and mutual interests, not because it tells the user to think that way, but because it demonstrates what thinking that way looks like in practice.

Key constraints on the response:

1. **No moralising.** The system never preaches or lectures. It elevates by demonstrating practical wisdom, not by telling the user they should be more ethical or empathetic.
2. **No therapeutic hedging.** Phrases like "It's important to remember that..." or "You might want to consider..." are explicitly prohibited. The advice is direct and actionable.
3. **Pre-Mortem analysis is mandatory.** Every response includes a structured risk assessment (see Section 5).

For **deepen** decisions (when the user is already at a high cell), the response takes a different approach: it acknowledges the user's sophisticated framing, sharpens the strongest version of their argument, and stress-tests their position against scenarios where key assumptions change. It does not try to push them higher.

### Stage 4: Self-Critique — "Did the response actually do what it was supposed to?"

Before delivering the response to the user, the system evaluates its own output against three criteria:

1. **Target cell match** (minimum 70%): Does the response's framing, vocabulary, and reasoning actually match the target cell's definition? Or did it drift back to the user's original cell?
2. **Pre-Mortem completeness** (minimum 80%): Did the response adequately address the downside, upside, and pivot scenarios?
3. **Instruction adherence** (minimum 75%): Did the response avoid moralising, hedging, and therapeutic language?

If all three scores meet their thresholds, the response is delivered. If not, the system revises and tries again, up to two refinement loops. This self-critique mechanism is one of the most important quality safeguards — without it, the system frequently drifts toward generic advice that sounds good but does not actually express the target cell.

---

## 4. When Elevation Would Be Harmful: Stay Overrides

The framework assumes that elevation is generally beneficial. But there are contexts where encouraging someone to think more collaboratively or more broadly would actively harm them.

**Example:** A user discovers their business partner has been secretly setting up a competing company using their shared client list. The system classifies this as (Transactional, Relational). The default policy would elevate them toward (Reciprocal, Systemic) — encouraging them to think about long-term relationship dynamics and broader system effects. But this is exactly wrong. The user is dealing with a breach of duty. Encouraging collaborative thinking toward someone who is actively betraying them would compromise their position.

The system detects three categories of context that trigger a stay override:

### 4.1. Hostile Counterparty / Power Asymmetry

The other party has demonstrably acted against the user's interests, is exploiting trust, or holds structural power over the user and is using it. Examples: a supplier threatening to pull inventory before peak season, an acquiring CEO privately planning to fire the user's team while publicly promising job safety.

**Why stay:** Elevating to Reciprocal or Collaborative thinking exposes the user to further exploitation. The advice must protect the user's position first.

### 4.2. Fraud or Breach of Duty

The situation describes financial misconduct, theft of intellectual property, embezzlement, misuse of shared resources, or evidence-gathering for enforcement. Examples: a CFO creating fictitious vendor accounts, a partner diverting profits into a personal venture, a manager awarding contracts to a relative's company at inflated rates.

**Why stay:** Enforcement contexts require Transactional rigour. Encouraging collaborative framing would compromise the user's evidentiary position and weaken their legal standing.

### 4.3. Safety-Critical

Physical safety, psychological safety from abuse or harassment, or imminent personal danger. Examples: a supervisor screaming at the user and blocking the door, a colleague following the user to their car, pressure to falsify safety inspection reports.

**Why stay:** Safety considerations override all elevation logic. The system holds position and, where appropriate, points toward professional resources.

### How Detection Works

The system uses a two-layer detection approach:

1. **Semantic detection:** The AI classifier reads the situation and identifies context signals — hostile behaviour, fraud indicators, safety threats, power imbalances, legal exposure — and reports its confidence for each. If any signal is detected with 70%+ confidence, the stay override fires.
2. **Keyword fallback:** If the semantic detection misses something, a set of explicit keywords acts as a safety net ("embezzlement," "harassment," "competing company," "threatened," etc.).

This dual approach was built because relying on AI judgment alone missed cases where the fraud or hostility was described in indirect language, while relying on keywords alone missed cases where the situation was clearly hostile but used no flagged words.

---

## 5. The Pre-Mortem: Built-In Risk Assessment

Every response includes a structured Pre-Mortem analysis with three tests:

| Test               | Question it answers                                                                                         | When it gets priority                                                                                                                               |
| ------------------ | ----------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Downside** | If the counterparty acts in bad faith, does the elevated advice expose the user dangerously?                | Priority for users at low cells (levels 1-2), where exposure risk is highest and the user has the least experience operating at the elevated level. |
| **Upside**   | If the situation scales favourably, does the advice create a flywheel — a self-reinforcing positive cycle? | Priority for users at mid-high cells (level 3), where the user has enough sophistication to capitalise on momentum.                                 |
| **Pivot**    | If core assumptions change (deadline, budget, key stakeholder), does the logic still hold?                  | Priority for users at the highest cells (level 4) and for deepen decisions, where stress-testing the position is more valuable than elevating it.   |

All three tests are always performed. The priority designation determines which test receives the most depth and detail.

The Pre-Mortem exists because elevation carries risk. Moving someone from Transactional to Reciprocal thinking means they start extending trust and considering long-term dynamics. If the other party is acting in bad faith, that extension of trust can be exploited. The Downside test catches this. Moving someone from Individual to Systemic scope means they start considering organisational precedent. If the situation is genuinely personal and the system effects are minimal, that broader framing wastes their attention. The Pivot test catches this.

---

## 6. What the User Experiences

The user sees a chat interface. They type a business dilemma or decision scenario. After a brief processing period, they receive:

1. **A direct, actionable response** that models the target mindset without lecturing about it.
2. **A "Diagnostics" panel** (expandable) showing:
   - The classified cell and confidence score
   - The target cell and elevation decision
   - The Pre-Mortem analysis
   - The self-critique scores

If their query is too short or ambiguous, they receive a clarification question instead of advice.

The diagnostics panel is visible for transparency and research purposes but is not the primary output. The response itself is the pedagogical intervention.

---

## 7. Key Design Decisions and Their Rationale

### 7.1. "Show, don't tell" — Why the system never preaches

Early prototypes generated responses that explicitly told users they should think more broadly or collaboratively. Testing revealed these responses felt patronising and were ignored. The current design models the target mindset in the structure and framing of the advice itself. A user at (Transactional, Individual) who asks about protecting their job receives advice framed in Reciprocal/Relational terms — advice about what their manager's pain points are and how to become the person who solves them — without ever being told "you should think about your manager's perspective."

### 7.2. Conservative classification — Why we classify into the lower cell when uncertain

Over-classifying a user's mindset (placing them higher than they actually are) leads to advice that feels disconnected and abstract. Under-classifying (placing them lower) leads to advice that meets them where they are and gently elevates. The cost of under-classification is a slightly smaller elevation step; the cost of over-classification is a response the user disengages from entirely. The asymmetry of these costs justifies the conservative default.

### 7.3. Self-critique loop — Why the system evaluates its own output

Without the self-critique stage, the response generator frequently drifts toward generic advice that sounds sophisticated but does not actually express the target cell. The most common failure mode is "moralising drift" — the system starts lecturing about ethics and empathy instead of demonstrating practical wisdom. The instruction adherence score specifically penalises this pattern. The critique loop catches and corrects these failures before the user sees the response.

### 7.4. Stay overrides — Why the system sometimes refuses to elevate

This was not part of the original framework design but emerged as a critical requirement during stress testing. The framework's assumption that elevation is always desirable breaks down in adversarial, fraudulent, and safety-critical contexts. A system that elevates a fraud victim toward collaborative thinking with their fraudster is actively harmful. The stay override mechanism ensures the system's first obligation is to protect the user, not to follow the elevation policy.

### 7.5. Dual detection (semantic + keyword) — Why context signals are detected twice

Purely keyword-based detection misses situations described in indirect language ("My partner has been quietly routing revenue to his personal consulting firm" contains no fraud keywords). Purely AI-based detection is probabilistic and sometimes fails to flag situations that are obviously hostile to a human reader. The dual approach uses AI judgment as the primary detector and keyword matching as a safety net.

### 7.6. Simple elevation policy — Why "+1 on each axis" and not something more sophisticated

The current policy is intentionally simple because the correct policy depends on data that does not yet exist: observed patterns from a real cohort of doctoral students using the system. Designing a complex policy based on intuition would be both fragile and hard to validate. The simple rule establishes a testable baseline. Phase 2 should replace it with empirically-informed transitions once labelled cohort data is available.

---

## 8. Configurable Parameters

The system's behaviour is controlled by a small number of parameters, all editable without touching any code:

### Classification Thresholds

- **Minimum confidence to proceed:** 60%. Below this, the system asks for clarification instead of generating advice.
- **Minimum confidence for stay decision:** 75%. Context signals must be detected with at least this confidence to trigger a stay override.

### Critique Thresholds

- **Target cell match:** 70%. The response must score at least this well on expressing the target cell's framing.
- **Pre-Mortem completeness:** 80%. The risk assessment must be at least this thorough.
- **Instruction adherence:** 75%. The response must avoid moralising, hedging, and therapeutic language at least this well.
- **Maximum refinement loops:** 2. If the response fails critique twice, the best available version is delivered.

### Elevation Policy

- **Default rule:** Elevate one step on each axis, capped at level 4.
- **Pre-Mortem priority by source level:** Downside for levels 1-2, Upside for level 3, Pivot for level 4.
- **Stay overrides:** Three categories (hostile negotiation, fraud/enforcement, safety-critical), each with keyword triggers and semantic signal triggers.

---

## 9. What the System Does NOT Do

To set appropriate expectations, it is worth being explicit about the boundaries:

1. **It does not assess personality.** It classifies the mindset expressed in a specific query, not the person's general disposition.
2. **It does not replace professional advice.** In fraud, legal, or safety contexts, it holds position and may suggest professional consultation. It does not provide legal or therapeutic guidance.
3. **It does not learn from individual users over time** (in v0.1). Each query is classified independently. Session memory and longitudinal tracking are Phase 2 features.
4. **It does not guarantee correct classification.** The AI classifier is probabilistic. It will sometimes place queries in the wrong cell, especially for boundary cases. The confidence score and clarification mechanism mitigate but do not eliminate this.
5. **It does not handle multi-cell queries.** A user who is operating at one level on substance ("What should I do about this industry-wide problem?") and a different level on process ("How do I protect my own reputation?") cannot be accurately represented by a single cell. This is a known framework limitation, not a technical bug.

---

## 10. Open Questions Requiring Input

These are decisions that cannot be made by engineering alone. They require framework-level judgment:

### Question 1: Cell boundary signals

The current disambiguation rules (Section 2.3) are engineering best-guesses. Which rules would you phrase differently? Which boundary calls do you disagree with?

### Question 2: Are the stay override categories complete?

Three categories are currently implemented: hostile negotiation, fraud/enforcement, and safety-critical. Are there other contexts where elevation would be harmful?

### Question 3: Pre-Mortem test overlap

The Downside Test ("what if the counterparty acts in bad faith?") and the Pivot Test ("what if core assumptions change?") overlap in practice. Should they be consolidated, or is there a sharp distinction worth preserving?

### Question 4: Policy refinement path

The current elevation policy is "+1 on each axis." To refine it empirically, we need a labelled dataset of 200-300 business dilemmas, each tagged with the correct cell by an expert rater. This dataset would reveal which transitions are most common and which produce the best outcomes, replacing intuition with evidence.

---

## 11. How to Evaluate Whether the System Is Working

The system's effectiveness can be assessed at three levels:

### Level 1: Does the classification match expert judgment?

Given a set of queries with expert-assigned cells, what percentage does the system classify correctly? Current target: 75%+ agreement on the primary cell.

### Level 2: Does the response actually model the target cell?

This is what the self-critique score measures. Current threshold: 70% target cell match. Can be validated by having an expert read the response and independently rate whether it expresses the target cell's framing.

### Level 3: Does the user's thinking actually shift?

This is the hardest and most important question. It requires comparing user behaviour before and after interacting with the system — a research design question, not an engineering one. The logging infrastructure is in place to support this analysis when the time comes.

---

## 12. Summary of the Processing Flow

```
User submits a business dilemma
        |
        v
[Stage 1: Classification]
  - Which of the 16 cells does this query express?
  - How confident are we? (If < 60%, ask for clarification and stop)
  - Are there hostile/fraud/safety signals?
        |
        v
[Stage 2: Policy Decision]
  - Should we elevate, stay, or deepen?
  - If context signals detected --> stay (protect the user)
  - If already at highest cell --> deepen (reinforce, don't elevate)
  - Otherwise --> elevate one step on each axis
        |
        v
[Stage 3: Response Generation]
  - Craft advice that models the target cell's way of thinking
  - Include Pre-Mortem risk assessment (downside, upside, pivot)
  - No moralising, no hedging, no therapeutic language
        |
        v
[Stage 4: Self-Critique]
  - Does the response match the target cell? (>= 70%)
  - Is the Pre-Mortem complete? (>= 80%)
  - Does it avoid moralising? (>= 75%)
  - If all pass --> deliver to user
  - If any fail --> revise and try again (up to 2 times)
        |
        v
User receives actionable, elevated advice
```
