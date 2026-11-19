"""Qualify the new public checkpoint bytecode and four preexisting local assertions."""

from collections import Counter
import gzip
from pathlib import Path
import re
import runpy
import xml.etree.ElementTree as ET


RUNNER = runpy.run_path(str(Path(__file__).with_name("5326_f02_group_lookup_upper.py")))
OPS, STORE, COMMON, PLAN = (RUNNER[key] for key in ("OPS", "EVIDENCE", "COMMON", "PLAN"))


def main():
    read, pin, git, sha = RUNNER["read"], *(COMMON[key] for key in ("pin", "git", "sha"))
    start = read(next(PLAN.glob("812_*")))["values"]
    run = STORE / start["run"]
    unit = run / "manifest.json"
    pmd = next(STORE.glob("PG40376-*/manifest.json"))
    m, p = map(read, (unit, pmd))
    assert m["source"] == p["source"] == m["productionCore"]
    assert m["actualExit"] == p["actualExit"] == 0 and m["notRun"] == []
    assert p["oldFindings"] == p["newRawFindings"] and not p["newlyObserved"]
    for key, stage in m["stages"].items():
        assert stage["actualExit"] == 0, key
        assert all(pin(Path(stage[name]["path"])) == stage[name] for name in ("stdout", "stderr"))
    for ref in start["oracleReferences"]:
        path = ref["path"]
        if path in start["targets"]:
            continue
        assert pin(Path(path)) == ref
        if path in start["tests"]:
            assert all(sha(git("show", f"{commit}:{path}")) == ref["sha256"]
                       for commit in (start["source"], m["source"]))
    package = "dev.codex.schubert.nk.bootstrap."
    selected = package + "CheckpointFatalBoundaryTest"
    target = package + "FixedNativeCoverageCheckpoint$PublicAgent"
    assert m["selectedTests"] == ["--select-class=" + selected]
    archive = read(start["oracleReferences"][3]["path"])
    original_test = package.replace(".", "/") + "FixedNativeCoverageCheckpointTest"
    archive_items = {original_test + suffix + ".class" for suffix in ("", "$PublicFixture", "$PublicRtFixture")}
    assert set(m["companionClasses"]) == archive_items
    for name, row in m["companionClasses"].items():
        assert pin(Path(row["path"])) == row
        assert row["sha256"] == archive["testPhysicalHashes"][name]

    report = run / "xml/TEST-junit-jupiter.xml"
    suite = ET.parse(report).getroot()
    assert [int(suite.get(key)) for key in ("tests", "failures", "errors", "skipped")] == [4, 0, 0, 0]
    actual = Counter((row.get("classname"), row.get("name")) for row in suite.iter("testcase"))
    historical = read(start["oracleReferences"][4]["path"])
    expected = Counter((row["classname"], row["name"]) for row in historical["cases"]
                       if row["classname"] == selected and row["result"] == "PASS")
    assert actual == expected and len(actual) == 4
    assert not any(row.tag in {"failure", "error", "skipped"} for row in suite.iter())

    compiled = read(m["compiled"]["path"])
    assert pin(Path(m["compiled"]["path"])) == m["compiled"]
    assert sum(compiled["modules"].values()) == 1102
    class_name = target.replace(".", "/")
    assert compiled["physicalDelta"] == dict(protocol=[], storage=[], bootstrap=[class_name + ".class"], batch=[])
    abi_before, abi_after, code = (
        gzip.decompress(Path(m["stages"][stage]["stdout"]["path"]).read_bytes())
        for stage in ("abi-before", "abi-after", "behavior-after"))
    assert abi_before == abi_after
    assert code.count(b"JdbcFailureGraph.preserveFatal:") == 3 and b"StorageIoException" not in code
    init = run / "class-init.log.gz"
    trace = gzip.decompress(init.read_bytes())
    assert b"Initializing '" + class_name.encode() + b"'" in trace
    assert not re.search(rb"Initializing '[^']*(NativeCoveragePrivateFile|FixedServiceIdentity\$NativeQuery|org/jacoco/agent/rt/RT)", trace)
    data = run / "jacoco.exec"
    decode = runpy.run_path("tools/quality/jacoco_readonly_exec_subset.py")["decode"]
    observed = decode(data.read_bytes(), {class_name})
    assert [row["labelBytesHex"] for row in observed["sessions"]] == [m["session"].encode().hex()]
    crc = observed["classes"][class_name]["crc64"]
    assert crc == compiled["selectedPhysicalCrc"][class_name]
    coverage = run / "coverage.xml"
    row, = [row for row in ET.parse(coverage).iter("class") if row.get("name") == class_name]
    counters = {counter.get("type"): {key: int(counter.get(key)) for key in ("covered", "missed")}
                for counter in row.findall("counter")}
    result = dict(actualExit=0, source=m["source"], productionCore=m["productionCore"],
                  firstPass=4, selected=4, requiredRequalification=4, newProductCases=0,
                  failed=0, errors=0, skipped=0, notRun=0, cases=sorted(name for _, name in actual),
                  privateAndPublicAbiSame=True, newAdapterCalls=3,
                  physicalDelta=compiled["physicalDelta"], physicalCrc={class_name: crc},
                  pmdRaw=p["newRawFindings"], newPmdFindings=0, rawCoverage=counters,
                  actualNativeAgentAuthorizationOrExport=False, heldTypesInitialized=False,
                  wholeF02Accepted=False, wholeP01808Accepted=False, whole451Accepted=False, newFormalAcceptance=0,
                  evidence=[pin(path) for path in (unit, pmd, report, init, coverage, data)],
                  terminalAtUTC=COMMON["timestamp"]())
    out = STORE / "PG40378-f02-public-checkpoint-independent-v1"
    out.mkdir()
    COMMON["dump"](out / "manifest.json", result)
    print(pin(out / "manifest.json"))


if __name__ == "__main__":
    main()
