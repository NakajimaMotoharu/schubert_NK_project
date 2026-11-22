#!/usr/bin/env python3
"""Map executed Admin PT methods to a verified, unchanged full-reactor source commit."""

import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import xml.etree.ElementTree as ET

from pgpt_evidence_checksums import write_scope_checksums
from pgpt_evidence_destination import evidence_output_root


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run_id")
    run = parser.parse_args().run_id
    if not run.startswith(("PT-ADM-", "PT-WEB-")) or not all(c.isalnum() or c == "-" for c in run):
        raise SystemExit("invalid run ID")
    repo = Path(__file__).resolve().parents[2]
    verified = json.loads((evidence_output_root(repo) / "008_NK-SCN-001/evidence/manifest.json").read_text())
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
    replay = "dev.codex.schubert.nk.api.application.admin.UserMutationReplayServiceTest"
    replay_names = [
        "adm028FiveLayoutsFreezeOriginalResultVersionAndFreshHeaders",
        "adm029DefiniteErrorsAndTransientFailuresKeepTheirProfiles",
        "adm030TamperedEncryptedRowsReferencesAndBodiesNeverReplay",
        "adm031NullClosedAndCrossRequestScopesFailWithoutSecrets",
        "adm032OneHundredIndependentReplaysDoNotShareHeadersOrVersions",
    ]
    expected.update({f"PT-ADM-{i:03d}": replay + "#" + name for i, name in enumerate(replay_names, 28)})
    application = "dev.codex.schubert.nk.api.application.admin.UserMutationApplicationServiceTest"
    application_names = [
        "adm033AllMutationsCommitOnceAndReplayFrozenVersions",
        "adm034CurrentAuthenticationAndIdentityDenialsAreAudited",
        "adm035SqlCryptoAuditAndTransactionFailuresNeverClaimSuccess",
        "adm036ConcurrentTokensAndReciprocalAdminsPreserveInvariants",
        "adm037DefiniteErrorsAndProcessingKeepApprovedResults",
        "adm038BrokerSendAndAckFailuresReplayOneCommittedMutation",
        "adm039NullLifecycleAndAuditAllowlistProtectBoundaries",
    ]
    expected.update({f"PT-ADM-{i:03d}": application + "#" + name for i, name in enumerate(application_names, 33)})
    query_requests = "dev.codex.schubert.nk.api.application.admin.UserQueryRequestTest"
    query_request_names = [
        "adm040DecodeAndCanonicalKeepAllOriginalQueryFields",
        "adm041RealReadOnlyQueriesUseTheSameDecodedValues",
        "adm042NullMalformedAndResponseMismatchNeverPass",
        "adm043ConcurrentRequestsOwnIndependentCanonicalBuffers",
    ]
    expected.update({f"PT-ADM-{i:03d}": query_requests + "#" + name for i, name in enumerate(query_request_names, 40)})
    query_replay = "dev.codex.schubert.nk.api.application.admin.UserQueryReplayServiceTest"
    query_replay_names = [
        "adm044FrozenListAndDetailRebuildExactFreshReplies",
        "adm045ErrorsAndAuthenticatedCorruptSnapshotsFailClosed",
        "adm046NullScopeRoleAndKeyLifecycleProtectReplies",
        "adm047ConcurrentSnapshotsNeverShareQueryResults",
    ]
    expected.update({f"PT-ADM-{i:03d}": query_replay + "#" + name for i, name in enumerate(query_replay_names, 44)})
    query_application = "dev.codex.schubert.nk.api.application.admin.UserQueryApplicationServiceTest"
    query_application_names = [
        "adm048QueriesCommitFrozenResponsesAndFullRetention",
        "adm049BothStagesRecheckIdentityRoleAndAuditDenials",
        "adm050DatabaseCryptoAndResourceFailuresRollbackSafely",
        "adm051ConcurrentRequestsReplayOnlyTheWinningSnapshot",
        "adm052SavedRowsCannotDisappearOrChangeBetweenStages",
        "adm053BrokerFailuresReplayOneCommittedQueryResult",
        "adm054PublicBoundariesAndStageOwnershipAreExplicit",
    ]
    expected.update({f"PT-ADM-{i:03d}": query_application + "#" + name for i, name in enumerate(query_application_names, 48)})
    log_queries = "dev.codex.schubert.nk.api.persistence.LogQueryRepositoryTest"
    log_query_names = [
        "adm055PagesAndEveryFilterMatchIndependentRows",
        "adm056ProjectionMatchesLiteralLogWireOffsets",
        "adm057DateBoundsAndOptionalEndpointsAreExact",
        "adm058NullRoleTransactionAndCapacityFailClosed",
        "adm059JdbcAndResourceFailuresPreserveCallerState",
        "adm060ConcurrentReadsDoNotBlockOrShareResults",
    ]
    expected.update({f"PT-ADM-{i:03d}": log_queries + "#" + name for i, name in enumerate(log_query_names, 55)})
    log_requests = "dev.codex.schubert.nk.api.application.log.LogRequestTest"
    log_request_names = [
        "adm061CanonicalPreservesEveryOriginalFilterAndDate",
        "adm062StrictBoundariesAndRealQueryUseOneDecodedRequest",
        "adm063ConcurrentCanonicalBuffersRemainIndependent",
    ]
    expected.update({f"PT-ADM-{i:03d}": log_requests + "#" + name for i, name in enumerate(log_request_names, 61)})
    log_replay = "dev.codex.schubert.nk.api.application.log.LogReplayServiceTest"
    log_replay_names = [
        "adm064FrozenRecordsAndCapacityRebuildExactReplies",
        "adm065CorruptSnapshotsAndPublicBoundariesFailClosed",
        "adm066ConcurrentSnapshotsDoNotShareBodiesOrHeaders",
    ]
    expected.update({f"PT-ADM-{i:03d}": log_replay + "#" + name for i, name in enumerate(log_replay_names, 64)})
    log_application = "dev.codex.schubert.nk.api.application.log.LogQueryApplicationServiceTest"
    log_application_names = [
        "adm067QueriesCommitFrozenRecordsAndFullRetention",
        "adm068BothStagesRecheckIdentityRoleAndAuditDenials",
        "adm069DatabaseCryptoAndResourceFailuresRollbackSafely",
        "adm070ConcurrentQueriesUseOnlyTheWinningSnapshot",
        "adm071SavedRowsCannotDisappearOrChangeBetweenStages",
        "adm072BrokerFailuresReplayOneCommittedLogResult",
        "adm073PublicBoundariesAndAuditAllowlistAreExplicit",
    ]
    expected.update({f"PT-ADM-{i:03d}": log_application + "#" + name for i, name in enumerate(log_application_names, 67)})
    expected["PT-ADM-074"] = authentication + "#adm074ProviderIllegalArgumentPlusCloseIsInfrastructure"
    expected["PT-ADM-075"] = log_application + "#adm075ProductionAssemblyUsesRealDependenciesAndNullContract"
    expected["PT-ADM-076"] = log_application + "#adm076ProductionLogRouteReceivesThroughBroker(Path)"
    methods, reports = [], {}
    for classname in (prefix, authentication, commands, requests, replay, application, query_requests, query_replay, query_application, log_queries, log_requests, log_replay, log_application):
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
    evidence = evidence_output_root(repo) / "010_NK-ADM-001/evidence"
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
        "logApplication": "PT-ADM-067..073/075 / PG-D-092/256: actual PostgreSQL read-only current ADMIN/query-or-verified-snapshot followed by fresh identity/role/owner and short Inbox/critical-audit write transaction, with JDBC close between stages and before wire/JMS. Independent UI235 whole-wire/JCE/LP-HMAC/SQL assertions: zero/one/100 rows, last-page clamp, filters, completed_at+24h and NONE, persistent9001, frozen0000/replay0200 after Log changes; replay audit is visible to a new broad search but never appended to old snapshots. Nonpersistent0102/0103 with current-actor-only closed LOG audit, canonical/owner mismatch audited then permanent rejection. 100 same/different messages and conflicting query/owner races, PROCESSING, disappeared/modified snapshots, every JDBC stage, rollback/audit/clock/UUID/crypto and committed-but-unsent boundary fail closed. Real Artemis send/ACK/DB faults redeliver count2, one Inbox, exact body/properties and DLQ/drain. Constructor/null, ownership, audit allowlist/bytes and standard UUID covered. PT-ADM-075 binds Production graph with caller-owned keys and verifies initial/replay SQL plus null contract. Full HTTP/startup/actual NK CHR and IT/ST remain incomplete.",
        "logRequestReplay": "PT-ADM-061..066 / SSC037 / PG-D-091: strict LGS656 and one decoded value for original nine-field HMAC and real ADMIN read-only query. Independent NULL LP/JCE, all128 optional-presence combinations, UTF8/NFC/case/leading-space/literal filter and UTC T1 timestamp identity, N6/pageSize100. Independent UI235 header256/PAGED48/LOG2088 full wire and JCE/Deflater envelope, zero/one/100 records and all optional fields, initial0000/replay0200, persistent9001 only/NONE and completion microseconds. Authenticated corrupt header/record/page/state/ref/time/layout/version/AAD/owner/key/cipher, public NULL/scope/role/closed-key failures reject. 100 independent canonical buffers zero on close and 100 independent full encrypted snapshots/replies. BUG054 authorization negative-oracle corrected, YKT049 query contracts reviewed and retested. Current authentication, 24-hour DB retention, Inbox/audit/JMS outer application and HTTP remain pending, not waived.",
        "logQuery": "PT-ADM-055..060 / PG-D-090 / SSC036: actual PostgreSQL app_logs projection, current verified ADMIN required and caller read-only ownership. One fixed-column/predicate count/list statement, 100 rows/page and occurredAt/id descending, capacity99999900, independent literal2088-byte records and exact optional/status/elapsed/UUID/inet/JSONB fields. Keyword in message/details, escaped literal path, category/action/level predicates; UI-approved INFO/WARN/ERROR subset consistently excludes but never deletes diagnostic TRACE/DEBUG. Optional date endpoints, inclusive DB microseconds, <=31 days when both present, wire-only millisecond truncation. Null/unknown/invalid/overflow/JDBC/close/aggregate faults fixed and 100 reads while writer locks held. BUG052 explicit-column SQL and BUG053 trailing-padding oracle corrected; no extra projection or wire enum changes. Request/replay/outer transaction/HTTP remain pending.",
        "queryApplication": "PT-ADM-048..054 / PG-D-089: actual PostgreSQL read-only preflight/query or verified frozen response, then fresh current identity/ADMIN/owner verification and short write Inbox/critical-audit transaction. Connection closes between stages and before wire/JMS. Independent wire and SQL retention completed_at+24h, 0000/0200, persistent0104/9001 and nonpersistent0102/0103; original body/version/expiry survive current User changes. Same-Message query/owner mismatch audits and DLQs, 100 same/different Message and conflicting-query/owner races use the DB winner only. Lost/changed encrypted snapshot or keys fail closed. DB/open/NULL/prepare/close/commit/rollback/audit/clock/UUID/crypto failures include committed-but-unsent retry. Real Artemis send/ACK faults redeliver with deliveryCount2 and one Inbox; exact broker body/properties/queue drain. No global dispatcher, HTTP or startup registration claim.",
        "queryRequestReplay": "PT-ADM-040..047 / SSC035 / PG-D-088: strict USR96/UDT12 decoding, optional NULL LP and original prefix/page HMAC with independent JCE; real PostgreSQL read-only ADMIN query and no SQL mutation. Request-bound page/target validation, frozen 0/1/50-record lists and details, full independent UI232/236 wire/JCE snapshot envelope, initial0000/replay0200, definite UDT0104/USR9001 errors only. Authenticated but inconsistent body/layout/owner/AAD/page/target/time/state, keys, NULL and scope reject. 100 independent canonical and snapshot operations. BUG050 NullAway and BUG051 negative oracle corrected with YKT045/046. Completion metadata is checked here; 24-hour retention belongs to the pending outer Inbox transaction, not this component.",
        "mutationReplay": "PT-ADM-028..032 / PG-D-086 / SSC033: independent hand-built 256+24 byte responses and JCE/Deflater NKENC1 envelope/AAD. Five layouts/seven mutations, create0/update+1/N9 limits/unlock initial0200, frozen USER ref/version and original definite errors. Bound source controls decryption, current request controls fresh response ID/correlation/context/time; success replay0200 only. NULL/closed/USER/owner/cross-request scope, valid-encryption but inconsistent header/body/ref/state/version/time/code/filler, cipher/key/AAD corruption and PROCESSING reject without secrets. 100 concurrent independent operations. Component has no DB/current authentication/transaction/HTTP effects; outer registration remains pending.",
        "scope": "UserQueryRepository search/detail, administrative authentication prelude, definite UserCommandService mutations and frozen replay, connected by UserMutationApplicationService to real PostgreSQL Inbox/HMAC/critical denial and business audit/session revocation plus real JMS send/ACK redelivery. Global layout registration, query processor, HTTP/startup/actual NK Characterization are not completed by this slice. IT/ST remains later server work.",
        "mutationApplication": "PT-ADM-033..039 / PG-D-087 / SSC031/034: actual PostgreSQL/Flyway/grants and current authenticated identity before ADMIN gate. Definite User/session/audit/encrypted Inbox commit, frozen version after a real later update, independent hand-built wire/LP/JCE-HMAC/PBKDF2 and SQL completion+7d retention. Current role/session/owner/token/message denials are minimally audited before response or permanent rejection; no new Inbox/business effect. 100 same-token and same-message calls, 20 distinct-token version contenders, separate owner token scope and reciprocal reducing/nonreducing ADMIN updates preserve membership and single effects. Public JDBC/NULL/crypto/audit/commit/rollback/close/clock/identifier faults never claim success, including commit-before-close ambiguity followed by replay. Real Artemis reply-send/ACK/DB failures redeliver exactly one committed mutation; mismatched Message is audited and isolated to DLQ. Legacy verify still requires ADMIN, new verifyIdentity is not a grant. Default UUID factory, caller key lifetime, JSON/role/target/context redaction and commit/close-before-reply are verified.",
        "administrativeAuthentication": "PT-ADM-008..013/074 / SSC-031 / PG-D-082: actual candidate owner lookup, required-only advisory71419601, ordered User union locks, session owner recheck and normal current ADMIN authentication/idle touch. All mutation kinds, reciprocal target and reducing/nonreducing overlap, changed current role/revocation/expiry/owner, independent NOWAIT/advisory/SQL time postconditions, null/row/JDBC/close/clock failures with caller rollback, 100 concurrent authentications. PT-ADM-074 adds provider unknown IAE plus ResultSet-close SQL with fixed redacted Infrastructure and unchanged session SQL after rollback (YKT-162 one class only). Candidate lookup never authorizes. Full command/Inbox registration remains pending; SSC031 is not closed by this component alone.",
        "administrativeCommands": "PT-ADM-014..023 / PG-D-083: actual PG/Flyway/grants and SSC031 prelude; ASCII username NFC/trim and independent JCA PBKDF2 with parsed stored salt, explicit USRMUT24 golden bytes. Create/status/role/password/unlock SQL postconditions, version/sequence limits and duplicate savepoint recovery, exact microsecond lock/no-op rules, all unrevoked sessions including expired, before/after allowlist audit and partial audit/revocation rollback. Public JDBC fault projections assert fail-closed null/unknown/count/row/resource contracts without private reflection. Password arrays zeroed on success/denial/boundary/encoding faults. 100 same-version contenders, reciprocal ADMIN reduction and 100 distinct targets assert serialized membership/version/audit results. Full message dispatcher/Inbox/HMAC/HTTP registration is still pending.",
        "mutationRequests": "PT-ADM-024..027 / SSC032 / PG-D-084: independent UI236 byte-offset input and hand-written LP/JCE HMAC expected fields for all five layouts, seven prelude kinds, N12/N9 bounds, independent role/enabled pairs, original-case/key binding, password NFC/256 bytes, separate token/header identity. Same decoded fields drive actual prelude/command/SQL postconditions. Strict wire errors remain protocol errors; database-dependent password/username conflict remains business0100 and duplicate name0105 (BUG048 oracle boundary correction). Independent canonical/request ownership, readOnly command failure, public close and direct test-only security observation of zeroed private buffer, closed-use denial, 100 independent concurrent operations. No private method invocation or coverage-only reflection; no production secret accessor added. Outer Inbox/replay/JMS/HTTP remains pending.",
        "relatedBug": ["BUG-045", "BUG-046", "BUG-047", "BUG-048", "BUG-050", "BUG-051", "BUG-052", "BUG-053", "BUG-054"], "relatedSsc": ["SSC-031", "SSC-032", "SSC-033", "SSC-034", "SSC-035", "SSC-036", "SSC-037"], "relatedYkt": ["YKT-040", "YKT-041", "YKT-042", "YKT-043", "YKT-045", "YKT-046", "YKT-047", "YKT-048", "YKT-049"],
        "preventionReferences": ["BUG-030/YKT-027 numeric null", "BUG-031/YKT-028 suppressed close redaction", "BUG-044/YKT-039 timestamp Instant oracle"],
        "notRunCountedAsPass": 0,
        "redaction": "JUnit names/timing/counters only; no properties/stdout/stderr, provider row dumps, raw identifiers or credentials.",
    })
    (evidence / "logs" / (run + "-summary.json")).write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
    manifest["files"] = [{"path": str(p.relative_to(evidence)), "sha256": hashlib.sha256(p.read_bytes()).hexdigest()}
                         for p in sorted(evidence.rglob("*")) if p.is_file() and p.name not in ("manifest.json", "checksums.sha256")]
    (evidence / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
    write_scope_checksums(evidence, manifest["files"])
    print(json.dumps({"runId": run, "tests": len(methods), "status": "SLICE_PASS / PROGRAM_IN_PROGRESS"}))


if __name__ == "__main__":
    main()
