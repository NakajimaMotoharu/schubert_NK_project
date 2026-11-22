#!/usr/bin/env python3
"""PG-D-142: database credential/connection PT only, never a private-main/OS certificate."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import xml.etree.ElementTree as ET

from pgpt_evidence_checksums import write_scope_checksums
import bootstrap_ownership

GROUPS = (
    ("dev.codex.schubert.nk.api.maintenance.InspectorDbCredentialTest", 193,
     ("validUtf8AndNewlines", "invalidEncodingAndBounds", "ownedCopiesAndClose", "concurrentOwnership")),
    ("dev.codex.schubert.nk.api.file.InspectorDatabaseCredentialLoaderTest", 197,
     ("validBoundedFile", "missingAndInvalidContent", "permissionsAndMetadata", "ioFailuresAndCleanup", "concurrentFilesAndAesRegression")),
    ("dev.codex.schubert.nk.api.maintenance.InspectorDatabaseConnectionsTest", 202,
     ("fixedConnectionProperties", "urlAndNullContracts", "connectionAdmission", "sqlFailuresRemainRedacted",
      "closeAndConcurrentOpen", "realScramRoleAndPassword", "ownedInspectionConnection")),
)
SUBJECTS = (
    "dev/codex/schubert/nk/api/maintenance/InspectorDbCredential",
    "dev/codex/schubert/nk/api/maintenance/InspectorDatabaseConnections",
    "dev/codex/schubert/nk/api/maintenance/InspectorCredentialAccess",
    "dev/codex/schubert/nk/api/file/InspectorCredentialLoader",
)
APPLICATION_GROUPS = (
    ("dev.codex.schubert.nk.api.maintenance.InspectorSettingsTest", 209,
     ("validSnapshot", "invalidSettings", "sharedValidation")),
    ("dev.codex.schubert.nk.api.file.InspectorApplicationTest", 212,
     ("successAndResume", "protectedResult", "databaseFailure", "credentialFailures", "rootFailures",
      "nativeAdmission", "nullContracts", "interruptedExecution", "concurrentLifetimes")),
)
APPLICATION_SUBJECTS = (
    "dev/codex/schubert/nk/api/maintenance/InspectorSettings",
    "dev/codex/schubert/nk/api/file/InspectorApplication",
    "dev/codex/schubert/nk/api/maintenance/InspectorProcess",
) + SUBJECTS


def validate_reports(suites, application=False):
    groups = APPLICATION_GROUPS if application else GROUPS
    if len(suites) != len(groups) or {s.get("name") for s in suites} != {g[0] for g in groups}:
        raise ValueError("missing or unmapped inspector database class")
    methods = {}
    for cls, start, expected in groups:
        suite = next(s for s in suites if s.get("name") == cls)
        cases = suite.findall("testcase")
        names = [c.get("name") for c in cases]
        if (suite.get("tests") != str(len(expected))
                or any(int(suite.get(k, "0")) for k in ("failures", "errors", "skipped"))
                or len(names) != len(set(names)) or set(names) != set(expected)
                or any(c.get("classname") != cls or any(
                    child.tag not in ("system-out", "system-err") for child in c) for c in cases)):
            raise ValueError("inspector database PT inventory or status is not certifiable")
        methods.update({f"PT-DB-INBOX-{i:03}": cls + "#" + name
                        for i, name in enumerate(expected, start)})
    return methods


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run_id")
    parser.add_argument("--application", action="store_true")
    args = parser.parse_args()
    run = args.run_id
    groups = APPLICATION_GROUPS if args.application else GROUPS
    subjects = APPLICATION_SUBJECTS if args.application else SUBJECTS
    folder = "inspector-application" if args.application else "inspector-database"
    if not run.startswith("PT-WEB-") or not all(c.isalnum() or c == "-" for c in run):
        raise SystemExit("invalid run ID")
    repo = Path(__file__).resolve().parents[2]
    full = repo / "evidence/01_PT/008_NK-SCN-001/evidence/manifest.json"
    verified = json.loads(full.read_text())
    if verified["runId"] != run or verified["exitCode"] != 0:
        raise SystemExit("matching successful full reactor required")
    subprocess.run(["git", "diff", "--exit-code", verified["targetCommit"], "--",
                    "src", "pom.xml", "program/characterization", "tools/quality"], cwd=repo, check=True)
    target = repo / "src/schubert-nk-api/target"
    methods = validate_reports([ET.parse(repo / ("src/schubert-nk-" + bootstrap_ownership.owner(g[0], test=True)) / "target/surefire-reports" / ("TEST-" + g[0] + ".xml")).getroot()
                                for g in groups], args.application)
    coverage = {}
    for subject in subjects:
        module = bootstrap_ownership.owner(subject)
        for cls in ET.parse(repo / ("src/schubert-nk-" + module) / "target/site/jacoco/jacoco.xml").getroot().iter("class"):
            name = cls.get("name")
            if name == subject or name.startswith(subject + "$"):
                coverage[name] = {c.get("type"): {"missed": int(c.get("missed")), "covered": int(c.get("covered"))}
                                  for c in cls.findall("counter")}
    if not set(subjects).issubset(coverage) or any(c["missed"] for v in coverage.values() for c in v.values()):
        raise SystemExit("missing or incomplete inspector database coverage")
    evidence = repo / "evidence/01_PT/004_NK-DAT-001/evidence" / folder
    evidence.mkdir(parents=True, exist_ok=True)
    sanitized = ET.Element("testsuite", name="NK-DAT-001-" + folder, tests=str(len(methods)), failures="0", errors="0", skipped="0")
    for test_id, method in methods.items():
        ET.SubElement(sanitized, "testcase", id=test_id, classname=method.split("#")[0], name=method.split("#")[1], result="PASS")
    ET.ElementTree(sanitized).write(evidence / "results.xml", encoding="utf-8", xml_declaration=True)
    sources = [bootstrap_ownership.source(repo, name.replace("/", ".")) for name in subjects]
    sources += [bootstrap_ownership.source(repo, g[0], test=True) for g in groups]
    sources += [repo / "src/schubert-nk-api/pom.xml",
                bootstrap_ownership.source(repo, "dev.codex.schubert.nk.api.file.InspectorCredentialLoaderTest", test=True),
                repo / "src/schubert-nk-bootstrap/pom.xml", repo / "tools/quality/bootstrap_ownership.py"]
    manifest = {key: verified[key] for key in ("runId", "targetCommit", "branch", "startedAt", "completedAt",
                 "exitCode", "command", "environment", "rawLogSha256")}
    manifest.update({
        "programId": "NK-DAT-001", "scopeResult": "PASS_DB_CREDENTIAL_AND_CONNECTION_ONLY", "programComplete": False,
        "testIdMethods": methods, "failed": 0, "errors": 0, "skipped": 0, "classCoverage": coverage,
        "staticAnalysis": verified["modules"]["api"]["spotbugs"],
        "staticAnalysisByModule": {m: verified["modules"][m]["spotbugs"] for m in ("api", "bootstrap")},
        "fullReactorManifest": "../../../008_NK-SCN-001/evidence/manifest.json", "fullReactorManifestSha256": digest(full),
        "related": ["QA-046", "UIC-006", "SSC-049", "PG-D-142", "BUG-130", "BUG-131", "BUG-132", "BUG-133", "YKT-103", "YKT-104", "BUG-014", "YKT-012"],
        "fixture": "Public UTF8/byte/ACL vectors, retained temporary files and real channels with explicitly synthetic privileged metadata; isolated PostgreSQL18.6 SCRAM role with runtime CSPRNG password; public JDBC fault/ownership probes. No secret content or raw logs saved.",
        "oracle": "047/PT193..208: literal UTF8/one terminal LF or CRLF/space preservation, 1..65536 bytes, strict decode/size/null rejection and owned buffer erasure; inherited file/root/link/ACL and all IO/close faults; four fixed JDBC properties, canonical loopback URL, role/session/db/recovery admission; SQL faults erase Properties, close invalid connections and expose no cause. Real SCRAM correct/wrong password and 42501 privileges; owned cleanup rollback2/0 then final1/1 with2 inspected/1deleted/1protected, same-run stable resume;100 independent fresh sessions and open/close lifetime locking.",
        "limitations": "JVM/JDBC immutable String copies cannot be physically erased by this API. Root-manager actual credential provisioning, dedicated main/unit, parent OS/real-backup/full-morning, actual NK CHR and IT/ST are NOT certified.",
        "sourceFiles": [{"path": str(p.relative_to(repo)), "sha256": digest(p)} for p in sources],
    })
    if args.application:
        manifest.update({
            "scopeResult": "PASS_INSPECTOR_RESOURCE_LIFETIME_ONLY",
            "related": ["QA-046", "UIC-006", "SSC-049", "PG-D-143", "BUG-134", "BUG-135", "YKT-105", "YKT-106", "BUG-014", "YKT-012"],
            "fixture": "Public immutable path/URL/version vectors; real retained temporary files and native descriptors with explicitly synthetic privileged metadata; isolated PG18.6 trust fixture for resource composition only, NOT a SCRAM authentication certificate (047/PT207 independently covers SCRAM). Runtime random AES keys and public byte65 fixture password, no deployed credentials.",
            "oracle": "049/PT209..220: immutable nonsecret configuration; null/empty/root/path/URL/version rejection before IO; real SQL empty-run END0/0/0 and same-run resume; malformed response retained END1/0/1; missing backup STORAGE_FAILURE and no durable progress; password/key failure closes all; root open/close failure never returns success and committed progress survives resume; default native RW root rejection; start interrupt flag retained with IO0, actual FileChannel interruption fails and closes;64 independent concurrent missing-file operations close every FD. Private reflection and production-derived expected values are not used.",
        })
    manifest["files"] = [{"path": str(p.relative_to(evidence)), "sha256": digest(p)}
                         for p in sorted(evidence.rglob("*")) if p.is_file() and p.name not in ("manifest.json", "checksums.sha256")]
    (evidence / "manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")
    write_scope_checksums(evidence, manifest["files"])
    print(json.dumps({"runId": run, "tests": len(methods), "coverage": coverage,
                      "scopeResult": manifest["scopeResult"], "programComplete": False}))


if __name__ == "__main__":
    main()
