"""Describe current admitted dependencies by physical Maven owner."""

from collections import Counter
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import re
import subprocess
from zipfile import ZipFile

OPS = Path("evidence/01_PT/018_NK-OPS-001/evidence")
KIND = "dev.codex.schubert.nk."
SS = Path("documents/300_SS/310_アプリケーション/311_モジュール・package・class責務設計.md")


def pin(path):
    return dict(path=str(path),sha256=sha256(path.read_bytes()).hexdigest())


def load(row):
    p = Path(row["path"])
    assert pin(p)==row
    return json.loads(p.read_bytes())


def for_name(name):
    return name.removesuffix(".class").replace("/", ".")


def classify(target, owners):
    if not target.startswith(KIND):
        return "third-party-or-jdk"
    return owners.get(target,"unresolved")


def controls():
    owner = {KIND+"api.bootstrap.OldName":"bootstrap", KIND+"api.FakeApi":"api",
             KIND+"protocol.Runtime":"protocol", KIND+"storage.Allowed":"storage"}
    expected = {"api.bootstrap.OldName":"bootstrap","api.FakeApi":"api",
                "protocol.Runtime":"protocol","storage.Allowed":"storage","batch.Absent":"unresolved"}
    assert all(classify(KIND+name,owner)==kind for name,kind in expected.items())
    assert classify("java.sql.Connection",owner)=="third-party-or-jdk"
    return len(expected)+1


def main():
    start, = Path("documents/400_PGPT/470_PMO").glob("601_*/1576_*.json")
    group = json.loads(start.read_bytes())
    values = group["values"]
    typed, checked, package, repo = map(load,values["oracleReferences"][1:])
    assert all(row["actualExit"]==0 for row in (typed,checked,package,repo))
    core=values["productionCoreMain"]
    assert core==typed["source"]==checked["productionCore"]==package["source"]==repo["productionCore"]
    assert set(package["savedUnchangedLibraryReferences"])=={"protocol","storage","bootstrap"}
    source = subprocess.check_output(
        ["git","show",f'{values["canonicalDesignSource"]}:{SS}'],timeout=15)
    assert "Batchはallowlist済みrepository".encode() in source
    current = {**package["savedUnchangedLibraryReferences"],"batch":package["batchArtifact"]}
    owners={}
    counts={}
    for key,row in current.items():
        with ZipFile(row["path"]) as jar:
            product = [for_name(name) for name in jar.namelist() if name.endswith(".class")]
        assert len(product)==len(set(product)) and not set(product)&owners.keys()
        counts[key]=len(product)
        owners.update({name:key for name in product})
    assert counts==dict(protocol=176,storage=79,bootstrap=201,batch=647)
    incident = Path(typed["steps"]["jdeps"]["stdout"]["path"])
    assert pin(incident)==typed["steps"]["jdeps"]["stdout"] and typed["steps"]["jdeps"]["actualExit"]==0
    rows = []
    for line in incident.read_text().splitlines():
        fields = re.fullmatch(r"\s+(\S+)\s+->\s+(\S+)\s+(.+)",line)
        if fields is not None:
            rows.append(fields.groups())
    assert rows and len({(a,b) for a,b,_ in rows}) == len(rows)
    closure = {for_name(row) for row in typed["newStaticTargets"] + typed["priorCurrentAlertReused"]}
    sibling_file, = OPS.glob("PG41140-*/manifest.json")
    inherited = json.loads(sibling_file.read_bytes())
    closure.update(map(for_name,inherited["sameMeasuredPhysical"]))
    assert len(closure)==checked["verifiedPhysical"]==278
    origins = {origin for origin,_,_ in rows}
    assert origins <= closure
    assert all(owners[origin]=="batch" for origin in origins)
    counts_by_owner = Counter(classify(target,owners) for _,target,_ in rows)
    prohibited=[(origin,target) for origin,target,_ in rows
                if classify(target,owners) not in {"batch","bootstrap","storage","third-party-or-jdk"}]
    assert not prohibited
    compatible=[(origin,target) for origin,target,_ in rows
                if target.startswith(KIND+"api.") and owners[target]=="bootstrap"]
    assert compatible and counts_by_owner["storage"] and counts_by_owner["bootstrap"]
    assert all(archive!="not found" for _,target,archive in rows if target.startswith(KIND))
    out = OPS/values["run"]
    out.mkdir()
    result=out/"manifest.json"
    with result.open("x") as f:
        json.dump(dict(actualExit=0,currentProductCore=core,designSource=values["canonicalDesignSource"],
                       designSha256=sha256(source).hexdigest(),qualifiedBatchPhysical=278,
                       unavailableBatchPhysical=checked["holdOrTransitive"],ownerCounts=counts,
                       typedReference=pin(incident),internalOrExternalEdges=len(rows),byPhysicalOwner=counts_by_owner,
                       batchDeclaredOrigins=len(origins),declaredNoEdges=len(closure-origins),
                       bootstrapCompatibilityPackageEdges=len(compatible),unknownInternalEdges=0,
                       prohibitedProductEdges=prohibited,independentClassifierCases=controls(),
                       typedToolReplayed=0,productClassBytesOpened=0,actualEnvironmentOperations=0,
                       whole451=False,wholeF02Accepted=False,formalDelta=0,
                       terminalAtUTC=datetime.now(timezone.utc).isoformat()),
                  f,ensure_ascii=False,indent=2)
        f.write("\n")
    print(pin(result),counts_by_owner)


if __name__=="__main__":
    main()
