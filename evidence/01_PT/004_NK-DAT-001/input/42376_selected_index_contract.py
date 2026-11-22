"""Check named schema index declarations without opening a database connection."""

import json
import re
import sys
from collections import defaultdict
from pathlib import Path


DEFINITIONS = {
    "ix_auth_sessions_user_active": "ON schubert.auth_sessions (user_id, last_accessed_at DESC, id) WHERE revoked = false",
    "ix_questions_owner_active": "ON schubert.questions (owner_user_id, submitted_at DESC, id DESC) WHERE is_deleted = false",
    "ix_questions_admin_active": "ON schubert.questions (submitted_at DESC, id DESC) WHERE is_deleted = false",
    "ix_questions_deleted": "ON schubert.questions (deleted_at, id) WHERE is_deleted = true",
    "ix_questions_body_trgm": "ON schubert.questions USING gin (body public.gin_trgm_ops) WHERE is_deleted = false",
    "ix_app_logs_message_trgm": "ON schubert.app_logs USING gin (message public.gin_trgm_ops)",
    "ix_notifications_owner": "ON schubert.notifications (owner_user_id, state_changed_at DESC, id DESC)",
    "ix_mq_outbox_dispatch": "ON schubert.mq_outbox (status, next_attempt_at, id)",
    "ix_mq_outbox_lease": "ON schubert.mq_outbox (lease_until) WHERE status = 'PENDING'",
    "ix_web_receipt_references_question_id": "ON schubert_web_session.web_receipt_references (question_id)",
}
SUCCESS_OLD = "ON schubert.batch_runs (business_date, step) WHERE status = 'SUCCESS'"
SUCCESS_CURRENT = SUCCESS_OLD + " AND step NOT IN ('BACKUP_DB', 'BACKUP_CONFIG')"
SUCCESS_INDEX = "uq_batch_runs_business_step_success"
STATEMENT = re.compile(
    r"^\s*(CREATE(?:\s+UNIQUE)?|DROP|ALTER)\s+INDEX\s+"
    r"(?:[a-z_][a-z_0-9]*\.)?([a-z_][a-z_0-9]*)\b([^;]*);",
    re.IGNORECASE | re.MULTILINE,
)
TOKEN = re.compile(r"'(?:[^']|'')*'|[a-zA-Z_][a-zA-Z_0-9]*|[^\s]")


def sql_tokens(text: str) -> list[str]:
    return [token if token.startswith("'") else token.lower() for token in TOKEN.findall(text)]


def verify(sources: dict[str, str]) -> None:
    events = defaultdict(list)
    for name, text in sorted(sources.items()):
        version = name[:4]
        text = re.sub(r"(?m)^\s*--[^\n]*", "", text)
        for verb, index, definition in STATEMENT.findall(text):
            events[index.lower()].append((version, " ".join(verb.upper().split()), sql_tokens(definition)))

    for index, definition in DEFINITIONS.items():
        version = (
            "V005"
            if index.endswith("_trgm")
            else "V026"
            if index.startswith("ix_web_receipt_")
            else "V004"
        )
        assert events[index] == [(version, "CREATE", sql_tokens(definition))], index
    assert events[SUCCESS_INDEX] == [
        ("V004", "CREATE UNIQUE", sql_tokens(SUCCESS_OLD)),
        ("V017", "DROP", []),
        ("V017", "CREATE UNIQUE", sql_tokens(SUCCESS_CURRENT)),
    ], SUCCESS_INDEX


def main(migrations: Path) -> None:
    sources = {path.name: path.read_text(encoding="utf-8") for path in migrations.glob("V[0-9][0-9][0-9]__*.sql")}
    assert sorted(name[:4] for name in sources) == [f"V{number:03}" for number in range(1, 31)]
    verify(sources)

    mutations = [
        ("V004", "submitted_at DESC, id DESC", "submitted_at ASC, id DESC"),
        ("V004", "WHERE status = 'PENDING';", ";"),
        ("V005", "body public.gin_trgm_ops", "body"),
        ("V017", "step NOT IN ('BACKUP_DB', 'BACKUP_CONFIG')", "step NOT IN ('BACKUP_DB')"),
        ("V026", "web_receipt_references(question_id);", "web_receipt_references(receipt_id);"),
    ]
    for version, old, new in mutations:
        name = next(name for name in sources if name.startswith(version))
        altered = sources[name].replace(old, new, 1)
        assert altered != sources[name]
        try:
            verify(sources | {name: altered})
        except AssertionError:
            continue
        raise AssertionError(f"accepted the {version} index mutation")
    print(json.dumps({
        "testId": "PT-DB-005-STATIC-INDEX",
        "versions": 30,
        "namedIndexes": sorted([*DEFINITIONS, SUCCESS_INDEX]),
        "negativeMutationsRejected": len(mutations),
    }, indent=2))


if __name__ == "__main__":
    main(Path(sys.argv[1]))
