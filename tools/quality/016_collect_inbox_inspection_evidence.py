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
    selection.add_argument("--full-sql", action="store_true")
    selection.add_argument("--full-cleanup", action="store_true")
    selection.add_argument("--outbox-only", action="store_true")
    selection.add_argument("--progress-sql", action="store_true")
    selection.add_argument("--progress-service", action="store_true")
    selection.add_argument("--cleanup-safety", action="store_true")
    selection.add_argument("--run-executor", action="store_true")
    selection.add_argument("--aes-credential", action="store_true")
    selection.add_argument("--credential-access", action="store_true")
    selection.add_argument("--inode-security", action="store_true")
    selection.add_argument("--credential-loader", action="store_true")
    args = parser.parse_args()
    args.sql = args.sql or args.deletion_sql or args.full_sql or args.outbox_only or args.progress_sql or args.cleanup_safety
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
    target = repo / ("src/schubert-nk-storage/target" if args.inode_security else "src/schubert-nk-api/target")
    subject = "AuthenticationInboxInspector" if args.authentication else "InboxResponseInspector"
    if args.sql:
        subject = "InboxInspectionBoundary"
    if args.deletion_sql:
        subject = "InboxDeletionBoundary"
    if args.cleanup or args.full_cleanup:
        subject = "InboxCleanup"
    if args.non_authentication:
        subject = "NonAuthenticationInboxInspector"
    if args.full_sql:
        subject = "InboxMaintenanceBoundary"
    if args.outbox_only:
        subject = "OutboxCleanupBoundary"
    if args.progress_sql:
        subject = "InboxInspectionProgressBoundary"
    if args.progress_service:
        subject = "InboxCleanup"
    if args.cleanup_safety:
        subject = "CleanupSafetyBoundary"
    if args.run_executor:
        subject = "InspectionRunExecutor"
    if args.aes_credential:
        subject = "InspectorAesCredential"
    if args.credential_access:
        subject = "InspectorCredentialAccess"
    if args.inode_security:
        subject = "LinuxInodeSecurity"
    if args.credential_loader:
        subject = "InspectorCredentialLoader"
    package = "dev.codex.schubert.nk.storage." if args.inode_security else "dev.codex.schubert.nk.api.maintenance."
    if args.credential_loader:
        package = "dev.codex.schubert.nk.api.file."
    class_name = package + subject + "Test"
    if args.cleanup:
        class_name = "dev.codex.schubert.nk.api.maintenance.AuthenticationInboxCleanupTest"
    if args.full_cleanup:
        class_name = "dev.codex.schubert.nk.api.maintenance.InboxCleanupNonAuthenticationTest"
    if args.progress_service:
        class_name = "dev.codex.schubert.nk.api.maintenance.InboxInspectionProgressTest"
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
    if args.full_sql:
        names = ["catalogAndColumnCapabilities", "candidateOrderStateAndUnknownRoutes",
                 "canonicalRoutesReferencesAndTokens", "exactRetentionCutoffAndReplay",
                 "argumentsHashAndTransactionBinding", "referencesStayLockedUntilTransactionEnds",
                 "backupGateAndSnapshotRace", "migrationAndExistingAuthenticationRemainCompatible"]
    if args.full_cleanup:
        names = ["validQueriesAndMutationsDeleteAtomically", "userAndScenarioReferencesStayProtected",
                 "canonicalMetadataAndTokensAreRequired", "mixedCursorsNeverSkipUnverifiedRows",
                 "transactionFaultsRollbackAndResume", "concurrentMixedRequestsStayIsolated",
                 "leastPrivilegeAndKeyLifetimes", "outcomesAndSideEffectsRemainBounded"]
    if args.outbox_only:
        names = ["inboxRowsAreNeverTouched", "outboxBoundariesAndSharedLimit",
                 "invalidArgumentsAndFixedReasons", "backupStatesAndDatesAreLocked",
                 "competingMaintenanceNeverDeletes", "backupSnapshotCannotBeReplaced",
                 "currentFunctionsAndRolesCloseBypasses", "migrationAndLegacyOraclesRemainExplicit"]
    if args.progress_sql:
        names = ["newAndResumedRunKeepOneCutoff", "outcomesAdvanceOnlyMatchingState",
                 "deletionAndCheckpointCommitTogether", "invalidInputsAndConstraintsReject",
                 "backupAndConcurrentRunsStayLocked", "completedProgressRetentionIsBounded",
                 "rolesAndFixedFunctionsCannotEscalate", "migrationAndInventoryAreAppendOnly"]
    if args.progress_service:
        names = ["mixedRowsPersistExactProgress", "boundedChunksResumeAndSkipCompleted",
                 "progressAndBoundaryContracts", "checkpointFaultsRollbackDeletion",
                 "uncertainCommitReloadsDurableCounts", "ownsLocksWithoutSavepoints",
                 "concurrentAttemptsNeverDoubleCount", "runIdentityKeysAndResultsStayPrivate"]
    cases = suite.findall("testcase")
    if args.run_executor:
        names = ["emptyAndCompletedRunsSucceed", "protectedRowsEndWithWarning",
                 "moreThanOneChunkCompletes", "deadlineAndClockBoundaries",
                 "interruptionRemainsVisible", "storageFailurePreservesLastConfirmedOnly",
                 "resultAndNullContracts", "failuresDoNotLeakOrBecomeSuccess"]
    if args.cleanup_safety:
        names = ["backupMatrixAndLegacyCounterexample", "backupLocksAndSnapshotRace",
                 "invalidInputsAndTimezone", "rolesInventoryAndImmutableHistory",
                 "rollbackAndRowLocks", "businessAndSessionBoundaries",
                 "logRetentionAndHold", "batchCompletionRetention"]
    if args.aes_credential:
        names = ["validKeyAndVersionBounds", "envelopeLengthAndMagic",
                 "versionAndLineBoundaries", "base64AndKeySize",
                 "consumedInputAndCopiedKeysDoNotAlias", "closeIsIdempotentAndRedacted",
                 "concurrentCopiesAndCloseStayConsistent", "nullAndInvalidInputsNeverEscape"]
    if args.credential_access:
        names = ["rootAclFileAndDirectory", "ownedReadonlyFallback", "inodeTypeAndMode",
                 "linkSizeAndUidBounds", "everyAclBitAndShape", "nullAndInputOwnership",
                 "concurrentPoliciesDoNotCross", "errorsAreFixedAndNonMutating"]
    if args.inode_security:
        names = ["actualAclAndUid", "filesystemFlagsAndFailures", "aclReturnAndErrnoBoundaries",
                 "canonicalCapabilityAndBounds", "platformAndSymbolAdmission",
                 "heldInodeSurvivesReplacement", "concurrentReadsStayIndependent", "interfacesAndRedaction"]
    if args.credential_loader:
        names = ["validAllIds", "optionalMissingOnlyBeforeOpen", "rootAdmissionBeforeRead",
                 "inodeTypeBeforeNativeOrContent", "fileAttributesAndNulls", "boundedReadsAndEof",
                 "postReadChangesReject", "ioAndCloseFailures", "heldEntryAndRootReplacement",
                 "constructorAndEnumContracts", "ownedBuffersAreCleared", "concurrentReadsAndRedaction"]
    if (len(cases) != len(names) or int(suite.get("tests", "0")) != len(names)
            or any(int(suite.get(k, "0")) for k in ("failures", "errors", "skipped"))
            or {c.get("name") for c in cases} != set(names)
            or any(c.get("classname") != class_name or len(c) != 0 for c in cases)):
        raise SystemExit("missing, nonpassing or noncanonical tests")
    coverage_xml = ET.parse(target / "site/jacoco/jacoco.xml").getroot()
    coverage_names = {subject}
    if args.cleanup or args.full_cleanup or args.progress_service:
        coverage_names |= {"InboxCleanup$Candidate", "InspectionRun", "InspectionStep",
                           "InspectionStep$Outcome", "InboxMaintenanceException"}
    if args.progress_service:
        coverage_names |= {"InboxCleanup$LoadedProgress", "InspectionProgress"}
    if args.run_executor:
        coverage_names |= {"InspectionExecution", "InspectionExecution$Status"}
    if args.credential_loader:
        coverage_names |= {"AesCredentialFile", "InspectorCredentialException",
                           "InspectorCredentialLoader$NioIo", "InspectorCredentialLoader$Metadata",
                           "InspectorCredentialLoader$Snapshot"}
    expected_classes = {package.replace(".", "/") + name for name in coverage_names}
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
    if args.full_sql:
        folder = "full-inbox-sql"
    if args.full_cleanup:
        folder = "full-inbox-cleanup"
    if args.outbox_only:
        folder = "outbox-only-cleanup"
    if args.progress_sql:
        folder = "inbox-progress-sql"
    if args.progress_service:
        folder = "inbox-progress-service"
    if args.cleanup_safety:
        folder = "cleanup-safety"
    if args.run_executor:
        folder = "inbox-run-executor"
    if args.aes_credential:
        folder = "inbox-aes-credential"
    if args.credential_access:
        folder = "credential-access"
    if args.inode_security:
        folder = "inode-security"
    if args.credential_loader:
        folder = "credential-loader"
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
                        "junit": "5.13.4", "jacoco": "0.8.15", "spotbugsPlugin": "4.10.4.0",
                        "postgresql": "18.6", "jdbc": "42.7.13", "flyway": "13.4.0"},
        "command": "JAVA_HOME=/home/mini/codex/project1/work/toolchain/jdk-25.0.4 ./mvnw -o -Dmaven.repo.local=/home/mini/codex/project1/work/toolchain/m2/repository --no-transfer-progress clean verify",
        "coverage": counters, "failed": 0, "errors": 0, "skipped": 0,
        "tests": {f"PT-DB-INBOX-{i:03d}": {"method": class_name + "#" + name,
                                         "result": "PASS"} for i, name in enumerate(names, 129 if args.credential_loader else 121 if args.inode_security else 113 if args.credential_access else 105 if args.aes_credential else 97 if args.run_executor else 89 if args.cleanup_safety else 81 if args.progress_service else 73 if args.progress_sql else 65 if args.outbox_only else 57 if args.full_cleanup else 49 if args.full_sql else 41 if args.non_authentication else 33 if args.cleanup else 25 if args.deletion_sql else 17 if args.sql else 9 if args.authentication else 1)},
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
        manifest["related"] += ["PG-D-122", "PG-D-125", "BUG-084", "YKT-075", "BUG-089", "YKT-080"]
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
    if args.full_sql:
        manifest["scopeResult"] = "PASS_FULL_CANDIDATE_24_ROUTE_SQL_ONLY"
        manifest["related"] += ["PG-D-124", "BUG-087", "BUG-088", "YKT-078", "YKT-079"]
        manifest["fixture"] = "Isolated PostgreSQL 18.6/real roles; public synthetic invalid ciphertext30 and independent JDK SHA-256. Isolated admin rollback-only constraint removal tests SQL defense in depth, never deployed data."
        manifest["oracle"] = "015/016 PT: literal 24 routes x 6 reference kinds, 24h/168h boundaries, private helper/minimal column grants/42501, fixed run and UUID scan, unsupported rows protected, all five batch states, 55P03 lock and controlled backup snapshot races, independent frozen V001..009 hashes."
        manifest["coverage"] = {"kind": "SQL_BRANCH_MATRIX_NOT_JACOCO",
                                "proof": "016 result maps all helper/candidate/delete procedural IF/ELSIF and WHERE/null/role/reference/token/expiry boundaries to PT049..056. Java coverage remains separately enforced; no invented SQL percentage.",
                                "functions": ["schubert.maintenance_lock_inbox_backup(uuid,timestamptz)",
                                              "schubert.maintenance_next_inbox(uuid,timestamptz,uuid)",
                                              "schubert.maintenance_delete_inbox(uuid,timestamptz,uuid,text,bytea)"],
                                "roles": ["schubert_inbox_inspector"]}
        migration = repo / "src/schubert-nk-api/src/main/resources/db/migration/V010__full_inbox_scan_and_restricted_deletion.sql"
        manifest["sqlSources"] = [{"path": str(migration.relative_to(repo)), "sha256": hashlib.sha256(migration.read_bytes()).hexdigest()}]
        manifest["remaining"] = "Java full-scan owned inspection/delete composition, Question/notification references, whole-run/oneshot and V006 replacement NOT certified; BUG014 remains open."
    if args.full_cleanup:
        manifest["scopeResult"] = "PASS_OWNED_NON_AUTH_22_RESPONSE_DELETE_SERVICE_ONLY"
        manifest["related"] += ["PG-D-125", "BUG-089", "BUG-090", "YKT-080", "YKT-081"]
        manifest["fixture"] = "Independent UI TSV wire builder/JCE snapshot, runtime keys, real PostgreSQL 18.6 and dedicated role, task-local public JDBC probes; no raw wire/context/token/cipher/credential saved."
        manifest["oracle"] = "017/018 PT: 22 routes success/persistent-error, ULK0200 and SCN I/F, literal row/ref/cursor/24h/168h postconditions, fault selectors must match real SQL, rollback/uncertain commit, 100 attempts in three completed waves (33/33/34) ensure progress; only observed55P03 is expected contention."
        manifest["classCoverage"] = {cls.get("name"): {c.get("type"): {"missed": int(c.get("missed")), "covered": int(c.get("covered"))}
                                     for c in cls.findall("counter")} for cls in classes}
        manifest["remaining"] = "Question/notification reference validation, whole-run persistence, oneshot key/process composition and V006 replacement NOT certified; BUG014 remains open."
    if args.outbox_only:
        manifest["scopeResult"] = "PASS_BATCH_OUTBOX_ONLY_INBOX_BYPASS_REMOVED"
        manifest["related"] = ["QA-046", "UIC-006", "SSC-049", "PG-D-126", "BUG-014", "YKT-012", "BUG-091", "YKT-082"]
        manifest["fixture"] = "Isolated PostgreSQL 18.6/real restricted roles; synthetic 31 routes plus unknown x 3 states; NULL/public invalid ciphertext and missing refs only; no credentials/raw wire/dump saved."
        manifest["oracle"] = "019/020 PT: all Inbox rows and columns unchanged, literal Outbox 168h/lease microsecond boundaries, combined chunk limit and rollback, all five backup states/JST date/locked snapshot race, public/direct/inspector bypass denied, V001..011 inventory and frozen V001..010 hashes."
        manifest["coverage"] = {"kind": "SQL_BRANCH_MATRIX_NOT_JACOCO",
                                "proof": "020 maps every argument/gate/exception/DELETE/WHERE/limit/role branch to PT065..072; full Java four-counter gate remains separate.",
                                "functions": ["schubert.maintenance_cleanup_message_stores(uuid,timestamptz,integer)"],
                                "roles": ["schubert_batch"]}
        migration = repo / "src/schubert-nk-api/src/main/resources/db/migration/V011__batch_outbox_only_cleanup.sql"
        manifest["sqlSources"] = [{"path": str(migration.relative_to(repo)), "sha256": hashlib.sha256(migration.read_bytes()).hexdigest()}]
    if args.progress_sql:
        manifest["scopeResult"] = "PASS_DURABLE_INSPECTION_CHECKPOINT_SQL_ONLY"
        manifest["related"] = ["QA-046", "UIC-006", "SSC-049", "PG-D-127", "BUG-014", "YKT-012"]
        manifest["fixture"] = "Isolated PostgreSQL 18.6/real roles; synthetic run/backup/Inbox; no real credentials or dump. SQL capability permits only trusted private transaction composition, not an AES certificate."
        manifest["oracle"] = "021/022 PT: fixed run cutoff/cursor/counts and UUID byte ordering; atomic delete/checkpoint commit/rollback, invalid arguments/constraints/overflow, role/table boundaries with backup SELECT only, 400-day retention and investigating-run protection; independent V001..012 inventory and frozen V001..011 hashes."
        manifest["coverage"] = {"kind": "SQL_BRANCH_MATRIX_NOT_JACOCO",
                                "proof": "022 maps open/record/purge procedural and SQL conditions to PT073..080. Java composition is a separate gate.",
                                "functions": ["schubert.maintenance_open_inbox_inspection(uuid,timestamptz)",
                                              "schubert.maintenance_record_inbox_inspection(uuid,timestamptz,uuid,bigint,uuid,text,text)",
                                              "schubert.maintenance_cleanup_inbox_progress(uuid,timestamptz,integer)"],
                                "roles": ["schubert_inbox_inspector", "schubert_batch", "schubert_backup"]}
        migration = repo / "src/schubert-nk-api/src/main/resources/db/migration/V012__durable_inbox_inspection_progress.sql"
        manifest["sqlSources"] = [{"path": str(migration.relative_to(repo)), "sha256": hashlib.sha256(migration.read_bytes()).hexdigest()}]
    if args.progress_service:
        manifest["scopeResult"] = "PASS_DURABLE_OWNED_INSPECTION_AND_BOUNDED_RESUME_SERVICE_ONLY"
        manifest["related"] = ["QA-046", "UIC-006", "SSC-049", "PG-D-128", "BUG-014", "YKT-012"]
        manifest["fixture"] = "Independent UI TSV and handbuilt auth wire/JCE snapshots with runtime keys; isolated PostgreSQL and restricted role; matched public JDBC fault probes; 1001 deliberately unverifiable rows for exact 1000-step cutoff. No raw wire/keys/context/dump saved."
        manifest["oracle"] = "023/024 PT: literal progress/cursor/counts and SQL row postconditions; mixed auth/query/User/SCN/delete/protect/unknown outcomes, chunk1000 then resume1001+END, complete short-circuit, NULL/invalid DB projections, open/save/health/resource/uncertain commit failures, no SAVEPOINT and continuous locks, 100 calls in completed33/33/34 waves permit only observed55P03."
        manifest["classCoverage"] = {cls.get("name"): {c.get("type"): {"missed": int(c.get("missed")), "covered": int(c.get("covered"))}
                                     for c in cls.findall("counter")} for cls in classes}
    if args.cleanup_safety:
        manifest["scopeResult"] = "PASS_CLEANUP_BACKUP_AND_RETENTION_SQL_BOUNDARIES"
        manifest["related"] = ["PG-D-129", "SSC-050", "BUG-092", "BUG-093", "YKT-083", "YKT-084", "BUG-014", "YKT-012"]
        manifest["fixture"] = "Isolated PostgreSQL 18.6, real roles and locks, literal public timestamps/IDs and rollback-only historical V006 definitions; no deployed data or credentials."
        manifest["oracle"] = "025/026: all7 backup/finite/limit/role gates, exact snapshot race and locks; literal90-day and completion400-day microsecond boundaries, hold/investigating/current-run protection; rollback/exception/legacy counterexamples; non-regression notification/question/session conditions. No production expected generation."
        manifest["coverage"] = {"kind": "SQL_BRANCH_MATRIX_NOT_JACOCO",
                                "proof": "026 maps the7 shared gates and5 replaced cleanup SQL branch/WHERE/null/retention/role conditions to PT089..096; full Java gate remains separately enforced.",
                                "functions": ["schubert.maintenance_cleanup_" + name + "(uuid,timestamptz,integer)" for name in
                                              ["notifications", "questions", "sessions", "logs", "batch_runs", "message_stores", "inbox_progress"]],
                                "roles": ["schubert_batch"]}
        manifest["sqlSources"] = [{"path": str(p.relative_to(repo)), "sha256": hashlib.sha256(p.read_bytes()).hexdigest()}
                                  for p in sorted((repo / "src/schubert-nk-api/src/main/resources/db/migration").glob("V01[0-3]__*.sql"))]
    if args.run_executor:
        manifest["scopeResult"] = "PASS_BOUNDED_INSPECTION_RUN_EXECUTOR_ONLY"
        manifest["related"] = ["QA-046", "UIC-006", "SSC-049", "PG-D-130", "BUG-014", "YKT-012"]
        manifest["fixture"] = "Real PostgreSQL/restricted role and prior independent JCE Login error; synthetic unverifiable1001 rows; deterministic monotonic nanoTime sequences, public JDBC close hook and actual thread interrupts. No secrets saved."
        manifest["oracle"] = "027/028: SUCCESS0/WARNING10 only committedEND;30min before/equal/after, clock rollback/natural wrap, interrupt before/after preserving flag;1001-row two chunks, failure inside second chunk confirms1000 while DB holds1001 and same-run resume recovers; record/null contracts and redaction, unexpected clock exceptions propagate."
        manifest["classCoverage"] = {cls.get("name"): {c.get("type"): {"missed": int(c.get("missed")), "covered": int(c.get("covered"))}
                                     for c in cls.findall("counter")} for cls in classes}
    if args.aes_credential:
        manifest["scopeResult"] = "PASS_OWNED_AES_CREDENTIAL_FORMAT_ONLY"
        manifest["related"] = ["QA-046", "UIC-006", "SSC-049", "PG-D-131", "BUG-096", "YKT-087"]
        manifest["fixture"] = "Runtime CSPRNG32-byte test material, independently assembled ASCII envelope and JDK Base64. No real credential, key, encoded value or raw output saved."
        manifest["oracle"] = "029/030: literal magic/length/version grammar and canonical padded32-byte Base64; original independent key copy, malformed length/ASCII/padding/low-bit negatives; input zero on success/failure, no alias, close idempotence and after-close rejection, private-lock and100-copy/close races; fixed cause-free errors. File/ACL admission is not certified."
        manifest["classCoverage"] = {cls.get("name"): {c.get("type"): {"missed": int(c.get("missed")), "covered": int(c.get("covered"))}
                                     for c in cls.findall("counter")} for cls in classes}
    # Scope success is not the completion certificate for the complete maintenance workflow.
    if args.credential_access:
        manifest["scopeResult"] = "PASS_RUNTIME_CREDENTIAL_ACCESS_POLICY_ONLY"
        manifest["related"] = ["QA-046", "UIC-006", "SSC-049", "PG-D-132"]
        manifest["fixture"] = "Public numeric UID/mode/link/size/readonly metadata and independently handwritten44-byte Linux UAPI ACL golden; no filesystem or key."
        manifest["oracle"] = "031/032: root plus exact dedicated UID ACL or dedicated owner plus readonly filesystem and empty ACL; exact inode type/mode, link/size/UID boundaries;352 bit mutations per file/directory ACL, extra zero-permission principals, null/alias/100 concurrent policies, fixed errors. Attribute provenance and real file admission remain separate."
    if args.inode_security:
        manifest["scopeResult"] = "PASS_HELD_INODE_NATIVE_ACCESS_METADATA_ONLY"
        manifest["related"] = ["QA-046", "UIC-006", "SSC-049", "PG-D-133", "BUG-097", "YKT-088"]
        manifest["fixture"] = "Public temporary byte files, installed setfacl2.3.2, independent Linux UAPI golden, real Linux/glibc FFM and task-local native-call/errno probes; no secret or daemon changes."
        manifest["oracle"] = "033/034: literal44-byte ACL, empty non-retrieval is not authorization, real ERANGE/inode replacement/UID; fixed path and buffer boundaries, native errno and size failures, statvfs112-byte/flag72/ST_RDONLY1 probes plus real FileStore comparison, platform/symbol/null/unsigned UID contracts,100 concurrent owned handles. Actual runtime is x86_64; AArch64 runtime not certified."
    if args.credential_loader:
        manifest["scopeResult"] = "PASS_BOUNDED_AES_FILE_READER_ONLY"
        manifest["related"] = ["QA-046", "UIC-006", "SSC-049", "PG-D-134", "BUG-098"]
        manifest["fixture"] = "Real temporary files/retained handles/FileChannel and runtime CSPRNG32-byte independently assembled envelopes; explicitly synthetic privileged UID/mode/ACL/readonly metadata and package-local fault ports. Real default IO rejects the unprivileged RW fixture. No key/file content saved."
        manifest["oracle"] = "035/036 PT129..140: four literal IDs; previous absent only before entry callback, current/mid-IO/close missing fail; type-before-native, metadata null/type/size/link/owner and all before-after fields; partial/short/long/zero/lying reads bounded70; channel and entry close plus root recheck before parse; actual path replacement cannot redirect, all working buffers zero, independent returned key copies and100 concurrent loads. Does not certify root-manager credential provisioning."
    if args.credential_access or args.inode_security or args.credential_loader:
        manifest["classCoverage"] = {cls.get("name"): {c.get("type"): {"missed": int(c.get("missed")), "covered": int(c.get("covered"))}
                                     for c in cls.findall("counter")} for cls in classes}
    manifest["remaining"] = "Mandatory private oneshot/parent composition, Question/notification reference validation and full cleanup cross-audit NOT certified. BUG014/YKT012 remain open. Separate slice manifests certify 24-route inspectors, V011 bypass removal and V012/Java durable progress; SQL/Java alone do not certify process/backup-file/OS-lock/key wiring."
    validate_trace(out, manifest, certified)
    (out / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
    (out / "checksums.sha256").write_text("".join(
        hashlib.sha256((out / name).read_bytes()).hexdigest() + "  " + name + "\n"
        for name in ("results.xml", "manifest.json")))
    print(json.dumps({"runId": run, "subject": subject, "inspectionTests": len(names), "coverage": counters, "programComplete": False}))


if __name__ == "__main__":
    main()
