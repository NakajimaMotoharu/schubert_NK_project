"""Verify the USRRSP01 fixed-field PT without repeating its unit execution."""

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
    "PT-PRO-USR-WIRE-001": "usr001DecodesNfcAndPreservesTheNextFieldAtThe64ByteLimit",
    "PT-PRO-USR-WIRE-002": "usr002RejectsTheAllSpaceMandatoryField",
    "PT-PRO-USR-WIRE-003": "usr003RejectsSurrogateEncodingAndTruncationAtTheFieldEnd",
    "PT-PRO-USR-WIRE-004": "usr004RejectsValidUtf8ThatIsNotNfc",
}


def pin(path):
    path = Path(path)
    return dict(path=str(path), sha256=hashlib.sha256(path.read_bytes()).hexdigest())


def read(path):
    return json.loads(Path(path).read_bytes())


def main():
    first, current = (next(EVIDENCE.glob(f"PG{n}-*")) for n in (40240, 40242))
    a, b = (read(path / "manifest.json") for path in (first, current))
    assert (a["actualExit"], b["actualExit"]) == (4, 0)
    assert "unit" not in a["stages"] and a["stages"]["pmd"]["actualExit"] == 4
    assert a["jar"] == b["jar"] == pin(b["jar"]["path"])
    assert a["jarOwnership"] == b["jarOwnership"] and b["jarOwnership"]["sameBeforeAndAfter"]
    assert a["productionCore"] == b["productionCore"] and a["source"] != b["source"]
    prior_findings = ET.parse(first / "pmd.xml").getroot().findall(".//{*}violation")
    assert [finding.get("rule") for finding in prior_findings] == ["AvoidDuplicateLiterals"]
    for name in ("pmd", "checkstyle"):
        assert not any(x.tag.rsplit("}", 1)[-1] in ("violation", "error", "suppressedviolation")
                       for x in ET.parse(current / (name + ".xml")).getroot().iter())
    assert set(b["stages"]) == {"format", "compile", "pmd", "checkstyle", "unit", "coverage"}
    assert all(row["actualExit"] == 0 and all(pin(row[k]["path"]) == row[k] for k in ("stdout", "stderr"))
               for row in b["stages"].values())
    source = subprocess.check_output(["git", "show", b["source"] + ":" + b["testFixture"]], timeout=20)
    assert hashlib.sha256(source).hexdigest() == b["testSha256"]
    previous_source = subprocess.check_output(
        ["git", "show", a["source"] + ":" + a["testFixture"]], timeout=20
    )
    constant = b'  private static final String ONE_NINE_DIGITS = "000000001";\n'
    assert source.count(constant) == 1
    assert source.replace(constant, b'').replace(b'ONE_NINE_DIGITS', b'"000000001"') == previous_source

    xml = current / "xml/TEST-junit-jupiter.xml"
    suite = ET.parse(xml).getroot()
    assert tuple(suite.get(k) for k in ("tests", "failures", "errors", "skipped")) == ("4", "0", "0", "0")
    selectors = list(suite.iter("testcase"))
    assert {case.get("name") for case in selectors} == {method + "()" for method in CASES.values()}
    assert all(case.get("classname") == "dev.codex.schubert.nk.protocol.codec.UserListReplyWireTest"
               and all(c.tag in ("system-out", "system-err") for c in case) for case in selectors)
    init = current / "class-init.log.gz"
    names = set(re.findall(rb"Initializing '(dev/codex/schubert/nk/[^']+)'", gzip.decompress(init.read_bytes())))
    assert names and all(name.startswith(b"dev/codex/schubert/nk/protocol/") for name in names)
    assert a["actualBackendActions"] == b["actualBackendActions"] == b["executedPreviouslyApprovedTests"] == 0

    decode = runpy.run_path("tools/quality/jacoco_readonly_exec_subset.py")["decode"]
    execution = current / "jacoco.exec"
    model = "dev/codex/schubert/nk/protocol/layout/admin/UserRecord"
    decoder = "dev/codex/schubert/nk/protocol/codec/FieldCodec"
    probe = decode(execution.read_bytes(), {model, decoder})
    assert probe["sessions"][0]["labelBytesHex"] == b["session"].encode().hex()
    coverage = current / "coverage.xml"
    tree = ET.parse(coverage).getroot()
    user_class, = [n for n in tree.iter("class") if n.get("name") == model]
    text_class, = [n for n in tree.iter("class") if n.get("name") == decoder]
    text_method, = [n for n in text_class.findall("method") if n.get("name") == "decodeText"]

    def counters(element):
        return {row.get("type"): dict(hit=int(row.get("covered")), miss=int(row.get("missed")))
                for row in element.findall("counter")}

    result = dict(actualExit=0, source=b["source"], productionCore=b["productionCore"], jar=b["jar"],
                  jarOwnership=b["jarOwnership"], cases=CASES, success=4, failures=0, errors=0, skipped=0, notRun=0,
                  field=dict(layout="USRRSP01", dataBytes=48, recordBytes=168, name="Username",
                             oneBasedOffset=13, length=64, required=True,
                             valid=["名😀", "60 ASCII bytes followed by one four-byte character"],
                             rejected=["all-space", "surrogate encoding", "truncation at byte 64", "non-NFC"]),
                  firstStatic=pin(first / "manifest.json"), firstStaticExit=4, firstRunTests=0,
                  firstIndependentExit=1,
                  postCorrection="ElementTree namespace-aware findall instead of iter wildcard",
                  fixtureRefactoringLiteralOnly=True, retest=pin(current / "manifest.json"),
                  junit=pin(xml), coverage=pin(coverage), exec=pin(execution), init=pin(init),
                  methodCounters=counters(text_method), userRecordCounters=counters(user_class),
                  classCrcs={name: row["crc64"] for name, row in probe["classes"].items()},
                  priorTestsReplayed=0, actualBackendActions=0, newFormalAcceptance=0,
                  whole451Accepted=False, terminalAtUTC=datetime.now(timezone.utc).isoformat())
    out = EVIDENCE / "PG40244-protocol-user-list-fixed-wire-independent-v1" / "manifest.json"
    out.parent.mkdir()
    with out.open("x") as stream:
        stream.write(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(pin(out), result["methodCounters"], result["userRecordCounters"])


if __name__ == "__main__":
    main()
