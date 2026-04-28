CREATE TABLE IF NOT EXISTS transactions (
    id TEXT PRIMARY KEY,
    session_id TEXT NOT NULL,
    user_id TEXT,
    timestamp_utc TEXT NOT NULL,
    user_query TEXT NOT NULL,
    final_response TEXT NOT NULL,
    pipeline_version TEXT NOT NULL,
    completed_successfully INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS classifications (
    transaction_id TEXT PRIMARY KEY REFERENCES transactions(id),
    top_cell TEXT NOT NULL,
    confidence REAL NOT NULL,
    cell_probabilities_json TEXT NOT NULL,
    justification TEXT,
    clarification_needed INTEGER NOT NULL,
    provider TEXT NOT NULL,
    model TEXT NOT NULL,
    latency_ms INTEGER
);

CREATE TABLE IF NOT EXISTS elevation_decisions (
    transaction_id TEXT PRIMARY KEY REFERENCES transactions(id),
    current_cell TEXT NOT NULL,
    target_cell TEXT NOT NULL,
    decision_type TEXT NOT NULL,
    rationale TEXT,
    pre_mortem_priority TEXT,
    policy_version TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS drafts (
    id TEXT PRIMARY KEY,
    transaction_id TEXT REFERENCES transactions(id),
    iteration INTEGER NOT NULL,
    response_text TEXT NOT NULL,
    target_cell_expressed TEXT NOT NULL,
    pre_mortem_json TEXT NOT NULL,
    safeguards_json TEXT,
    provider TEXT NOT NULL,
    model TEXT NOT NULL,
    latency_ms INTEGER
);

CREATE TABLE IF NOT EXISTS critiques (
    id TEXT PRIMARY KEY,
    draft_id TEXT REFERENCES drafts(id),
    passed INTEGER NOT NULL,
    target_cell_match_score REAL,
    pre_mortem_completeness_score REAL,
    instruction_adherence_score REAL,
    issues_json TEXT,
    provider TEXT NOT NULL,
    model TEXT NOT NULL,
    latency_ms INTEGER
);

CREATE TABLE IF NOT EXISTS expert_ratings (
    id TEXT PRIMARY KEY,
    transaction_id TEXT REFERENCES transactions(id),
    rater_id TEXT NOT NULL,
    rated_cell TEXT NOT NULL,
    notes TEXT,
    timestamp_utc TEXT NOT NULL
);
