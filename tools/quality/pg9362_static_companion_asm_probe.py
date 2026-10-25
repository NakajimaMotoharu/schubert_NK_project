"""ASM code-reference witness, independently joined to JDK metadata and real Main source family."""
from collections import defaultdict
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import subprocess
from host_tool_invocation import capture, verify

ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional'
TC=ROOT.parent/'toolchain'
COMPILE=ROOT.parent/'pgpt-runs/PG379/pg9358-static-companion-compile55-v1'
SLOT=ROOT.parent/'pgpt-runs/PG379/pg9362-static-companion-asm-v1'
OUT=BASE/'PG9362-static-companion-asm-v1'
SOURCE='64446a9f8901084a4ad7eba1f66ae975eb2bbdea'
HELPER=ROOT/'tools/quality/architecture/StaticCompanionBytecodeAudit.java'
ASM=TC/'m2/repository/org/ow2/asm/asm/9.10.1/asm-9.10.1.jar'
ASM_SHA='ed825d10ab1399c8c0cb669e688cf0c8c82629b4c8399b58352b68e92ca10fcb'
ENV={'PATH':str(TC/'jdk-25.0.4/bin')+':/usr/bin:/bin','LANG':'C.UTF-8'}

def sha(raw):return hashlib.sha256(raw).hexdigest()
def write(path,value):
    with path.open('x') as stream:json.dump(value,stream,sort_keys=True,indent=2);stream.write('\n')
def step(label,command):
    start=dt.datetime.now(dt.timezone.utc).isoformat()
    write(SLOT/(label+'-begin.safe.json'),dict(command=command,startUTC=start,environment=ENV))
    with (SLOT/(label+'.stdout')).open('xb') as stdout,(SLOT/(label+'.stderr')).open('xb') as stderr:
        child=subprocess.Popen(command,cwd=SLOT,env=ENV,stdin=subprocess.DEVNULL,stdout=stdout,stderr=stderr,close_fds=True)
        write(SLOT/(label+'-process.safe.json'),dict(pid=child.pid,ownerPid=os.getpid(),command=command,startUTC=start,cwd=str(SLOT)))
        timed_out=False
        try:code=child.wait(timeout=180)
        except subprocess.TimeoutExpired:timed_out=True;child.kill();code=child.wait(timeout=15)
    record=dict(command=command,startUTC=start,endUTC=dt.datetime.now(dt.timezone.utc).isoformat(),actualExit=code,timedOut=timed_out,
      stdoutSha256=sha((SLOT/(label+'.stdout')).read_bytes()),stderrSha256=sha((SLOT/(label+'.stderr')).read_bytes()))
    write(SLOT/(label+'-exit.safe.json'),record);return record

def main():
    invocation=capture(Path(__file__));assert not SLOT.exists() and not OUT.exists()
    compile_path=BASE/'PG9358-static-companion-compile55-v1/manifest.json'
    javap_path=BASE/'PG9360-static-companion-javap-v1/manifest.json'
    assert sha(compile_path.read_bytes())=='1e6283063e08ae26c4abe5b9cd2d4eb4fce69a45365c4aae14b996641f61d751'
    assert sha(javap_path.read_bytes())=='a6cc01273a2d12b966524fdf7366ec90f9650d4826b5fcffc944cb1e115a65b6'
    compiled=json.loads(compile_path.read_bytes());javap=json.loads(javap_path.read_bytes())
    assert compiled['source']==javap['source']==SOURCE and compiled['actualExit']==javap['actualExit']==0
    map_path=javap_path.parent/'class-map.json';assert sha(map_path.read_bytes())==javap['classMapSha256']
    class_map=json.loads(map_path.read_bytes());assert len(class_map)==96
    by_class={row['classPath']:row for row in class_map};assert len(by_class)==96
    class_root=COMPILE/'fresh-test-classes'
    assert all(sha((class_root/path).read_bytes())==digest for path,digest in compiled['freshClassFiles'].items())
    assert sha(ASM.read_bytes())==ASM_SHA;helper_sha=sha(HELPER.read_bytes())
    os.umask(0o077);SLOT.mkdir();classes=SLOT/'helper-classes';classes.mkdir();catalog=SLOT/'class-catalog.tsv'
    with catalog.open('x') as stream:
        for path,row in sorted(by_class.items()):stream.write('\t'.join((path,row['sourceFile'],row['targetInternalName']))+'\n')
    begin=dict(source=SOURCE,invocation=invocation,compileManifestSha256=sha(compile_path.read_bytes()),javapManifestSha256=sha(javap_path.read_bytes()),
      helperPath=str(HELPER.relative_to(ROOT)),helperSha256=helper_sha,asmJarPath=str(ASM),asmJarSha256=ASM_SHA,
      classCatalogSha256=sha(catalog.read_bytes()),targetRuntimeClasspathEntries=0,environment=ENV)
    write(SLOT/'begin.safe.json',begin)
    stages=[step('compile-helper',[str(TC/'jdk-25.0.4/bin/javac'),'--release','25','-proc:none','-Xlint:all','-Werror',
      '-cp',str(ASM),'-d',str(classes),str(HELPER)])]
    if stages[0]['actualExit']==0:
        stages.append(step('probe-fresh-bytes',[str(TC/'jdk-25.0.4/bin/java'),'-cp',str(classes)+os.pathsep+str(ASM),HELPER.stem,str(class_root),str(catalog)]))
    code=stages[-1]['actualExit'];proofs=[];vectors=0;by_test=defaultdict(list)
    if code==0:
        lines=(SLOT/'probe-fresh-bytes.stdout').read_text().splitlines();assert lines[0]=='SELFTEST\t10';vectors=10
        seen=set()
        for line in lines[1:]:
            path,matched,kinds,source_file,class_name,owners=line.split('\t')
            assert path not in seen and matched in ('true','false');seen.add(path)
            original=by_class[path];assert source_file==original['sourceFile'] and class_name==original['className']
            observed=set(owners.split(',')) if owners else set()
            actual=observed & set(original['allowedMainFamily'])
            independent={row['owner'] for row in original['javapOwnerReferences']}
            cross=actual & independent
            confirmed=matched=='true' and bool(cross)
            proof=dict(classPath=path,classSha256=original['classSha256'],sourceFile=source_file,className=class_name,
              testPath=original['testPath'],mainPath=original['mainPath'],asmFamilySyntaxReference=matched=='true',
              kinds=sorted(kinds.split(',')) if kinds else [],observedFamilyOwners=sorted(observed),
              sourceBoundMainOwners=sorted(actual),independentJavapOwners=sorted(independent),confirmedOwners=sorted(cross),
              referenceConfirmed=confirmed,unknownFamilyNotAssigned=sorted(observed-set(original['allowedMainFamily'])))
            proofs.append(proof);by_test[original['testPath']].append(proof)
        assert seen==set(by_class)
    selected=compiled['begin']['selected55SourceRows'];confirmed=[];unconfirmed=[]
    if code==0:
        assert set(by_test)=={row['path'] for row in selected}
        for row in selected:
            witnesses=[proof for proof in by_test[row['path']] if proof['referenceConfirmed']]
            if witnesses:
                confirmed.append(dict(path=row['path'],sha256=row['sha256'],mainPath=row['mainPath'],mainSha256=row['mainSha256'],
                  owner=row['proposedOwner'],costOwner=row['proposedCostOwner'],basis='FRESH_STATIC_COMPILE_ASM_JAVAP_SAME_SOURCE_MAIN_REFERENCE',
                  witnessClasses=[proof['classPath'] for proof in witnesses],status='PROPOSED_CANDIDATE_REVIEW_REQUIRED_NOT_ACCEPTED'))
            else:unconfirmed.append(dict(path=row['path'],reason='DIRECT_CODE_REFERENCE_NOT_PROVED_KEEP_UNKNOWN'))
    assert sha(HELPER.read_bytes())==helper_sha and sha(ASM.read_bytes())==ASM_SHA
    assert all(sha((class_root/path).read_bytes())==digest for path,digest in compiled['freshClassFiles'].items())
    assert all(sha((ROOT/row['path']).read_bytes())==row['sha256'] for row in selected)
    verify(invocation);OUT.mkdir();write(OUT/'class-proofs.json',proofs);write(OUT/'confirmed-candidates.json',confirmed);write(OUT/'unconfirmed-candidates.json',unconfirmed)
    result=dict(actualExit=code,source=SOURCE,begin=begin,stages=stages,bytecodeFixtureVectors=vectors,
      classProofs=len(proofs),sourceFiles=55,confirmedCandidates=len(confirmed),unconfirmedCandidates=len(unconfirmed),
      proofsSha256=sha((OUT/'class-proofs.json').read_bytes()),confirmedSha256=sha((OUT/'confirmed-candidates.json').read_bytes()),
      unconfirmedSha256=sha((OUT/'unconfirmed-candidates.json').read_bytes()),allowedOwnerFamiliesBoundToActualMainSourceFile=True,
      rawLiteralValuesPublished=False,actualRegistered=0,productTestsExecuted=0,targetRuntimeClassLoading=0,targetRuntimeInvocation=0,
      actualVmActions=0,actualNativeActions=0,coverage=None,newTestIds=0,newMain=0,formalUpdated=False,newAccepted=0,
      wholeG13Accepted=False,whole451Accepted=False,effortPercent=None)
    write(SLOT/'manifest.safe.json',result);write(OUT/'manifest.json',result)
    print(json.dumps(dict(actualExit=code,classProofs=len(proofs),confirmed=len(confirmed),unconfirmed=len(unconfirmed),fixtureVectors=vectors,manifestSha256=sha((OUT/'manifest.json').read_bytes()))))
    raise SystemExit(code)

if __name__=='__main__':main()
