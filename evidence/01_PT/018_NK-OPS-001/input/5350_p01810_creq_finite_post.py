"""Verify seven existing codec cases, unchanged vectors and finite isolated teardown."""

import gzip
import json
from pathlib import Path
import re
import runpy
import xml.etree.ElementTree as ET


RUN = runpy.run_path(str(Path(__file__).with_name("5349_p01810_creq_finite_scope.py")))
STORE, COMMON, OUTER = (RUN[name] for name in ("STORE", "COMMON", "OUTER"))


def main():
    path = next(STORE.glob("PG40408-*"))
    unit = path / "manifest.json"
    result = json.loads(unit.read_bytes())
    assert result["actualExit"] == 0
    assert result["newProductTests"] == 0
    assert result["stages"]["pmd"]["actualExit"] == 4
    assert all(stage["actualExit"] == 0 for label, stage in result["stages"].items() if label != "pmd")
    pin = COMMON["pin"]
    assert all(pin(Path(row[k]["path"])) == row[k] for row in result["stages"].values()
               for k in ("stdout", "stderr"))
    xml = path / "xml/TEST-junit-jupiter.xml"
    suite = ET.parse(xml).getroot()
    assert [int(suite.get(k)) for k in ("tests", "errors", "failures", "skipped")] == [7, 0, 0, 0]
    cases = {row.get("name") for row in suite.iter("testcase")}
    assert len(cases) == 7 and sorted(name[:7] for name in cases) == [f"creq{i:03}" for i in range(1, 8)]
    assert all(row.get("classname") == RUN["TEST"] for row in suite.iter("testcase"))
    assert not any(node.tag in {"failure", "error", "skipped"} for node in suite.iter())
    assert not list(ET.parse(path / "checkstyle.xml").getroot().iter("error"))
    pm = ET.parse(path / "pmd.xml").getroot()
    decisions = []
    for row in pm.iter():
        tag = row.tag.rsplit("}", 1)[-1]
        assert tag not in {"error", "processingError", "configurationError"}
        if tag != "violation":
            continue
        assert row.get("method") == "creq007ConcurrentIndependentBuffersAndParserLevelReplay"
        rule = row.get("rule")
        assert rule in {"CloseResource", "DoNotUseThreads"}
        reason = (
            "Explicit shutdownNow and bounded awaitTermination verify the owned executor's terminal state."
            if rule == "CloseResource" else
            "The test owns exactly two virtual memory tasks outside any application container.")
        decisions.append(dict(line=int(row.get("beginline")), variable=row.get("variable"), rule=rule,
                              disposition="NOT_APPLICABLE", reason=reason))
    assert sorted(row["rule"] for row in decisions) == ["CloseResource"] + ["DoNotUseThreads"] * 5

    trace = gzip.decompress((path / "class-init.log.gz").read_bytes())
    assert not re.search(rb"Initializing '[^']*(CleanupFailedBackupRequest|CleanupWorkerRequestFiles|NativeIo|RootStartup|org/postgresql|org/apache/activemq)", trace)
    decode = runpy.run_path("tools/quality/jacoco_readonly_exec_subset.py")["decode"]
    execution = path / "jacoco.exec"
    record = decode(execution.read_bytes(), {OUTER})
    assert [row["labelBytesHex"] for row in record["sessions"]] == [result["session"].encode().hex()]
    crc = record["classes"][OUTER]["crc64"]
    assert int(crc, 16) == int(result["inventory"][OUTER]["crc64"], 16)
    coverage = path / "coverage.xml"
    element, = [row for row in ET.parse(coverage).iter("class") if row.get("name") == OUTER]
    counters = {row.get("type"): {k: int(row.get(k)) for k in ("covered", "missed")}
                for row in element.findall("counter")}
    assert all(counters[k]["missed"] == 0 for k in ("LINE", "METHOD", "CLASS", "BRANCH"))
    out = STORE / "PG40410-p01810-creq-worker-bound-independent-v1"
    out.mkdir()
    data = dict(actualExit=0, source=result["source"], productionCore=result["productionCore"],
                existingCasesSorted=sorted(cases), tests=7, failures=0, errors=0, skipped=0,
                notRunInSelectedScope=0, newProductDefinitions=0, productSourceChanged=False,
                positiveOuterCrc=crc, outerStandardXmlCounters=counters, freshSingleSession=result["session"],
                pmdRaw=len(decisions), pmdApplicable=0, pmdUnclassified=0, perSite=decisions,
                noHeldOrExternalInitialization=True, broaderExpiryTestsUsedAsNew=False,
                wholeP01810Accepted=False, whole451Accepted=False, formalDelta=0,
                evidence=list(map(pin, (unit, xml, coverage, execution, path / "pmd.xml"))),
                terminalAtUTC=COMMON["timestamp"]())
    COMMON["dump"](out / "manifest.json", data)
    print(pin(out / "manifest.json"), counters)


if __name__ == "__main__":
    main()
