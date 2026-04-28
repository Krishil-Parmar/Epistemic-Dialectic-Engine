import json
import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

SCHEMA_PATH = Path(__file__).parent / "schema.sql"
DEFAULT_DB_PATH = os.environ.get("EDE_DB_PATH", "./data/ede.sqlite")


class TransactionLogger:
    def __init__(self, db_path: str = DEFAULT_DB_PATH):
        self.db_path = db_path
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(db_path)
        self.init_db()

    def init_db(self):
        self.conn.executescript(SCHEMA_PATH.read_text())
        self.conn.commit()

    def log_transaction(
        self,
        transaction_id: str,
        session_id: str,
        user_query: str,
        final_response: str,
        completed_successfully: bool,
        user_id: str | None = None,
        pipeline_version: str = "0.1.0",
    ):
        self.conn.execute(
            "INSERT INTO transactions (id, session_id, user_id, timestamp_utc, user_query, final_response, pipeline_version, completed_successfully) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (
                transaction_id,
                session_id,
                user_id,
                datetime.now(timezone.utc).isoformat(),
                user_query,
                final_response,
                pipeline_version,
                int(completed_successfully),
            ),
        )
        self.conn.commit()

    def log_classification(
        self,
        transaction_id: str,
        top_cell: str,
        confidence: float,
        cell_probabilities: dict,
        justification: str,
        clarification_needed: bool,
        provider: str,
        model: str,
        latency_ms: int | None = None,
    ):
        self.conn.execute(
            "INSERT INTO classifications (transaction_id, top_cell, confidence, cell_probabilities_json, justification, clarification_needed, provider, model, latency_ms) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                transaction_id,
                top_cell,
                confidence,
                json.dumps(cell_probabilities),
                justification,
                int(clarification_needed),
                provider,
                model,
                latency_ms,
            ),
        )
        self.conn.commit()

    def log_elevation(
        self,
        transaction_id: str,
        current_cell: str,
        target_cell: str,
        decision_type: str,
        rationale: str,
        pre_mortem_priority: str,
        policy_version: str = "0.1.0",
    ):
        self.conn.execute(
            "INSERT INTO elevation_decisions (transaction_id, current_cell, target_cell, decision_type, rationale, pre_mortem_priority, policy_version) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (
                transaction_id,
                current_cell,
                target_cell,
                decision_type,
                rationale,
                pre_mortem_priority,
                policy_version,
            ),
        )
        self.conn.commit()

    def log_draft(
        self,
        transaction_id: str,
        iteration: int,
        response_text: str,
        target_cell_expressed: str,
        pre_mortem_json: str,
        safeguards_json: str,
        provider: str,
        model: str,
        latency_ms: int | None = None,
    ) -> str:
        draft_id = str(uuid4())
        self.conn.execute(
            "INSERT INTO drafts (id, transaction_id, iteration, response_text, target_cell_expressed, pre_mortem_json, safeguards_json, provider, model, latency_ms) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                draft_id,
                transaction_id,
                iteration,
                response_text,
                target_cell_expressed,
                pre_mortem_json,
                safeguards_json,
                provider,
                model,
                latency_ms,
            ),
        )
        self.conn.commit()
        return draft_id

    def log_critique(
        self,
        draft_id: str,
        passed: bool,
        target_cell_match_score: float,
        pre_mortem_completeness_score: float,
        instruction_adherence_score: float,
        issues: list[str],
        provider: str,
        model: str,
        latency_ms: int | None = None,
    ):
        self.conn.execute(
            "INSERT INTO critiques (id, draft_id, passed, target_cell_match_score, pre_mortem_completeness_score, instruction_adherence_score, issues_json, provider, model, latency_ms) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                str(uuid4()),
                draft_id,
                int(passed),
                target_cell_match_score,
                pre_mortem_completeness_score,
                instruction_adherence_score,
                json.dumps(issues),
                provider,
                model,
                latency_ms,
            ),
        )
        self.conn.commit()

    def close(self):
        self.conn.close()
