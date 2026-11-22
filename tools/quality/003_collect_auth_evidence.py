#!/usr/bin/env python3
"""Collect only allowlisted execution metadata, never raw JVM properties/test stdout/secret values."""

import argparse
import hashlib
import json
import platform
from pathlib import Path
import shutil
import subprocess
import xml.etree.ElementTree as ET

from pgpt_evidence_checksums import write_scope_checksums


RESOURCE_METHODS = {
    "PT-AUT-003-D06": "dev.codex.schubert.nk.api.security.LoginAttemptRepositoryTest#providerIllegalArgumentAndCloseSqlRemainRedactedInfrastructure",
    "PT-AUT-008-R05": "dev.codex.schubert.nk.api.security.AuthSessionRevocationServiceTest#providerIllegalArgumentAndRowCloseAreInfrastructure",
    "PT-AUT-LOGOUT-INBOX-007": "dev.codex.schubert.nk.api.security.LogoutInboxServiceTest#providerIllegalArgumentOwnerAndCloseRollbackAllEffects",
}

PRODUCTION_LOGIN_METHODS = {
    "PT-AUT-INBOX-007": "dev.codex.schubert.nk.api.security.LoginInboxServiceTest#productionAssemblyAuthenticatesWithRealInboxSessionAndAudit",
    "PT-AUT-INBOX-008": "dev.codex.schubert.nk.api.security.LoginInboxServiceTest#productionAssemblyFailedLoginReplaysWithoutSecondAttempt",
    "PT-AUT-INBOX-009": "dev.codex.schubert.nk.api.security.LoginInboxServiceTest#productionApiReceiveGroupConsumesRealBrokerLoginAndReplay(Path)",
}


def validate_resource_method(methods):
    if any(methods.count(method) != 1 for method in RESOURCE_METHODS.values()):
        raise ValueError("missing or duplicate authentication resource PT")
    if any(methods.count(method) != 1 for method in PRODUCTION_LOGIN_METHODS.values()):
        raise ValueError("missing or duplicate production Login PT")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run_id")
    args = parser.parse_args()
    if not args.run_id.startswith(("PT-AUT-", "PT-SCN-", "PT-MED-", "PT-ADM-", "PT-WEB-")) or not all(c.isalnum() or c == "-" for c in args.run_id):
        raise SystemExit("invalid run ID")
    repo = Path(__file__).resolve().parents[2]
    evidence = repo / "evidence/01_PT/007_NK-AUT-001/evidence"
    metadata = Path("/tmp")
    read = lambda suffix: (metadata / (args.run_id + suffix)).read_text().strip()
    if read(".exit") != "0":
        raise SystemExit("failed execution cannot be certified")
    commit = read(".commit")
    subprocess.run(["git", "diff", "--exit-code", commit, "--", "src", "pom.xml",
                    "program/characterization", "tools/quality"], cwd=repo, check=True,
                   stdout=subprocess.DEVNULL)
    raw_log = (metadata / (args.run_id + ".log")).read_bytes()
    if b"BUILD SUCCESS" not in raw_log or b"[ERROR]" in raw_log:
        raise SystemExit("build log is not successful")
    for folder in ("output", "coverage", "logs"):
        (evidence / folder).mkdir(parents=True, exist_ok=True)
    modules = {}
    auth_methods = []
    for module, directory in (("characterization", "program/characterization"),
                              ("protocol", "src/schubert-nk-protocol"),
                              ("storage", "src/schubert-nk-storage"),
                              ("api", "src/schubert-nk-api"), ("web", "src/schubert-nk-web"),
                              ("batch", "src/schubert-nk-batch")):
        target = repo / directory / "target"
        reports = sorted((target / "surefire-reports").glob("TEST-*.xml"))
        if not reports:
            raise SystemExit("missing JUnit reports")
        count = 0
        for report in reports:
            suite = ET.parse(report).getroot()
            if any(int(suite.get(name, "0")) for name in ("errors", "failures", "skipped")):
                raise SystemExit("nonpassing JUnit report")
            cases = suite.findall("testcase")
            if len(cases) != int(suite.get("tests")):
                raise SystemExit("JUnit method count mismatch")
            for case in cases:
                if any(child.tag not in ("system-out", "system-err") for child in case):
                    raise SystemExit("failure/rerun/flaky/skipped test is not certifiable")
            count += len(cases)
            if ".api.security." in suite.get("name", ""):
                clean = ET.Element("testsuite", {name: suite.get(name) for name in
                                                ("name", "time", "tests", "errors", "failures", "skipped")})
                for case in cases:
                    attributes = {name: case.get(name) for name in ("name", "classname", "time")}
                    ET.SubElement(clean, "testcase", attributes)
                    auth_methods.append(attributes["classname"] + "#" + attributes["name"])
                ET.indent(clean)
                ET.ElementTree(clean).write(evidence / "output" / report.name,
                                            encoding="UTF-8", xml_declaration=True)
        jacoco = ET.parse(target / "site/jacoco/jacoco.xml").getroot()
        counters = {counter.get("type"): {"missed": int(counter.get("missed")),
                                         "covered": int(counter.get("covered"))}
                    for counter in jacoco.findall("counter")}
        if not counters or any(value["missed"] for value in counters.values()):
            raise SystemExit("coverage is not 100 percent")
        shutil.copyfile(target / "site/jacoco/jacoco.csv", evidence / "coverage" / (module + "-jacoco.csv"))
        static = "not configured for characterization runner"
        if module != "characterization":
            spot = ET.parse(target / "spotbugsXml.xml").getroot()
            errors = spot.find("Errors")
            if spot.findall("BugInstance") or errors is None or int(errors.get("errors", "0")):
                raise SystemExit("static analysis not clean")
            static = {"tool": "SpotBugs 4.10.4.0", "violations": 0, "errors": 0}
        modules[module] = {"tests": count, "coverage": counters, "spotbugs": static}
    validate_resource_method(auth_methods)
    manifest = {
        "runId": args.run_id, "programId": "NK-AUT-001", "targetCommit": commit,
        "branch": subprocess.check_output(["git", "branch", "--show-current"], cwd=repo, text=True).strip(),
        "startedAt": read(".started"), "completedAt": read(".completed"), "exitCode": 0,
        "command": "JAVA_HOME=/home/mini/codex/project1/work/toolchain/jdk-25.0.4 ./mvnw -o -Dmaven.repo.local=/home/mini/codex/project1/work/toolchain/m2/repository --no-transfer-progress clean verify",
        "environment": {"os": platform.platform(), "jdk": "25.0.4", "maven": "3.9.12",
                        "springSecurityCrypto": "7.1.1", "springCore": "7.0.9"},
        "modules": modules, "authenticationMethods": auth_methods,
        "testIdsPassed": ["PT-AUT-001", "PT-AUT-002", "PT-AUT-007-R01", "PT-AUT-007-R02", "PT-AUT-007-R03", "PT-AUT-007-R04", *PRODUCTION_LOGIN_METHODS],
        "testIdsPartial": {"PT-AUT-003": "policy, persisted User/IP counters and Login hash-skip/threshold/audit plus anonymous Inbox/JDBC/JMS replay passed; full dispatcher/bootstrap/HTTP connection remains",
                           "PT-AUT-004": "real PBKDF2 Login/counter/session/critical-audit and anonymous HMAC/Inbox transaction, dummy work, fault rollback, 100 concurrent redeliveries and actual JDBC/JMS commit boundaries passed; Production Login graph and API sync receive group are connected, but Web POST/full bootstrap/CHR remain",
                           "PT-AUT-005": "ASCII SHA256, AES-GCM, Login issuance and immutable Inbox replay passed; Web recovery and expiry orchestration remain",
                           "PT-AUT-006": "session issuance/oldest replacement/tie/expiry/100 requests and real Login transaction, atomic replacement audit and fault rollback passed; wire and CHR connection remains",
                           "PT-AUT-007": "real PostgreSQL verifier/idle/role/state/rollback/concurrency/faults passed; dispatcher/wire error mapping remains",
                           "PT-AUT-008": "actor/role/owner policy, real DB Logout owner Inbox/frozen replay/idempotency/admin all-revocation/audit/fault/concurrency and absent remote IP contract passed; management command/predicates/full dispatcher/HTTP remain"},
        "testIdsNotRun": ["PT-AUT-009"],
        "programStatus": "IN_PROGRESS", "notRunCountedAsPass": 0,
        "relatedBug": ["BUG-020", "BUG-021", "BUG-022", "BUG-023", "BUG-024", "BUG-026", "BUG-027", "BUG-028", "BUG-029"], "relatedYkt": ["YKT-007", "YKT-008", "YKT-017", "YKT-018", "YKT-019", "YKT-020", "YKT-021", "YKT-023", "YKT-024", "YKT-025", "YKT-026"], "relatedSsc": ["SSC-009", "SSC-010", "SSC-011", "SSC-012", "SSC-013", "SSC-014", "SSC-015", "SSC-016", "SSC-023"],
        "additionalTests": {
            "PT-AUT-003-D06": "LoginAttemptRepository two catch sites: real PostgreSQL transaction with public JDBC provider-IAE plus close-SQL composite, fixed redacted Infrastructure exception, rollback and literal zero-row/count postconditions. Other API authentication classes remain YKT-162 open",
            "PT-AUT-008-R05": "AuthSessionRevocationService session-row provider-IAE plus row-close SQL: fixed redacted Infrastructure, caller rollback, revoked0/audit0 on real PostgreSQL. YKT-162 API fifth catch is separate",
            "PT-AUT-LOGOUT-INBOX-007": "LogoutInboxService owner-row provider-IAE plus row-close SQL: fixed redacted Infrastructure, caller rollback, inbox0/revoked0/audit0 on real PostgreSQL. YKT-162 other domains remain open",
            "PT-AUT-WIRE-001..003": "Login success/failure/lock/9000 and Logout 0000/0200 fixed DATA mapper passed with independent byte vectors; dispatcher/Inbox/HTTP connection remains",
            "PT-AUT-REPLAY-001..005": "Immutable encrypted Login snapshot, AUTH_SESSION cross-check, fresh response header, original failure codes, tamper/NULL/JDBC faults/100 concurrent replays/key rotation and anonymous HMAC/Inbox/application transaction passed; JMS/HTTP connection remains",
            "PT-AUT-INBOX-001..006": "Real PostgreSQL anonymous Login Inbox with independent wire/LP-HMAC/PBKDF2/SQL expectations: atomic commit/rollback, 7-day completion retention, original failure/lock replay, identity conflict, 100 deliveries -> 1 session/1 audit, key/JDBC failures, owned-secret cleanup and distinct sender-NFC/receiver-NFD boundaries passed",
            "PT-AUT-TX-001..004": "JDBC owner commits success and definite business errors before JMS reply/ACK; acquisition/begin/handler/commit-before/commit-after/close/rollback/null/permanent-plus-cleanup fault matrix is redacted and retryable as specified. Actual isolated Artemis redelivery after reply-send/ACK failure and independent cache-miss send produce one session/audit/Inbox with original DATA; DB outage redelivers before any effects. OS process kill/reboot belongs to later IT",
            "PT-AUT-LOGOUT-INBOX-001..006": "Known-context owner-only lookup, atomic Logout/Inbox/audit, immutable 280-byte snapshot and AUTH_SESSION reference, same-message 100 concurrent replays with one audit, new-message idempotent audit, unknown/expired/disabled context, owner mismatch, ciphertext/header/ref/hash/time/NULL/JDBC/key tampering and rollback passed; never grants a principal or extends idle",
            "PT-AUT-AUDIT-IP-001": "Unavailable current IP on Logout/admin revocation is SQL NULL, not prior Login IP or loopback; explicit IP remains canonical, actual Login/REPLACED retains current IP, null Optional is rejected",
            "PT-AUT-CLOCK-001..002": "Independent moving-clock SQL/byte oracle: business state and audit at t+1, Inbox completion at t+2 and expiry t+2+7 days, initial header at t+3, replay header at t+4 with original DATA and unchanged retention/audit",
            "PT-AUT-NAME-001..004": "64-byte display and 96-byte Locale.ROOT comparison key, independent Unicode literals/scalar expansion bound, old CHECK rejection to V007 upgrade, database bounds/UK/NULL and real Login with 64-byte audit passed; User management adoption remains"},
        "baseline": "Current baseline remains unchanged; authentication application CHR not run yet",
        "rawLogSha256": hashlib.sha256(raw_log).hexdigest(),
        "redaction": "Only fixed metadata, class/method names and counters collected; all test output and properties omitted.",
        "expectations": "007 PT specification; literal Unicode/Instant/authorization matrix, independent JCA PBKDF2/AES-GCM and DataOutputStream envelope/AAD, independently calculated SHA256 vectors. No production function constructs expected values.",
    }
    (evidence / "logs" / (args.run_id + "-summary.json")).write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    manifest["files"] = [
        {"path": str(path.relative_to(evidence)), "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
        for path in sorted(evidence.rglob("*"))
        if path.is_file() and path.name not in ("manifest.json", "checksums.sha256")]
    (evidence / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_scope_checksums(evidence, manifest["files"])
    print(json.dumps({"runId": args.run_id, "tests": sum(item["tests"] for item in modules.values()),
                      "authenticationTests": len(auth_methods), "status": "SLICE_PASS / PROGRAM_IN_PROGRESS"}))


if __name__ == "__main__":
    main()
