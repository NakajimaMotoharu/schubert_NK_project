"""Execute the current AlertThresholds against independent, adjacent int64 queue values."""

from datetime import datetime, timezone
import hashlib
from pathlib import Path
import re
import runpy
import subprocess
from tempfile import TemporaryDirectory
from xml.etree import ElementTree as XML
from zipfile import ZipFile


common = runpy.run_path(str(Path(__file__).with_name("5391_f03_storage_current_two_junit.py")))
pin, checked, read, write, run = (common[k] for k in ("pin", "checked", "read", "write", "run"))
PLAN, OPS, ROOT, JAVA, AGENT, JUNIT, TOOLS = (common[k] for k in ("PLAN", "OPS", "ROOT", "JAVA", "AGENT", "JUNIT", "TOOLS"))
PKG = "dev.codex.schubert.nk.batch.monitoring"
CLASS = PKG.replace(".", "/") + "/AlertThresholds.class"
SEVERITY = PKG.replace(".", "/") + "/AlertLifecycle$Severity.class"
FIXTURE = Path("src/schubert-nk-batch/src/test/java") / PKG.replace(".", "/") / "AlertThresholdsTest.java"
ID = "PT-OPS-THRESH-015"


def source(ref, path):
    return subprocess.check_output(["git", "show", f"{ref}:{path}"])


def main():
    start = read(next(PLAN.glob("1012_*")))["values"]
    refs = [checked(ref) for ref in start["oracleReferences"]]
    original = read(refs[1])
    core = start["productionCoreMain"]
    assert original["tests"] == 14 and original["actualExit"] == 0
    artifact = checked(read(refs[2])["packagedBuild"]["batch"]["artifact"])
    cp = common["bin_report"](refs[3])
    unit = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    assert not subprocess.check_output(["git", "diff", "--name-only", core, unit, "--",
                                        ":(glob)src/**/src/main/**"])
    fixture = source(unit, FIXTURE)
    unchanged = source(start["source"], FIXTURE)
    new_cases = re.findall(rb"@Test\s+void\s+(\w+)\(", fixture)
    old_cases = re.findall(rb"@Test\s+void\s+(\w+)\(", unchanged)
    assert len(new_cases) == 15 and len(old_cases) == 14 and set(old_cases) < set(new_cases)
    assert set(new_cases) - set(old_cases) == {b"threshold015AsyncByteRatiosDistinguishAdjacentValuesAtLongCapacity"}
    cap = 2**63 - 1
    expected = []
    for percent, below_label, at_label in ((70, "NORMAL", "WARNING"), (90, "WARNING", "CRITICAL")):
        minimum = (percent * cap + 99) // 100
        assert (minimum - 1) * 100 < percent * cap <= minimum * 100
        assert float(minimum - 1) == float(minimum)
        expected += [dict(testId=ID, percentage=percent, queuedMessages=0, usedBytes=minimum-1, expected=below_label),
                     dict(testId=ID, percentage=percent, queuedMessages=0, usedBytes=minimum, expected=at_label)]
    for row in expected:
        literal = f"{row['usedBytes']:,}".replace(",", "_").encode()
        assert literal+b"L, capacity" in fixture
    out = (OPS / start["run"]).resolve()
    out.mkdir()
    local = ROOT.parent / "pgpt-runs/PG379/pg40636-c07-async-int64-retained-v1"
    local.mkdir(mode=0o700)
    session = "PG40636-C07-ASYNC-INT64"
    receipts = {}
    with TemporaryDirectory(dir="/dev/shm", prefix="pgpt-c07-threshold-") as name:
        root = Path(name)
        main_classes = root / "classes"
        with ZipFile(artifact) as jar:
            for n in (CLASS, SEVERITY):
                path = main_classes / n
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(jar.read(n))
        test = root / FIXTURE.name
        test.write_bytes(fixture)
        built = root / "fixture-classes"
        receipts["compile"] = run([JAVA.with_name("javac"), "--release", "25", "-Xlint:all",
                                   "-Werror", "-proc:none", "-cp", f"{main_classes}:{JUNIT}",
                                   "-d", built, test], root, out, "compile")
        assert receipts["compile"]["actualExit"] == 0
        exec_path = local / "jacoco.exec"
        reports = local / "xml"
        receipts["unit"] = run([JAVA, f"-javaagent:{AGENT}=destfile={exec_path},sessionid={session},append=false,includes={PKG}.AlertThresholds",
                                "-jar", JUNIT, "execute", "--disable-banner", "--disable-ansi-colors",
                                "--class-path", f"{main_classes}:{built}", "--reports-dir", reports,
                                "--select-class", PKG+".AlertThresholdsTest"], root, out, "unit")
        assert receipts["unit"]["actualExit"] == 0
        xml = reports / "TEST-junit-jupiter.xml"
        suite = XML.parse(xml).getroot()
        cases = sorted(node.get("name").removesuffix("()") for node in suite.findall("testcase"))
        assert set(cases)=={n.decode() for n in new_cases} and len(cases)==15
        assert all(int(suite.get(k))==0 for k in ("failures", "errors", "skipped"))
        receipts["raw"] = run([JAVA, "-cp", cp, "org.jacoco.core.internal.analysis.UnfilteredCodeMeasurement",
                               exec_path, main_classes / CLASS], root, out, "unfiltered")
        assert receipts["raw"]["actualExit"] == 0
        raw = Path(receipts["raw"]["stdout"]["path"]).read_text()
        classes = [line.split("\t") for line in raw.splitlines() if line.startswith("CLASS\t")]
        assert len(classes)==1 and classes[0][1]+".class"==CLASS
        counts = {item.split(":")[0]: list(map(int, item.split(":")[1:])) for item in classes[0][6:]}
        assert all(miss==0 for miss, _ in counts.values())
        did = pin(main_classes / CLASS)["sha256"]
    result = out / "manifest.json"
    write(result, dict(actualExit=0, productionCore=core, testSource=unit, tests=15, newDefinitions=1,
                       failed=0, errors=0, skipped=0, notRun=0, cases=cases, inputFour=expected,
                       allCovered=True, individualRaw=counts, currentJvmCrc=classes[0][2], exactSha=did,
                       fixtureSha=hashlib.sha256(fixture).hexdigest(), currentBatchJar=pin(artifact),
                       originalEvidence=pin(refs[1]), session=session, exec=pin(exec_path), xml=pin(xml),
                       receipts=receipts, noExternalRuntime=0, oldExecMerge=False, wholeC07Accepted=False,
                       whole451Accepted=False, terminalAtUTC=datetime.now(timezone.utc).isoformat()))
    print(pin(result), counts)


if __name__ == "__main__":
    main()
