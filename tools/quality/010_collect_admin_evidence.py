#!/usr/bin/env python3
"""Map executed Admin PT methods to a verified, unchanged full-reactor source commit."""

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
    if not run.startswith("PT-ADM-") or not all(c.isalnum() or c == "-" for c in run):
        raise SystemExit("invalid run ID")
    repo = Path(__file__).resolve().parents[2]
    verified = json.loads((repo / "evidence/01_PT/008_NK-SCN-001/evidence/manifest.json").read_text())
    if verified["runId"] != run or verified["exitCode"] != 0:
        raise SystemExit("collect the matching verified full reactor first")
    subprocess.run(["git", "diff", "--exit-code", verified["targetCommit"], "--", "src", "pom.xml",
                    "program/characterization", "tools/quality"], cwd=repo, check=True,
                   stdout=subprocess.DEVNULL)
    prefix = "dev.codex.schubert.nk.api.persistence.UserQueryRepositoryTest"
    names = [
        "adm001SearchFiltersLiteralPrefixesAndStablePages",
        "adm002DetailProjectsActorsTimesAndActiveSessions",
        "adm003DisabledAndLockBoundariesUseOneFixedInstant",
        "adm004AuthorizationNullAndInputContractsRejectBeforeSql",
        "adm005JdbcNullUnknownAndCloseFailuresNeverBecomeMissing",
        "adm006CapacityAndPageMetadataRejectTruncation",
        "adm007ConcurrentReadOnlyQueriesNeverMutateOrLock",
    ]
    expected = {f"PT-ADM-{i:03d}": prefix + "#" + name for i, name in enumerate(names, 1)}
    authentication = "dev.codex.schubert.nk.api.security.AdminCommandAuthenticatorTest"
    authentication_names = [
        "adm008AllMutationKindsLockThenAuthenticateCurrentAdmin",
        "adm009ReciprocalAdminsFollowOneGlobalUserOrder",
        "adm010RevokedExpiredChangedOwnerAndRoleNeverAuthorize",
        "adm011NullTargetsAndWriteTransactionContractsFailClosed",
        "adm012JdbcClockAndResourceFailuresRollbackWithoutLeaks",
        "adm013ConcurrentAuthenticationKeepsNoCrossRequestState",
    ]
    expected.update({f"PT-ADM-{i:03d}": authentication + "#" + name for i, name in enumerate(authentication_names, 8)})
    commands = "dev.codex.schubert.nk.api.application.admin.UserCommandServiceTest"
    command_names = [
        "adm014CreateNormalizesAsciiUsersAndIndependentlyVerifiesPassword",
        "adm015StatusChangesAtomicallyRevokeSessions",
        "adm016RoleChangesProtectSelfAndLastActiveAdmin",
        "adm017PasswordResetConsumesSecretsAndRevokesEverySession",
        "adm018UnlockUsesExactExpiryAndNoopVersionRules",
        "adm019ExpectedVersionDuplicateAndCapacityAreBusinessResults",
        "adm020SqlRevocationAndAuditFailuresRollbackTogether",
        "adm021NullPolicyAndHashFailuresAlwaysErasePasswords",
        "adm022ConcurrentMutationsPreserveAdminAndVersionInvariants",
        "adm023ResultAndAuditProjectionsContainOnlyApprovedFields",
    ]
    expected.update({f"PT-ADM-{i:03d}": commands + "#" + name for i, name in enumerate(command_names, 14)})
    requests = "dev.codex.schubert.nk.api.application.admin.UserMutationRequestTest"
    request_names = [
        "adm024DecodeAndCanonicalMatchIndependentWireAndHmac",
        "adm025DispatchUsesTheSameDecodedFieldsInRealTransactions",
        "adm026MalformedNullAndClosedRequestsFailWithoutSecretLeak",
        "adm027ConcurrentIndependentRequestsNeverShareIdentityOrBuffers",
    ]
    expected.update({f"PT-ADM-{i:03d}": requests + "#" + name for i, name in enumerate(request_names, 24)})
    methods, reports = [], {}
    for classname in (prefix, authentication, commands, requests):
        report = repo / "src/schubert-nk-api/target/surefire-reports" / ("TEST-" + classname + ".xml")
        suite = ET.parse(report).getroot()
        cases = suite.findall("testcase")
        if any(int(suite.get(key, "0")) for key in ("errors", "failures", "skipped")):
            raise SystemExit("nonpassing Admin PT")
        if int(suite.get("tests", "0")) != len(cases):
            raise SystemExit("inconsistent Admin test count")
        clean = ET.Element("testsuite", {k: suite.get(k) for k in ("name", "time", "tests", "errors", "failures", "skipped")})
        for case in cases:
            if any(child.tag not in ("system-out", "system-err") for child in case):
                raise SystemExit("failed/skipped/flaky/rerun Admin case")
            attributes = {key: case.get(key) for key in ("name", "classname", "time")}
            methods.append(attributes["classname"] + "#" + attributes["name"])
            ET.SubElement(clean, "testcase", attributes)
        ET.indent(clean)
        reports[report.name] = ET.ElementTree(clean)
    if set(methods) != set(expected.values()) or len(methods) != len(expected):
        raise SystemExit("Admin Test IDs do not exactly cover executed methods")
    evidence = repo / "evidence/01_PT/010_NK-ADM-001/evidence"
    for name in ("logs", "output", "coverage"):
        (evidence / name).mkdir(parents=True, exist_ok=True)
    for name, report in reports.items():
        report.write(evidence / "output" / name, encoding="UTF-8", xml_declaration=True)
    for suffix in ("csv", "xml"):
        shutil.copyfile(repo / "src/schubert-nk-api/target/site/jacoco" / ("jacoco." + suffix),
                        evidence / "coverage" / ("api-jacoco." + suffix))
    manifest = {key: verified[key] for key in ("runId", "targetCommit", "branch", "startedAt", "completedAt",
                                              "exitCode", "command", "environment", "modules", "rawLogSha256")}
    manifest.update({
        "programId": "NK-ADM-001", "programStatus": "IN_PROGRESS",
        "tests": {"program": len(methods), "reactor": sum(m["tests"] for m in verified["modules"].values())},
        "testIdMethods": expected, "methods": methods,
        "inputAndExpected": "PT-ADM-001..007 / PG-D-081: actual isolated PostgreSQL/Flyway roles and synthetic users, independent UI236 PAGED48/168-byte records/320-byte detail golden arrays. Empty/one/50/51/101 users, stable C/id order, NFC/literal escaped prefix and role/state filters, fixed 50 rows and bounded pages. Explicit UTC Instants/JST strings, disabled/lock and active-session expiry microsecond boundaries, SYSTEM for absent bootstrap actors only, 0/1/2 sessions. SQL postconditions never select credentials. Null/unknown/wire/JDBC/readOnly/resource-close/row aggregate faults and N6-page capacity boundary are independently asserted; one-statement snapshot and 100 concurrent reads under held writer locks leave data and caller connections unchanged.",
        "actual": "All mapped assertion sets passed; no failures/errors/skips/flaky or not-run counted",
        "scope": "UserQueryRepository search/detail, redacted query exception, SSC031 administrative authentication prelude, and definite UserCommandService mutations/critical audit/session revocation in a caller-owned transaction. Outer Inbox/HMAC/replay/denial audit registration, HTTP/startup/actual NK Characterization are not completed by this slice. IT/ST remains later server work.",
        "administrativeAuthentication": "PT-ADM-008..013 / SSC-031 / PG-D-082: actual candidate owner lookup, required-only advisory71419601, ordered User union locks, session owner recheck and normal current ADMIN authentication/idle touch. All mutation kinds, reciprocal target and reducing/nonreducing overlap, changed current role/revocation/expiry/owner, independent NOWAIT/advisory/SQL time postconditions, null/row/JDBC/close/clock failures with caller rollback, 100 concurrent authentications. Candidate lookup never authorizes. Full command/Inbox registration remains pending; SSC031 is not closed by this component alone.",
        "administrativeCommands": "PT-ADM-014..023 / PG-D-083: actual PG/Flyway/grants and SSC031 prelude; ASCII username NFC/trim and independent JCA PBKDF2 with parsed stored salt, explicit USRMUT24 golden bytes. Create/status/role/password/unlock SQL postconditions, version/sequence limits and duplicate savepoint recovery, exact microsecond lock/no-op rules, all unrevoked sessions including expired, before/after allowlist audit and partial audit/revocation rollback. Public JDBC fault projections assert fail-closed null/unknown/count/row/resource contracts without private reflection. Password arrays zeroed on success/denial/boundary/encoding faults. 100 same-version contenders, reciprocal ADMIN reduction and 100 distinct targets assert serialized membership/version/audit results. Full message dispatcher/Inbox/HMAC/HTTP registration is still pending.",
        "mutationRequests": "PT-ADM-024..027 / SSC032 / PG-D-084: independent UI236 byte-offset input and hand-written LP/JCE HMAC expected fields for all five layouts, seven prelude kinds, N12/N9 bounds, independent role/enabled pairs, original-case/key binding, password NFC/256 bytes, separate token/header identity. Same decoded fields drive actual prelude/command/SQL postconditions. Strict wire errors remain protocol errors; database-dependent password/username conflict remains business0100 and duplicate name0105 (BUG048 oracle boundary correction). Independent canonical/request ownership, readOnly command failure, public close and direct test-only security observation of zeroed private buffer, closed-use denial, 100 independent concurrent operations. No private method invocation or coverage-only reflection; no production secret accessor added. Outer Inbox/replay/JMS/HTTP remains pending.",
        "relatedBug": ["BUG-045", "BUG-046", "BUG-047", "BUG-048"], "relatedSsc": ["SSC-031", "SSC-032"], "relatedYkt": ["YKT-040", "YKT-041", "YKT-042", "YKT-043"],
        "preventionReferences": ["BUG-030/YKT-027 numeric null", "BUG-031/YKT-028 suppressed close redaction", "BUG-044/YKT-039 timestamp Instant oracle"],
        "notRunCountedAsPass": 0,
        "redaction": "JUnit names/timing/counters only; no properties/stdout/stderr, provider row dumps, raw identifiers or credentials.",
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
