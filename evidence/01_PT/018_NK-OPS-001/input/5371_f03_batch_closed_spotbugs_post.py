"""Independently rebuild the hold propagation and reconcile the archived static report."""

from collections import defaultdict, deque
from pathlib import Path
import gzip
import json
import re
import runpy
from xml.etree import ElementTree
from zipfile import ZipFile


H = runpy.run_path(str(Path(__file__).with_name("5370_f03_batch_admitted_spotbugs.py")))
OPS, PLAN, UPPER, COMMON = (H[key] for key in ("OPS", "PLAN", "UPPER", "COMMON"))


def main():
    read = UPPER["read"]
    pin, sha, dump = (COMMON[key] for key in ("pin", "sha", "dump"))
    p = next(OPS.glob("PG40482-*/manifest.json"))
    manifest = read(p)
    assert manifest["actualExit"] == 0 and manifest["observed"] == manifest["closedTypedClasses"]
    assert manifest["analyzerErrors"] == 0 and not any((manifest["rawMissing"],manifest["rawFindings"]))
    graph = manifest["evidence"]["graph"]
    assert pin(Path(graph["path"])) == graph
    stages = manifest["stages"]
    for terminal in stages.values():
        assert terminal["actualExit"] == 0 and all(pin(Path(terminal[c]["path"])) == terminal[c]
                                                   for c in ("stdout","stderr"))
    joined = read(graph["path"])
    promised, future, held = [set(joined[item]) for item in
                              ("checkedSet","deferredTransitive","explicitPhysicalHoldMetadataOnly")]
    assert len(promised) + len(future) + len(held) == 646
    assert not (promised & future or promised & held or held & future)
    start = read(next(PLAN.glob("887_*")))
    package = read(start["values"]["oracleReferences"][1]["path"])
    peers = set()
    for name in ("protocol","storage","bootstrap"):
        art = package["packagedJars"][name]["artifact"]
        assert pin(Path(art["path"])) == art
        with ZipFile(art["path"]) as z:
            peers.update(z.namelist())
    assert len({key for key in peers if key.endswith(".class")})==456
    batch = package["packagedJars"]["batch"]["artifact"]
    assert pin(Path(batch["path"])) == batch
    with ZipFile(batch["path"]) as archive:
        assert {name for name in archive.namelist() if name.endswith(".class")} == promised|future|held
        sizes = {name:sha(archive.read(name)) for name in sorted(promised)}
    assert sha(json.dumps(sizes,sort_keys=True).encode()) == manifest["candidatePhysicalMapSha256"]
    internal = re.compile(rb"^\s*(dev\.codex\.schubert\.nk\.\S+)\s+->\s+(dev\.codex\.schubert\.nk\.\S+)", re.M)
    source_text = gzip.decompress(Path(stages["typed"]["stdout"]["path"]).read_bytes())
    pred = defaultdict(set)
    for o,t in internal.findall(source_text):
        l,r = (part.decode().replace(".","/")+".class" for part in (o,t))
        assert l in promised | future
        pred[r].add(l)
    excluded_roots = set(pred) - (promised|future|peers)
    queue = deque(excluded_roots)
    excluded = set(excluded_roots)
    while queue:
        item=queue.popleft()
        next_wave=pred[item]-excluded
        queue.extend(next_wave)
        excluded.update(next_wave)
    assert excluded & (promised|future) == future
    raw_xml = manifest["evidence"]["rawXml"]
    assert pin(Path(raw_xml["path"])) == raw_xml
    report=ElementTree.parse(raw_xml["path"]).getroot()
    observed = {item.get("class").replace(".","/")+".class" for item in report.findall(".//ClassStats")}
    assert not any(report.findall(path) for path in ("BugInstance",".//MissingClass",".//Error"))
    assert len(observed) == len(promised) and observed == promised
    out=OPS/"PG40484-f03-batch-current-closed-typed-independent-v1"
    out.mkdir()
    d=dict(actualExit=0,source=manifest["source"],productionCore=manifest["productionCore"],
           packageReference=pin(Path(start["values"]["oracleReferences"][1]["path"])),testReceipt=pin(p),
           filterIsSafetyAdmissionNotStaticWaiver=True,batchTotal=646,closed=len(promised),
           deferredTransitive=len(future),heldExplicit=len(held),dependentRootTypes=sorted(excluded_roots),
           excludedBytesOpenedByPost=0,officialNewAcceptance=0,wholeF03Accepted=False,whole451Accepted=False,
           terminalAtUTC=COMMON["timestamp"]())
    dump(out/"manifest.json",d)
    print(pin(out/"manifest.json"),len(promised),len(future),len(held))


if __name__=="__main__":
    main()
