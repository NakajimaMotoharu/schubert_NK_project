"""Reconcile the current three admitted P004-03 product owners without merging executions."""

from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import subprocess
from zipfile import ZipFile

OPS = Path("evidence/01_PT/018_NK-OPS-001/evidence")


def pin(p):
    return dict(path=str(p),sha256=sha256(p.read_bytes()).hexdigest())


def read(record):
    path=Path(record["path"])
    assert pin(path)==record
    return json.loads(path.read_bytes())


def git_blob(source,path):
    return sha256(subprocess.check_output(["git","show",f"{source}:{path}"],timeout=15)).hexdigest()


def main():
    cp,=Path("documents/400_PGPT/470_PMO").glob("601_*/1582_*.json")
    grp=json.loads(cp.read_bytes())
    group=grp["values"]
    refs=group["oracleReferences"]
    dao, former, codec, build, maven=map(read,refs[1:])
    assert all(row["actualExit"]==0 for row in (dao,former,codec,build,maven))
    core=group["productionCoreMain"]
    assert dao["productionCore"]==maven["source"]==core
    assert build["sourceCore"]==codec["sourceCore"]
    assert dao["currentTests"]==12 and codec["tests"]==20 and codec["targetRawFour100"]
    assert all(codec[key]==0 for key in ("failed","errors","skipped","notRun"))
    allowed = {
        "file/MaintenanceRecords",
        "repository/MaintenanceRetirement",
        "repository/BatchRun",
        "repository/MaintenanceActivation",
        "repository/MaintenanceCompletion",
        "repository/MaintenanceCompletion$Outcome",
    }
    selected = {
        "dev/codex/schubert/nk/batch/" + name + ".class":
            build["physicalClassHashes"]["dev/codex/schubert/nk/batch/" + name + ".class"]
        for name in sorted(allowed)
    }
    assert all(name.removesuffix(".class") in codec["classIds"] for name in selected)
    assert len(selected)==codec["targetPhysicalClasses"]==6
    dao_manifest=read(dao["run"])
    dao_physical=dao_manifest["physicalQualified"]
    assert len(dao_physical)==5
    by_name={row["realBatchJarEntry"]:row for row in former["partialOwnersBoundToCurrentPhysical"]}
    assert len(by_name)==3 and len(former["heldOwners"])==2
    assert all(selected[name]==dao_physical[name] for name in selected.keys() & dao_physical.keys())
    physical={**selected,**dao_physical}
    expected_source=group["source"]
    stable_tests={}
    for name, recorded in build["testSourceHashes"].items():
        actual=git_blob(expected_source,name)
        stable_tests[name]=dict(originalSha256=recorded, currentSha256=actual, same=recorded==actual)
    assert len(stable_tests)==4
    with ZipFile(maven["batchArtifact"]["path"]) as jar:
        inventory=jar.namelist()
        assert all(inventory.count(name)==1 for name in physical)
        assert all(sha256(jar.read(name)).hexdigest()==h for name,h in physical.items())
        assert {row["path"].split("/src/main/java/")[1].replace(".java",".class")
                for row in former["heldOwners"]}.isdisjoint(physical)
    three=[]
    for name,owner in by_name.items():
        is_dao=name in dao_physical
        proof_type="current-borrowed-dao" if is_dao else "same-package-bytes-historical-pure-codec"
        assert physical[name]==owner["actualClassSha256"]
        three.append(dict(path=owner["path"],classEntry=name,sha256=physical[name],proof=proof_type,
                          testEvidence=refs[1] if is_dao else refs[3]))
    assert len(three)==3
    out=OPS/group["run"]
    out.mkdir()
    path=out/"manifest.json"
    with path.open("x") as f:
        json.dump(dict(actualExit=0,productionCore=core,source=expected_source,threeScopedOwners=three,
                       otherOwnersHeld=former["heldOwners"],unchangedCodecFixtures=stable_tests,
                       originalCodecTests=20,currentBorrowingAndValueTests=12,combinedTestCount=None,
                       oldExecAndCurrentExecCombined=False,retainedTargetPhysical=len(physical),
                       heldClassesOpened=0,newTestsRun=0,realDbOrOriginalRetentionOperations=0,
                       whole451=False,formalDelta=0,terminalAtUTC=datetime.now(timezone.utc).isoformat()),
                  f,ensure_ascii=False,indent=2)
        f.write("\n")
    print(pin(path),len(three),sum(x["same"] for x in stable_tests.values()))


if __name__=="__main__":
    main()
