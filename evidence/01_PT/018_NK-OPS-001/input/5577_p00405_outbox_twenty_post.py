"""Independently recheck the actual JUnit set and the three target records in one exec."""

from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import subprocess
from xml.etree import ElementTree as ET


OPS = Path("evidence/01_PT/018_NK-OPS-001/evidence")
DECODER = "dba164629c:tools/quality/jacoco_readonly_exec_subset.py"
NAMESPACE = "dev/codex/schubert/nk/api/monitoring/"
TARGETS = {NAMESPACE + "OutboxMetricCollector",
           NAMESPACE + "persistence/OutboxObservationRepository",
           NAMESPACE + "persistence/OutboxObservationRepository$Snapshot"}
EXPECTED = dict(LINE=89, METHOD=14, CLASS=3, BRANCH=30, INSTRUCTION=379)


def pin(path):
    return dict(path=str(path), sha256=sha256(path.read_bytes()).hexdigest())


def read(path):
    return json.loads(path.read_bytes())


def main():
    path, = OPS.glob("PG41076-*/manifest.json")
    result = read(path)
    assert result["unitRuns"] == 1 and result["stages"]["unit"]["actualExit"] == 0
    for key in ("unitXmlPrivate", "unitXmlPublic", "execRun", "rawTable", "previous19", "previousOne"):
        ref = result[key]
        assert pin(Path(ref["path"])) == ref
    xml = ET.parse(result["unitXmlPrivate"]["path"]).getroot()
    assert [int(xml.attrib[name]) for name in ("tests", "failures", "errors", "skipped")] == [20, 0, 0, 0]
    names = [(row.attrib["classname"], row.attrib["name"].removesuffix("()"))
             for row in xml.findall("testcase")]
    assert len(names) == len(set(names)) == 20
    before, = OPS.glob("PG39596-*/manifest.json")
    prior = {(c["classname"], c["name"].removesuffix("()")) for c in read(before)["cases"]}
    assert len(prior) == 19 and prior < set(names)
    extra, = set(names) - prior
    assert extra[0].endswith(".OutboxObservationRepositoryTest")
    assert extra[1] == "outboxDb012CompleteReadWithTwoCloseFailuresKeepsFirstReleaseAsPrimary"
    code = subprocess.check_output(["git", "show", DECODER], timeout=15)
    ns = {}
    exec(compile(code, DECODER, "exec"), ns)
    payload = Path(result["execRun"]["path"]).read_bytes()
    actual = ns["decode"](payload, TARGETS)
    assert len(actual["sessions"]) == 1 and actual["sessions"][0]["labelBytesHex"] == b"PG41076".hex()
    direct = {row["className"]: row for row in result["measured"] if row["className"] in TARGETS}
    for name, row in direct.items():
        assert int(row["crc64"], 16) == int(actual["classes"][name]["crc64"], 16)
        assert all(row["counters"][metric]["missed"] == 0 for metric in EXPECTED)
    assert set(direct) == TARGETS
    assert {i: sum(r["counters"][i]["covered"] for r in direct.values()) for i in EXPECTED} == EXPECTED
    assert result["backendOperations"] == result["postgresDriverOrHeldTypeInit"] == 0
    target = OPS / "PG41078-p00405-outbox-current-twenty-independent-v1"
    target.mkdir()
    manifest = target / "manifest.json"
    with manifest.open("x") as stream:
        json.dump(dict(actualExit=0, productionCore=result["productionCore"], originalUnit=pin(path),
                       tests=20, suites=2, failed=0, skipped=0, errors=0, notRun=0,
                       originalFixture19=pin(before), additionalIncludedCase="PT-OPS-OUTBOXDB-012",
                       executionDecoderSha256=sha256(code).hexdigest(), matchingPositiveCrcs=3,
                       rawTargetCounters=EXPECTED, unresolvedAuxiliaryCounterDataRetained=True,
                       whole451=False, wholeP00405=False, actualDBStarted=0,
                       originalRunsReplayed=0, formalDelta=0,
                       terminalAtUTC=datetime.now(timezone.utc).isoformat()),
                  stream, ensure_ascii=False, indent=2)
        stream.write("\n")
    print(pin(manifest))


if __name__ == "__main__":
    main()
