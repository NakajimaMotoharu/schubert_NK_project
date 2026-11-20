"""Run the two pure question-form / QSSREQ01 cases against the pinned Protocol JAR."""

from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
import json
import os
import platform
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
from zipfile import ZipFile


ROOT = Path(__file__).resolve().parents[4]
SDK = ROOT.parent / "toolchain"
OPS = ROOT / "evidence/01_PT/018_NK-OPS-001/evidence"
BASE = "ae02f5e5dce5ea5af6c533715c5db84a586948e2"
CORE = "517a23cddc9f3883550942f6fa90a4256ef39b73"
RUN = "PG40746-question-search-composite-wire-v2"
FORM = Path("src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/form/QuestionSearchForm.java")
TEST = Path("tools/quality/architecture/QuestionSearchCompositeWireContractTest.java")
SUITE = "dev.codex.schubert.nk.web.form.QuestionSearchCompositeWireContractTest"
CASES = {
    "qsformWire001BothNormalizedMaximaKeepAdjacentFieldsAndPadding()": "QSFORM-WIRE-001",
    "qsformWire002EachOverflowWithTheOtherFieldAtItsMaximumStopsAtBinding()": "QSFORM-WIRE-002",
}


def proof(path):
    return {"path": str(path), "sha256": sha256(path.read_bytes()).hexdigest()}


def now():
    return datetime.now(timezone.utc).isoformat()


def main(output):
    output.mkdir()
    begin = now()
    old = OPS / "PG37950-search-three-current38-independent-v1/manifest.json"
    binder = OPS / "PG37940-search-three-current38-closure-v1/manifest.json"
    build = OPS / "PG40744-f02-cleanup-terminal-current-four-jars-v1/manifest.json"
    current = json.loads(build.read_text())
    artifact = current["privateJars"]["protocol"]["artifact"]
    protocol = Path(artifact["path"])
    assert current["candidateProductionSource"] == CORE
    assert proof(protocol) == artifact
    expected = {
        name: digest
        for name, digest in json.loads(old.read_text())["allPhysicalHashes"].items()
        if "/protocol/" in name
    }
    with ZipFile(protocol) as jar:
        actual = {
            name: sha256(jar.read(name)).hexdigest()
            for name in jar.namelist()
            if name.endswith(".class")
        }
    assert len(actual) == 176 and actual == expected
    form_hash = proof(ROOT / FORM)["sha256"]
    assert json.loads(binder.read_text())["inputHashes"][str(FORM)] == form_hash
    for source in [BASE, CORE]:
        data = subprocess.check_output(["git", "show", f"{source}:{FORM}"], cwd=ROOT)
        assert sha256(data).hexdigest() == form_hash
    java = SDK / "jdk-25.0.4/bin/java"
    javac = SDK / "jdk-25.0.4/bin/javac"
    junit = SDK / "junit-platform-console-standalone-1.13.4.jar"
    specify = SDK / "m2/repository/org/jspecify/jspecify/1.0.1/jspecify-1.0.1.jar"
    style = SDK / "static-gates-20261015/checkstyle-14.3.0-all.jar"
    style_config = ROOT / "tools/quality/static/checkstyle.xml"
    steps = {}
    cases = []
    style_errors = None
    code = 1
    with tempfile.TemporaryDirectory(prefix="pg40746-", dir="/dev/shm") as location:
        temp = Path(location)
        classes = temp / "classes"
        classes.mkdir()
        env = {"PATH": os.defpath, "LANG": "C.UTF-8", "HOME": str(temp), "TZ": "Asia/Tokyo"}

        def command(label, *args):
            resolved = list(map(str, args))
            proc = subprocess.run(
                resolved, cwd=ROOT, env=env, text=True, capture_output=True, timeout=45
            )
            steps[label] = {"command": resolved, "exitCode": proc.returncode}
            if proc.returncode:
                print(proc.stdout + proc.stderr, file=sys.stderr)
                raise subprocess.CalledProcessError(proc.returncode, resolved)
            return proc.stdout or proc.stderr

        try:
            jdk_version = command("jdk", java, "--version").splitlines()[0]
            classpath = os.pathsep.join(map(str, (classes, protocol, specify, junit)))
            command(
                "compile", javac, "--release", "25", "-Xlint:all", "-Werror", "-proc:none",
                "-g", "-classpath", classpath, "-d", classes, FORM, TEST,
            )
            report = temp / "checkstyle.xml"
            command(
                "checkstyle", java, "-jar", style, "-c", style_config, "-f", "xml",
                "-o", report, TEST,
            )
            style_errors = len(ET.parse(report).findall(".//error"))
            reports = temp / "results"
            try:
                command(
                    "test", java, "-jar", junit, "execute", "--disable-banner",
                    "--disable-ansi-colors", "--class-path", classpath, "--select-class", SUITE,
                    "--reports-dir", reports, "--fail-if-no-tests",
                )
            finally:
                result = reports / "TEST-junit-jupiter.xml"
                if result.is_file():
                    for case in ET.parse(result).findall("testcase"):
                        assert case.get("classname") == SUITE
                        cases.append({
                            "method": case.get("name"),
                            "testId": CASES[case.get("name")],
                            "outcome": next(
                                (kind for kind in ("failure", "error", "skipped")
                                 if case.find(kind) is not None), "pass"
                            ),
                        })
            assert len(cases) == len(CASES)
            assert {case["testId"] for case in cases} == set(CASES.values())
            assert all(case["outcome"] == "pass" for case in cases) and style_errors == 0
            code = 0
        finally:
            result = {
                "run": RUN, "branch": "dev-foundation", "snapshot": BASE, "sourceCore": CORE,
                "startedAtUTC": begin, "terminalAtUTC": now(), "actualExit": code,
                "os": platform.platform(), "jdk": locals().get("jdk_version"),
                "steps": steps, "cases": cases, "expectedTests": len(CASES),
                "passed": sum(case["outcome"] == "pass" for case in cases),
                "notRun": len(CASES) - len(cases), "checkstyleFindings": style_errors,
                "inputHashes": [proof(path) for path in
                                [Path(__file__), ROOT / FORM, ROOT / TEST, old, binder, build,
                                 style_config, java, javac, junit, specify, style, protocol]],
                "protocolClassesByteIdentical": len(actual), "coverage": None,
                "whole451": False, "newFormalAcceptance": 0,
            }
            (output / "manifest.json").write_text(json.dumps(result, indent=2) + "\n")


if __name__ == "__main__":
    main(Path(sys.argv[1]).resolve())
