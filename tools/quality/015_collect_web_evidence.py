#!/usr/bin/env python3
"""Certify executed Web PT IDs against the verified full reactor; omit raw session and JVM data."""

import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import xml.etree.ElementTree as ET


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run_id")
    run = parser.parse_args().run_id
    if not run.startswith("PT-WEB-") or not all(c.isalnum() or c == "-" for c in run):
        raise SystemExit("invalid run ID")
    repo = Path(__file__).resolve().parents[2]
    verified = json.loads((repo / "evidence/01_PT/008_NK-SCN-001/evidence/manifest.json").read_text())
    if verified["runId"] != run or verified["exitCode"] != 0:
        raise SystemExit("collect the matching full verified reactor first")
    subprocess.run(["git", "diff", "--exit-code", verified["targetCommit"], "--", "src", "pom.xml",
                    "program/characterization", "tools/quality"], cwd=repo, check=True,
                   stdout=subprocess.DEVNULL)
    expected = {}
    groups = {
        "dev.codex.schubert.nk.web.session.WebSessionIdTest": (
            (1, "web001CanonicalIdsAndIndependentHashes"),
            (2, "web002NullLengthAlphabetAndUnusedBitsReject"),
            (3, "web003GenerationOwnsAndErasesRandomBuffers"),
            (4, "web004ConcurrentIdsAndHashesShareNoMutableDigest")),
        "dev.codex.schubert.nk.web.security.SavedRequestTargetTest": (
            (5, "web005SafeGetTargetsPreservePathAndQuery"),
            (6, "web006ExternalMalformedAndStateChangingTargetsReject"),
            (7, "web007Utf8LimitAndUnicodeBoundariesAreExact"),
            (8, "web008ConcurrentTargetsRemainIndependent")),
        "dev.codex.schubert.nk.web.session.SessionAttributeCodecTest": (
            (9, "web009AnonymousAndAuthenticatedGoldenJson"),
            (10, "web010PrincipalTokenAndCollectionInvariantsFailFast"),
            (11, "web011UnknownDuplicateNullAndTypesNeverDeserialize"),
            (12, "web012MalformedUtf8AndBoundedDocumentsRejectSafely"),
            (13, "web013UnicodeSavedTargetsAndTokenPurposesPreserveMeaning"),
            (14, "web014IndependentDecodeAcceptsOrderButRejectsInvalidValues"),
            (15, "web015ConcurrentAttributesHaveNoCrossSessionState")),
        "dev.codex.schubert.nk.web.session.SessionPayloadCodecTest": (
            (16, "web016IndependentEnvelopeAndDefensiveOwnership"),
            (17, "web017CurrentPreviousAndUnknownKeyFailClosed"),
            (18, "web018EnvelopeAndEveryAadFieldMutationReject"),
            (19, "web019AuthenticatedInvalidJsonAndSizeBoundariesReject"),
            (20, "web020NullConfigurationIdentityAndClosedLifetime"),
            (21, "web021ConcurrentNonceAndCallerMonitorIsolation"),
            (22, "web022ProviderAndRandomFailuresAreRedacted"),
            (23, "web023RotationKeysAndCloseAreSerialized")),
        "dev.codex.schubert.nk.web.logging.JdbcWebSessionStoreTest": (
            (24, "web024RoundTripCiphertextAndExplicitColumns"),
            (25, "web025CompareAndSwapNoResurrection"),
            (26, "web026CallerTransactionsRollbackFixation"),
            (27, "web027RoleIsolationAndConstraints"),
            (28, "web028NullRowAndConfigurationBoundaries"),
            (29, "web029EveryJdbcFailureIsRedactedAndResourcesClose"),
            (30, "web030InvalidDatabaseRowsFailClosed"),
            (31, "web031ConcurrentLocksAndVersionsStayConsistent")),
    }
    methods, reports = [], {}
    for classname, cases in groups.items():
        expected.update({f"PT-WEB-{i:03d}": classname + "#" + name for i, name in cases})
        report = repo / "src/schubert-nk-web/target/surefire-reports" / ("TEST-" + classname + ".xml")
        suite = ET.parse(report).getroot()
        actual = suite.findall("testcase")
        if any(int(suite.get(key, "0")) for key in ("errors", "failures", "skipped")):
            raise SystemExit("nonpassing Web PT")
        if int(suite.get("tests", "0")) != len(actual):
            raise SystemExit("inconsistent Web PT count")
        clean = ET.Element("testsuite", {key: suite.get(key) for key in
                                        ("name", "time", "tests", "errors", "failures", "skipped")})
        for case in actual:
            if any(child.tag not in ("system-out", "system-err") for child in case):
                raise SystemExit("failed/skipped/flaky/rerun Web case")
            attributes = {key: case.get(key) for key in ("name", "classname", "time")}
            methods.append(attributes["classname"] + "#" + attributes["name"])
            ET.SubElement(clean, "testcase", attributes)
        ET.indent(clean)
        reports[report.name] = ET.ElementTree(clean)
    if set(methods) != set(expected.values()) or len(methods) != len(expected):
        raise SystemExit("Web Test IDs do not exactly cover executed methods")
    evidence = repo / "evidence/01_PT/015_NK-WEB-001/evidence"
    for name in ("logs", "output", "coverage"):
        (evidence / name).mkdir(parents=True, exist_ok=True)
    for name, report in reports.items():
        report.write(evidence / "output" / name, encoding="UTF-8", xml_declaration=True)
    for suffix in ("csv", "xml"):
        shutil.copyfile(repo / "src/schubert-nk-web/target/site/jacoco" / ("jacoco." + suffix),
                        evidence / "coverage" / ("web-jacoco." + suffix))
    manifest = {key: verified[key] for key in ("runId", "targetCommit", "branch", "startedAt", "completedAt",
                                              "exitCode", "command", "environment", "modules", "rawLogSha256")}
    manifest.update({
        "programId": "NK-WEB-001", "programStatus": "IN_PROGRESS",
        "tests": {"program": len(methods), "reactor": sum(m["tests"] for m in verified["modules"].values())},
        "testIdMethods": expected, "methods": methods,
        "inputAndExpected": "PT-WEB-001..008 / PG-D-093: synthetic 32-byte zero/sequence/FF CSPRNG data with independent Python base64/hashlib fixed vectors; canonical unpadded43-character base64url and raw-ASCII SHA256 lookup, temporary random/decode/hash arrays erased. Null/length/alphabet/padding/unused-bits negatives, provider failure and100 concurrent random IDs/per-call hashes. Explicit GET URL strings preserve path/query/Unicode and valid query escapes with no trim/decode; reject schemes/authority/fragment/malformed/control/dot-segments/encoded path delimiters and nonGET. Exact2047/2048/2049 UTF8-byte, malformed surrogate and100 independent query cases. toString and validation errors contain no values.",
        "actual": "All mapped independent assertion sets passed; no failed/skipped/flaky/not-run counted",
        "sessionSchemaExpected": "PT-WEB-009..015 / SSC-038 / PG-D-094: independently handwritten UTF8 JSON for anonymous/authenticated all-or-none principal, every optional combination, USER/ADMIN, ordered0/1/10 purpose-tagged UUIDs, canonical UTC timestamps, NFC64byte usernames, csrf64..128 and saved GET2048byte. Reject missing/duplicate/unknown/null/wrong types, invalid UTF8/BOM/trailing documents, noncanonical UUID/time and over16384byte/deep inputs. Immutable values/collection copies, fixed redacted exceptions without parser cause/suppressed and100 concurrent inputs. BUG-055 malformed loginAt/issuedAt reproduction followed by explicit DateTimeException conversion and regression.",
        "sessionEncryptionExpected": "PT-WEB-016..023 / SSC-039 / PG-D-095: independently handcrafted JSON/DataOutputStream seven-field LP AAD and JCE AES256-GCM full NKENC1 envelopes. DB UUID/hash/created_at microseconds bind row; every AAD field and envelope/nonce/tag/body mutation rejects. Current writes/previous reads/unknown key and DB-vs-envelope version mismatch, defensive key/ciphertext copies, nonce erasure, valid16384byte JSON and16436byte envelope limits, authenticated bad JSON/UTF8 reject. Null/config/closed negatives;100 distinct concurrent nonces and attributes; caller-monitor isolation; fixed provider/random failures with no diagnostic cause/suppressed; latch-controlled close serialization and restart/rotation.",
        "sessionStoreExpected": "PT-WEB-024..031 / SSC-040 / PG-D-096 / BUG-056 / YKT-051: isolated PostgreSQL18 with production Flyway/grants, independent nine-column metadata/SQL afterconditions, every ciphertext/key/time/TTL/version update field changed, row identity and expected-version predicates. Caller-owned read/write transactions, rollback/atomic old-delete and new-insert, stale CAS false and no resurrection. Web business-schema denial and all nine SQL NULL/DDL constraints; public null/time/precision/TTL/version limits; every JDBC operation/resource failure with fixed redacted exception. Invalid row/duplicate/null resource and non-unit update counts reject.100 row-locked updates retain all versions and CAS race has one winner. No production SQL/schema expectation is used as oracle.",
        "scope": "Web values, closed JSON, encryption and low-level transactional ciphertext store only. Encrypted session lifecycle/invalidation/rotation persistence/fixation orchestration/dirty merge/CSRF/security/SavedRequest route allowlist/HTTP/startup/actual NK Characterization remain required and incomplete; no IT/ST claim.",
        "relatedBug": ["BUG-055", "BUG-056"], "relatedSsc": ["SSC-038", "SSC-039", "SSC-040"], "relatedYkt": ["YKT-050", "YKT-051"],
        "notRunCountedAsPass": 0,
        "redaction": "Only allowlisted method names/timing/counters/coverage and metadata. No JVM properties/stdout/stderr, raw cookie/session/context/token/key or database dump.",
    })
    (evidence / "logs" / (run + "-summary.json")).write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
    manifest["files"] = [{"path": str(p.relative_to(evidence)), "sha256": hashlib.sha256(p.read_bytes()).hexdigest()}
                         for p in sorted(evidence.rglob("*")) if p.is_file() and p.name not in ("manifest.json", "checksums.sha256")]
    (evidence / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
    (evidence / "checksums.sha256").write_text("".join(hashlib.sha256(p.read_bytes()).hexdigest() + "  " + str(p.relative_to(evidence)) + "\n"
                                                        for p in sorted(evidence.rglob("*")) if p.is_file() and p.name != "checksums.sha256"))
    print(json.dumps({"runId": run, "tests": len(methods), "status": "SLICE_PASS / PROGRAM_IN_PROGRESS"}))


if __name__ == "__main__":
    main()
