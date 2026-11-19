"""Independently bind QSS and NTS outcomes to the original sealed Protocol JAR."""

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
CASES = {
    "PT-PRO-QSS-WIRE-001": "qss001DecodesExactKeywordUsernameAndBlankFields",
    "PT-PRO-QSS-WIRE-002": "qss002RejectsMalformedAndNonNfcAtBothTextOffsets",
    "PT-PRO-NTS-WIRE-001": "nts001DecodesEveryDefinedTypeAndTheExactUtcDateBoundary",
    "PT-PRO-NTS-WIRE-002": "nts002RejectsUnknownTypeInvalidDateReversalAndOneMillisecondOver",
}


def pin(path):
    path = Path(path)
    return dict(path=str(path), sha256=hashlib.sha256(path.read_bytes()).hexdigest())


def read(path):
    return json.loads(Path(path).read_bytes())


def main():
    first, current = (next(EVIDENCE.glob(f"PG{n}-*")) for n in (40232, 40234))
    a, b = (read(p / "manifest.json") for p in (first, current))
    assert (a["actualExit"], b["actualExit"]) == (1, 0) and a["source"] != b["source"]
    assert a["jar"] == b["jar"] == pin(b["jar"]["path"])
    assert a["jarOwnership"] == b["jarOwnership"] and b["jarOwnership"]["sameBeforeAndAfter"]
    assert a["productionCore"] == b["productionCore"]
    assert a["actualBackendActions"] == b["actualBackendActions"] == b["executedPreviouslyApprovedTests"] == 0
    assert set(b["stages"]) == {"format", "compile", "pmd", "checkstyle", "unit", "coverage"}
    assert all(r["actualExit"] == 0 and all(pin(r[k]["path"]) == r[k] for k in ("stdout", "stderr"))
               for r in b["stages"].values())
    source = subprocess.check_output(["git", "show", b["source"] + ":" + b["testFixture"]], timeout=20)
    assert hashlib.sha256(source).hexdigest() == b["testSha256"]
    for name in ("pmd", "checkstyle"):
        assert not any(x.tag.rsplit("}", 1)[-1] in ("violation", "error", "suppressedviolation")
                       for x in ET.parse(current / (name + ".xml")).getroot().iter())

    xml = "xml/TEST-junit-jupiter.xml"
    first_xml, current_xml = [ET.parse(path / xml).getroot() for path in (first, current)]
    for root, failures in ((first_xml, "1"), (current_xml, "0")):
        assert tuple(root.get(k) for k in ("tests", "failures", "errors", "skipped")) == ("4", failures, "0", "0")
        assert {case.get("name") for case in root.iter("testcase")} == {n + "()" for n in CASES.values()}
    failed, = [case for case in first_xml.iter("testcase") if case.find("failure") is not None]
    assert failed.get("name") == CASES["PT-PRO-NTS-WIRE-002"] + "()"
    assert "layout semantic violation: date range is reversed" in failed.find("failure").get("message")
    assert all(all(child.tag in ("system-out", "system-err") for child in case)
               for case in current_xml.iter("testcase"))

    init = gzip.decompress((current / "class-init.log.gz").read_bytes())
    names = set(re.findall(rb"Initializing '(dev/codex/schubert/nk/[^']+)'", init))
    assert names and all(n.startswith(b"dev/codex/schubert/nk/protocol/") for n in names)
    targets = {"QSSREQ01": "QuestionSearchRequestData", "NTSREQ01": "NotificationSearchRequestData"}
    classes = {layout: "dev/codex/schubert/nk/protocol/layout/question/" + name
               for layout, name in targets.items()}
    decode = runpy.run_path("tools/quality/jacoco_readonly_exec_subset.py")["decode"]
    stream = decode((current / "jacoco.exec").read_bytes(), set(classes.values()))
    assert stream["sessions"][0]["labelBytesHex"] == b["session"].encode().hex()
    xml_coverage = ET.parse(current / "coverage.xml").getroot()
    observed = {}
    for layout, name in classes.items():
        klass, = [item for item in xml_coverage.iter("class") if item.get("name") == name]
        observed[layout] = dict(crc64=stream["classes"][name]["crc64"],
                                counters={r.get("type"): dict(hit=int(r.get("covered")), miss=int(r.get("missed")))
                                          for r in klass.findall("counter")})
    result = dict(actualExit=0, source=b["source"], productionCore=b["productionCore"], jar=b["jar"],
                  jarOwnership=b["jarOwnership"], cases=CASES,
                  resultsByLayout={
                      "QSSREQ01": dict(success=2, wireBytes=384, fieldOffsets={"keyword": [1, 256], "username": [257, 64]},
                                        expected="問題😀, Café, blank optionals; reject malformed UTF-8 and non-NFC at both offsets"),
                      "NTSREQ01": dict(success=2, wireBytes=64, fieldOffsets={"type": [1, 12], "from": [13, 17], "to": [30, 17]},
                                        expected="Three closed types plus absent; UTC conversion and 366-day inclusive boundary; reject unknown, invalid, reversed, and over-limit"),
                  }, observed=observed, firstRun=pin(first / "manifest.json"), firstXml=pin(first / xml),
                  firstSuccess=3, firstFailure=1, retestSuccess=4, failed=0, errors=0, skipped=0, notRun=0,
                  retryReason="Expected semantic message omitted its standard prefix; product and JAR unchanged",
                  retest=pin(current / "manifest.json"), xml=pin(current / xml), coverage=pin(current / "coverage.xml"),
                  execution=pin(current / "jacoco.exec"), init=pin(current / "class-init.log.gz"),
                  toolsStaticViolations=0, lgsReplayed=0, apiOrBackendExecuted=0, whole451Accepted=False,
                  newFormalAcceptance=0, terminalAtUTC=datetime.now(timezone.utc).isoformat())
    out = EVIDENCE / "PG40236-protocol-qss-nts-fixed-wire-independent-v1" / "manifest.json"
    out.parent.mkdir()
    with out.open("x") as f:
        f.write(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(pin(out), observed)


if __name__ == "__main__":
    main()
