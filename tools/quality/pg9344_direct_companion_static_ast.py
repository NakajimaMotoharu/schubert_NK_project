"""Bounded public Java source AST candidates; no target classpath, test or native execution."""
from collections import Counter
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
from host_tool_invocation import capture, verify

ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional'
TC=ROOT.parent/'toolchain'
SLOT=ROOT.parent/'pgpt-runs/PG379/pg9344-direct-companion-ast-v1'
OUT=BASE/'PG9344-direct-companion-ast-v1'
SOURCE='64446a9f8901084a4ad7eba1f66ae975eb2bbdea'
JAR=TC/'m2/repository/com/github/javaparser/javaparser-core/3.28.2/javaparser-core-3.28.2.jar'
JAR_SHA='b5499a3b1c40b16c0671fabe478c9aafeab38160c6fde74a6c13f42d86716ecd'
HELPER=ROOT/'tools/quality/architecture/DirectCompanionSourceAudit.java'
JAVA=re.compile(r'src/schubert-nk-(protocol|storage|bootstrap|api|web|batch)/src/(main|test)/java/.+\.java')
ENV={'PATH':str(TC/'jdk-25.0.4/bin')+':/usr/bin:/bin','LANG':'C.UTF-8'}

def sha(raw):return hashlib.sha256(raw).hexdigest()
def write(path,value):
    with path.open('x') as stream:json.dump(value,stream,sort_keys=True,indent=2);stream.write('\n')

def step(label,command):
    start=dt.datetime.now(dt.timezone.utc).isoformat()
    write(SLOT/(label+'-begin.safe.json'),dict(command=command,startUTC=start,environment=ENV))
    with (SLOT/(label+'.stdout')).open('xb') as stdout,(SLOT/(label+'.stderr')).open('xb') as stderr:
        child=subprocess.Popen(command,cwd=SLOT,env=ENV,stdin=subprocess.DEVNULL,stdout=stdout,stderr=stderr,close_fds=True)
        write(SLOT/(label+'-process.safe.json'),dict(pid=child.pid,ownerPid=os.getpid(),command=command,cwd=str(SLOT),startUTC=start))
        timed_out=False
        try:code=child.wait(timeout=180)
        except subprocess.TimeoutExpired:timed_out=True;child.kill();code=child.wait(timeout=15)
    record=dict(command=command,startUTC=start,endUTC=dt.datetime.now(dt.timezone.utc).isoformat(),
      actualExit=code,timedOut=timed_out,stdoutSha256=sha((SLOT/(label+'.stdout')).read_bytes()),stderrSha256=sha((SLOT/(label+'.stderr')).read_bytes()))
    write(SLOT/(label+'-exit.safe.json'),record);return record

def main():
    invocation=capture(Path(__file__));assert not SLOT.exists() and not OUT.exists()
    normal_path=BASE/'PG9246-web-life-lock-six-compile-v1/manifest.json'
    owners_path=BASE/'PG9334-g13-storage-residual-join-v1/manifest.json'
    assert sha(normal_path.read_bytes())=='989d9e912a0a6531ad8a2417467ddca6d37a292d6582206fb696b324c600ee46'
    assert sha(owners_path.read_bytes())=='69df39386cdb70e792f3ab31de0c050c6c465a4d9a6b0264e17f29b9d1390ffd'
    normal=json.loads(normal_path.read_bytes());owners=json.loads(owners_path.read_bytes())
    assert normal['source']==owners['source']==SOURCE and normal['actualExit']==owners['actualExit']==0
    inventory=json.loads((ROOT/'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json').read_bytes())
    logical={row['path']:row for row in inventory['artifacts']};known={row['path']:row for row in owners['sourceRows']}
    hashes=normal['begin']['inputHashes'];java_paths={path for path in hashes if JAVA.fullmatch(path)}
    mains={path for path in java_paths if JAVA.fullmatch(path)[2]=='main'}
    tests=java_paths-mains;unknown=sorted(tests-set(logical)-set(known))
    assert len(java_paths)==1789 and len(mains)==965 and len(tests)==824 and len(unknown)==675
    main_owners={}
    for path in mains:
        if path in logical:owner,cost=logical[path]['owner'],logical[path]['costOwner']
        else:owner,cost=known[path]['canonicalOwner'],known[path]['canonicalCostOwner']
        assert owner and cost==owner;main_owners[path]=(owner,cost)
    candidates=[];rows=[]
    for path in unknown:
        assert sha((ROOT/path).read_bytes())==hashes[path]
        row=dict(path=path,sha256=hashes[path],module=JAVA.fullmatch(path)[1],canonicalOwner=None,canonicalCostOwner=None,
          testExecuted=False,accepted=False,astParsed=False)
        if not path.endswith('Test.java'):row['status']='NO_EXACT_TEST_SUFFIX'
        else:
            main=path.replace('/src/test/java/','/src/main/java/').removesuffix('Test.java')+'.java'
            if main not in main_owners:row['status']='NO_EXACT_COMPANION_MAIN'
            else:
                assert sha((ROOT/main).read_bytes())==hashes[main]
                qualified=main.split('/src/main/java/',1)[1].removesuffix('.java').replace('/','.')
                package,target=qualified.rsplit('.',1)
                row.update(mainPath=main,mainSha256=hashes[main],proposedOwner=main_owners[main][0],proposedCostOwner=main_owners[main][1])
                candidates.append((path,package,target));row['status']='AST_PENDING'
        rows.append(row)
    assert candidates and sha(JAR.read_bytes())==JAR_SHA
    helper_sha=sha(HELPER.read_bytes())
    assert subprocess.check_output(['git','diff','--name-only',SOURCE,'--','src','pom.xml','.mvn','mvnw'],cwd=ROOT)==b''
    os.umask(0o077);SLOT.mkdir();classes=SLOT/'classes';classes.mkdir()
    catalog=SLOT/'input.tsv'
    with catalog.open('x') as stream:
        for fields in candidates:assert all('\t' not in field and '\n' not in field for field in fields);stream.write('\t'.join(fields)+'\n')
    begin=dict(source=SOURCE,head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
      invocation=invocation,helperPath=str(HELPER.relative_to(ROOT)),helperSha256=helper_sha,
      parserJarPath=str(JAR),parserJarSha256=JAR_SHA,parserVersion='3.28.2',normalManifestSha256=sha(normal_path.read_bytes()),
      priorOwnershipManifestSha256=sha(owners_path.read_bytes()),unknownSourcePaths=675,exactCompanionParseInputs=len(candidates),
      inputCatalogSha256=sha(catalog.read_bytes()),targetModuleJarsInClasspath=0,targetClassesCompiled=0,environment=ENV)
    write(SLOT/'begin.safe.json',begin)
    stages=[step('compile-helper',[str(TC/'jdk-25.0.4/bin/javac'),'--release','25','-proc:none','-Xlint:all','-Werror','-cp',str(JAR),'-d',str(classes),str(HELPER)])]
    if stages[0]['actualExit']==0:
        stages.append(step('parse-public-sources',[str(TC/'jdk-25.0.4/bin/java'),'-cp',str(classes)+os.pathsep+str(JAR),HELPER.stem,str(ROOT),str(catalog)]))
    code=stages[-1]['actualExit'];proposed=[];statuses={};self_vectors=0
    if code==0:
        lines=(SLOT/'parse-public-sources.stdout').read_text().splitlines()
        assert lines[0]=='SELFTEST\t16';self_vectors=16
        for line in lines[1:]:
            path,status=line.split('\t');assert path not in statuses
            assert status in {'REFERENCED_TARGET','PARSE_UNRESOLVED','PACKAGE_MISMATCH','CONFLICTING_IMPORT','SHADOWED_TYPE',
              'SHADOWED_TYPE_PARAMETER','SHADOWED_IDENTIFIER','INHERITANCE_UNRESOLVED','NO_TYPED_TARGET_REFERENCE'}
            statuses[path]=status
        assert set(statuses)=={row[0] for row in candidates}
        for row in rows:
            if row['path'] in statuses:
                row.update(status=statuses[row['path']],astParsed=True)
                if row['status']=='REFERENCED_TARGET':
                    proposed.append(dict(path=row['path'],sha256=row['sha256'],mainPath=row['mainPath'],mainSha256=row['mainSha256'],
                      owner=row['proposedOwner'],costOwner=row['proposedCostOwner'],basis='EXACT_SAME_PACKAGE_COMPANION_WITH_UNSHADOWED_AST_TYPE_REFERENCE',
                      status='PROPOSED_CANDIDATE_REVIEW_REQUIRED_NOT_ACCEPTED'))
    assert sha(HELPER.read_bytes())==helper_sha and sha(JAR.read_bytes())==JAR_SHA
    assert all(sha((ROOT/path).read_bytes())==hashes[path] for path in unknown)
    assert subprocess.check_output(['git','diff','--name-only',SOURCE,'--','src','pom.xml','.mvn','mvnw'],cwd=ROOT)==b''
    verify(invocation);OUT.mkdir()
    write(OUT/'proposals.json',proposed);write(OUT/'source-statuses.json',rows)
    result=dict(actualExit=code,source=SOURCE,begin=begin,stages=stages,selfTestVectors=self_vectors,
      statusCounts=dict(Counter(row['status'] for row in rows)),unregisteredBefore=675,parsedInputs=len(candidates),
      proposedCandidates=len(proposed),remainingUnproposed=675-len(proposed),proposalsSha256=sha((OUT/'proposals.json').read_bytes()),
      statusesSha256=sha((OUT/'source-statuses.json').read_bytes()),ownerCounts=dict(Counter(row['owner'] for row in proposed)),
      actualRegistered=0,productTestsExecuted=0,targetClassLoading=0,targetClassesCompiled=0,
      actualVmActions=0,actualNativeActions=0,actualDatabaseActions=0,coverage=None,newTestIds=0,newMain=0,
      formalUpdated=False,newAccepted=0,wholeG13Accepted=False,whole451Accepted=False,effortPercent=None)
    write(SLOT/'manifest.safe.json',result);write(OUT/'manifest.json',result)
    print(json.dumps(dict(actualExit=code,parseInputs=len(candidates),proposed=len(proposed),statuses=result['statusCounts'],manifestSha256=sha((OUT/'manifest.json').read_bytes()))))
    raise SystemExit(code)

if __name__=='__main__':main()
