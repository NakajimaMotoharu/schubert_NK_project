"""JDK parse-only23 Test methods, frozen case families and responsibility roles; never run targets."""
from collections import Counter
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import subprocess
import pg9346_direct_companion_jdk_post as jdk
from host_tool_invocation import capture,verify

ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional'
OUT=BASE/'PG9554-cross-method23-source-ast-v1'
SLOT=ROOT.parent/'pgpt-runs/PG379/pg9554-cross-method23-source-ast-v1'
SOURCE='64446a9f8901084a4ad7eba1f66ae975eb2bbdea'
HELPER=ROOT/'tools/quality/architecture/ExistingTestMethodJdkAudit.java'
SPEC=ROOT/'evidence/01_PT/018_NK-OPS-001/1936_G13CrossMethod23_TestID・責任対応仕様.md'
PATHS={
 'API':'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/persistence/BorrowedJdbcFatal329Test.java',
 'WEB':'src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/session/TargetBusinessControllerTest.java'}

def sha(raw):return hashlib.sha256(raw).hexdigest()
def write(path,value):
    with path.open('x') as f:json.dump(value,f,sort_keys=True,indent=2);f.write('\n')

def main():
    invocation=capture(Path(__file__));assert not OUT.exists() and not SLOT.exists()
    spec=SPEC.read_bytes();assert sha(spec)=='c87fe5eb73645d2f8a0055ffc8d7cc65bf8d0ceff68b61d8552ba85a94209aef'
    oracle={}
    for line in spec.decode().splitlines():
        if not line.startswith(('|API|','|WEB|')):continue
        _,label,name,ids,business,mains,notes,_=line.split('|');key=(PATHS[label],name)
        assert key not in oracle
        oracle[key]=dict(existingTestFamilies=ids.split(','),businessContractWbs=business.split(','),
          reviewedMainSubjects=dict(p.split(':') for p in mains.split(',')),independentOracleReference=notes,
          oracleDocument='evidence/01_PT/018_NK-OPS-001/1431_SSC329_green23原資格・借用repository仕様.md' if label=='API' else 'evidence/01_PT/016_NK-WEB-002/083_NK-WEB-002_通知取消・質問削除単体テスト仕様書.md')
    assert len(oracle)==23 and Counter(p for p,_ in oracle)==Counter({PATHS['API']:9,PATHS['WEB']:14})
    for path,digest in (
      ('evidence/01_PT/018_NK-OPS-001/1431_SSC329_green23原資格・借用repository仕様.md','ea7121841475c0bed4e0ce3ef84534846db00d8d051b2039223a50553e95a938'),
      ('evidence/01_PT/016_NK-WEB-002/083_NK-WEB-002_通知取消・質問削除単体テスト仕様書.md','9fc856dfea8c2bd56d0448ba4ed8f605decee436bde54d33b1f6d5f5fc693324')):
        assert sha((ROOT/path).read_bytes())==digest
    nr=(BASE/'PG9246-web-life-lock-six-compile-v1/manifest.json').read_bytes()
    assert sha(nr)=='989d9e912a0a6531ad8a2417467ddca6d37a292d6582206fb696b324c600ee46'
    hashes=json.loads(nr)['begin']['inputHashes'];snapshot=ROOT.parent/'pgpt-runs/PG379/pg9246-web-life-lock-six-compile-v1/snapshot'
    source_hashes={}
    for path in PATHS.values():
        assert sha((ROOT/path).read_bytes())==hashes[path]==sha((snapshot/path).read_bytes());source_hashes[path]=hashes[path]
    assert subprocess.check_output(['git','diff','--name-only',SOURCE,'--','src','pom.xml','.mvn','mvnw'],cwd=ROOT)==b''
    helper_sha=sha(HELPER.read_bytes());os.umask(0o077);SLOT.mkdir();classes=SLOT/'classes';classes.mkdir()
    catalog=SLOT/'input-paths.txt'
    with catalog.open('x') as f:f.write('\n'.join(PATHS.values())+'\n')
    jdk.SLOT=SLOT
    stages=[jdk.step('compile-helper',[str(jdk.TC/'jdk-25.0.4/bin/javac'),'--release','25','-proc:none','-Xlint:all','-Werror','-d',str(classes),str(HELPER)])]
    assert stages[0]['actualExit']==0 and not stages[0]['timedOut']
    stages.append(jdk.step('parse-test-methods',[str(jdk.TC/'jdk-25.0.4/bin/java'),'-cp',str(classes),HELPER.stem,str(ROOT),str(catalog)]))
    assert stages[-1]['actualExit']==0 and not stages[-1]['timedOut']
    lines=(SLOT/'parse-test-methods.stdout').read_text().splitlines();assert lines[0]=='SELFTEST\t7'
    observed={}
    for line in lines[1:]:
        path,owner,name,parameters,start,end=line.split('\t');key=(path,name)
        assert key in oracle and key not in observed and int(parameters)==0 and 0<int(start)<=int(end)
        observed[key]=dict(path=path,sourceSha256=source_hashes[path],methodKey=path+'#'+name+'()',className=owner,
          method=name,parameterCount=0,startLine=int(start),endLine=int(end),**oracle[key])
    assert set(observed)==set(oracle) and len(observed)==23
    rows=[observed[key] for key in sorted(observed)]
    assert all(p.name.startswith(HELPER.stem) for p in classes.rglob('*.class'))
    assert sha(HELPER.read_bytes())==helper_sha and all(sha((ROOT/p).read_bytes())==d for p,d in source_hashes.items())
    verify(invocation);OUT.mkdir();write(OUT/'method-trace.json',rows)
    value=dict(actualExit=0,source=SOURCE,timeUTC=dt.datetime.now(dt.timezone.utc).isoformat(),invocation=invocation,
      specSha256=sha(spec),normalManifestSha256=sha(nr),helperPath=str(HELPER.relative_to(ROOT)),helperSha256=helper_sha,
      inputHashes=source_hashes,methodTraceSha256=sha((OUT/'method-trace.json').read_bytes()),sourceFiles=2,methodDeclarations=23,
      existingDistinctTestFamilies=len({x for row in rows for x in row['existingTestFamilies']}),
      methodCaseFamilyRelations=sum(len(row['existingTestFamilies']) for row in rows),syntaxVectors=7,stages=stages,
      compilerOperations=['JavacTask.parse'],analyzeInvoked=False,generateInvoked=False,targetClassesCompiled=0,targetClassLoading=0,
      targetRuntimeInvocations=0,productTestsExecuted=0,newTestIds=0,coverage=None,newAccepted=0,formalUpdated=False,
      filePrimaryOwnersReassigned=False,fileOwnershipRegistered=1781,fileOwnershipUnregistered=8)
    write(OUT/'manifest.json',value);print(json.dumps(dict(actualExit=0,methods=23,manifestSha256=sha((OUT/'manifest.json').read_bytes()))))

if __name__=='__main__':main()
