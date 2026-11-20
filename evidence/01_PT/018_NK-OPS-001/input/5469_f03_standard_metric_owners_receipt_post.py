"""Check the original scoped static reports without replaying any analyzer."""
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
from xml.etree import ElementTree as ET
import json


def pin(path):
    return dict(path=str(path), sha256=sha256(path.read_bytes()).hexdigest())


def read(path):
    return json.loads(path.read_bytes())


def exact_members(expected, listed):
    return len(listed) == len(expected) and set(listed) == expected


evidence = Path("evidence/01_PT/018_NK-OPS-001/evidence")
original = next(evidence.glob("PG40880-*/manifest.json"))
manifest = read(original)
assert manifest["actualExit"] == 1
assert set(manifest["steps"]) == {"maven", "spotbugs", "pmd"}
assert all(stage["exit"] == 0 for stage in manifest["steps"].values())
assert all(manifest["controls"].values()) and len(manifest["sourceInputs"]) == 20

spotbugs = Path(manifest["spotbugs"]["report"]["path"])
pmd = Path(manifest["pmd"]["report"]["path"])
assert pin(spotbugs) == manifest["spotbugs"]["report"] and pin(pmd) == manifest["pmd"]["report"]
expected = {member.removesuffix(".class").replace("/", ".") for member in manifest["exactPhysical"]}
metadata = {member for member in expected if member.endswith(".package-info")}
assert len(expected) == 27 and len(metadata) == 3
sb = ET.parse(spotbugs).getroot()
members = [node.attrib["class"] for node in sb.findall(".//ClassStats")]
assert exact_members(expected, members) and not exact_members(expected - metadata, members)
assert set(manifest["spotbugs"]["statsOutsideDeclared"]) == metadata
controls = [
    not exact_members(expected, members[:-1]),
    not exact_members(expected, members + members[:1]),
    not exact_members(expected, ["fixture.Unassessed", *members[1:]]),
]
assert all(controls)
aux = [node.text for node in sb.findall("./Project/AuxClasspathEntry")]
assert aux == [dep["path"] for dep in manifest["dependencies"]]
target, = sb.findall("./Project/Jar")
assert target.text == manifest["steps"]["spotbugs"]["command"][-1]
assert not (sb.findall(".//BugInstance") or sb.findall(".//MissingClass") or sb.findall(".//Error"))
pmd_root = ET.parse(pmd).getroot()
assert not any(node.tag.rpartition("}")[2] in ("error", "violation", "suppressedviolation")
               for node in pmd_root.iter())

old_runs = [next(evidence.glob("PG40874-*/manifest.json")), *sorted(evidence.glob("PG40878-*/manifest.json"))]
pins = {}
for run_path in old_runs:
    run = read(run_path)
    selected = next(row["path"] for row in run["productionInputs"]
                    if row["path"].endswith("StandardMetricSource.java"))
    binary = selected.split("/src/main/java/")[1].removesuffix(".java") + ".class"
    assert manifest["exactPhysical"][binary] == run["targetClassSha256"]
    pins[binary] = {"classSha256": run["targetClassSha256"], "ptProof": pin(run_path),
                    "ptCore": run["source"], "staticCore": manifest["source"]}
assert len(pins) == 3
old_receipt = next(evidence.glob("PG40870-*/manifest.json"))
old = read(old_receipt)
assert all(not name.endswith(".package-info") for name in old["spotbugsReportedNineClasses"])
result = dict(actualExit=0, original=pin(original), core=manifest["source"], actualOriginalStatus=1,
              toolsOriginalStatuses={name: stage["exit"] for name, stage in manifest["steps"].items()},
              physical=sorted(expected), metadata=sorted(metadata), reported=len(members),
              threeNegativeMetadataChecks=controls, exactTargetByteJoins=pins,
              originalSpotBugs=pin(spotbugs), originalPMD=pin(pmd), oldNineReport=pin(old_receipt),
              oldNineReportHasNoPackageInfo=False if metadata & set(old["spotbugsReportedNineClasses"]) else True,
              staticCommandsReplayed=0, testsReplayed=0, full451=False, formalDelta=0,
              terminalAtUTC=datetime.now(timezone.utc).isoformat())
out = evidence / "PG40882-f03-standard-sdk-fixed-receipt-v1"
out.mkdir()
path = out / "manifest.json"
path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
print(pin(path), len(members))
