"""Verify the current typed Batch delta and keep each source proof separate."""

from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import subprocess
from xml.etree import ElementTree
from zipfile import ZipFile

OPS = Path("evidence/01_PT/018_NK-OPS-001/evidence")


def pin(path):
    return dict(path=str(path), sha256=sha256(path.read_bytes()).hexdigest())


def load(path):
    return json.loads(Path(path).read_bytes())


def find(number):
    p, = OPS.glob(f"{number}-*/manifest.json")
    return p, load(p)


def names(raw):
    report = ElementTree.parse(raw).getroot()
    classes = [entry.attrib["class"].replace(".", "/")+".class"
               for entry in report.findall(".//ClassStats")]
    assert len(classes)==len(set(classes))
    assert not report.findall(".//BugInstance") + report.findall(".//MissingClass") + report.findall(".//Error")
    return set(classes)


def main():
    rp, test = find("PG41142")
    lp, lineage = find("PG41140")
    pp, packed = find("PG41074")
    qp, earlier = find("PG40482")
    ap, alert = find("PG41070")
    assert all(row["actualExit"]==0 for row in (test,lineage,packed,earlier,alert))
    assert all(step["actualExit"]==0 for step in test["steps"].values())
    for step in test["steps"].values():
        assert all(pin(Path(step[k]["path"])) == step[k] for k in ("stdout","stderr"))
    assert test["notAdmittedCurrent"] == {} and test["missing"] == test["findings"] == []
    assert test["errors"] == test["heldClassBytesRead"] == 0
    raw = Path(test["rawSpotBugs"]["path"])
    assert pin(raw) == test["rawSpotBugs"]
    tested = names(raw)
    assert len(tested)==72 and tested == set(test["newStaticTargets"]) == set(test["actualAnalyzed"])
    history = set(lineage["sameMeasuredPhysical"])
    exact = set(test["priorCurrentAlertReused"])
    impacted = set(lineage["scopeWithMainOrDependencyChanges"])
    assert len(history)==199 and len(impacted)==78 and len(exact)==7
    assert len((tested|exact)&impacted)==78 and len(exact-impacted)==1
    assert not (history&tested or history&exact or tested&exact)
    all_proved = history|tested|exact
    old_file = Path(earlier["evidence"]["rawXml"]["path"])
    assert pin(old_file) == earlier["evidence"]["rawXml"]
    assert names(old_file) == all_proved - (exact-impacted)
    alert_file = Path(alert["spotbugs"]["report"]["path"])
    assert pin(alert_file)==alert["spotbugs"]["report"] and exact <= names(alert_file)
    core = test["source"]
    assert lineage["productionCore"] == packed["source"] == alert["source"] == core
    protected = load(earlier["evidence"]["graph"]["path"])
    untouched = set(protected["explicitPhysicalHoldMetadataOnly"])|set(protected["deferredTransitive"])
    assert len(untouched)==369 and not all_proved&untouched
    expected = {**lineage["sameMeasuredPhysical"],**test["currentPhysicalSha256"],
                **{c["classPath"]:c["sha256"] for c in packed["qualifiedAlertPhysical"]}}
    assert set(expected)==all_proved and len(all_proved)==278
    with ZipFile(packed["batchArtifact"]["path"]) as jar:
        inventory = [n for n in jar.namelist() if n.endswith(".class")]
        assert len(inventory)==len(set(inventory))==647
        assert set(inventory)==all_proved|untouched
        assert all(sha256(jar.read(name)).hexdigest()==digest for name,digest in expected.items())
    head = subprocess.check_output(["git","rev-parse","HEAD"],text=True,timeout=10).strip()
    assert not subprocess.check_output(["git","diff","--name-only",core,head,"--",":(glob)src/**/src/main/**"],
                                       timeout=10)
    out = OPS/"PG41144-f03-current-batch-typed-independent-v1"
    out.mkdir()
    path = out/"manifest.json"
    with path.open("x") as f:
        json.dump(dict(actualExit=0,productionCore=core,rootInputs=[pin(p) for p in (rp,lp,pp,qp,ap)],
                       currentNewAnalyzed=72,affectedPrior=78,affectedCoveredFromCurrentAlert=6,
                       oldUnchangedByteAndClosure=199,currentIndependentAlert=7,
                       verifiedPhysical=278,wholePhysical=647,holdOrTransitive=369,
                       currentFullModuleUnverified=True,wholeF03=False,whole451=False,holdBytesOpened=0,
                       priorRunsReplayed=0,productTests=0,formalDelta=0,
                       terminalAtUTC=datetime.now(timezone.utc).isoformat()),f,indent=2)
        f.write("\n")
    print(pin(path))


if __name__=="__main__":
    main()
