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
    args = parser.parse_args()
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
    cases = suite.findall("testcase")
    if (len(cases) != 8 or int(suite.get("tests", "0")) != 8
            or any(int(suite.get(k, "0")) for k in ("failures", "errors", "skipped"))
            or {c.get("name") for c in cases} != set(names)
            or any(c.get("classname") != class_name or len(c) != 0 for c in cases)):
        raise SystemExit("missing, nonpassing or noncanonical tests")
    coverage_xml = ET.parse(target / "site/jacoco/jacoco.xml").getroot()
    classes = [c for p in coverage_xml.findall("package") for c in p.findall("class")
               if c.get("name") == "dev/codex/schubert/nk/api/maintenance/" + subject]
    if not args.sql and len(classes) != 1:
        raise SystemExit("missing inspection class coverage")
    counters = {c.get("type"): {"missed": int(c.get("missed")), "covered": int(c.get("covered"))}
                for c in ([] if args.sql else classes[0].findall("counter"))}
    if not args.sql and (not {"LINE", "METHOD", "CLASS", "BRANCH"}.issubset(counters)
                        or any(v["missed"] or not v["covered"] for v in counters.values())):
        raise SystemExit("inspection coverage below 100 percent")
    folder = "authentication-inspection" if args.authentication else "inbox-inspection"
    if args.sql:
        folder = "inspection-sql"
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
                                         "result": "PASS"} for i, name in enumerate(names, 17 if args.sql else 9 if args.authentication else 1)},
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
    validate_trace(out, manifest, certified)
    (out / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
    (out / "checksums.sha256").write_text("".join(
        hashlib.sha256((out / name).read_bytes()).hexdigest() + "  " + name + "\n"
        for name in ("results.xml", "manifest.json")))
    print(json.dumps({"runId": run, "subject": subject, "inspectionTests": 8, "coverage": counters, "programComplete": False}))


if __name__ == "__main__":
    main()
