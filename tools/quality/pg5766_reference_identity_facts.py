"""Compile/resolve immutable current849, never run Production code or mutate runtime."""
import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess
import shutil
from pg5756_private_contract_qualification import SOURCE,ROOT,W,BASE
from pg5540_snapshot_scratch_selected import TC,sha
from pg5584_field_accessor_inspection import compile_only_artifacts
from source_reference_identity_inventory_test import facts

SLOT='pg5766-reference-identity-facts-v2'


def inputs():
    qp=BASE/'PG5754-current3932-cases/qualification.json'
    if sha(qp)!='ac4d3ccf6e9be8c1222aec8d09dd17508975f6475b3380faced765ce4c836b18':raise ValueError('actual independently qualified3932')
    q=json.loads(qp.read_bytes());private=W/'pg5750-exception-static-v1/manifest.safe.json';static=json.loads(private.read_bytes())
    snapshot=W/'pg5748-exception-green-v1/source'
    current={p.relative_to(ROOT).as_posix():sha(p)for p in ROOT.glob('src/*/src/main/java/**/*.java')}
    mirrored={p.relative_to(snapshot).as_posix():sha(p)for p in snapshot.glob('src/*/src/main/java/**/*.java')}
    if len(current)!=849 or current!=mirrored or current!=static['allSourceHashes']or static['source']!=SOURCE:raise ValueError('immutable849 actual source in snapshot and current')
    roots=[snapshot/('src/schubert-nk-'+m+'/target/classes')for m in('protocol','storage','bootstrap','api','web','batch')]
    physical={root.parts[-3].removeprefix('schubert-nk-')+':'+p.relative_to(root).as_posix():sha(p)for root in roots for p in root.rglob('*.class')}
    if physical!=q['allPhysicalMainSha256']or len(physical)!=1664:raise ValueError('all1664 exact same-source actual classpath')
    release=W/'pg5430-release-v1';bom=release/'RELEASE-MANIFEST.json'
    if sha(bom)!='85fbce34711ac798d1e71a3e3a8a7a54cc070e074ec1255047c4ac75ef18fbd6':raise ValueError('fixed third-party BOM only, no PT imported')
    jars={}
    for row in json.loads(bom.read_bytes())['artifacts']:
        p=Path(row['path'])
        if '/lib/'not in row['path']or p.suffix!='.jar'or p.name.startswith('schubert-nk-'):continue
        target=release/p
        if target.is_symlink()or sha(target)!=row['sha256']:raise ValueError('actual dependency jar hash')
        jars.setdefault(row['sha256'],target)
    provided,metadata=compile_only_artifacts()
    return snapshot,os.pathsep.join(map(str,[*roots,*jars.values(),*provided])),{'sourceHashes':current,'physicalMainSha256':physical,'qualifiedWholeSha256':sha(qp),'thirdPartyJarSha256':list(jars),'providedAnnotations':metadata}


def main():
    snapshot,classpath,identity=inputs();helper=ROOT/'tools/quality/SourceReferenceIdentityInventory.java';fixture=ROOT/'tools/quality/source_reference_identity_inventory_test.py';helper_sha=sha(helper);fixture_sha=sha(fixture)
    os.umask(0o077);out=W/SLOT;out.mkdir(mode=0o700);classes=out/'toolclasses';classes.mkdir()
    start=datetime.datetime.now(datetime.timezone.utc).isoformat();commands=[['python3','-B','-m','unittest','source_reference_identity_inventory_test'],[str(TC/'jdk-25.0.4/bin/javac'),'--release','25','-Xlint:all','-Werror','-d',str(classes),str(helper)]]
    for i,command in enumerate(commands):
        with(out/('phase-'+str(i)+'.private.log')).open('xb')as f:r=subprocess.run(command,stdout=f,stderr=subprocess.STDOUT,timeout=60)
        if r.returncode:raise ValueError('independent fixture and lint0 required before facts')
    # Snapshot src also has Tests; copy exactly the849 qualified Main files only.
    mirror=out/'input';mirror.mkdir()
    for name in identity['sourceHashes']:
        dest=mirror/name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(snapshot/name,dest)
    if {p.relative_to(mirror).as_posix():sha(p)for p in mirror.rglob('*.java')}!=identity['sourceHashes']:raise ValueError('all849 immutable Main-only parser inputs')
    command=[str(TC/'jdk-25.0.4/bin/java'),'-Xmx1536m','-cp',str(classes),'SourceReferenceIdentityInventory',str(mirror),classpath]
    r=subprocess.run(command,capture_output=True,text=True,timeout=180)
    with(out/'typed.private.log').open('x')as f:f.write(r.stdout+r.stderr);f.flush();os.fsync(f.fileno())
    if r.returncode:raise ValueError('all reference symbols must resolve; preserve failure')
    rows=facts(r.stdout)
    if any(row['path']not in identity['sourceHashes']for row in rows)or inputs()!=(snapshot,classpath,identity)or sha(helper)!=helper_sha or sha(fixture)!=fixture_sha:raise ValueError('all source/type/helper inputs unchanged')
    value={'actualExit':0,'source':SOURCE,'startUTC':start,'endUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'identity':identity,'helperSha256':helper_sha,'fixtureSha256':fixture_sha,'independentFixtureExit':0,'compileExit':0,'command':command,'rows':rows,'outputSha256':hashlib.sha256(r.stdout.encode()).hexdigest(),'formalAccepted':False,'F03Accepted':False,'disposition':'FACTS_ONLY_NOT_RULE_EXEMPTION','executedProductionPtAdded':0,'vmActions':0}
    with(out/'manifest.safe.json').open('x')as f:json.dump(value,f,sort_keys=True);f.flush();os.fsync(f.fileno())
    print(json.dumps({'actualExit':0,'source':SOURCE,'typedReferenceSites':len(rows),'manifestSha256':sha(out/'manifest.safe.json'),'F03Accepted':False}))
    return 0


if __name__=='__main__':main()
