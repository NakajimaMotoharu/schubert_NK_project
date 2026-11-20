"""Independently reconcile the current three-module SpotBugs XML with its JAR inputs."""

import json
from pathlib import Path
import runpy
from xml.etree import ElementTree
from zipfile import ZipFile


RUN = runpy.run_path(str(Path(__file__).with_name("5368_f03_current_three_whole_spotbugs.py")))
OPS, COMMON, UPPER = (RUN[k] for k in ("OPS", "COMMON", "UPPER"))
DENIED = ("TemporaryInfrastructureException", "FingerprintKeyRing",
          "ResponseSnapshotCodec", "WebStartupException")


def main():
    read = UPPER["read"]
    pin, sha, dump = (COMMON[k] for k in ("pin", "sha", "dump"))
    receipt = next(OPS.glob("PG40474-*/manifest.json"))
    record = read(receipt)
    before = next(OPS.glob("PG40472-*/manifest.json"))
    failed = next(OPS.glob("PG40476-*/manifest.json"))
    assert read(before)["actualExit"] == read(failed)["actualExit"] == 1
    assert not read(before)["spotbugsStarted"] and not read(failed)["priorStaticAnalyzerRerun"]
    assert record["actualExit"] == record["terminal"]["actualExit"] == record["errors"] == 0
    assert record["observed"] == 456 and not record["findings"] and not record["missing"]
    xml = Path(record["staticReport"]["path"])
    assert pin(xml) == record["staticReport"]
    report = ElementTree.parse(xml).getroot()
    assert not report.findall("BugInstance") and not report.findall(".//MissingClass") and not report.findall(".//Error")
    class_names = [item.get("class").replace(".", "/")+".class" for item in report.findall(".//ClassStats")]
    assert len(class_names) == len(set(class_names)) == 456
    counts = {}
    universe = set()
    owner_of_compatibility = {}
    compatibility = {name.replace(".", "/") + ".class" for name in read(failed)["compatPackageNames"]}
    for module, item in record["inputs"].items():
        archive = Path(item["jar"]["path"])
        assert pin(archive) == item["jar"]
        with ZipFile(archive) as contents:
            blob = {name: sha(contents.read(name)) for name in contents.namelist() if name.endswith(".class")}
        assert len(blob) == item["classes"] and not (blob.keys() & universe)
        assert sha(json.dumps(blob, sort_keys=True).encode()) == item["classMapSha256"]
        for name in compatibility & blob.keys():
            owner_of_compatibility[name] = module
        universe.update(blob)
        counts[module] = len(blob)
    assert set(class_names) == universe and counts == RUN["MODULES"]
    assert set(owner_of_compatibility) == compatibility and set(owner_of_compatibility.values()) == {"bootstrap"}
    assert all(Path(member).stem.split("$",1)[0] not in DENIED for member in universe)
    prior = read(next(OPS.glob("PG40366-*/manifest.json")))
    assert len(universe & prior["targetHashes"].keys()) == 456 and prior["excludedEarlierHoldClasses"] == 53
    assert len(record["physicalChangedInScope"]) == 3
    for log in (record["terminal"]["stdout"],record["terminal"]["stderr"]):
        assert pin(Path(log["path"])) == log
    out = OPS / "PG40478-f03-current-three-whole-static-independent-v1"
    out.mkdir()
    data = dict(actualExit=0,source=record["source"],productionCore=record["productionCore"],
                receipt=pin(receipt),failedPrepare=pin(before),failedPost=pin(failed),xml=record["staticReport"],
                wholeModuleCounts=counts,allObserved456=True,compatibilityPackageOwnership=owner_of_compatibility,
                batchApiWebArtifactsRead=0,protectedClassFilesRead=0,
                priorBroadMissingCount=len(prior["missing"]),newFindings=0,missingReferences=0,analyzerErrors=0,
                actualProductTests=0,wholeF03Accepted=False,whole451Accepted=False,
                nextPrerequisite="A closed admitted Batch target scope requires individually approved peers. API and Web full scopes still depend on QA056.",
                terminalAtUTC=COMMON["timestamp"]())
    dump(out/"manifest.json",data)
    print(pin(out/"manifest.json"))


if __name__ == "__main__":
    main()
