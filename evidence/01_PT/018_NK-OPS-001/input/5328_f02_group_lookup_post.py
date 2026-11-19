"""Check the actual selected GID run, narrow binary edge and remaining scope."""

from datetime import datetime, timezone
import gzip
import json
from pathlib import Path
import re
import runpy
import xml.etree.ElementTree as ET


RUNNER = runpy.run_path(str(Path(__file__).with_name("5326_f02_group_lookup_upper.py")))
STORE, COMMON = RUNNER["EVIDENCE"], RUNNER["COMMON"]
CLASS = RUNNER["CLASS"]
TARGET = CLASS.removesuffix("Test").replace(".", "/")


def main():
    run = next(STORE.glob("PG40308-*"))
    unit = run / "manifest.json"
    pmd = next(STORE.glob("PG40310-*/manifest.json"))
    pin, dump = COMMON["pin"], COMMON["dump"]
    m, p = map(RUNNER["read"], (unit, pmd))
    assert m["source"] == p["source"] and m["actualExit"] == p["actualExit"] == 0
    assert set(m["stages"]) == {"compile", "format", "checkstyle", "abi-before", "abi-after",
                               "behavior-after", "testcompile", "unit", "coverage"}
    for stage in m["stages"].values():
        assert stage["actualExit"] == 0
        for key in ("stdout", "stderr"):
            assert pin(Path(stage[key]["path"])) == stage[key]
    assert p["newlyObserved"] == [] and p["oldFindings"] == p["newRawFindings"] == 34
    assert all(stage["actualExit"] == 4 for stage in p["stages"].values())
    report = run / "xml/TEST-junit-jupiter.xml"
    root = ET.parse(report).getroot()
    assert [int(root.get(k)) for k in ("tests", "skipped", "errors", "failures")] == [8, 0, 0, 0]
    cases = list(root.iter("testcase"))
    assert sorted(c.get("name") for c in cases) == sorted(s + "()" for s in RUNNER["METHODS"])
    assert all(c.get("classname") == CLASS for c in cases)
    assert m["notRun"] == ["nativeFactory"] and m["namedActualHostActions"] == 0
    assert pin(Path(m["compiled"]["path"])) == m["compiled"]
    compiled = RUNNER["read"](m["compiled"]["path"])
    assert sum(compiled["modules"].values()) == 1102
    assert compiled["physicalDelta"] == dict(protocol=[], storage=[], bootstrap=[],
                                             batch=[TARGET + ".class"])
    abi_before, abi_after, instructions = [
        gzip.decompress(Path(m["stages"][s]["stdout"]["path"]).read_bytes())
        for s in ("abi-before", "abi-after", "behavior-after")
    ]
    assert abi_before == abi_after
    assert instructions.count(b"JdbcFailureGraph.preserveFatal:") == 2
    assert b"StorageIoException" not in instructions
    init = run / "class-init.log.gz"
    initialized = gzip.decompress(init.read_bytes())
    assert b"Initializing '" + TARGET.encode() + b"'" in initialized
    assert b"Initializing '" + TARGET.encode() + b"$NativeProcess'" not in initialized
    assert not re.search(rb"Initializing 'dev/codex/schubert/nk/(web/|api/(?!bootstrap/))", initialized)
    coverage = run / "coverage.xml"
    raw = {row.get("name"): {k.get("type"): dict(hit=int(k.get("covered")), miss=int(k.get("missed")))
                             for k in row.findall("counter")}
           for row in ET.parse(coverage).iter("class") if row.get("name").startswith(TARGET)}
    assert TARGET in raw
    exec_path = run / "jacoco.exec"
    metadata = runpy.run_path("tools/quality/jacoco_readonly_exec_subset.py")["decode"](
        exec_path.read_bytes(), {TARGET})
    assert [s["labelBytesHex"] for s in metadata["sessions"]] == [b"PG40308-GID".hex()]
    crc = metadata["classes"][TARGET]["crc64"]
    post = dict(source=m["source"], productionCore=m["productionCore"], actualExit=0,
                firstPass=8, selected=8, newProductCases=1, requiredSelectedRequalification=7,
                failed=0, errors=0, skipped=0, explicitNotRun=["PT-OPS-GID-008"],
                changedProductClassSha256=compiled["classHashes"]["batch"][TARGET + ".class"],
                changedPhysicalFiles=compiled["physicalDelta"], typedCompileModules=compiled["modules"],
                privateAndPublicAbiSame=True, newAdapterCalls=2, oldAdapterCallsInTarget=0,
                matchedRawPmd34=True, newPmdFindings=0, execObservedCrc=crc,
                crcIndependentlyComparedWithRawClassBytes=False,
                scopedRawCounters=raw, nativeFactoryInitialized=False, backendOperations=0,
                wholeF02Accepted=False, wholeF03Accepted=False, whole451Accepted=False, newFormalAcceptance=0,
                evidence=[pin(path) for path in (unit, pmd, report, init, coverage, exec_path)],
                terminalAtUTC=datetime.now(timezone.utc).isoformat())
    out = STORE / "PG40312-f02-ssc461-group-lookup-independent-v1"
    out.mkdir()
    dump(out / "manifest.json", post)
    print(pin(out / "manifest.json"))


if __name__ == "__main__":
    main()
