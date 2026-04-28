# Cell Definitions (v0.1)

> Authoritative source for the 16 mindset cells in the Mindset Elevation Framework. This file is loaded into Layer 1, 3, and 4 prompts at runtime. Edits to this file must be reflected in README.md Appendix B and vice versa. The pipeline performs a hash check at startup to enforce consistency.

Owner: Krishil Parmar (engineering)
Last updated: 2026-04-28

## Appendix B: Operational Cell Definitions (v0.1)

This appendix is the canonical source for what each cell means in operational terms. It is loaded into the Layer 1, 3, and 4 prompts at runtime. A copy lives at** **`docs/framework/cell_definitions.md` and the pipeline performs a hash check at startup to guarantee that what the model sees and what is documented here are identical. This document is v0.1 and should be co-refined before Phase 2.

### Reading the cells

A cell is written** **`(Interaction, Scope)` where Interaction is one of {Transactional, Reciprocal, Collaborative, Co-Evolutionary} and Scope is one of {Individual, Relational, Systemic, Universal}. Cells are not personality types. They are the mindset expressed in a specific query at a specific moment. The same person can be in different cells across queries, and the framework predicts that the cell expressed in a query is the appropriate diagnostic anchor, not the person's general disposition.

### Interaction Mode signals

**Transactional** is signaled by language of exchange, timing, and discrete completion. The user describes the situation as a deal, a trade, a one-off. They use phrases like "what do I get," "what's in it for me," "after this is done." The relationship in the query has a defined endpoint. Trust is not assumed; verification mechanisms (contracts, deliverables, conditions) are emphasized.

**Reciprocal** is signaled by language of long-term balance and ongoing exchange. The user describes the situation as a relationship with memory: past favors are remembered, future favors are expected, fairness is measured across time rather than within a single transaction. Phrases like "I'll owe them," "they helped me before," "next time," "build the relationship." Trust is assumed at the level of the relationship but accounted for at the level of specific exchanges.

**Collaborative** is signaled by language of co-creation and joint output. The user frames the situation as a problem that cannot be solved by one party acting alone. Phrases like "we need to figure this out together," "neither of us can do this without the other," "combining our strengths," "1+1=3." The output of the interaction is something that did not exist before either party engaged. Trust is operational, not just affective.

**Co-Evolutionary** is signaled by language of mutual transformation and systemic change. The user frames the situation as one where both parties (and the broader system they operate in) will be different at the end. Phrases like "this changes how we both work," "we are growing together," "the way our industry approaches this is shifting," "this becomes the new norm." The interaction is not just about producing outputs; it is about reshaping the conditions of future interaction. Note: this is not "altruistic." Co-Evolutionary mindset is calibrated and strategic; it just operates at a different level of abstraction.

### Scope signals

**Individual** is signaled by exclusive focus on the user's own outcomes. Stakeholders are mentioned only as instruments or obstacles. Phrases like "how do I," "I need," "what should I do," "for me." Decisions are evaluated against personal gain, safety, or achievement.

**Relational** is signaled by inclusion of named immediate counterparties whose outcomes the user genuinely cares about. Phrases like "my team," "my partner," "my co-founder," "my manager." The user can articulate what success looks like for the other party as well as themselves.

**Systemic** is signaled by reference to broader contexts the user is part of: a company, an industry, a market, a profession, an organizational culture. The user evaluates the decision against effects on this larger system. Phrases like "the team's morale," "our company culture," "the precedent this sets," "the industry standard," "what this means for the whole department."

**Universal** is signaled by reference to durations, populations, or principles that exceed the user's direct sphere. Phrases like "future generations," "the planet," "society," "the kind of leader I want to be remembered as," "fundamental fairness." Universal scope is rare in operational business queries and should be classified with caution; users frequently invoke universal language rhetorically while reasoning at Systemic or Relational scope.

### Disambiguation rules

These are the boundary calls Layer 1 will need to make. They are deliberately conservative; when in doubt, classify the lower cell.

**Transactional vs Reciprocal:** if the user mentions any expectation of future interaction with the same counterparty beyond completing the current item, classify Reciprocal. If the relationship ends at delivery, classify Transactional.

**Reciprocal vs Collaborative:** if the user describes the output as something each party could in principle produce alone (just better together), classify Reciprocal. If the user describes the output as genuinely joint (neither party could produce it alone in any form), classify Collaborative.

**Collaborative vs Co-Evolutionary:** if the user describes the interaction as producing a one-time output that ends when delivered, classify Collaborative. If the user describes the interaction as changing how either party will operate in future analogous situations, classify Co-Evolutionary.

**Individual vs Relational:** if the user mentions counterparties only to describe the situation but does not articulate their interests or outcomes, classify Individual. If the user articulates what success looks like for the counterparty, classify Relational.

**Relational vs Systemic:** if the user's concerns extend only to named individuals they directly interact with, classify Relational. If the user references effects on people beyond their direct sphere (the broader team, the company, the market), classify Systemic.

**Systemic vs Universal:** if the system the user references is bounded (a company, an industry), classify Systemic. If the system is unbounded (humanity, future generations, principles that apply across domains), classify Universal. Universal classification requires explicit textual evidence; do not infer Universal scope from rhetorical flourishes.

### Worked examples

The three anchor queries are calibration anchors. They are reproduced here with their v0.1 classifications for use in Layer 1 prompt few-shot examples.

**Query 1:** "I am doing an internship at a startup for last 4 months without pay. they really like my work and I have build major production grade components for them. how do I convince them for a paid role with atleast 2000 aud in stipend"

Classification:** **`(Transactional, Individual)`. Justification: query frames the situation as an exchange ("convince them for a paid role"), focuses on the user's own outcome (the stipend), and treats the startup as a counterparty rather than a partner whose interests are articulated.

**Query 2:** "How do I protect my job during layoffs?"

Classification:** **`(Transactional, Individual)`. Justification: defensive framing centered on self-preservation. No mention of team, manager, or company outcomes as objects of concern. The bot's elevated response correctly moved the user toward Reciprocal/Relational thinking.

**Query 3:** "My partner isn't pulling their weight on this project. What should I do?"

Classification:** **`(Transactional, Relational)`. Justification: the user names an immediate counterparty ("my partner") and engages with them as a person, but the framing is still about getting fair output rather than co-creating. The elevated response correctly moved toward Collaborative.

### Confidence calibration guidance for Layer 1

The classifier should report confidence below 0.6 (and trigger the clarification flow) when:

* The query is too short to extract meaningful signals (under roughly 15 words).
* The query mixes signals from non-adjacent cells (e.g., Transactional language with Universal scope claims).
* The query is ambiguous between two adjacent cells and the disambiguation rules above do not resolve it.

The classifier should report confidence above 0.85 when:

* Multiple independent signals point to the same cell.
* Linguistic markers are unambiguous.
* The query closely matches a worked example.
