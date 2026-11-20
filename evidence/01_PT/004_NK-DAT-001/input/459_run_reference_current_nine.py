"""Measure the current nine synthetic JDBC cases in one execution against the packaged DAO."""
from collections import Counter
from datetime import datetime, timezone
from hashlib import sha256
import json
import os
from pathlib import Path
import subprocess
import sys
from xml.etree import ElementTree as ET
from zipfile import ZipFile


def read(path):
    return json.loads(path.read_bytes())


def pin(path):
    return dict(path=str(path), sha256=sha256(path.read_bytes()).hexdigest())


def utc():
    return datetime.now(timezone.utc).isoformat()


def main(recover):
    ctx_path = next(Path("documents/400_PGPT/470_PMO").glob("601_*/1494_*.json"))
    g = read(ctx_path)
    v = g["values"]
    refs = v["oracleReferences"]
    assert all(pin(Path(p["path"])) == p for p in refs)
    old, single, maven = (read(Path(r["path"])) for r in refs[1:])
    assert old["actualExit"] == single["actualExit"] == maven["actualExit"] == 0
    assert old["targetCoverage100"] and old["tests"] == 8 and single["observedJUnit"]["tests"] == 1
    target_name = old["target"]
    suite_name = single["observedCases"][0]["className"]
    old_suite = next(x for x in old["xml"] if x["path"].endswith("TEST-junit-jupiter.xml"))
    assert pin(Path(old_suite["path"])) == old_suite
    expected = Counter((x.attrib["classname"], x.attrib["name"])
                       for x in ET.parse(old_suite["path"]).iter("testcase"))
    extra = single["observedCases"][0]
    expected.update({(extra["className"], extra["method"]): 1})
    assert len(expected) == 9 and all(owner == suite_name for owner, method in expected)
    paths = single["sourceClosure"] + [single["fixture"]]
    for p in paths:
        relative = Path(p["path"])
        frozen = subprocess.check_output(["git", "show", f"{v['productionCoreMain']}:{relative}"], timeout=15)
        assert p == pin(relative) and sha256(frozen).hexdigest() == p["sha256"]
    tools = [Path(item["path"]) for item in single["tools"]]
    assert [pin(p) for p in tools] == single["tools"]
    release, junit, jspecify, agent, cli = tools
    java = release.parent / "bin/java"
    javac = release.parent / "bin/javac"
    env = {"LANG": "C.UTF-8", "TZ": "Asia/Tokyo", "PATH": os.defpath}
    archive = Path("../pgpt-runs/PG379").resolve() / v["run"]
    if recover:
        assert archive.is_dir() and not (archive / "unfiltered.json").exists()
    else:
        archive.mkdir(mode=0o700)
    files = archive / "classes"
    xml_dir = archive / "unit"
    stream = archive / "unit.exec"
    outputs = []

    def run(label, args):
        argv = list(map(str, args))
        if recover and label in ("compile", "unit", "execinfo"):
            saved = read(archive / f"{label}.json")
            assert saved["exitCode"] == 0 and saved["command"] == argv
            for output in ("stdout", "stderr"):
                assert saved[output] == pin(Path(saved[output]["path"]))
            outputs.append(saved)
            return Path(saved["stdout"]["path"]).read_bytes()
        start = utc()
        result = subprocess.run(argv, env=env, capture_output=True, timeout=45, check=False)
        stdout, stderr = [archive / f"{label}.{ext}" for ext in ("stdout", "stderr")]
        stdout.write_bytes(result.stdout)
        stderr.write_bytes(result.stderr)
        step = dict(command=argv, startedAtUTC=start, terminalAtUTC=utc(), exitCode=result.returncode,
                    stdout=pin(stdout), stderr=pin(stderr))
        outputs.append(step)
        (archive / f"{label}.json").write_text(json.dumps(step, indent=2) + "\n")
        if result.returncode:
            raise SystemExit(result.returncode)
        return result.stdout

    run("compile", [javac, "--release", "25", "-g", "-Xlint:all", "-Werror", "-proc:none",
                    "-implicit:none", "-sourcepath", "", "-cp", f"{junit}:{jspecify}", "-d", files,
                    *(p["path"] for p in paths)])
    target = files / (target_name + ".class")
    package_entry = maven["packaged"]["batch"]
    jar_path = Path(package_entry["path"])
    assert pin(jar_path)["sha256"] == package_entry["sha256"]
    with ZipFile(jar_path) as jar:
        package_body = jar.read(target_name + ".class")
    assert package_body == target.read_bytes()
    assert pin(target)["sha256"] == single["scopedDefaultCoverage"]["targetClass"]["sha256"]
    session = "PG41040-RRF-PURE-CURRENT-NINE"
    run("unit", [java, f"-javaagent:{agent}=destfile={stream},append=false,sessionid={session}",
                 "-jar", junit, "execute", "--disable-ansi-colors", "--fail-if-no-tests",
                 "--class-path", f"{files}:{jspecify}", "--select-class", suite_name,
                 "--config=junit.jupiter.execution.parallel.enabled=false", "--reports-dir", xml_dir])
    xml = xml_dir / "TEST-junit-jupiter.xml"
    suite = ET.parse(xml).getroot()
    totals = {name: int(suite.attrib[name]) for name in ("tests", "failures", "errors", "skipped")}
    assert totals == dict(tests=9, failures=0, errors=0, skipped=0)
    assert Counter((x.attrib["classname"], x.attrib["name"]) for x in suite.iter("testcase")) == expected
    streams = run("execinfo", [java, "-jar", cli, "execinfo", stream]).decode().splitlines()
    assert sum(line.startswith(f'Session "{session}":') for line in streams) == 1
    physical = sorted(p for p in files.rglob("*.class")
                      if not p.stem.startswith("RunReferenceRepositoryPureJdbcTest"))
    assert len(physical) == old["scopePhysical"] == 9
    raw = run("unfiltered", [*old["rawCommand"][:4], stream, *physical])
    parsed = {}
    for line in raw.decode().splitlines():
        r = line.split("\t")
        if r[0] == "CLASS":
            assert r[1] not in parsed
            parsed[r[1]] = dict(crc64=r[2], crcMatched=r[3]=="true",
                counters={key: dict(missed=int(missed), covered=int(covered))
                          for key, missed, covered in (field.split(":") for field in r[6:])})
    assert len(parsed) == len(physical)
    own = parsed[target_name]
    assert own["counters"] == old["targetCounters"] and own["crcMatched"]
    assert [pin(Path(p["path"])) for p in paths] == paths
    out = Path("evidence/01_PT/004_NK-DAT-001/evidence") / v["run"]
    out.mkdir()
    public = out / "unfiltered.tsv"
    public.write_bytes(raw)
    post = dict(actualExit=0, source=v["productionCoreMain"], sourceSnapshot=v["source"], run=v["run"],
                startEvent=g["eventId"], terminalAtUTC=utc(), ids=[f"RRF-PURE-{n:03}" for n in range(1,10)],
                sourceInputs=paths, originalReceipts=refs[1:], exactMavenArtifact=package_entry,
                exactMeasuredDao=pin(target), packageEntry=target_name+".class", roster=sorted(expected),
                session=session, xml=pin(xml), exec=pin(stream), raw=pin(public), counts=totals,
                physical=[pin(p) for p in physical], measured=parsed, target=own, steps=outputs,
                inheritedStaticEvidence=old["static"], firstRunSuccess=True, proofOnlyRepeat=False, recoveredOriginalTerminal=recover,
                realDbOrNativeOrLifecycleActions=0, newDefinitions=0, whole451=False, formalDelta=0)
    (out / "manifest.json").write_text(json.dumps(post, ensure_ascii=False, indent=2) + "\n")
    print(totals, own["counters"])


if __name__ == "__main__":
    assert sys.argv[1:] in ([], ["--recover"])
    main(sys.argv[1:] == ["--recover"])
