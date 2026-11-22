"""Check the V019 summary declaration against SS331 §3.13 and SS332 without a DB."""

import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path


OBJECT_NAME = "maintenance_read_inbox_summary"
MIGRATIONS = "src/schubert-nk-api/src/main/resources/db/migration"
SUMMARY_DECLARATION = f"schubert.{OBJECT_NAME}(uuid,timestamptz)"


def normalized(sql: str) -> str:
    lines = (line.partition("--")[0] for line in sql.splitlines())
    return " ".join(" ".join(lines).lower().split())


def summary_contract(sql: str) -> dict[str, bool]:
    body = normalized(sql)
    _, implementation, after = body.split("$function$")
    projection = (
        "return query select progress.inspected_count,progress.deleted_count, "
        "progress.protected_count,progress.completed_at is not null;"
    )
    return {
        "row_shape_and_order": (
            "returns table(inspected_count bigint,deleted_count bigint,"
            "protected_count bigint,complete boolean)"
        )
        in body
        and projection in implementation,
        "argument_boundary": (
            "p_run_id is null or p_cutoff is null or not pg_catalog.isfinite(p_cutoff)"
            in implementation
            and "p_cutoff < timestamptz '0001-01-01 00:00:00+00'" in implementation
            and "p_cutoff >= timestamptz '10000-01-01 00:00:00+00'" in implementation
            and "errcode='22023'" in implementation
        ),
        "fixed_self_lock_observation": all(
            clause in implementation
            for clause in (
                "pg_catalog.pg_locks",
                "pid=pg_catalog.pg_backend_pid()",
                "datname=pg_catalog.current_database()",
                "classid=0 and objid=71419602 and objsubid=1",
                "mode='exclusivelock' and granted",
                "errcode='55000'",
            )
        )
        and "pg_advisory_" not in implementation,
        "read_only_fresh_identity": all(
            clause in implementation
            for clause in (
                "from schubert.inbox_inspection_progress p where p.run_id=p_run_id;",
                "if not found then return; end if;",
                "if progress.cutoff<>p_cutoff then",
            )
        )
        and implementation.count("from schubert.inbox_inspection_progress") == 1
        and not re.search(r"\b(insert|update|delete|execute|perform)\b", implementation),
        "sealed_declared_scope": all(
            clause in body
            for clause in (
                "set role nk_owner;",
                "security definer set search_path = pg_catalog, schubert set timezone = 'utc'",
                f"revoke all on function {SUMMARY_DECLARATION} from public;",
            )
        )
        and after.strip().endswith("reset role;")
        and re.findall(r"\bgrant (.*?);", after)
        == [f"execute on function {SUMMARY_DECLARATION} to schubert_batch"],
    }


def reference_contract(sql: str) -> dict[str, bool]:
    declaration = normalized(sql)
    _, separator, tail = declaration.partition(
        "create or replace function schubert.maintenance_delete_inbox("
    )
    if not separator:
        raise ValueError("expected the final declared Inbox reference boundary")
    signature, body, _ = tail.split("$function$")
    return {
        "consistent_reference_types": all(
            clause in body
            for clause in (
                "i.result_ref_type = 'none' and i.result_ref_id is null and i.result_ref_uuid is null",
                "i.result_ref_type = 'auth_session' and i.result_ref_id is null",
                "i.result_ref_type = 'user'",
                "i.result_ref_type = 'scenario_file'",
                "i.result_ref_type = 'question'",
                "i.result_ref_type = 'job'",
            )
        ),
        "terminal_snapshot_predicates": all(
            clause in body
            for clause in (
                "i.processing_state in ('completed', 'error')",
                "sha256(i.response_body_encrypted) = p_expected_response_sha256",
                "i.request_version = '001' and i.response_version = '001'",
                "and i.expires_at < p_cutoff;",
            )
        )
        and "returns boolean" in signature
        and body.strip().endswith("return found; end"),
    }


def check_candidate(source: str) -> dict:
    roster = subprocess.check_output(
        ["git", "ls-tree", "-r", "--name-only", source, "--", MIGRATIONS], text=True
    ).splitlines()
    inputs = {
        Path(path).name: subprocess.check_output(["git", "show", f"{source}:{path}"])
        for path in roster
    }
    summary_name = "V019__parent_inbox_inspection_summary.sql"
    summary = inputs[summary_name].decode("utf-8")
    conditions = summary_contract(summary)
    if not all(conditions.values()):
        raise ValueError(f"V019 declaration incomplete: {conditions}")
    summary_mentions = [
        name for name, data in inputs.items() if OBJECT_NAME in normalized(data.decode("utf-8"))
    ]
    if summary_mentions != [summary_name]:
        raise ValueError("V019 summary appears in other migrations")
    reference_versions = [
        name
        for name, data in inputs.items()
        if re.search(
            r"create (?:or replace )?function schubert\.maintenance_delete_inbox\(",
            normalized(data.decode("utf-8")),
        )
    ]
    ref_name = "V016__question_mutation_inbox_references.sql"
    if reference_versions[-1:] != [ref_name]:
        raise ValueError("the final reference declaration does not match the V016 design")
    reference = inputs[ref_name].decode("utf-8")
    reference_conditions = reference_contract(reference)
    if not all(reference_conditions.values()):
        raise ValueError(f"V016 reference declaration incomplete: {reference_conditions}")
    progress_name = "V012__durable_inbox_inspection_progress.sql"
    progress = normalized(inputs[progress_name].decode("utf-8"))
    for clause in (
        "protected_count = inspected_count - deleted_count",
        "completed_at timestamptz",
        "primary key",
    ):
        if clause not in progress:
            raise ValueError("summary storage constraint was not found")
    mutations = {
        "row_shape_and_order": ("progress.protected_count,progress.completed_at", "progress.completed_at"),
        "argument_boundary": (" OR NOT pg_catalog.isfinite(p_cutoff)", ""),
        "fixed_self_lock_observation": (" AND pid=pg_catalog.pg_backend_pid()", ""),
        "read_only_fresh_identity": ("IF NOT FOUND THEN RETURN; END IF;", ""),
        "sealed_declared_scope": ("TO schubert_batch;", "TO synthetic_other_recipient;"),
    }
    for criterion, (old, new) in mutations.items():
        if summary.count(old) != 1 or summary_contract(summary.replace(old, new))[criterion]:
            raise ValueError(f"declaration self-test did not reject {criterion}")
    return {
        "source": source,
        "summaryCriteria": conditions,
        "referenceCriteria": reference_conditions,
        "referenceDefinitionFiles": reference_versions,
        "negativeSelfChecks": list(mutations),
        "migrationFileCount": len(inputs),
        "summaryDefinitionFiles": summary_mentions,
        "verifiedSourceSHA256": {
            name: hashlib.sha256(inputs[name]).hexdigest()
            for name in (summary_name, progress_name, ref_name)
        },
        "databaseOperations": 0,
    }


if __name__ == "__main__":
    print(json.dumps(check_candidate(sys.argv[1]), ensure_ascii=False, indent=2))
