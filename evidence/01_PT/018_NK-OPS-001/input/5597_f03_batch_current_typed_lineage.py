"""Project the original admitted Batch static report onto unchanged physical inputs."""

from collections import defaultdict, deque
from datetime import datetime, timezone
import gzip
from hashlib import sha256
import json
from pathlib import Path
import re
import subprocess
from xml.etree import ElementTree
from zipfile import ZipFile

OPS = Path("evidence/01_PT/018_NK-OPS-001/evidence")
MAIN = ":(glob)src/**/src/main/**/*.java"
NK = b"dev.codex.schubert.nk."


def pin(path):
    return dict(path=str(path), sha256=sha256(path.read_bytes()).hexdigest())


def source(row):
    path = Path(row["path"])
    assert pin(path) == row
    return json.loads(path.read_bytes())


def class_path(name):
    return name.decode().replace(".", "/")+".class"


def owner(member):
    return member.split("$",1)[0].removesuffix(".class")


def affected(roots, incoming):
    pending = deque(roots)
    seen = set(roots)
    while pending:
        name = pending.popleft()
        current = incoming[name] - seen
        seen.update(current)
        pending.extend(current)
    return seen


def main():
    start, = Path("documents/400_PGPT/470_PMO").glob("601_*/1567_*.json")
    group = json.loads(start.read_bytes())
    refs = group["values"]["oracleReferences"]
    assert all(pin(Path(row["path"])) == row for row in refs)
    prior, post, current, alert = map(source, refs[1:])
    assert all(item["actualExit"]==0 for item in (prior,post,current,alert))
    assert prior["closedTypedClasses"] == prior["observed"] == post["closed"] == 277
    assert prior["analyzerErrors"] == 0 and prior["rawMissing"] == prior["rawFindings"] == []
    graph = source(prior["evidence"]["graph"])
    reported = set(graph["checkedSet"])
    deferred = set(graph["deferredTransitive"])
    held = set(graph["explicitPhysicalHoldMetadataOnly"])
    assert len(reported | deferred | held) == 646 and len(held)==53 and len(deferred)==316
    direct = prior["stages"]["typed"]["stdout"]
    data = Path(direct["path"])
    assert pin(data) == direct
    incoming = defaultdict(set)
    for left, right in re.findall(rb"^\s*(" + re.escape(NK) + rb"\S+)\s+->\s+("
                                  + re.escape(NK) + rb"\S+)", gzip.decompress(data.read_bytes()),re.M):
        incoming[class_path(right)].add(class_path(left))
    xml = Path(prior["evidence"]["rawXml"]["path"])
    assert pin(xml) == prior["evidence"]["rawXml"]
    old_analyzed = {row.attrib["class"].replace(".","/")+".class"
                    for row in ElementTree.parse(xml).findall(".//ClassStats")}
    assert old_analyzed == reported
    core = group["values"]["productionCoreMain"]
    before = prior["productionCore"]
    assert current["source"] == core == alert["productionCore"]
    assert not subprocess.check_output(
        ["git","diff","--name-only",before,core,"--","pom.xml","src/*/pom.xml","tools/quality/static"],
        timeout=20)
    names = subprocess.check_output(["git","diff","--name-only",before,core,"--",MAIN],timeout=20).decode().splitlines()
    removed_owners = {name.split("/src/main/java/")[1].removesuffix(".java") for name in names
                      if "/schubert-nk-api/" not in name and "/schubert-nk-web/" not in name}
    assert len(removed_owners)==14
    assert {p for p in removed_owners if p.endswith("SchemaHistoryAdmission")}
    old_jar = source(post["packageReference"])["packagedJars"]["batch"]["artifact"]
    new_jar = current["batchArtifact"]
    known_inventory = reported | deferred | held
    fixed_roots = {member for member in incoming.keys() | known_inventory if owner(member) in removed_owners}
    source_impact = affected(fixed_roots,incoming)
    count = 0
    verified = {}
    actual_changes = set()
    with ZipFile(old_jar["path"]) as old, ZipFile(new_jar["path"]) as new:
        assert {name for name in old.namelist() if name.endswith(".class")} == known_inventory
        now = {name for name in new.namelist() if name.endswith(".class")}
        assert len(now) == current["currentClassNames"] == 647
        for name in sorted((reported & now)-source_impact):
            assert name not in held|deferred and owner(name) not in removed_owners
            assert old.namelist().count(name)==new.namelist().count(name)==1
            old_hash,new_hash = (sha256(a.read(name)).hexdigest() for a in (old,new))
            count += 1
            if old_hash == new_hash:
                verified[name] = new_hash
            else:
                actual_changes.add(name)
        remain = affected(actual_changes,incoming)
        verified = {name:h for name,h in verified.items() if name not in remain}
    assert len(verified)>0
    source_deferred = reported-(set(verified)|actual_changes)
    assert len(verified)+len(actual_changes)+len(source_deferred)==277
    out = OPS/group["values"]["run"]
    out.mkdir()
    p = out/"manifest.json"
    with p.open("x") as f:
        json.dump(dict(actualExit=0, productionCore=core, originalProductionCore=before,
                       inputStart=pin(start), originalScope=len(reported), originalBatchPhysical=646,
                       currentBatchPhysical=647, checkedSameScopeWithoutDependencyDelta=len(verified),
                       sameMeasuredPhysical=verified, selectedMemberReads=count,
                       scopeWithMainOrDependencyChanges=sorted(source_deferred),
                       actualChangedBytecodeWithoutRecognizedSource=list(sorted(actual_changes)),
                       changedSymbolSources=names, knownDirectAndTransitiveImpact=sorted(source_impact & reported),
                       originalProtectedAndTransitiveUntouched=len(held|deferred),
                       currentSeparateAlertProof=refs[4], appliedSameRunWholeF03=False,
                       productJunitReplays=0, typedAnalyzerReplays=0, heldMembersRead=0,
                       officialDelta=0, terminalAtUTC=datetime.now(timezone.utc).isoformat()),
                  f,ensure_ascii=False,indent=2)
        f.write("\n")
    print(pin(p),len(verified),len(source_deferred),actual_changes)


if __name__=="__main__":
    main()
