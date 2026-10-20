"""Current typed guard facts from selected1664 bytes; no claim of pending whole3939 success."""
import json
import os
from pathlib import Path
import shutil
import types
import pg5689_current_identity_facts as previous
from pg5540_snapshot_scratch_selected import ROOT,TC,sha
from pg5584_field_accessor_inspection import compile_only_artifacts
from pg5780_jms_primary_whole import SOURCE,W

SLOT='pg5786-jms-identity-facts-v2'


def inputs():
    sp=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG5776-jms-primary-static-v1/manifest.json';pp=W/'pg5776-jms-primary-static-v1/manifest.safe.json'
    if sha(sp)!='aa0368e648a0d1e25d2413e9aa8c08966a30feeea5ea87b3841e78fc66abf72f'or sha(pp)!=json.loads(sp.read_bytes())['privateManifestSha256']:raise ValueError('fixed current849/1664 static input authority')
    proof=json.loads(pp.read_bytes());gp=W/'pg5774-jms-primary-green-v1/manifest.safe.json';green=json.loads(gp.read_bytes());snapshot=gp.parent/'source'
    if not(proof['source']==green['source']==SOURCE and proof['actualExit']==green['actualExit']==0 and green['selectedQualified']and(green['tests'],green['suites'])==(14,7)):raise ValueError('actual same-source selected14 only, not pending3939 success')
    current={p.relative_to(ROOT).as_posix():sha(p)for p in ROOT.glob('src/*/src/main/java/**/*.java')}
    mirrored={p.relative_to(snapshot).as_posix():sha(p)for p in snapshot.glob('src/*/src/main/java/**/*.java')}
    if len(current)!=849 or current!=mirrored or current!=proof['allSourceHashes']:raise ValueError('all849 exact current Main')
    roots=[snapshot/('src/schubert-nk-'+m+'/target/classes')for m in('protocol','storage','bootstrap','api','web','batch')]
    physical={p.parts[-3].removeprefix('schubert-nk-')+':'+c.relative_to(p).as_posix():sha(c)for p in roots for c in p.rglob('*.class')}
    if len(physical)!=1664 or physical!=proof['auxClassHashes']or physical!=green['allPhysicalMainSha256']:raise ValueError('all actual1664 current selected class bytes')
    release=W/'pg5430-release-v1';bom=release/'RELEASE-MANIFEST.json'
    if sha(bom)!='85fbce34711ac798d1e71a3e3a8a7a54cc070e074ec1255047c4ac75ef18fbd6':raise ValueError('immutable third-party BOM only')
    jars={}
    for row in json.loads(bom.read_bytes())['artifacts']:
        p=Path(row['path'])
        if '/lib/'not in row['path']or p.suffix!='.jar'or p.name.startswith('schubert-nk-'):continue
        target=release/p
        if target.is_symlink()or sha(target)!=row['sha256']:raise ValueError('every actual dependency hash')
        jars.setdefault(row['sha256'],target)
    provided,metadata=compile_only_artifacts();mirror=W/'pg5786-current-main-input-v1'
    if not mirror.exists():
        mirror.mkdir(mode=0o700)
        for name in current:
            target=mirror/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(snapshot/name,target)
    if {p.relative_to(mirror).as_posix():sha(p)for p in mirror.rglob('*.java')}!=current:raise ValueError('exact Main-only parser input, never overwrite existing mirror')
    return mirror,os.pathsep.join(map(str,[*roots,*jars.values(),*provided])),{'sourceHashes':current,'physicalMainSha256':physical,'selectedManifestSha256':sha(gp),'staticManifestSha256':sha(sp),'thirdPartyJarSha256':list(jars),'compileOnlyArtifacts':metadata,'pendingWholeNotQualified':True}


def namespace():
    scope={**vars(previous),'ROOT':ROOT,'W':W,'SOURCE':SOURCE,'SLOT':SLOT,'inputs':inputs}
    if scope['JDK']!=TC/'jdk-25.0.4/bin'or any(not(scope['JDK']/n).is_file()for n in('java','javac')):raise ValueError('existing JDK bin/tools contract required before output or execution')
    return scope


def main():
    os.umask(0o077)
    return types.FunctionType(previous.main.__code__,namespace())()


if __name__=='__main__':main()
