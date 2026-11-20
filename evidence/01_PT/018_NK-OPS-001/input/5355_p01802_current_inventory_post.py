"""Independently match the 18 case identifiers, current CRCs and unfiltered owner counts."""

import gzip
from pathlib import Path
import re
import runpy
import xml.etree.ElementTree as ET


RUN = runpy.run_path(str(Path(__file__).with_name("5354_p01802_current_inventory_unit.py")))
UPPER, STORE, COMMON, TARGETS, SHARED = (
    RUN[name] for name in ("UPPER", "STORE", "COMMON", "TARGETS", "SHARED"))


def main():
    read = UPPER["read"]
    pin, dump = COMMON["pin"], COMMON["dump"]
    run = next(STORE.glob("PG40422-*"))
    unit = run / "manifest.json"
    m = read(unit)
    prior_run = next(STORE.glob("PG37438-*"))
    prior = read(prior_run / "manifest.json")
    assert m["actualExit"] == 0 and m["source"] != prior["source"]
    assert m["actualBackendActions"] == m["executableProductEntryPoints"] == 0
    assert all(stage["actualExit"] == 0 and all(pin(Path(stage[k]["path"])) == stage[k]
                                               for k in ("stdout", "stderr")) for stage in m["stages"].values())
    xml = run / "xml/TEST-junit-jupiter.xml"
    old_receipt = next(STORE.glob("PG37440-*/manifest.json"))
    old_independent = read(old_receipt)
    assert old_independent["originalUnit"] == pin(prior_run / "manifest.json")
    old_xml = old_receipt.parent / "xml/TEST-junit-jupiter.xml"
    assert pin(old_xml)["sha256"] == prior["xmlHashes"][old_xml.name]
    assert pin(old_xml)["sha256"] == old_independent["files"]["xml/TEST-junit-jupiter.xml"]
    before = ET.parse(old_xml).getroot()
    after = ET.parse(xml).getroot()
    assert all([int(row.get(k)) for k in ("tests", "failures", "errors", "skipped")] == [18, 0, 0, 0]
               for row in (before, after))
    positions = [{(r.get("classname"), r.get("name")) for r in s.iter("testcase")} for s in (before, after)]
    assert positions[0] == positions[1] and len(positions[1]) == 18
    assert len({c for c, _ in positions[1]}) == 2
    assert not any(row.tag in {"failure", "error", "skipped"} for row in after.iter())
    init = run / "class-init.log.gz"
    trace = gzip.decompress(init.read_bytes())
    assert not re.search(rb"Initializing '[^']*(ReleasePayloadVerification|StartupReleaseManifest|RootRelease"
                         rb"|NativeCoveragePrivateFile|org/postgresql|JdbcAdmissionFailures|JdbcFailureGraph)", trace)
    target = TARGETS | SHARED
    stream = run / "jacoco.exec"
    decoder = runpy.run_path("tools/quality/jacoco_readonly_exec_subset.py")["decode"]
    info = decoder(stream.read_bytes(), target)
    assert [row["labelBytesHex"] for row in info["sessions"]] == [m["session"].encode().hex()]
    assert {k: int(value["crc64"], 16) for k, value in info["classes"].items()} == {
        k: int(m["inputClasses"][k]["crc64"], 16) for k in target}
    raw = Path(m["stages"]["raw"]["stdout"]["path"])
    totals, held_methods = {}, {}
    for line in gzip.decompress(raw.read_bytes()).decode().splitlines():
        row = line.split("\t")
        if row[0] == "CLASS":
            totals[row[1]] = {i.split(":")[0]: dict(zip(("missed", "covered"),
                                  map(int, i.split(":")[1:]))) for i in row[6:]}
        elif row[0] == "METHOD" and row[1] in SHARED:
            held_methods[row[1], row[2], row[3]] = [item for item in row[5:] if int(item.split(":")[1])]
    assert set(totals) == target
    assert all(not result["missed"] for name in TARGETS for result in totals[name].values())
    assert any(result["missed"] for name in SHARED for result in totals[name].values())
    for ident, pending in held_methods.items():
        if ident[1] in {"inspect", "closeRows", "closeStatement"}:
            assert any(i.startswith("METHOD:1:0") for i in pending)
    raw_sum = {key: sum(totals[n][key]["covered"] for n in TARGETS)
               for key in ("LINE", "METHOD", "CLASS", "BRANCH", "INSTRUCTION")}
    out = STORE / "PG40424-p01802-current-inventory18-independent-v1"
    out.mkdir()
    proof = dict(actualExit=0, source=m["source"], productionCore=m["productionCore"],
                 currentCases=18, originalCases=sorted(name for _, name in positions[1]),
                 freshSingleSession=m["session"], originalCasesRerunNeededDueToSharedByteChanges=18,
                 newTestDefinitions=0, failed=0, errors=0, skipped=0, notRun=0,
                 selectedCurrentPhysicals=5, ownCurrentPhysicals=3, heldOrActualReleaseActions=0,
                 ownRawCovered=raw_sum, ownRawMissed={k: 0 for k in raw_sum},
                 sharedRetained={k: totals[k] for k in sorted(SHARED)},
                 fullSharedTypedScopeProved=False, previousRawOrExecMerged=False,
                 wholeP01802Accepted=False, whole451Accepted=False, formalDelta=0,
                 evidence=list(map(pin, (unit, xml, init, stream, raw, old_receipt, old_xml))),
                 terminalAtUTC=COMMON["timestamp"]())
    dump(out / "manifest.json", proof)
    print(pin(out / "manifest.json"), raw_sum)


if __name__ == "__main__":
    main()
