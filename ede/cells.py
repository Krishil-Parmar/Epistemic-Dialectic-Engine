from enum import IntEnum


class Interaction(IntEnum):
    TRANSACTIONAL = 1
    RECIPROCAL = 2
    COLLABORATIVE = 3
    CO_EVOLUTIONARY = 4

    @classmethod
    def from_string(cls, s: str) -> "Interaction":
        return cls[s.upper().replace("-", "_")]


class Scope(IntEnum):
    INDIVIDUAL = 1
    RELATIONAL = 2
    SYSTEMIC = 3
    UNIVERSAL = 4

    @classmethod
    def from_string(cls, s: str) -> "Scope":
        return cls[s.upper().replace("-", "_")]


type Cell = tuple[Interaction, Scope]


def cell_from_strings(interaction: str, scope: str) -> Cell:
    return (Interaction.from_string(interaction), Scope.from_string(scope))


INTERACTION_LABELS = {
    Interaction.TRANSACTIONAL: "Transactional",
    Interaction.RECIPROCAL: "Reciprocal",
    Interaction.COLLABORATIVE: "Collaborative",
    Interaction.CO_EVOLUTIONARY: "Co-Evolutionary",
}

SCOPE_LABELS = {
    Scope.INDIVIDUAL: "Individual",
    Scope.RELATIONAL: "Relational",
    Scope.SYSTEMIC: "Systemic",
    Scope.UNIVERSAL: "Universal",
}


def cell_label(cell: Cell) -> str:
    return f"({INTERACTION_LABELS[cell[0]]}, {SCOPE_LABELS[cell[1]]})"
