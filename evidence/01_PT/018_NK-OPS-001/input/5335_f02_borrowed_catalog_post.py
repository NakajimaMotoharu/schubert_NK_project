"""Verify the two complete local Artemis fixture suites and the four migrated call sites."""

from datetime import datetime, timezone
import gzip
from pathlib import Path
import re
import runpy
import xml.etree.ElementTree as ET


RUNNER = runpy.run_path(str(Path(__file__).with_name("5326_f02_group_lookup_upper.py")))
STORE, COMMON, PLAN = (RUNNER[key] for key in ("EVIDENCE", "COMMON", "PLAN"))
PACKAGE = "dev.codex.schubert.nk.batch.mq."
EXPECTED = {PACKAGE + "ArtemisCatalogFatalBoundaryTest": 5, PACKAGE + "TopologyQueryPortTest": 6}


def main():
    run = next(STORE.glob("PG40338-*"))
    unit = run / "manifest.json"
    pmd = next(STORE.glob("PG40340-*/manifest.json"))
    read, pin = RUNNER["read"], COMMON["pin"]
    m, p = map(read, (unit, pmd))
    assert m["source"] == p["source"] == m["productionCore"]
    assert m["actualExit"] == p["actualExit"] == 0 and m["notRun"] == []
    assert p["newlyObserved"] == [] and p["newRawFindings"] == p["oldFindings"]
    assert len(m["extraDependencies"]) == 5 and all("server" not in entry["path"] for entry in m["extraDependencies"])
    assert all(stage["actualExit"] == 0 and all(pin(Path(stage[key]["path"])) == stage[key]
                                                for key in ("stdout", "stderr"))
               for stage in m["stages"].values())
    start = read(next(PLAN.glob("788_*")))["values"]
    for unit_ref in start["oracleReferences"]:
        path = unit_ref["path"]
        if path in start["tests"]:
            for commit in (start["source"], m["source"]):
                assert COMMON["sha"](COMMON["git"]("show", commit + ":" + path)) == unit_ref["sha256"]
    report = run / "xml/TEST-junit-jupiter.xml"
    suite = ET.parse(report).getroot()
    assert [int(suite.get(key)) for key in ("tests", "skipped", "errors", "failures")] == [11, 0, 0, 0]
    cases = {name: [] for name in EXPECTED}
    for row in suite.iter("testcase"):
        cases[row.get("classname")].append(row.get("name"))
    assert {name: len(set(items)) for name, items in cases.items()} == EXPECTED
    assert not any(node.tag in {"failure", "error", "skipped"} for node in suite.iter())
    assert pin(Path(m["compiled"]["path"])) == m["compiled"]
    compiled = read(m["compiled"]["path"])
    expected_changes = [path.split("/src/main/java/")[1].removesuffix(".java")
                        for path in start["targets"]]
    assert sum(compiled["modules"].values()) == 1102
    assert compiled["physicalDelta"] == dict(protocol=[], storage=[], bootstrap=[],
                                             batch=sorted(name + ".class" for name in expected_changes))
    abi_before, abi_after, instructions = [
        gzip.decompress(Path(m["stages"][s]["stdout"]["path"]).read_bytes())
        for s in ("abi-before", "abi-after", "behavior-after")]
    assert abi_before == abi_after
    assert instructions.count(b"JdbcFailureGraph.preserveFatal:") == 4
    assert b"StorageIoException" not in instructions
    init = run / "class-init.log.gz"
    trace = gzip.decompress(init.read_bytes())
    assert not re.search(rb"Initializing '[^']*(EmbeddedActiveMQ|ClientSessionFactoryImpl|ActiveMQServerImpl)'", trace)
    assert all(b"Initializing '" + name.encode() + b"'" in trace for name in expected_changes)
    data = run / "jacoco.exec"
    decode = runpy.run_path("tools/quality/jacoco_readonly_exec_subset.py")["decode"]
    observed = decode(data.read_bytes(), set(expected_changes))
    assert [s["labelBytesHex"] for s in observed["sessions"]] == [m["session"].encode().hex()]
    crc = {name: value["crc64"] for name, value in observed["classes"].items()}
    assert crc == {name: compiled["selectedPhysicalCrc"][name] for name in expected_changes}
    coverage = run / "coverage.xml"
    counters = {row.get("name"): {metric.get("type"): {k: int(metric.get(k)) for k in ("covered", "missed")}
                                  for metric in row.findall("counter")}
                for row in ET.parse(coverage).iter("class") if row.get("name") in expected_changes}
    result = dict(actualExit=0, source=m["source"], productionCore=m["productionCore"],
                  firstPass=11, selected=11, requiredRequalification=11, newProductCases=0,
                  failed=0, errors=0, skipped=0, notRun=0, cases=cases,
                  privateAndPublicAbiSame=True, newAdapterCalls=4, oldAdapterCallsInTarget=0,
                  physicalDelta=compiled["physicalDelta"], physicalReadinessCrc=crc,
                  pmdRaw=p["newRawFindings"], newPmdFindings=0, partialRawCoverage=counters,
                  actualBrokerActions=0, embeddedBrokerInitialized=False,
                  wholeF02Accepted=False, whole451Accepted=False, newFormalAcceptance=0,
                  evidence=[pin(path) for path in (unit, pmd, report, init, coverage, data)],
                  terminalAtUTC=datetime.now(timezone.utc).isoformat())
    out = STORE / "PG40342-f02-borrowed-catalog-independent-v1"
    out.mkdir()
    COMMON["dump"](out / "manifest.json", result)
    print(pin(out / "manifest.json"))


if __name__ == "__main__":
    main()
