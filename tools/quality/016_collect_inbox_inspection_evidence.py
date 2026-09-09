#!/usr/bin/env python3
"""Collect eight structure, auth-reference or SQL-boundary PT from a certified reactor.

NK-DAT-001; PG-D-119; QA-046/SSC-049; no declaration of DB cleanup completion.
Raw JUnit properties, stdout, stderr and ciphertext are never copied.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import xml.etree.ElementTree as ET


def validate_trace(out, manifest, certified):
    """Reject missing, redirected or stale links before declaring the slice certified."""
    linked = out / manifest["fullReactorManifest"]
    if (linked.resolve() != certified.resolve() or not linked.is_file()
            or hashlib.sha256(linked.read_bytes()).hexdigest() != manifest["fullReactorManifestSha256"]):
        raise ValueError("invalid full reactor evidence reference")
    for entry in manifest["files"]:
        item = out / entry["path"]
        if (not item.resolve().is_relative_to(out.resolve()) or not item.is_file()
                or hashlib.sha256(item.read_bytes()).hexdigest() != entry["sha256"]):
            raise ValueError("invalid local evidence reference")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run_id")
    selection = parser.add_mutually_exclusive_group()
    selection.add_argument("--authentication", action="store_true")
    selection.add_argument("--sql", action="store_true")
    selection.add_argument("--deletion-sql", action="store_true")
    selection.add_argument("--cleanup", action="store_true")
    selection.add_argument("--non-authentication", action="store_true")
    args = parser.parse_args()
    args.sql = args.sql or args.deletion_sql
    run = args.run_id
    if not re.fullmatch(r"PT-(ADM|WEB|SCN|MED)-[A-Za-z0-9-]+", run):
        raise SystemExit("invalid run ID")
    repo = Path(__file__).resolve().parents[2]
    certified = repo / "evidence/01_PT/008_NK-SCN-001/evidence/manifest.json"
    base = json.loads(certified.read_text())
    if base["runId"] != run or base["exitCode"] != 0:
        raise SystemExit("collect matching full reactor evidence first")
    subprocess.run(["git", "diff", "--exit-code", base["targetCommit"], "--",
                    "src", "pom.xml", "program/characterization", "tools/quality"],
                   cwd=repo, check=True, stdout=subprocess.DEVNULL)
    target = repo / "src/schubert-nk-api/target"
    subject = "AuthenticationInboxInspector" if args.authentication else "InboxResponseInspector"
    if args.sql:
        subject = "InboxInspectionBoundary"
    if args.deletion_sql:
        subject = "InboxDeletionBoundary"
    if args.cleanup:
        subject = "AuthenticationInboxCleanup"
    if args.non_authentication:
        subject = "NonAuthenticationInboxInspector"
    class_name = "dev.codex.schubert.nk.api.maintenance." + subject + "Test"
    suite = ET.parse(target / "surefire-reports" / ("TEST-" + class_name + ".xml")).getroot()
    names = ["validSuccessAndErrorProfiles", "headerAndMetadataMismatchesReject",
             "payloadEncodingAndSemanticFaultsReject", "cryptographicDamageAndMissingSnapshotReject",
             "exactLengthsAndTimestampPrecision", "nullContractsFailBeforeValidation",
             "concurrentInspectionsDoNotShareState", "databaseReferenceIsNotCertifiedByStructure"]
    if args.authentication:
        names = ["loginOriginalAndLaterAccountState", "logoutOwnerAndRevokedReference",
                 "deterministicErrorReferences", "missingAndInconsistentLoginRows",
                 "identityStructureAndNullContracts", "databaseFaultsAndTransactionOwnership",
                 "keyRotationAndClosedLifetimes", "concurrentReferencesDoNotCross"]
    if args.sql:
        names = ["roleAndFunctionCatalogAreClosed", "backupAndNullArgumentsFailClosed",
                 "expiryStateLayoutAndCursorAreExact", "candidateLocksLiveUntilCallerEndsTransaction",
                 "sessionAndBackupLocksProtectReadOnlyValidation", "noRoleCanEscalateInspectionPrivileges",
                 "advisoryContentionAndEmptyCandidatesAreExplicit", "appendOnlyMigrationAndUnverifiedCiphertextRemainDistinct"]
    if args.deletion_sql:
        names = ["exactDeleteRollbackAndReplay", "argumentsAndTransactionIdentity",
                 "retainedAndMalformedMetadata", "ciphertextAndMessageBinding", "backupAndLockGate",
                 "leastPrivilegeIsUnchanged", "concurrentRowsCannotChangeDuringValidation",
                 "migrationInventoryAndSqlScope"]
    if args.cleanup:
        names = ["validAuthRowsDeleteAtomically", "invalidRowsAreProtectedWithoutMutation",
                 "nullUnknownAndFactoryContracts", "ownsTransactionAndKeepsLocks",
                 "failuresRollbackAndRemainRedacted", "orderedCursorAndFixedRunReplay",
                 "concurrentAttemptsCannotDoubleDelete", "keysAndResultsNeverEscape"]
    if args.non_authentication:
        names = ["querySuccessAndPersistentErrors", "userMutationReferencesAndVersions",
                 "scenarioInlineAndFileReferences", "identityCryptoAndNullContracts",
                 "databaseFaultsAndNullRows", "preservesTransactionAndBusinessState",
                 "concurrentInspectionsDoNotCross", "boundaryDescriptorsAndFrozenSnapshots"]
    cases = suite.findall("testcase")
    if (len(cases) != 8 or int(suite.get("tests", "0")) != 8
            or any(int(suite.get(k, "0")) for k in ("failures", "errors", "skipped"))
            or {c.get("name") for c in cases} != set(names)
            or any(c.get("classname") != class_name or len(c) != 0 for c in cases)):
        raise SystemExit("missing, nonpassing or noncanonical tests")
    coverage_xml = ET.parse(target / "site/jacoco/jacoco.xml").getroot()
    coverage_names = {subject}
    if args.cleanup:
        coverage_names |= {"AuthenticationInboxCleanup$Candidate", "InspectionRun", "InspectionStep",
                           "InspectionStep$Outcome", "InboxMaintenanceException"}
    expected_classes = {"dev/codex/schubert/nk/api/maintenance/" + name for name in coverage_names}
    classes = [c for p in coverage_xml.findall("package") for c in p.findall("class")
               if c.get("name") in expected_classes]
    if not args.sql and {c.get("name") for c in classes} != expected_classes:
        raise SystemExit("missing inspection class coverage")
    counters = {}
    for cls in ([] if args.sql else classes):
        for counter in cls.findall("counter"):
            counts = counters.setdefault(counter.get("type"), {"missed": 0, "covered": 0})
            for key in ("missed", "covered"):
                counts[key] += int(counter.get(key))
    if not args.sql and (not {"LINE", "METHOD", "CLASS", "BRANCH"}.issubset(counters)
                        or any(v["missed"] or not v["covered"] for v in counters.values())):
        raise SystemExit("inspection coverage below 100 percent")
    folder = "authentication-inspection" if args.authentication else "inbox-inspection"
    if args.sql:
        folder = "inspection-sql"
    if args.deletion_sql:
        folder = "deletion-sql"
    if args.cleanup:
        folder = "authentication-cleanup"
    if args.non_authentication:
        folder = "non-authentication-inspection"
    out = repo / "evidence/01_PT/004_NK-DAT-001/evidence" / folder
    out.mkdir(parents=True, exist_ok=True)
    clean = ET.Element("testsuite", {k: suite.get(k) for k in
                                    ("name", "tests", "failures", "errors", "skipped", "time")})
    for case in cases:
        ET.SubElement(clean, "testcase", {k: case.get(k) for k in ("name", "classname", "time")})
    ET.indent(clean)
    ET.ElementTree(clean).write(out / "results.xml", encoding="UTF-8", xml_declaration=True)
    manifest = {
        "runId": run, "programId": "NK-DAT-001", "targetCommit": base["targetCommit"],
        "branch": subprocess.check_output(["git", "branch", "--show-current"], cwd=repo, text=True).strip(),
        "exitCode": 0,
        "scopeResult": "PASS_AUTH_REFERENCES_ONLY" if args.authentication else "PASS_STRUCTURE_ONLY",
        "programStatus": "IN_PROGRESS",
        "startedAt": Path("/tmp", run + ".started").read_text().strip(),
        "completedAt": Path("/tmp", run + ".completed").read_text().strip(),
        "fullReactorManifest": os.path.relpath(certified, out),
        "fullReactorManifestSha256": hashlib.sha256(certified.read_bytes()).hexdigest(),
        "environment": {"os": "Ubuntu 26.04.1 LTS x86_64", "java": "25.0.4+7", "maven": "3.9.12",
                        "junit": "5.13.4", "jacoco": "0.8.15", "spotbugsPlugin": "4.10.4.0"},
        "command": "JAVA_HOME=/home/mini/codex/project1/work/toolchain/jdk-25.0.4 ./mvnw -o -Dmaven.repo.local=/home/mini/codex/project1/work/toolchain/m2/repository --no-transfer-progress clean verify",
        "coverage": counters, "failed": 0, "errors": 0, "skipped": 0,
        "tests": {f"PT-DB-INBOX-{i:03d}": {"method": class_name + "#" + name,
                                         "result": "PASS"} for i, name in enumerate(names, 41 if args.non_authentication else 33 if args.cleanup else 25 if args.deletion_sql else 17 if args.sql else 9 if args.authentication else 1)},
        "fixture": "Runtime CSPRNG test-only keys; independent JCE/Deflater envelope and hand-written UI234/SS322/323 wire. No credential or ciphertext saved.",
        "oracle": ("005 PT specification: literal true/false and SQL Instant postconditions under UTC/JST; LOG error N17 zero accepted, spaces rejected; Login immutable refs and Logout owner/revocation. No production expected generation."
                   if args.authentication else "003 PT specification: literal true/false, unsigned N3 000/999 valid, nonnumeric/descending invalid. No production expected generation."),
        "remaining": "Complete DB references, expiry/backup/lock/deletion, least-privilege SQL and oneshot wiring NOT certified.",
        "related": ["QA-046", "UIC-006", "SSC-049", "BUG-014", "YKT-012", "BUG-075", "YKT-067", "BUG-076", "YKT-068"],
        "files": [{"path": "results.xml", "sha256": hashlib.sha256((out / "results.xml").read_bytes()).hexdigest()}]
    }
    if args.authentication:
        manifest["related"] += ["PG-D-120", "BUG-077", "BUG-078", "YKT-069"]
    if args.sql:
        manifest["scopeResult"] = "PASS_AUTH_CANDIDATE_SQL_ONLY"
        manifest["related"] += ["PG-D-121", "BUG-079", "BUG-080", "YKT-070", "YKT-071"]
        manifest["fixture"] = "Isolated PostgreSQL 18.6, synthetic rows, real restricted roles, controlled competing SQL row locks. No deployed DB or credential used. PT021 reuses independent JCE auth fixture."
        manifest["oracle"] = "007/008 specifications: literal IDs/counts/SQLSTATE/catalog, exact expiry/cursor, rollback/lock postconditions; BUG080 backup inserted after first snapshot must not authorize an unlocked candidate."
        manifest["coverage"] = {"kind": "SQL_BRANCH_MATRIX_NOT_JACOCO",
                                "proof": "008 result section3: all five procedural IF true/false and WHERE/null/expiry/role/lock boundaries mapped to executed PT017..024. Java coverage remains in full reactor; no invented Java class or SQL JaCoCo percentage.",
                                "functions": ["schubert.maintenance_next_auth_inbox(uuid,timestamptz,uuid)"],
                                "roles": ["schubert_inbox_inspector"]}
        manifest["sqlSources"] = [
            {"path": str(p.relative_to(repo)), "sha256": hashlib.sha256(p.read_bytes()).hexdigest()}
            for p in [repo / "src/schubert-nk-api/src/main/resources/db/migration/V008__auth_inbox_inspection_boundary.sql",
                      repo / "src/schubert-nk-api/src/main/resources/db/provisioning/001_roles.sql"]]
        manifest["remaining"] = "Atomic deletion/fixed-run replay, non-auth references and oneshot wiring NOT certified; V006 unchecked Inbox deletion remains BUG014."
    if args.deletion_sql:
        manifest["scopeResult"] = "PASS_AUTH_CONDITIONAL_DELETE_SQL_ONLY"
        manifest["related"] += ["PG-D-122", "BUG-081", "BUG-082", "BUG-083", "YKT-072", "YKT-073", "YKT-074"]
        manifest["oracle"] = "009/010 specifications: literal row counts/SQLSTATE/catalog; JDK SHA-256 of public synthetic bytes; fixed 168h/expiry microsecond boundaries, stale transaction/hash rejected; real row/advisory locks and backup snapshot race. SQL capability does NOT certify AES/reference validation."
        manifest["coverage"] = {"kind": "SQL_BRANCH_MATRIX_NOT_JACOCO",
                                "proof": "010 result: arguments, transaction, advisory, locked backup and DELETE outcome; full WHERE/NULL/expiry/reference/role matrix mapped to PT025..032. No invented SQL JaCoCo percentage.",
                                "functions": ["schubert.maintenance_delete_auth_inbox(uuid,timestamptz,uuid,text,bytea)"],
                                "roles": ["schubert_inbox_inspector"]}
        migration = repo / "src/schubert-nk-api/src/main/resources/db/migration/V009__conditional_auth_inbox_deletion.sql"
        manifest["sqlSources"] = [{"path": str(migration.relative_to(repo)),
                                  "sha256": hashlib.sha256(migration.read_bytes()).hexdigest()}]
        manifest["remaining"] = "Java owned validation-to-deletion composition, fixed-run replay, non-auth references and oneshot wiring NOT certified; V006 unchecked Inbox deletion remains BUG014."
    if args.cleanup:
        manifest["scopeResult"] = "PASS_AUTH_OWNED_INSPECTION_DELETE_SERVICE_ONLY"
        manifest["related"] += ["PG-D-122", "BUG-084", "YKT-075"]
        manifest["oracle"] = "011/012 PT: independent JCE/handwritten Login/Logout wire, literal SQL rows/state/cursor, current/previous keys, expected failure/rollback/uncertain commit/close, JDBC NULL and public-interface faults; 100 attempts permit ONLY observed 55P03, all other failures reject."
        manifest["classCoverage"] = {cls.get("name"): {c.get("type"): {"missed": int(c.get("missed")), "covered": int(c.get("covered"))}
                                     for c in cls.findall("counter")} for cls in classes}
        manifest["remaining"] = "Non-auth reference inspection/deletion, oneshot key/process composition, whole-run persistence and replacement of V006 unchecked Inbox cleanup NOT certified; BUG014 remains open."
    if args.non_authentication:
        manifest["scopeResult"] = "PASS_NON_AUTH_22_RESPONSE_REFERENCES_ONLY"
        manifest["related"] += ["PG-D-123"]
        manifest["fixture"] = "Independent UI233/234-236 TSV offsets and handwritten field values, JCE/Deflater envelope with runtime keys; isolated real PostgreSQL 18.6 and public JDBC failure probes; no raw wire/context/key saved."
        manifest["oracle"] = "013/014 PT: literal 22-layout x 12-code allowlist, User ID/version and Scenario ID/game SQL postconditions, descriptor boundaries, mutable query snapshots remain frozen, NULL/SQL faults protect, 100 concurrent expected booleans. No production expected generation."
        manifest["remaining"] = "Non-auth least-privilege SQL/locking/atomic deletion, Question/notification 7 responses, oneshot and V006 replacement NOT certified; BUG014 remains open."
    validate_trace(out, manifest, certified)
    (out / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
    (out / "checksums.sha256").write_text("".join(
        hashlib.sha256((out / name).read_bytes()).hexdigest() + "  " + name + "\n"
        for name in ("results.xml", "manifest.json")))
    print(json.dumps({"runId": run, "subject": subject, "inspectionTests": 8, "coverage": counters, "programComplete": False}))


if __name__ == "__main__":
    main()
