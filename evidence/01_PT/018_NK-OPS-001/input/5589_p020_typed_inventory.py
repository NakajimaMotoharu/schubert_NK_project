"""Run a new source-inventory regression with the admitted local comparator roster."""

from collections import Counter
from datetime import datetime, timezone
from hashlib import sha256
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET

OPS = Path("evidence/01_PT/018_NK-OPS-001/evidence")
MODULE = Path("program/characterization")
PACKAGE = Path("dev/codex/schubert/characterization")
CORE = MODULE/"src/main/java"/PACKAGE/"GateCli.java"
TEST = MODULE/"tests/java"/PACKAGE/"GateCliTest.java"
TEST_NAME = "dev.codex.schubert.characterization.GateCliTest"
METHOD = "sourceInventoryRejectsWrongJsonTypesEvenWhenTheCountTextMatches"
WORK = Path("../pgpt-runs/PG379").resolve()


def utc():
    return datetime.now(timezone.utc).isoformat()


def pin(path):
    return dict(path=str(path), sha256=sha256(path.read_bytes()).hexdigest())


def dump(path, value):
    with path.open("x") as output:
        json.dump(value, output, ensure_ascii=False, indent=2)
        output.write("\n")


def git(*parts):
    return subprocess.check_output(["git", *parts], timeout=20)


def physical(classe_dir):
    return {path.relative_to(classe_dir).as_posix(): pin(path)["sha256"]
            for path in sorted(classe_dir.rglob("*.class"))}


def parse_report(path):
    xml = ET.parse(path).getroot()
    counts = {key: int(xml.attrib[key]) for key in ("tests", "failures", "errors", "skipped")}
    rows = xml.findall("testcase")
    assert counts["tests"] == len(rows)
    return counts, rows


def main(red):
    cp, = Path("documents/400_PGPT/470_PMO").glob("601_*/1555_*.json")
    group = json.loads(cp.read_bytes())
    values = group["values"]
    assert all(pin(Path(ref["path"])) == ref for ref in values["oracleReferences"])
    prior_path = Path(values["oracleReferences"][1]["path"])
    old = json.loads(prior_path.read_bytes())
    assert old["testExit"] == 0 and old["testCounts"] == dict(tests=213, failures=0, errors=0, skipped=0)
    head = git("rev-parse", "HEAD").decode().strip()
    changed = {TEST} if red else {TEST, CORE}
    assert {Path(name) for name in git("diff", "--name-only", old["source"], head, "--", MODULE)
            .decode().splitlines()} == changed
    assert not git("diff", "--name-only", values["source"], head, "--", "src")
    assert not git("diff", "--name-only", values["productionCoreMain"], head,
                   "--", ":(glob)src/**/src/main/**")
    baseline = git("rev-parse", f"{head}:{MODULE}/baseline/current").decode().strip()
    assert baseline == old["unchangedCurrentTree"]
    run = values["run"] if red else "PG41118-p020-source-count-green-v1"
    work, old_work = WORK/run, WORK/old["run"]
    work.mkdir(mode=0o700)
    snap = work/"snapshot"
    old_snap = old_work/"snapshot"
    steps = {}

    def execute(step, argv, permitted=(0,)):
        argv = list(map(str, argv))
        env = {"JAVA_HOME": str(Path(old["steps"][0]["command"][0]).parents[1]),
               "PATH": os.defpath, "LANG": "C.UTF-8", "TZ": "Asia/Tokyo"}
        start = utc()
        result = subprocess.run(argv, cwd=work, env=env, check=False, capture_output=True, timeout=120)
        stdout, stderr = work/(step+".stdout"), work/(step+".stderr")
        stdout.write_bytes(result.stdout)
        stderr.write_bytes(result.stderr)
        steps[step] = dict(exitCode=result.returncode, command=argv, startedAtUTC=start,
                           terminalAtUTC=utc(), stdout=pin(stdout), stderr=pin(stderr))
        dump(work/(step+"-terminal.json"), steps[step])
        if result.returncode not in permitted:
            raise SystemExit(result.returncode)
        return result.stdout

    inputs = {}
    for name, digest in old["inputSha256"].items():
        rel = Path(name)
        assert rel == Path("pom.xml") or rel.is_relative_to(MODULE)
        assert pin(old_snap/rel)["sha256"] == digest
        dest = snap/rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(git("show", f"{head}:{rel}") if rel in changed else (old_snap/rel).read_bytes())
        inputs[name] = pin(dest)["sha256"]
    commands = {step["step"]: step["command"] for step in old["steps"]}
    classes = snap/MODULE/"target/classes"
    previous_classes = old_snap/MODULE/"target/classes"
    assert physical(previous_classes) == old["physical"]
    if red:
        shutil.copytree(previous_classes, classes)
    else:
        execute("compile-tool", [x.replace(str(old_work), str(work)) for x in commands["compile-tool"]])
    fmt = commands["format"]
    execute("format", [*fmt[:5], *(snap/path for path in sorted(changed))])
    tests = [x.replace(str(old_work), str(work)) for x in commands["compile-test"]]
    if red:
        tests = tests[:12] + [str(snap/TEST)]
    execute("compile-test", tests)
    for path in (work/"tmp", work/"reports"):
        path.mkdir()
    junit = [x.replace(str(old_work), str(work)).replace("PG41028-DUPLICATE-JSON-FIELDS",
             run.split("-")[0]+"-TYPED-SOURCE-INVENTORY") for x in commands["unit"]]
    if red:
        junit = junit[:junit.index("--select-class")] + ["--select-method", TEST_NAME+"#"+METHOD]
    execute("unit", junit, (1,) if red else (0,))
    xml = work/"reports/TEST-junit-jupiter.xml"
    counts, cases = parse_report(xml)
    matches = [row for row in cases if row.attrib["classname"] == TEST_NAME and row.attrib["name"] == METHOD+"()"]
    assert len(matches) == 1
    expected = Counter((row.attrib["classname"], row.attrib["name"]) for row in cases)
    current_physical = physical(classes)
    assert len(current_physical) == 17
    out = OPS/run
    out.mkdir()
    raw = None
    if red:
        assert counts == dict(tests=1, failures=1, errors=0, skipped=0)
        assert "nothing was thrown" in matches[0].find("failure").attrib["message"]
    else:
        old_xml = Path(old["xml"]["path"])
        assert pin(old_xml) == old["xml"]
        previous_cases = parse_report(old_xml)[1]
        assert counts == dict(tests=214, failures=0, errors=0, skipped=0)
        assert expected == Counter((row.attrib["classname"], row.attrib["name"]) for row in previous_cases) + Counter({
            (TEST_NAME, METHOD+"()"): 1})
        for name, digest in old["physical"].items():
            if not Path(name).name.startswith("GateCli"):
                assert current_physical[name] == digest
        result = execute("unfiltered", [*commands["unfiltered"][:4], work/"unit.exec",
                         *(classes/name for name in current_physical)])
        raw_path = out/"unfiltered.tsv"
        raw_path.write_bytes(result)
        raw = pin(raw_path)
    assert all(pin(snap/name)["sha256"] == digest for name,digest in inputs.items())
    m = out/"manifest.json"
    dump(m, dict(actualExit=int(red), source=head, productionCore=values["productionCoreMain"],
                 run=run, startEvent=group["eventId"], observedTestCounts=counts, prior=pin(prior_path),
                 testId="PT-CHR-VERIFY-TYPE001", regressionScope=20 if not red else 1,
                 missingOwnedActualFileStoreFromLocalRun=True, whole451=False, realChr=False,
                 noProducts=0, baselineTree=baseline, oldExecCombined=False,
                 inputSha256=inputs, physical=current_physical,
                 execData=pin(work/"unit.exec"), junit=pin(xml), raw=raw, steps=steps, terminalAtUTC=utc()))
    print(pin(m), counts)


if __name__ == "__main__":
    main({"red": True, "green": False}[sys.argv[1]])
