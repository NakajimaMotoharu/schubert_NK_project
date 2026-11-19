"""Independently check the complete ten public signature-verification tests."""

from datetime import datetime, timezone
import gzip
from pathlib import Path
import re
import runpy
import xml.etree.ElementTree as ET


RUNNER = runpy.run_path(str(Path(__file__).with_name("5326_f02_group_lookup_upper.py")))
STORE, COMMON = RUNNER["EVIDENCE"], RUNNER["COMMON"]
CLASS = RUNNER["RELEASE_CLASS"]
TARGET = CLASS.removesuffix("Test").replace(".", "/")


def main():
    run = next(STORE.glob("PG40314-*"))
    unit = run / "manifest.json"
    pmd = next(STORE.glob("PG40316-*/manifest.json"))
    pin = COMMON["pin"]
    m, p = map(RUNNER["read"], (unit, pmd))
    assert m["source"] == p["source"] == m["productionCore"]
    assert m["actualExit"] == p["actualExit"] == 0 and m["notRun"] == []
    assert set(m["stages"]) == {"compile", "format", "checkstyle", "abi-before", "abi-after",
                               "behavior-after", "testcompile", "unit", "coverage"}
    for stage in m["stages"].values():
        assert stage["actualExit"] == 0
        for key in ("stdout", "stderr"):
            assert pin(Path(stage[key]["path"])) == stage[key]
    assert p["newlyObserved"] == []
    assert p["oldFindings"] == p["newRawFindings"]
    report = run / "xml/TEST-junit-jupiter.xml"
    root = ET.parse(report).getroot()
    assert [int(root.get(k)) for k in ("tests", "skipped", "errors", "failures")] == [10, 0, 0, 0]
    cases = list(root.iter("testcase"))
    methods = {c.get("name") for c in cases}
    assert len(methods) == 10 and all(c.get("classname") == CLASS for c in cases)
    assert {name[:7] for name in methods} == {f"sign{i:03d}" for i in range(1, 11)}
    assert m["namedActualHostActions"] == 0
    assert pin(Path(m["compiled"]["path"])) == m["compiled"]
    compiled = RUNNER["read"](m["compiled"]["path"])
    assert sum(compiled["modules"].values()) == 1102
    assert compiled["physicalDelta"] == dict(protocol=[], storage=[], bootstrap=[TARGET + ".class"], batch=[])
    abi_before, abi_after, instructions = [
        gzip.decompress(Path(m["stages"][s]["stdout"]["path"]).read_bytes())
        for s in ("abi-before", "abi-after", "behavior-after")
    ]
    assert abi_before == abi_after
    assert instructions.count(b"JdbcFailureGraph.preserveFatal:") == 1
    assert b"StorageIoException" not in instructions
    init = run / "class-init.log.gz"
    present = gzip.decompress(init.read_bytes())
    initialized = {name.decode().split("$$Lambda", 1)[0] for name in re.findall(
        rb"Initializing '(dev/codex/schubert/nk/[^']+)'", present)}
    assert TARGET in initialized and TARGET + "$NativeCrypto" in initialized
    assert all(name.startswith(TARGET) or name.startswith(TARGET + "Test") or
               name in {"dev/codex/schubert/nk/api/bootstrap/JdbcFailureGraph",
                        "dev/codex/schubert/nk/storage/StorageIoException"}
               for name in initialized)
    coverage = run / "coverage.xml"
    raw = {row.get("name"): {k.get("type"): dict(hit=int(k.get("covered")), miss=int(k.get("missed")))
                             for k in row.findall("counter")}
           for row in ET.parse(coverage).iter("class") if row.get("name").startswith(TARGET)}
    expected = compiled["selectedPhysicalCrc"]
    code = {TARGET, TARGET + "$NativeCrypto"}
    assert set(raw) == set(expected) and raw[TARGET + "$Crypto"] == {}
    exec_path = run / "jacoco.exec"
    metadata = runpy.run_path("tools/quality/jacoco_readonly_exec_subset.py")["decode"](
        exec_path.read_bytes(), code)
    assert [s["labelBytesHex"] for s in metadata["sessions"]] == [m["session"].encode().hex()]
    assert {name: item["crc64"] for name, item in metadata["classes"].items()} == {
        name: expected[name] for name in code}
    scoped_all_hit = all(detail["miss"] == 0 for name in code for detail in raw[name].values())
    result = dict(source=m["source"], productionCore=m["productionCore"], actualExit=0,
                  firstPass=10, selected=10, newProductCases=0, requiredRequalification=10,
                  failed=0, errors=0, skipped=0, notRun=0, originalMethods=sorted(methods),
                  changedPhysicalFiles=compiled["physicalDelta"], typedCompileModules=compiled["modules"],
                  privateAndPublicAbiSame=True, newAdapterCalls=1, oldAdapterCallsInTarget=0,
                  rawPmdFindings=p["newRawFindings"], newPmdFindings=0, crc=expected,
                  scopedRawCounters=raw, exactTargetsFullRawHit=scoped_all_hit,
                  privateKeyOrReleaseActions=0, wholeF02Accepted=False, whole451Accepted=False,
                  newFormalAcceptance=0, evidence=[pin(path) for path in (unit, pmd, report, init, coverage, exec_path)],
                  terminalAtUTC=datetime.now(timezone.utc).isoformat())
    out = STORE / "PG40318-f02-public-rfc-independent-v1"
    out.mkdir()
    COMMON["dump"](out / "manifest.json", result)
    print(pin(out / "manifest.json"), "exact targets full raw", scoped_all_hit)


if __name__ == "__main__":
    main()
