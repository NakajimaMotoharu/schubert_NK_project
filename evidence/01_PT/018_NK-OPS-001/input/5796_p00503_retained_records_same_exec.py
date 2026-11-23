"""Verify the two record observations with the twelve approved local cases in one JVM."""

from pathlib import Path
import runpy
import subprocess
from xml.etree import ElementTree as ET


EARLIER = runpy.run_path(str(Path(__file__).with_name("5795_p00503_jms_proxy_fixture_quality.py")))
ROOT, RUNS, RECORDS = (EARLIER[k] for k in ("ROOT", "RUNS", "RECORDS"))
get, pin, git, now, put, manifest = (EARLIER[k] for k in ("get", "pin", "git", "now", "put", "manifest"))
OLD = EARLIER["RUN_AFTER"]
RUN = "PG43204-p00503-guard-dlq-record-observations-v1"
NEW = (
    ("dev.codex.schubert.nk.api.messaging.guard.JmsMessageGuardTest",
     "retainedSnapshotRemainsFindableAfterCallerCopiesChange()"),
    ("dev.codex.schubert.nk.api.messaging.outbound.FatalDlqMessageWriterTest",
     "fatalMetadataRetainsOnlyTheSpecifiedNonSecretValues()"),
)


def main():
    point, = RECORDS.glob("3472_*")
    state = get(point)["values"]
    core = state["productionCoreMain"]
    head = git("rev-parse", "HEAD").decode().strip()
    assert state["run"] == RUN
    proof, record = manifest("PG43202")
    assert record["productCore"] == core and record["actualExit"] == 0 and record["tests"] == 12
    private = RUNS / OLD
    old_begin = private / "begin.json"
    stored = record["commandReceipt"]
    assert old_begin.resolve() == Path(stored["path"]).resolve()
    assert pin(old_begin)["sha256"] == stored["sha256"]
    before = get(old_begin)
    assert all(pin(p["path"]) == p for p in before["dependencies"])
    files = []
    for ref in before["sources"]:
        path = Path(ref["path"])
        data = path.read_bytes()
        assert data == git("show", f"{head}:{path}")
        if "/main/" in path.as_posix():
            assert pin(path) == ref and data == git("show", f"{core}:{path}")
        else:
            assert pin(path) != ref
            files.append(path)
    assert len(files) == 2
    out = RUNS / RUN
    out.mkdir(mode=0o700)
    for name in ("target/classes", "test", "xml", "meter"):
        (out / name).mkdir(parents=True)
    for ref in record["currentPhysical"]:
        item = Path("target/classes") / ref["className"]
        old = private / item
        assert pin(old)["sha256"] == ref["sha256"]
        copied = out / item
        copied.parent.mkdir(exist_ok=True, parents=True)
        copied.write_bytes(old.read_bytes())
        assert pin(copied)["sha256"] == ref["sha256"]
    wanted = ("format", "fixtures", "style", "spotbugs", "pmd", "junit", "rawCompile", "unfiltered")
    commands = {key: [a.replace(OLD, RUN) for a in before["commands"][key]] for key in wanted}
    (out / "current-static-sources.txt").write_text("".join(f"{x}\n" for x in files))
    put(out / "begin.json", dict(run=RUN, source=head, productCore=core, startedAtUTC=now(), commands=commands,
        scopedInputs=list(map(pin, files)), physical=record["currentPhysical"], previous=pin(proof)))
    exits = {}
    for key, cmd in commands.items():
        result = subprocess.run(cmd, cwd=ROOT, capture_output=True, timeout=120, check=False)
        (out / f"{key}.stdout").write_bytes(result.stdout)
        (out / f"{key}.stderr").write_bytes(result.stderr)
        exits[key] = result.returncode
        print(key, result.returncode, flush=True)
        assert result.returncode in {"spotbugs": {0, 1}, "pmd": {0, 4}}.get(key, {0}), key
    junit = out / "xml/TEST-junit-jupiter.xml"
    xml = ET.parse(junit).getroot()
    assert xml.get("tests") == "14" and all(xml.get(k) == "0" for k in ("failures", "errors", "skipped"))
    cases = {(case.get("classname"), case.get("name")) for case in xml.findall("testcase")}
    original = {tuple(x) for x in before["expectedCases"]}
    assert cases == original.union(NEW) and len(original) == 12
    spot = ET.parse(out / "spotbugs.xml").getroot()
    assert not spot.findall("./Errors/Error") and not spot.findall("./Errors/MissingClass")
    findings = [x.get("type") for x in spot.findall("BugInstance")]
    violations = [x.get("rule") for x in ET.parse(out / "pmd.xml").findall(".//{*}violation")]
    put(out / "terminal.json", dict(run=RUN, source=head, productCore=core, terminalAtUTC=now(), actualExit=0,
        scopedCases=sorted(cases), new=NEW, stages=exits, spotBugs=findings, pmd=violations, ordinaryScopeOnly=True,
        evidence=list(map(pin, (junit, out / "unit.exec", out / "unfiltered.stdout")))))
    print(len(cases), len(findings), len(violations))


if __name__ == "__main__":
    main()
