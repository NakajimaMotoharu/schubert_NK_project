"""Check the revocation codec's bounded ownership in an isolated synthetic JVM."""

from collections import Counter
from datetime import datetime, timezone
from hashlib import sha256
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[4]
WORK = ROOT.parent / "pgpt-runs/PG379"
TOOLS = ROOT.parent / "toolchain"
SOURCE = ROOT / "src/schubert-nk-web"
SPEC = ROOT / "evidence/01_PT/016_NK-WEB-002/evidence"
MAIN = Path("dev/codex/schubert/nk/web")
NAMES = ("RevocationPayloadCodec", "RevocationPayloadIdentity", "EncryptedRevocationPayload",
         "RevocationPayloadException", "package-info")
TESTS = ("RevocationPayloadCodecTest", "RevocationPayloadFatalContractTest")
NOTE = "dev.codex.schubert.nk.web.revocation."


def utc():
    return datetime.now(timezone.utc).isoformat()


def pin(path):
    return {"path": str(path), "sha256": sha256(path.read_bytes()).hexdigest()}


def read(path):
    return json.loads(path.read_bytes())


def write(path, data):
    with path.open("x") as stream:
        json.dump(data, stream, indent=2)
        stream.write("\n")


def main():
    mode = sys.argv[1]
    assert mode in ("baseline", "changes")
    baseline = mode == "baseline"
    run = "PG41358-p01810-revoke-ownership-baseline-v1" if baseline else "PG41360-p01810-revoke-ownership-qualified-v1"
    previous = ROOT / "evidence/01_PT/006_NK-MSG-002/evidence/PG41354-p01810-web-log-single-ownership-v1/manifest.json"
    reference = read(previous)
    work = WORK / run
    work.mkdir(mode=0o700)
    source = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    assert not subprocess.check_output(["git", "diff", "--name-only", reference["source"], source,
                                        "--", "pom.xml", ".mvn", "src/schubert-nk-protocol"], cwd=ROOT)
    assert pin(Path(reference["pom"]["path"])) == reference["pom"]
    assert pin(Path(reference["protocolPackage"]["path"])) == reference["protocolPackage"]
    sources = []

    def freeze(kind, rel, target):
        path = SOURCE / f"src/{kind}/java" / rel
        data = subprocess.check_output(["git", "show", f"{source}:{path.relative_to(ROOT)}"], cwd=ROOT)
        assert path.read_bytes() == data
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
        sources.append(pin(path))
        return target

    for rel in [*[MAIN / "revocation" / (name + ".java") for name in NAMES],
                MAIN / "session/SessionStoreException.java", MAIN / "session/InvalidSessionRowException.java"]:
        freeze("main", rel, work / "src/main/java" / rel)
    expected_pom = Path(reference["pom"]["path"])
    pom = work / "pom.xml"
    pom.write_bytes(expected_pom.read_bytes())
    archive = Path(reference["protocolPackage"]["path"])
    repository = TOOLS / "m2/repository"
    java = TOOLS / "jdk-25.0.4/bin"
    env = {"JAVA_HOME": str(java.parent), "PATH": os.defpath, "LANG": "C.UTF-8", "TZ": "Asia/Tokyo"}
    receipts = {}

    def run_cmd(label, arguments):
        argv = list(map(str, arguments))
        done = subprocess.run(argv, cwd=work, env=env, capture_output=True, timeout=110, check=False)
        stdout, stderr = work / (label + ".out"), work / (label + ".err")
        stdout.write_bytes(done.stdout)
        stderr.write_bytes(done.stderr)
        records = dict(argv=argv, exit=done.returncode, stdout=pin(stdout), stderr=pin(stderr))
        write(work / (label + "-terminal.json"), records)
        receipts[label] = records
        assert done.returncode == 0, (label, done.stderr[-400:])
        return stdout

    compile_cmd = [a.replace(str(expected_pom.parent), str(work))
                   for a in reference["steps"]["compile"]["argv"]]
    assert "-o" in compile_cmd
    run_cmd("compile", compile_cmd)
    output = work / "target/classes"
    target = output / MAIN / "revocation/RevocationPayloadCodec.class"
    binary = run_cmd("javap", [java / "javap", "-p", "-s", "-c", target])
    start = binary.read_text().index("  " + NOTE + "RevocationPayloadCodec(java.lang.String, byte[], java.lang.String, byte[], java.security.SecureRandom);")
    code = binary.read_text()[start:].split("\n  public", 1)[0]
    copy = re.findall(r"^\s*(\d+):[^\n]+clone:", code, re.MULTILINE)
    allocation = re.findall(r"^\s*(\d+):\s+newarray\s+byte", code, re.MULTILINE)
    bounded = re.findall(r"^\s*(\d+):[^\n]+java/lang/System.arraycopy:", code, re.MULTILINE)
    assert "Exception table:" not in code
    if baseline:
        assert len(copy) == 2 and not allocation and not bounded
    else:
        assert len(allocation) == 1 and len(bounded) == 2 and not copy
        assert int(allocation[0]) < min(map(int, bounded))
    result = dict(priorClones=list(map(int, copy)), oneAllocation=list(map(int, allocation)),
                  boundedCopies=list(map(int, bounded)))
    if not baseline:
        files = []
        for name in TESTS:
            rel = MAIN / "revocation" / (name + ".java")
            files.append(freeze("test", rel, work / "tests-source" / rel))
        junit = TOOLS / "junit-platform-console-standalone-1.13.4.jar"
        anno = repository / "org/jspecify/jspecify/1.0.1/jspecify-1.0.1.jar"
        agent = repository / "org/jacoco/org.jacoco.agent/0.8.15/org.jacoco.agent-0.8.15-runtime.jar"
        cp = os.pathsep.join(map(str, (output, archive, anno, junit)))
        tclasses = work / "test-classes"
        tclasses.mkdir()
        run_cmd("compile-tests", [java / "javac", "--release", "25", "-Xlint:all", "-Werror",
                    "-cp", cp, "-d", tclasses, *files])
        run_cmd("junit", [java / "java", f"-javaagent:{agent}=destfile={work / 'unit.exec'},sessionid={run}",
                    "-cp", str(tclasses) + os.pathsep + cp, "org.junit.platform.console.ConsoleLauncher",
                    "execute", "--disable-ansi-colors", "--fail-if-no-tests",
                    *[item for cls in TESTS for item in ("--select-class", NOTE + cls)], "--reports-dir", work / "reports"])
        tests = work / "reports/TEST-junit-jupiter.xml"
        root = ET.parse(tests).getroot()
        cases = root.findall("testcase")
        assert Counter(x.get("classname") for x in cases) == {NOTE + TESTS[0]: 8, NOTE + TESTS[1]: 5}
        assert all(not any(c.tag in ("failure", "error", "skipped") for c in x) for x in cases)
        assert {key: int(root.attrib[key]) for key in ("tests", "failures", "errors", "skipped")} == {
            "tests": 13, "failures": 0, "errors": 0, "skipped": 0}
        result.update(tests=13, rawXml=pin(tests), rawExec=pin(work / "unit.exec"), scopeTests=TESTS)
    dest = SPEC / run
    dest.mkdir(parents=True)
    write(dest / "manifest.json", dict(
        run=run, actualExit=0, source=source, terminalAtUTC=utc(), inputs=sources,
        compilerPolicy=reference["compilerSettingsSha256"], derivedPom=pin(pom),
        protocolJar=pin(archive), classfile=pin(target), result=result, steps=receipts,
        actualOutOfMemoryTest=False, actualBackendOperations=0, whole451=False, formalDelta=0))
    print(run, result)


if __name__ == "__main__":
    main()
