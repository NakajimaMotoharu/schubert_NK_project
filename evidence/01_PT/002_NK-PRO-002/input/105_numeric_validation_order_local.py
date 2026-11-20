"""Run the fixed numeric precedence case against the exact Protocol sources."""

from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
from xml.etree import ElementTree as XML


ROOT = Path(__file__).resolve().parents[4]
TOOLS = ROOT.parent / "toolchain"
JAVA = TOOLS / "jdk-25.0.4/bin/java"
JUNIT = TOOLS / "junit-platform-console-standalone-1.13.4.jar"
JSPECIFY = TOOLS / "m2/repository/org/jspecify/jspecify/1.0.1/jspecify-1.0.1.jar"
MODULE = Path("src/schubert-nk-protocol")
PKG = "dev.codex.schubert.nk.protocol.codec"
REL = Path(PKG.replace(".", "/"))
TEST = MODULE / "src/test/java" / REL / "FieldCodecTest.java"
ID = "numericDecodeValidatesEveryByteBeforeAccumulatingTheValue"


def now():
    return datetime.now(timezone.utc).isoformat()


def pin(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git(*args):
    return subprocess.check_output(["git", *args], cwd=ROOT, timeout=15)


def main(mode, run):
    assert mode in ("before", "after")
    head = git("rev-parse", "HEAD").decode().strip()
    plan, = (ROOT / "documents/400_PGPT/470_PMO").glob("601_*/1697_*.json")
    ctx = json.loads(plan.read_bytes())["values"]
    assert all(pin(Path(row["path"])) == row["sha256"] for row in ctx["oracleReferences"])
    base = ctx["source"]
    main_inputs = [MODULE / "src/main/java" / REL / (name + ".java")
                   for name in ("FieldCodec", "FieldCodecRules",
                                "FieldEncodingException", "PermanentProtocolException")]
    changed = git("diff", "--name-only", base, head, "--", str(MODULE)).decode().splitlines()
    assert set(changed) == ({TEST.as_posix(), main_inputs[0].as_posix()} if mode == "after" else set())
    work = ROOT.parent / "pgpt-runs/PG379" / run
    work.mkdir(mode=0o700)
    snap = work / "input"
    snap.mkdir()
    inputs = {}
    for rel in [*main_inputs, TEST]:
        before = git("show", f"{head}:{rel}")
        data = (ROOT / rel).read_bytes()
        assert before == data or (mode == "before" and rel == TEST)
        (snap / rel.name).write_bytes(data)
        inputs[str(rel)] = pin(snap / rel.name)
    classes = work / "classes"
    classes.mkdir()
    reports = work / "reports"
    ck = {}

    def execute(name, command):
        args = list(map(str, command))
        began = now()
        result = subprocess.run(args, cwd=work, env={"PATH": os.defpath, "LANG": "C.UTF-8", "TZ": "Asia/Tokyo"},
                                timeout=60, check=False, capture_output=True)
        out, err = work / (name + ".stdout"), work / (name + ".stderr")
        out.write_bytes(result.stdout)
        err.write_bytes(result.stderr)
        ck[name] = dict(command=args, exitCode=result.returncode, beganAtUTC=began, terminalAtUTC=now(),
                        stdout=pin(out), stderr=pin(err))
        (work / (name + "-terminal.json")).write_text(json.dumps(ck[name], indent=2) + "\n")
        return result.returncode

    cp = os.pathsep.join(map(str, (JUNIT, JSPECIFY)))
    assert execute("compile", [JAVA.with_name("javac"), "--release", "25", "-Xlint:all",
                              "-Werror", "-proc:none", "-cp", cp, "-d", classes,
                              *sorted(snap.glob("*.java"))]) == 0
    selector = ["--select-method", PKG + ".FieldCodecTest#" + ID] if mode == "before" else [
        "--select-class", PKG + ".FieldCodecTest"]
    code = execute("junit", [JAVA, "-cp", str(classes) + os.pathsep + cp,
                            "org.junit.platform.console.ConsoleLauncher", "execute", "--disable-banner",
                            "--disable-ansi-colors", "--fail-if-no-tests", *selector, "--reports-dir", reports])
    raw = reports / "TEST-junit-jupiter.xml"
    suite = XML.parse(raw).getroot()
    tests = suite.findall("testcase")
    selected, = [item for item in tests if item.attrib["name"] == ID + "()"]
    outcomes = {key: int(suite.attrib[key]) for key in ("tests", "failures", "errors", "skipped")}
    assert len(tests) == outcomes["tests"]
    if mode == "before":
        assert code == 1 and outcomes == dict(tests=1, failures=1, errors=0, skipped=0)
        assert selected.find("failure").attrib["message"] == (
            "expected: <numeric field contains a non-digit byte> but was: <numeric field overflows signed long>")
    else:
        assert code == 0 and outcomes == dict(tests=8, failures=0, errors=0, skipped=0)
    target = ROOT / "evidence/01_PT/002_NK-PRO-002/evidence" / run
    target.mkdir()
    with (target / "manifest.json").open("x") as obj:
        json.dump(dict(source=head, run=run, mode=mode, unitExit=code, testCounts=outcomes, notRun=0,
                       testId="PT-PRO-002-N03", testMethods=[x.attrib["name"] for x in tests],
                       normalizedDiagnostic=(selected.find("failure").attrib["message"] if mode == "before" else None),
                       inputSHA256=inputs, outputXmlSha256=pin(raw), steps=ck, java="25.0.4",
                       junit="1.13.4", actualBackendActions=0, whole451=False,
                       terminalAtUTC=now(), formalNewAcceptance=0), obj, indent=2)
        obj.write("\n")
    print(outcomes, code)


if __name__ == "__main__":
    main(*sys.argv[1:])
