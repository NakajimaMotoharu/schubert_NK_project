"""Bind fixed LGSREQ01 test outcomes to their saved Protocol-only artifacts."""

from datetime import datetime, timezone
import gzip
import hashlib
import json
from pathlib import Path
import re
import runpy
import subprocess
import xml.etree.ElementTree as ET

EVIDENCE = Path("evidence/01_PT/018_NK-OPS-001/evidence")
METHODS = {
    "PT-PRO-LOG-UTF8-001": "retainsNfcAndSupplementaryCharactersWithoutConflatingAbsentFields",
    "PT-PRO-LOG-UTF8-002": "rejectsMalformedAndNonNfcInputAtEachFreeTextPosition",
}


def ref(path):
    p = Path(path)
    return dict(path=str(p), sha256=hashlib.sha256(p.read_bytes()).hexdigest())


def main():
    run = next(EVIDENCE.glob("PG40226-*"))
    unit = run / "manifest.json"
    m = json.loads(unit.read_bytes())
    assert m["actualExit"] == m["actualBackendActions"] == 0
    assert set(m["stages"]) == {"format", "compile", "pmd", "checkstyle", "unit", "coverage"}
    assert all(r["actualExit"] == 0 and all(ref(r[f]["path"]) == r[f] for f in ("stdout", "stderr"))
               for r in m["stages"].values())
    source = subprocess.check_output(["git", "show", m["source"] + ":" + m["testFixture"]], timeout=20)
    assert hashlib.sha256(source).hexdigest() == m["testSha256"]
    assert ref(m["jar"]["path"]) == m["jar"]
    xml = run / "xml/TEST-junit-jupiter.xml"
    suite = ET.parse(xml).getroot()
    assert {k: suite.get(k) for k in ("tests", "failures", "errors", "skipped")} == {
        "tests": "2", "failures": "0", "errors": "0", "skipped": "0"
    }
    expected_class = "dev.codex.schubert.nk.protocol.codec.LogSearchWireUnicodeTest"
    tests = list(suite.iter("testcase"))
    assert {c.get("name") for c in tests} == {f"{method}()" for method in METHODS.values()}
    assert all(c.get("classname") == expected_class and
               all(child.tag in ("system-out", "system-err") for child in c) for c in tests)
    for name in ("pmd", "checkstyle"):
        assert not any(x.tag.rsplit("}", 1)[-1] in ("violation", "error", "suppressedviolation")
                       for x in ET.parse(run / (name + ".xml")).getroot().iter())
    init = run / "class-init.log.gz"
    names = set(re.findall(rb"Initializing '(dev/codex/schubert/nk/[^']+)'", gzip.decompress(init.read_bytes())))
    assert names and all(n.startswith(b"dev/codex/schubert/nk/protocol/") for n in names)
    target = "dev/codex/schubert/nk/protocol/codec/FieldCodec"
    decode = runpy.run_path("tools/quality/jacoco_readonly_exec_subset.py")["decode"]
    data = run / "jacoco.exec"
    metadata = decode(data.read_bytes(), {target})
    assert metadata["sessions"][0]["labelBytesHex"] == m["session"].encode().hex()
    coverage = run / "coverage.xml"
    method, = [entry for klass in ET.parse(coverage).getroot().iter("class") if klass.get("name") == target
               for entry in klass.findall("method") if entry.get("name") == "decodeText"]
    counters = {r.get("type"): dict(covered=int(r.get("covered")), missed=int(r.get("missed")))
                for r in method.findall("counter")}
    result = dict(actualExit=0, source=m["source"], productionCore=m["productionCore"],
                  tests=METHODS, selectors=2, success=2, failed=0, errors=0, skipped=0, notRun=0,
                  methodFootprint=counters, dataCrc=metadata["classes"][target]["crc64"],
                  oracle="UI235 independent fixed positions. Three fields preserve NFC and supplementary scalars; "
                         "both invalid encoding and valid non-NFC text are rejected at each offset. "
                         "All-space absence, enum values and fixed UTC conversion preserved.",
                  qualifier="Protocol decoder only. API caller, HMAC, DB and runtime remain separately held.",
                  unit=ref(unit), junit=ref(xml), classInit=ref(init), exec=ref(data), coverage=ref(coverage),
                  firstReview='Initial verifier rejected JUnit system-out metadata; corrected XML parser only.',
                  limitedToProtocolInitialization=True, priorTestsExecuted=0, actualBackendActions=0,
                  whole451Accepted=False, newFormalAcceptance=0, terminalAtUTC=datetime.now(timezone.utc).isoformat())
    out = EVIDENCE / "PG40228-protocol-log-wire-scalar-independent-v1" / "manifest.json"
    out.parent.mkdir()
    with out.open("x") as stream:
        stream.write(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(ref(out), counters)


if __name__ == "__main__":
    main()
