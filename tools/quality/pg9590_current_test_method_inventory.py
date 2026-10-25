"""Parse current public Test declarations only; this denominator is never an executed test count."""
from collections import Counter
import datetime as dt
import json
import os
from pathlib import Path
import subprocess
import g07_host_class_provenance_inputs as data
import pg9346_direct_companion_jdk_post as steps
from host_tool_invocation import capture,verify

ROOT=data.ROOT;BASE=data.BASE;SOURCE=data.SOURCE
SLOT=ROOT.parent/'pgpt-runs/PG379/pg9590-current-test-method-inventory-v1'
OUT=BASE/'PG9590-current-test-method-inventory-v1'
SPEC=ROOT/'evidence/01_PT/018_NK-OPS-001/1944_G13TestMethodInventory_現source分母仕様.md'
SPEC_SHA='54118e47ab989b30faa6073be88de5f07a70207c56e11fd2dbdc2268f17325b6'
HELPER=ROOT/'tools/quality/architecture/ExistingTestMethodJdkAudit.java'

def main():
    invocation=capture(Path(__file__));assert not OUT.exists() and not SLOT.exists()
    assert data.sha(SPEC.read_bytes())==SPEC_SHA
    normal=data.read_checked(BASE/'PG9246-web-life-lock-six-compile-v1/manifest.json',data.PINS['normal'][1])
    assert normal['source']==SOURCE and normal['actualExit']==0
    hashes={p:h for p,h in normal['begin']['inputHashes'].items() if '/src/test/java/' in p and p.endswith('.java')}
    assert len(hashes)==824
    for path,digest in hashes.items():
        assert data.sha((ROOT/path).read_bytes())==data.sha((data.NORMAL/path).read_bytes())==digest
    owners=data.read_checked(BASE/'PG9546-shared-fixture7-source-join-v1/manifest.json','4d82743eb894ccd448a2ef88b40f566bc0fb08a8ee4b5128a925e49c08b7dd61')
    owner_rows={r['path']:r for r in owners['sourceRows']}
    cross=data.read_checked(BASE/'PG9554-cross-method23-source-ast-v1/manifest.json','1894885ded2b7d5bab5fc3ee741a8ea2bb0b1bc49665b5417c62158c01224f78')
    cross_rows=data.read_checked(BASE/'PG9554-cross-method23-source-ast-v1/method-trace.json',cross['methodTraceSha256'])
    existing={(r['path'],r['className'],r['method'],r['parameterCount']):r for r in cross_rows}
    assert len(existing)==23
    assert subprocess.check_output(['git','diff','--name-only',SOURCE,'--','src','pom.xml','.mvn','mvnw'],cwd=ROOT)==b''
    os.umask(0o077);SLOT.mkdir();classes=SLOT/'reader';classes.mkdir();catalog=SLOT/'input-paths.txt'
    with catalog.open('x') as stream:stream.write('\n'.join(sorted(hashes))+'\n')
    helper_sha=data.sha(HELPER.read_bytes());steps.SLOT=SLOT;tc=ROOT.parent/'toolchain'
    stages=[steps.step('compile-source-reader',[str(tc/'jdk-25.0.4/bin/javac'),'--release','25','-proc:none','-Xlint:all','-Werror','-d',str(classes),str(HELPER)])]
    assert stages[0]['actualExit']==0 and not stages[0]['timedOut']
    stages.append(steps.step('parse-all-test-declarations',[str(tc/'jdk-25.0.4/bin/java'),'-cp',str(classes),HELPER.stem,str(ROOT),str(catalog)]))
    assert stages[-1]['actualExit']==0 and not stages[-1]['timedOut']
    lines=(SLOT/'parse-all-test-declarations.stdout').read_text().splitlines();assert lines[0]=='SELFTEST\t7'
    rows=[];keys=set();referenced=set();source_counts=Counter()
    for line in lines[1:]:
        path,owner,name,parameters,start,end=line.split('\t');parameters=int(parameters);start=int(start);end=int(end)
        assert path in hashes and 0<start<=end and parameters>=0
        key=path+'#'+owner+'#'+name+'/'+str(parameters)+'@'+str(start)
        assert key not in keys;keys.add(key);source_counts[path]+=1
        known=owner_rows.get(path);basis=existing.get((path,owner,name,parameters))
        if known:assert known['sha256']==hashes[path]
        if basis:referenced.add((path,owner,name,parameters))
        rows.append(dict(methodDeclarationKey=key,path=path,sourceSha256=hashes[path],className=owner,method=name,
          parameterCount=parameters,startLine=start,endLine=end,annotationKind='org.junit.jupiter.api.Test',
          fileCanonicalOwner=known.get('canonicalOwner') if known else None,
          fileCanonicalCostOwner=known.get('canonicalCostOwner') if known else None,
          fileOwnerMeaning='FILE_RESPONSIBILITY_CANDIDATE_NOT_METHOD_ORACLE_OR_ACCEPTANCE',
          existingCross23MethodTrace=basis,otherMethodTestIdOrOracleNotInferred=True,
          productExecutedByThisInventory=False))
    assert referenced==set(existing)
    rows.sort(key=lambda r:r['methodDeclarationKey'])
    assert data.sha(HELPER.read_bytes())==helper_sha and all(data.sha((ROOT/p).read_bytes())==d for p,d in hashes.items())
    assert all(p.name.startswith(HELPER.stem) for p in classes.rglob('*.class'))
    verify(invocation);OUT.mkdir();data.write(OUT/'test-method-declarations.json',rows)
    data.write(OUT/'test-source-counts.json',[dict(path=p,sourceSha256=hashes[p],ordinaryTestDeclarations=source_counts[p]) for p in sorted(hashes)])
    value=dict(actualExit=0,source=SOURCE,timeUTC=dt.datetime.now(dt.timezone.utc).isoformat(),invocation=invocation,
      specSha256=SPEC_SHA,normalManifestSha256=data.PINS['normal'][1],helperSha256=helper_sha,helperStages=stages,
      compilerOperations=['JavacTask.parse'],analyzeInvoked=False,generateInvoked=False,syntaxVectors=7,
      sourceFiles=824,sourceFilesWithOrdinaryTests=len(source_counts),sourceFilesWithoutOrdinaryTests=824-len(source_counts),
      methodDeclarations=len(rows),declarationsWithFileOwner=sum(r['fileCanonicalOwner'] is not None for r in rows),
      declarationsWithExistingCross23MethodTrace=sum(r['existingCross23MethodTrace'] is not None for r in rows),
      sourceHashes=hashes,methodDeclarationsSha256=data.sha((OUT/'test-method-declarations.json').read_bytes()),
      sourceCountsSha256=data.sha((OUT/'test-source-counts.json').read_bytes()),
      otherTestAnnotationKindsNotQualified=['org.junit.jupiter.api.RepeatedTest'],methodTestIdsNotInvented=True,
      targetClassesCompiled=0,targetClassLoading=0,targetRuntimeInvocations=0,productTestsExecuted=0,newTestIds=0,newMain=0,
      coverage=None,formalUpdated=False,newAccepted=0,effortPercent=None,wholeG13Accepted=False,whole451Accepted=False)
    data.write(SLOT/'manifest.safe.json',value);data.write(OUT/'manifest.json',value)
    print(json.dumps({k:value[k] for k in ('actualExit','sourceFiles','methodDeclarations','declarationsWithFileOwner','declarationsWithExistingCross23MethodTrace')}))
    print('manifestSha256='+data.sha((OUT/'manifest.json').read_bytes()))

if __name__=='__main__':main()
