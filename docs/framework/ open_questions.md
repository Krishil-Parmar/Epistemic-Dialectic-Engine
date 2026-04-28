# Open Framework Questions

These are refinements to the Mindset Elevation Framework that surfaced during
operationalization. Each one is a real engineering blocker, not a
philosophical aside.

## Question 1: Cell boundary signals

What linguistic, structural, or topical signals distinguish Reciprocal
from Collaborative? Relational from Systemic? Appendix B of the README
contains my v0.1 attempt at operational disambiguation rules. These need
your review and refinement before the classifier can be evaluated.

Specific request: please review the disambiguation rules in
README.md Appendix B and mark any that you would phrase differently or
that you disagree with.

## Question 2: The "stay" case

The framework as documented assumes elevation is always desirable. In
hostile negotiations, fraud investigations, and enforcement contexts,
elevation toward Co-Evolutionary thinking would be harmful. I have
implemented stay overrides for three categories (hostile negotiation,
fraud or enforcement, safety-critical). Please review whether this
captures the cases you want, and whether there are others.

## Question 3: Pre-Mortem test redundancy

The Downside Test and the Pivot Test overlap operationally. Both ask
"what if conditions change adversely." Should they be consolidated, or
do you see a sharp distinction worth preserving in the implementation?

## Question 4: Combinatorial coverage

16 cells x stay/elevate/horizontal/deepen decisions x 3 Pre-Mortem
priorities is a large policy surface. The v0.1 policy uses a simple
default rule (elevate one step on each axis). To make the system
empirically defensible, we need to know which transitions are most
common in your cohort's actual queries. The labeled dataset proposed
in the demo email is the path to answering this empirically rather
than by intuition.
