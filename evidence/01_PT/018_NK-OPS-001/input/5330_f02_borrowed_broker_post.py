"""Bind the borrowed-session exception tests to the current four-module compile."""

from datetime import datetime, timezone
import gzip
from pathlib import Path
import re
import runpy
import xml.etree.ElementTree as ET


RUNNER = runpy.run_path(str(Path(__file__).with_name("5326_f02_group_lookup_upper.py")))
STORE, COMMON = RUNNER["EVIDENCE"], RUNNER["COMMON"]
CLASS = RUNNER["BROKER_CLASS"]
TARGET = CLASS.removesuffix("Test").replace(".", "/")
CASE_NAMES = {
    "PT-OPS-MQ-029": "opsMq029OrderedReadOnlyObservation()",
    "PT-OPS-MQ-030": "opsMq030FailClosedAndNoLaterChecks()",
    "PT-OPS-MQ-031": "opsMq031MalformedPressureAndFatalContracts()",
    "PT-OPS-MQ-OBS-GRAPH-001": "opsMqObsGraph001PreservesFatalFromIsolatedTopologyPort()",
    "PT-OPS-MQ-OBS-GRAPH-002": "opsMqObsGraph002PreservesFatalFromBorrowedDetailedObservation()",
}


def main():
    run = next(STORE.glob("PG40320-*"))
    unit = run / "manifest.json"
    pmd = next(STORE.glob("PG40322-*/manifest.json"))
    pin = COMMON["pin"]
    m, p = map(RUNNER["read"], (unit, pmd))
    assert m["source"] == p["source"] and m["actualExit"] == 0 and p["actualExit"] == 1
    assert m["namedActualHostActions"] == 0 and m["notRun"] == []
    assert p["oldFindings"] == 5 and p["newRawFindings"] == 7
    assert len(p["newlyObserved"]) == 2
    pmd_rules = {r["rule"] for r in p["newlyObserved"]}
    assert pmd_rules == {"CloseResource", "UseProperClassLoader"}
    finding_method = CASE_NAMES["PT-OPS-MQ-OBS-GRAPH-002"].removesuffix("()")
    assert all(r["method"] == finding_method and r["file"] == "ArtemisStartupObservationTest.java"
               and r["count"] == 1 for r in p["newlyObserved"])
    fixture = COMMON["git"]("show", m["source"] + ":" + m["testFixture"]).decode()
    method = fixture.split("void " + finding_method + "()", 1)[1].split(
        "  private static ArtemisReadinessException topologyFailure", 1)[0]
    assert method.count("Proxy.newProxyInstance(") == 1
    assert method.count("ClientSession.class.getClassLoader()") == 1
    assert "throw failure;" in method and '"addressQuery", method.getName()' in method
    assert not any(text in method for text in ("createSession(", "createServerLocator(", "close()"))
    assert len(m["extraDependencies"]) == 5
    assert all(pin(Path(row["path"])) == row and "server" not in Path(row["path"]).name
               for row in m["extraDependencies"])
    assert set(m["stages"]) == {"compile", "format", "checkstyle", "abi-before", "abi-after",
                               "behavior-after", "testcompile", "unit", "coverage"}
    for stage in m["stages"].values():
        assert stage["actualExit"] == 0
        assert all(pin(Path(stage[key]["path"])) == stage[key] for key in ("stdout", "stderr"))
    info = run / "xml/TEST-junit-jupiter.xml"
    root = ET.parse(info).getroot()
    assert [int(root.get(key)) for key in ("tests", "skipped", "errors", "failures")] == [5, 0, 0, 0]
    cases = list(root.iter("testcase"))
    assert {c.get("name") for c in cases} == set(CASE_NAMES.values())
    assert all(c.get("classname") == CLASS and not any(child.tag in ("failure", "error") for child in c)
               for c in cases)
    assert pin(Path(m["compiled"]["path"])) == m["compiled"]
    inventory = RUNNER["read"](m["compiled"]["path"])
    assert sum(inventory["modules"].values()) == 1102
    assert inventory["physicalDelta"] == dict(protocol=[], storage=[], bootstrap=[], batch=[TARGET + ".class"])
    before, after, instructions = [
        gzip.decompress(Path(m["stages"][stage]["stdout"]["path"]).read_bytes())
        for stage in ("abi-before", "abi-after", "behavior-after")
    ]
    assert before == after and instructions.count(b"JdbcFailureGraph.preserveFatal:") == 2
    assert b"StorageIoException" not in instructions
    init = run / "class-init.log.gz"
    trace = gzip.decompress(init.read_bytes())
    assert b"Initializing '" + TARGET.encode() + b"'" in trace
    assert not re.search(rb"Initializing '[^']*(EmbeddedActiveMQ|ClientSessionFactoryImpl|ActiveMQServerImpl)'", trace)
    coverage = run / "coverage.xml"
    counters = {row.get("name"): {metric.get("type"): {k: int(metric.get(k)) for k in ("covered", "missed")}
                                  for metric in row.findall("counter")}
                for row in ET.parse(coverage).iter("class") if row.get("name").startswith(TARGET)}
    physical = inventory["selectedPhysicalCrc"]
    data = run / "jacoco.exec"
    exec_meta = runpy.run_path("tools/quality/jacoco_readonly_exec_subset.py")["decode"](data.read_bytes(), {TARGET})
    assert [entry["labelBytesHex"] for entry in exec_meta["sessions"]] == [m["session"].encode().hex()]
    assert exec_meta["classes"][TARGET]["crc64"] == physical[TARGET]
    result = dict(source=m["source"], productionCore=m["productionCore"], actualExit=0,
                  firstPass=5, selected=5, newProductCases=2, requiredRequalification=3,
                  failed=0, errors=0, skipped=0, notRun=0, cases=CASE_NAMES,
                  changedPhysicalFiles=inventory["physicalDelta"], typedCompileModules=inventory["modules"],
                  privateAndPublicAbiSame=True, newAdapterCalls=2, oldAdapterCallsInTarget=0,
                  pmdRaw=p["newRawFindings"], newPmdFindings=2, newApplicablePmdFindings=0,
                  pmdDisposition={
                      "CloseResource": "The local proxy owns no session or transport and every forwarded call throws before any broker action.",
                      "UseProperClassLoader": "The selected fixed ClientSession interface and its loader are used solely by a plain JUnit JDK Proxy fixture. No Java EE container or context loader is used.",
                  },
                  rawPmdDeltaToolExit=p["actualExit"], pmdRulesOrSuppressionsChanged=False,
                  targetCrc=physical[TARGET],
                  scopedRawCounters=counters, localProxyOnly=True, actualBrokerActions=0,
                  wholeF02Accepted=False, whole451Accepted=False, newFormalAcceptance=0,
                  evidence=[pin(path) for path in (unit, pmd, info, init, coverage, data)],
                  terminalAtUTC=datetime.now(timezone.utc).isoformat())
    out = STORE / "PG40324-f02-borrowed-broker-independent-v1"
    out.mkdir()
    COMMON["dump"](out / "manifest.json", result)
    print(pin(out / "manifest.json"))


if __name__ == "__main__":
    main()
