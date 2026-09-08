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
        "dev.codex.schubert.nk.web.security.WebCsrfTokenTest": (
            (32, "web032GenerationMatchesIndependentHexAndErasesBuffers"),
            (33, "web033EveryAllowedLengthMatchesOnlyIdenticalToken"),
            (34, "web034MissingMalformedAndNullBoundariesStayRedacted"),
            (35, "web035ConcurrentGenerationAndMatchingStayIndependent")),
        "dev.codex.schubert.nk.web.session.EncryptedWebSessionRepositoryTest": (
            (36, "web036CreateReadRestartAndIdleAreEncrypted"),
            (37, "web037ExpiryAndCorruptRowsCommitInvalidation"),
            (38, "web038MutationPreservesCurrentAttributesAndSecurityIdentity"),
            (39, "web039LoginFixationIsAtomicAndPreservesAllowlist"),
            (40, "web040VersionRolloverPreservesCookieAndRejectsOldPk"),
            (41, "web041DatabaseCryptoAndCommitFailuresNeverGrantSession"),
            (42, "web042NullConfigurationAndIdentityInvariants"),
            (43, "web043ConcurrentReadMutateInvalidateNeverResurrect")),
        "dev.codex.schubert.nk.web.session.SpringWebSessionTest": (
            (44, "web044LifecycleRotateAndTouchPreserveIdentity"),
            (45, "web045ProjectionAndImmediatePersistenceAreClosed"),
            (46, "web046TokenDeltasPreserveConcurrentChanges"),
            (47, "web047RepositoryOwnershipExpiryAndFailuresReject"),
            (48, "web048ServletFilterCookiesRestartAndFixation"),
            (49, "web049ServletInvalidationAndStaleCommitNeverResurrect")),
        "dev.codex.schubert.nk.web.session.WebCsrfIntegrationTest": (
            (50, "web050RepositoryPersistsGeneratesAndInvalidates"),
            (51, "web051OnlySingleBodyParameterResolves"),
            (52, "web052EveryPostRejectsBeforeBusinessWithoutCsrf"),
            (53, "web053FixationExpiryFaultsAndConcurrentRequestsStayBound")),
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
        "frameworkVersions": {"springSession": "4.1.1", "springWeb": "7.0.9", "springTest": "7.0.9", "springSecurityWeb": "7.1.1", "micrometerWeb": "1.17.1", "servletApi": "6.1.0", "commonsLoggingWeb": "1.4.0", "jspecifyWeb": "1.0.1", "sourceAndHashes": "documents/400_PGPT/420_環境/421_開発環境・toolchain構築記録.md sections5.7/5.8"},
        "programId": "NK-WEB-001", "programStatus": "IN_PROGRESS",
        "tests": {"program": len(methods), "reactor": sum(m["tests"] for m in verified["modules"].values())},
        "testIdMethods": expected, "methods": methods,
        "inputAndExpected": "PT-WEB-001..008 / PG-D-093: synthetic 32-byte zero/sequence/FF CSPRNG data with independent Python base64/hashlib fixed vectors; canonical unpadded43-character base64url and raw-ASCII SHA256 lookup, temporary random/decode/hash arrays erased. Null/length/alphabet/padding/unused-bits negatives, provider failure and100 concurrent random IDs/per-call hashes. Explicit GET URL strings preserve path/query/Unicode and valid query escapes with no trim/decode; reject schemes/authority/fragment/malformed/control/dot-segments/encoded path delimiters and nonGET. Exact2047/2048/2049 UTF8-byte, malformed surrogate and100 independent query cases. toString and validation errors contain no values.",
        "actual": "All mapped independent assertion sets passed; no failed/skipped/flaky/not-run counted",
        "sessionSchemaExpected": "PT-WEB-009..015 / SSC-038 / PG-D-094: independently handwritten UTF8 JSON for anonymous/authenticated all-or-none principal, every optional combination, USER/ADMIN, ordered0/1/10 purpose-tagged UUIDs, canonical UTC timestamps, NFC64byte usernames, csrf64..128 and saved GET2048byte. Reject missing/duplicate/unknown/null/wrong types, invalid UTF8/BOM/trailing documents, noncanonical UUID/time and over16384byte/deep inputs. Immutable values/collection copies, fixed redacted exceptions without parser cause/suppressed and100 concurrent inputs. BUG-055 malformed loginAt/issuedAt reproduction followed by explicit DateTimeException conversion and regression.",
        "sessionEncryptionExpected": "PT-WEB-016..023 / SSC-039 / PG-D-095: independently handcrafted JSON/DataOutputStream seven-field LP AAD and JCE AES256-GCM full NKENC1 envelopes. DB UUID/hash/created_at microseconds bind row; every AAD field and envelope/nonce/tag/body mutation rejects. Current writes/previous reads/unknown key and DB-vs-envelope version mismatch, defensive key/ciphertext copies, nonce erasure, valid16384byte JSON and16436byte envelope limits, authenticated bad JSON/UTF8 reject. Null/config/closed negatives;100 distinct concurrent nonces and attributes; caller-monitor isolation; fixed provider/random failures with no diagnostic cause/suppressed; latch-controlled close serialization and restart/rotation.",
        "sessionStoreExpected": "PT-WEB-024..031 / SSC-040 / PG-D-096 / BUG-056 / YKT-051: isolated PostgreSQL18 with production Flyway/grants, independent nine-column metadata/SQL afterconditions, every ciphertext/key/time/TTL/version update field changed, row identity and expected-version predicates. Caller-owned read/write transactions, rollback/atomic old-delete and new-insert, stale CAS false and no resurrection. Web business-schema denial and all nine SQL NULL/DDL constraints; public null/time/precision/TTL/version limits; every JDBC operation/resource failure with fixed redacted exception. Invalid row/duplicate/null resource and non-unit update counts reject.100 row-locked updates retain all versions and CAS race has one winner. No production SQL/schema expectation is used as oracle.",
        "scope": "Web values/JSON/crypto/store/lifecycle/Spring Session and actual CsrfFilter connected on Mock Servlet plus isolated PostgreSQL. Full Security chain/MQ authentication/real redacting audit403 handler/logger policy/SavedRequest route allowlist/API revoke queue/screens/startup/actual NK Characterization remain required and incomplete; no IT/ST claim.",
        "csrfPostExpected": "PT-WEB-050..053 / PG-D-100: persistent CSRF repository generates via anonymous create or atomic session rotate; closed readonly existing token validation, null save invalidates only as an externally coordinated Logout step. load/save/generate null/wrong type/field/value and DB/key failures fail closed. Deferred request attributes, exactly one valid64..128 body parameter _csrf, no header alternative or decoded query _csrf key, duplicates/null/empty/malformed reject. Independent literal token/HTTP403/business count for every SS313 POST including Login/Logout/User four operations/create/question/cancel/delete. GET/HEAD pass this CSRF layer only; unsafe PUT/DELETE/PATCH remain protected. Old fixation/different-session/expired token reject,100 concurrent valid requests succeed without creating operation tokens. Audit callback is a fixed PT double, final production audit/security chain/logger configuration remain mandatory, not counted as complete.",
        "springSessionExpected": "PT-WEB-044..049 / SSC-042 / PG-D-099 / BUG-058..059 / YKT-053..054: closed principal/csrfToken/savedRequest/operationTokens projection with immediate persistence; generic cast localized and unknown/type/null/read-only security boundaries. Rotate preserves principal with fresh Cookie/UUID/CSRF, microsecond touch never reduces last access, fixed idle value. Request snapshot token deltas merge into current DB state;10 parallel add/remove, identical retry, UUID-metadata collisions including stale delete, max10 and no resurrection. Repository ownership/expiry/fault/close/private monitor isolation. Actual Spring filter/Mock Servlet sets opaque32byte SCHUBERT_NK_SESSION, Secure/HttpOnly/Lax/Path=/, no domain/persistent expiry/extra base64; restart/fixation/Logout/invalid cookie/response-before-commit stale save checks. Explicit path dot segments reject across value/JSON/session while normal dotted names and query dots remain unchanged.",
        "sessionLifecycleExpected": "PT-WEB-036..043 / SSC-041 / PG-D-098 / BUG-057 / YKT-052: isolated production-DDL PostgreSQL with independently constructed JSON/AAD/AES vectors and SQL afterconditions. Microsecond8h idle boundaries/backward clock/restart/key rotation; expiry/corrupt tag/key/schema/NULL invalidate only their row with mandatory deletion verified. Pure current-state mutation preserves principal and CSRF, max10 tokens; atomic Login fixation preserves SavedRequest/tokens even with previously absent CSRF; Cookie/UUID/CSRF and neighbour UUID collisions rollback. Version999999999 rollover preserves Cookie and attributes, renews DB UUID and rejects old-PK CAS. All lifecycle JDBC/resource/commit/rollback/close/random/crypto/config faults return fixed errors; postcommit close may commit and retry checks actual state, never assumes rollback.100 concurrent counter changes,10 concurrent token adds/removes and invalidate races retain state without resurrection. Constructor/API null contracts and no provider cause/suppressed disclosure.",
        "csrfValueExpected": "PT-WEB-032..035 / PG-D-097:32 CSPRNG bytes to independent fixed64hex vector and provider-failure buffer erasure. All persisted lengths64..128 with explicit same/different first/middle/last/length booleans; nullable submitted missing is false and malformed tokens reject. Valid secrets compare via MessageDigest.isEqual over fixed129byte length-plus-padding arrays, then erase.100 unique concurrent generated tokens and shared immutable matching; toString/cause/suppressed redacted. Value only, no claim of POST/filter/403/session wiring completion.",
        "relatedBug": ["BUG-055", "BUG-056", "BUG-057", "BUG-058", "BUG-059"], "relatedSsc": ["SSC-038", "SSC-039", "SSC-040", "SSC-041", "SSC-042"], "relatedYkt": ["YKT-050", "YKT-051", "YKT-052", "YKT-053", "YKT-054"],
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
