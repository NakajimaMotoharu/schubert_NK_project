"""Independently verify the two-type static result against raw inputs and reports."""

from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import subprocess
from xml.etree import ElementTree as ET


E = Path("evidence/01_PT/018_NK-OPS-001/evidence")
TYPES = {"OutboxRetrySchedule", "OutboxDispatchReport", "package-info"}
API_PACKAGE = "dev.codex.schubert.nk.api.messaging.outbound"
TEST_IDS = {f"PT-F03-OUTBOX-STAT-00{index}" for index in (1, 2, 3)}


def load(path):
    return json.loads(path.read_bytes())


def digest(path):
    return sha256(Path(path).read_bytes()).hexdigest()


def pin(path):
    return dict(path=str(path), sha256=digest(path))


def simple_tag(tag):
    return tag.rsplit("}", 1)[-1]


def main():
    first = next(E.glob("PG40688-*/manifest.json"))
    retry = next(E.glob("PG40690-*/manifest.json"))
    before, after = map(load, (first, retry))
    initial = load(first.with_name("begin.json"))
    repaired = load(retry.with_name("begin.json"))
    assert before["source"] == after["source"] and before["productionCore"] == after["productionCore"]
    assert initial["sourceHashes"] == repaired["sourceHashes"]
    core = before["productionCore"]
    for source, expected in initial["sourceHashes"].items():
        assert digest(source) == expected
        data = subprocess.check_output(["git", "show", f"{core}:{source}"], timeout=15)
        assert sha256(data).hexdigest() == expected
    assert {Path(name).stem for name in initial["sourceHashes"]} == TYPES
    assert before["physical"] == after["physical"]
    assert {name.removesuffix(".class").replace("/", ".") for name in before["physical"]} == {
        f"{API_PACKAGE}.{kind}" for kind in TYPES
    }
    assert initial["jspecify"] == repaired["jspecify"]
    assert after["onlyAdditionalAux"] == "org.jspecify:jspecify:1.0.1"
    assert before["actualExit"] == 1 and after["actualExit"] == 0
    assert set(before["stages"]) == {"compile", "format", "checkstyle", "pmd", "spotbugs"}
    assert set(after["stages"]) == {"compile", "spotbugs"}
    for record in (before, after):
        for job in record["stages"].values():
            assert job["actualExit"] == 0
            assert all(digest(job[kind]["path"]) == job[kind]["sha256"] for kind in ("stdout", "stderr"))

    files = first.with_name("checkstyle.xml")
    rule = ET.parse(files).getroot()
    assert rule.tag == "checkstyle" and not list(rule.iter("error"))
    assert len(rule.findall("file")) == 3
    assert {Path(row.attrib["name"]).stem for row in rule.findall("file")} == TYPES
    pmd = first.with_name("pmd.xml")
    assert simple_tag(ET.parse(pmd).getroot().tag) == "pmd"
    assert {simple_tag(row.tag) for row in ET.parse(pmd).iter()}.isdisjoint({
        "violation", "error", "configerror", "suppressedviolation"
    })
    assert "3/3" in first.with_name("pmd.stdout").read_text()

    prior_xml, final_xml = first.with_name("spotbugs.xml"), retry.with_name("spotbugs.xml")
    old, new = (ET.parse(path).getroot() for path in (prior_xml, final_xml))
    assert [node.text for node in old.iter("MissingClass")] == ["org.jspecify.annotations.NullMarked"]
    for root in (old, new):
        assert [node for node in root.iter("Error")] == []
        assert [node for node in root.iter("BugInstance")] == []
        classes = [node.attrib["class"] for node in root.iter("ClassStats")]
        assert len(classes) == 3 and set(classes) == {f"{API_PACKAGE}.{kind}" for kind in TYPES}
    assert list(new.iter("MissingClass")) == []
    assert any(node.text.endswith("/jspecify-1.0.1.jar") for node in new.iter("AuxClasspathEntry"))
    evidence = [first, retry, files, pmd, prior_xml, final_xml]
    result = dict(
        actualExit=0, source=before["source"], productionCore=core, testIds=sorted(TEST_IDS),
        passedStaticChecks=3, productSources=2, physicalClasses=3, successfulActualCommands=7,
        firstReportMissingClasses=1, finalMissingClasses=0, finalFindings=0, finalErrors=0,
        analysisScope="current API Outbox value types", oldSuccessfulGateReruns=0,
        samePhysicalClassHashes=True, productTests=0, coverageAdded=0, newFormalAcceptance=0,
        wholeF03Accepted=False, whole451Accepted=False, bugs=["BUG-3401", "YKT-2728"],
        receipts=list(map(pin, evidence)), terminalAtUTC=datetime.now(timezone.utc).isoformat(),
    )
    out = E / "PG40692-f03-outbox-static-independent-v1"
    out.mkdir()
    with (out / "manifest.json").open("x") as stream:
        json.dump(result, stream, indent=2)
        stream.write("\n")
    print({"passedScopedChecks": len(TEST_IDS), "formalDelta": 0})


if __name__ == "__main__":
    main()
