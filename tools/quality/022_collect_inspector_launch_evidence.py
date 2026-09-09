#!/usr/bin/env python3
"""PG-D-144/146: private launcher, deployment and Linux flock PT, not parent OS acceptance."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import xml.etree.ElementTree as ET

PREFIX = "dev.codex.schubert.nk.api.maintenance."
GROUPS = (
    (PREFIX + "InspectorLaunchConfigurationTest", 221,
     ("validConfiguration", "missingUnknownAndArguments", "scalarBoundaries", "versionAndSnapshotContracts")),
    (PREFIX + "InspectorLauncherTest", 225,
     ("successWarningAndFailureStatus", "expectedFailuresAndRedaction", "nativeFactoryFailure",
      "receiptAndOutputFailure", "nullContracts", "mainAndFatalHandler", "concurrentInvocations", "actualJvmEntry")),
)
DEPLOYMENT_GROUPS = ((PREFIX + "InspectorDeploymentTest", 1,
    ("renderedShellCheck", "statusMapping", "malformedReceipts", "argumentsAndPlaceholders",
     "realMainBridge", "baseUnitAndSyntax", "previousProfiles", "releaseClasspathAndIsolation")),
    ("dev.codex.schubert.nk.storage.LinuxFileLockTest", 1,
     ("nativeRoundTrip", "externalFlockInteroperability", "fcntlIsNotFlock", "callbackFailureAndClose",
      "nativeErrorsAndFlags", "inputAndPlatformContracts", "concurrentSingleWinner", "retainedInodeAndDescriptorLifetime")))
FLOCK_SUBJECT = "dev/codex/schubert/nk/storage/LinuxFileLock"
SUBJECTS = tuple("dev/codex/schubert/nk/api/maintenance/" + c
                 for c in ("InspectorLaunchConfiguration", "InspectorLauncher"))
TRACES = {"renderedShellCheck": 3, "statusMapping": 9, "malformedReceipts": 29,
          "argumentsAndPlaceholders": 3, "realMainBridge": 1, "baseUnitAndSyntax": 1, "previousProfiles": 4}


def validate_reports(suites, deployment=False):
    groups = DEPLOYMENT_GROUPS if deployment else GROUPS
    if len(suites) != len(groups) or {s.get("name") for s in suites} != {g[0] for g in groups}:
        raise ValueError("missing or unmapped launcher/deployment class")
    methods = {}
    for cls, start, expected in groups:
        suite = next(s for s in suites if s.get("name") == cls)
        cases = suite.findall("testcase")
        names = [c.get("name") for c in cases]
        if (suite.get("tests") != str(len(expected))
                or any(int(suite.get(k, "0")) for k in ("failures", "errors", "skipped"))
                or len(names) != len(set(names)) or set(names) != set(expected)
                or any(c.get("classname") != cls or any(child.tag not in ("system-out", "system-err")
                   for child in c) for c in cases)):
            raise ValueError("launcher/deployment PT inventory or status is not certifiable")
        prefix = ("PT-OPS-FLOCK" if cls == "dev.codex.schubert.nk.storage.LinuxFileLockTest"
                  else "PT-OPS-INBOX") if deployment else "PT-DB-INBOX"
        methods.update({f"{prefix}-{i:03}": cls + "#" + name for i, name in enumerate(expected, start)})
    return methods


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run_id")
    parser.add_argument("--deployment", action="store_true")
    args = parser.parse_args()
    run = args.run_id
    if not run.startswith("PT-WEB-") or not all(c.isalnum() or c == "-" for c in run):
        raise SystemExit("invalid run ID")
    repo = Path(__file__).resolve().parents[2]
    full = repo / "evidence/01_PT/008_NK-SCN-001/evidence/manifest.json"
    verified = json.loads(full.read_text())
    if verified["runId"] != run or verified["exitCode"] != 0:
        raise SystemExit("matching successful full reactor required")
    subprocess.run(["git", "diff", "--exit-code", verified["targetCommit"], "--", "src", "pom.xml",
                    "program/characterization", "tools/quality"], cwd=repo, check=True)
    target = repo / "src/schubert-nk-api/target"
    groups = DEPLOYMENT_GROUPS if args.deployment else GROUPS
    def module_for(cls):
        return "storage" if cls == "dev.codex.schubert.nk.storage.LinuxFileLockTest" else "api"
    methods = validate_reports([ET.parse(repo / ("src/schubert-nk-" + module_for(g[0])) / "target/surefire-reports" / ("TEST-" + g[0] + ".xml")).getroot()
                                for g in groups], args.deployment)
    coverage = {}
    for cls in ET.parse(target / "site/jacoco/jacoco.xml").getroot().iter("class"):
        name = cls.get("name")
        if any(name == s or name.startswith(s + "$") for s in SUBJECTS):
            coverage[name] = {c.get("type"): {"missed": int(c.get("missed")), "covered": int(c.get("covered"))}
                             for c in cls.findall("counter")}
    if not set(SUBJECTS).issubset(coverage) or any(c["missed"] for v in coverage.values() for c in v.values()):
        raise SystemExit("missing or incomplete launcher coverage")
    if args.deployment:
        for cls in ET.parse(repo / "src/schubert-nk-storage/target/site/jacoco/jacoco.xml").getroot().iter("class"):
            name = cls.get("name")
            if name == FLOCK_SUBJECT or name.startswith(FLOCK_SUBJECT + "$"):
                coverage[name] = {c.get("type"): {"missed": int(c.get("missed")), "covered": int(c.get("covered"))}
                                 for c in cls.findall("counter")}
        if FLOCK_SUBJECT not in coverage or any(c["missed"] for v in coverage.values() for c in v.values()):
            raise SystemExit("missing or incomplete Linux flock coverage")
    directory = "018_NK-OPS-001/evidence" if args.deployment else "004_NK-DAT-001/evidence/inspector-launch"
    evidence = repo / "evidence/01_PT" / directory
    evidence.mkdir(parents=True, exist_ok=True)
    program = "NK-OPS-001" if args.deployment else "NK-DAT-001"
    sanitized = ET.Element("testsuite", name=program + "-inspector-launch", tests=str(len(methods)), failures="0", errors="0", skipped="0")
    for test_id, method in methods.items():
        ET.SubElement(sanitized, "testcase", id=test_id, classname=method.split("#")[0], name=method.split("#")[1], result="PASS")
    ET.ElementTree(sanitized).write(evidence / "results.xml", encoding="utf-8", xml_declaration=True)
    sources = [repo / "src/schubert-nk-api/src/main/java" / (s + ".java") for s in SUBJECTS]
    sources += [repo / ("src/schubert-nk-" + module_for(g[0])) / "src/test/java" / (g[0].replace(".", "/") + ".java") for g in groups]
    sources += [repo / "src/schubert-nk-api/pom.xml"]
    if args.deployment:
        sources += [repo / "src/schubert-nk-storage/src/main/java" / (FLOCK_SUBJECT + ".java"),
                    repo / "src/schubert-nk-storage/pom.xml"]
        sources += [repo / "src/deployment" / p for p in (
            "operations/inbox-inspector.sh.template", "systemd/schubert-nk-inbox-inspector.service",
            "systemd/optional/inbox-inspector-context-previous.conf", "systemd/optional/inbox-inspector-response-previous.conf")]
        trace_root = target / "inspector-deployment"
        expected_paths = {f"{method}/{i:03}.json" for method, count in TRACES.items() for i in range(1, count + 1)}
        if {str(p.relative_to(trace_root)) for p in trace_root.rglob("*") if p.is_file()} != expected_paths:
            raise SystemExit("incomplete deployment execution trace inventory")
        for relative in sorted(expected_paths):
            data = json.loads((trace_root / relative).read_text())
            if data["method"] != relative.split("/")[0] or set(data) != {"method", "command", "exitCode", "stdout", "stderr"}:
                raise SystemExit("invalid deployment trace")
            destination = evidence / "logs" / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_text(json.dumps(data, indent=2) + "\n")
    manifest = {k: verified[k] for k in ("runId", "targetCommit", "branch", "startedAt", "completedAt", "exitCode", "command", "environment", "rawLogSha256")}
    manifest.update({
        "programId": program, "scopeResult": "PASS_DEPLOYMENT_AND_FLOCK_SLICES_ONLY" if args.deployment else "PASS_PRIVATE_LAUNCHER_ONLY",
        "programComplete": False, "testIdMethods": methods, "failed": 0, "errors": 0, "skipped": 0,
        "classCoverage": coverage, "staticAnalysis": verified["modules"]["api"]["spotbugs"],
        "fullReactorManifest": ("../../" if args.deployment else "../../../") + "008_NK-SCN-001/evidence/manifest.json",
        "fullReactorManifestSha256": digest(full), "related": ["QA-046", "UIC-006", "SSC-049", "SSC-053", "PG-D-144", "BUG-136", "BUG-137", "YKT-107", "BUG-014", "YKT-012"],
        "fixture": "Public environment/path/UUID/time/version/receipt vectors only. Fresh real JVM negative tests. OPS uses fixed fake Java and local static unit syntax verification; no host manager/service/credential changes.",
        "oracle": "051/PT221..232: bounded nonsecret canonical input, missing/null/unknown rejection, no parsing diagnostics, exact ASCII receipt after owned resource closure, 0/10/50/70 mapping, unexpected runtime escape/fixed fatal message, native admission negatives,64 independent invocations. 018/PT001..008: fixed receipt byte matrix and JVM exit override; all base directives and4 selected previous-key profiles; actual sh/ShellCheck/systemd-analyze with recorded outputs; release classpath/JDBC runtime/Java25 flags.",
        "limitations": "Java coverage belongs to launcher, not a shell percentage. Parent OS flock/inactive/backup/run binding, root-owned environment validation/publication, actual unit credential provisioning and timeout/TERM behavior, full batch, NK CHR and IT/ST are NOT certified.",
        "sourceFiles": [{"path": str(p.relative_to(repo)), "sha256": digest(p)} for p in sources],
    })
    if args.deployment:
        manifest["staticAnalysisByModule"] = {m: verified["modules"][m]["spotbugs"] for m in ("api", "storage")}
        manifest["related"] += ["PG-D-146", "BUG-140", "YKT-110"]
        manifest["fixture"] += " FLOCK uses isolated retained regular files, real libc and util-linux2.41.3 with narrow native fault ports. No host lockfile, UID or service mutation."
        manifest["oracle"] += " 003/PT-OPS-FLOCK-001..008: independent flock exit20 while Java holds and Java empty while external holds; fcntl does not conflict; one of32 wins; retained original inode remains locked after path replacement; errno11 alone is contention; fixed open flags0x80000/flock6, close once and IO diagnostic redaction."
        manifest["limitations"] += " LinuxFileLock is a low-level capability only; root/type/UID/ACL/stable-namespace admission and parent lifecycle are not supplied by it. CLOEXEC is asserted at the native call boundary, not an actual inherited-FD inspection; aarch64 ABI selection only, execution is amd64."
        manifest["deploymentCoverage"] = {
            "class": "not applicable", "method": "not applicable",
            "basis": "Every executable statement and decision outcome in the hashed shell template has an asserting test and recorded sh -x trace; no code is excluded. Unit is declarative, validated by independent exact directive map, not JaCoCo.",
            "decisions": {"argument count zero/nonzero": "PT004 and PT002", "placeholder absent/present": "PT001/PT004",
                          "JVM success/failure and dot/exclamation marker": "PT002", "hex converter success/failure": "PT002 test-only fixed executable fault",
                          "receipt cases0/10/50/70/default including NUL at all16 positions": "PT002/PT003"},
            "profiles": {"none": 3, "context": 4, "response": 4, "both": 5},
            "tools": {"ShellCheck": "0.11.0", "systemd-analyze": "259.5-0ubuntu3.4", "shell": "/bin/sh", "od": "uutils coreutils0.8.0"},
        }
    manifest["files"] = [{"path": str(p.relative_to(evidence)), "sha256": digest(p)} for p in sorted(evidence.rglob("*"))
                         if p.is_file() and p.name not in ("manifest.json", "checksums.sha256")]
    (evidence / "manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")
    (evidence / "checksums.sha256").write_text("".join(digest(p) + "  " + str(p.relative_to(evidence)) + "\n"
        for p in sorted(evidence.rglob("*")) if p.is_file() and p.name != "checksums.sha256"))
    print(json.dumps({"runId": run, "tests": len(methods), "scopeResult": manifest["scopeResult"], "programComplete": False}))


if __name__ == "__main__":
    main()
