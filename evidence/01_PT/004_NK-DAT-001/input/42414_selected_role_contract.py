"""Check declared grants for three constrained database roles without a DB connection."""

import json
import re
import sys
from pathlib import Path


BACKUP = "schubert_backup"
OPS = "schubert_ops_ro"
RECEIPTS = "schubert_web_session.web_receipt_references"
ACL_STATEMENT = re.compile(r"^\s*((?:grant|revoke)\s+[^;]+);", re.IGNORECASE | re.MULTILINE)


def normalize(statement: str) -> str:
    return re.sub(r"\s*,\s*", ",", " ".join(statement.lower().split()))


def verify(sources: dict[str, str]) -> None:
    all_clauses = [
        (path[:4], normalize(clause))
        for path, text in sorted(sources.items())
        for clause in ACL_STATEMENT.findall(re.sub(r"(?m)^\s*--[^\n]*", "", text))
    ]

    base_usage = "grant usage on schema schubert to schubert_app,schubert_batch,schubert_backup,schubert_ops_ro"

    def grants(role: str) -> list[tuple[str, str]]:
        result = []
        for version, clause in all_clauses:
            if not clause.startswith("grant ") or " to " not in clause:
                continue
            recipients = clause.rsplit(" to ", 1)[1]
            if role in re.findall(r"[a-z_]+", recipients):
                result.append((version, clause))
        return result

    assert grants(BACKUP) == [
        ("V005", base_usage),
        ("V005", "grant usage on schema schubert_web_session to schubert_web_session,schubert_backup"),
        ("V005", "grant usage on schema schubert_meta to schubert_backup"),
        ("V005", "grant select on all tables in schema schubert,schubert_web_session,schubert_meta to schubert_backup"),
        ("V005", "grant usage,select on all sequences in schema schubert,schubert_web_session to schubert_backup"),
        ("V005", "grant select on tables to schubert_backup"),
        ("V005", "grant select on tables to schubert_backup"),
        ("V012", "grant select on schubert.inbox_inspection_progress to schubert_backup"),
        ("V014", "grant select on schubert.log_cleanup_progress to schubert_backup"),
        ("V026", f"grant select on {RECEIPTS} to schubert_backup"),
    ], "backup role direct grants"
    assert grants(OPS) == [
        ("V005", base_usage),
        ("V005", "grant select on schubert.v_ops_component_counts,schubert.v_ops_recent_events to schubert_ops_ro"),
    ], "operations role direct grants"
    receipts = [(version, clause) for version, clause in all_clauses if f" on {RECEIPTS} " in clause]
    assert receipts == [
        ("V026", f"revoke all on {RECEIPTS} from public,schubert_app,schubert_batch,schubert_web_session"),
        ("V026", f"grant select,insert,delete on {RECEIPTS} to schubert_web_session"),
        ("V026", f"grant select on {RECEIPTS} to schubert_backup"),
    ], "receipt table grants"


def main(migrations: Path) -> None:
    sources = {
        path.name: path.read_text(encoding="utf-8")
        for path in migrations.glob("V[0-9][0-9][0-9]__*.sql")
    }
    assert sorted(name[:4] for name in sources) == [f"V{number:03}" for number in range(1, 31)]
    verify(sources)
    receipts = next(name for name in sources if name.startswith("V026"))
    last = next(name for name in sources if name.startswith("V030"))
    alternatives = [
        (receipts, sources[receipts].replace("FROM PUBLIC,schubert_app", "FROM schubert_app", 1)),
        (receipts, sources[receipts].replace("GRANT SELECT,INSERT,DELETE", "GRANT SELECT,INSERT,UPDATE,DELETE", 1)),
        (last, sources[last] + "\nGRANT DELETE ON schubert.batch_runs TO schubert_backup;\n"),
        (last, sources[last] + "\nGRANT nk_owner TO schubert_backup;\n"),
        (last, sources[last] + "\nGRANT SELECT ON schubert.app_logs TO schubert_ops_ro;\n"),
    ]
    for name, changed in alternatives:
        assert changed != sources[name]
        try:
            verify(sources | {name: changed})
        except AssertionError:
            continue
        raise AssertionError(f"accepted an invalid permission in {name}")
    print(json.dumps({
        "testId": "PT-DB-012-STATIC-ROLE",
        "migrations": 30,
        "backupDirectGrants": 10,
        "opsDirectGrants": 2,
        "receiptClauses": 3,
        "rejectedMutations": 5,
    }, indent=2))


if __name__ == "__main__":
    main(Path(sys.argv[1]))
