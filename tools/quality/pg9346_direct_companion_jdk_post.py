"""Independent JDK parse-only source witness; no target analysis, compilation or loading."""
from collections import Counter
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
SLOT=ROOT.parent/'pgpt-runs/PG379/pg9346-direct-companion-jdk-post-v1'
OUT=BASE/'PG9346-direct-companion-jdk-post-v1'
PRIMARY=BASE/'PG9344-direct-companion-ast-v1/manifest.json'
PRIMARY_SHA='6a8bea332ad27bccd567949395166f4cef2334bc9770063c3a7ed0d0f405c5d0'
SOURCE='64446a9f8901084a4ad7eba1f66ae975eb2bbdea'
HELPER=ROOT/'tools/quality/architecture/DirectCompanionJdkSourceAudit.java'
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
    invocation=capture(Path(__file__));assert not SLOT.exists() and not OUT.exists() and sha(PRIMARY.read_bytes())==PRIMARY_SHA
    primary=json.loads(PRIMARY.read_bytes());assert primary['source']==SOURCE and primary['actualExit']==0 and primary['parsedInputs']==337
    proposal_path=PRIMARY.parent/'proposals.json';status_path=PRIMARY.parent/'source-statuses.json'
    assert sha(proposal_path.read_bytes())==primary['proposalsSha256'] and sha(status_path.read_bytes())==primary['statusesSha256']
    proposals=json.loads(proposal_path.read_bytes());rows=json.loads(status_path.read_bytes());assert len(proposals)==280 and len(rows)==675
    catalog=ROOT.parent/'pgpt-runs/PG379/pg9344-direct-companion-ast-v1/input.tsv'
    catalog_raw=catalog.read_bytes();assert sha(catalog_raw)==primary['begin']['inputCatalogSha256']
    helper_sha=sha(HELPER.read_bytes())
    assert subprocess.check_output(['git','diff','--name-only',SOURCE,'--','src','pom.xml','.mvn','mvnw'],cwd=ROOT)==b''
    assert all(sha((ROOT/row['path']).read_bytes())==row['sha256'] for row in rows)
    os.umask(0o077);SLOT.mkdir();classes=SLOT/'classes';classes.mkdir();empty=SLOT/'empty-classpath';empty.mkdir()
    begin=dict(source=SOURCE,invocation=invocation,primaryManifestSha256=PRIMARY_SHA,helperPath=str(HELPER.relative_to(ROOT)),
      helperSha256=helper_sha,inputCatalogSha256=sha(catalog_raw),parseInputs=337,actualExternalLibraries=0,
      compilerOperations=['JavacTask.parse'],analyzeInvoked=False,generateInvoked=False,targetClassLoading=0,
      targetCompilationOutput=0,environment=ENV)
    write(SLOT/'begin.safe.json',begin)
    stages=[step('compile-helper',[str(TC/'jdk-25.0.4/bin/javac'),'--release','25','-proc:none','-Xlint:all','-Werror',
      '-d',str(classes),str(HELPER)])]
    if stages[0]['actualExit']==0:
        stages.append(step('independent-jdk-parse',[str(TC/'jdk-25.0.4/bin/java'),'-cp',str(classes),HELPER.stem,str(ROOT),str(catalog),str(empty)]))
    code=stages[-1]['actualExit'];statuses={};confirmed=[];unconfirmed=[];self_vectors=0
    if code==0:
        lines=(SLOT/'independent-jdk-parse.stdout').read_text().splitlines();assert lines[0]=='SELFTEST\t13';self_vectors=13
        for line in lines[1:]:
            path,status=line.split('\t');assert path not in statuses and status in ('true','false');statuses[path]=status=='true'
        requested={line.split('\t',1)[0] for line in catalog_raw.decode().splitlines()}
        assert set(statuses)==requested and len(statuses)==337
        for row in proposals:
            if statuses[row['path']]:confirmed.append(row)
            else:unconfirmed.append(dict(path=row['path'],reason='INDEPENDENT_JDK_TYPED_REFERENCE_NOT_PROVED; KEEP_UNREGISTERED'))
    assert sha(HELPER.read_bytes())==helper_sha and all(sha((ROOT/row['path']).read_bytes())==row['sha256'] for row in rows)
    assert all(path.name.startswith(HELPER.stem) for path in classes.rglob('*.class')) and not list(empty.iterdir())
    assert subprocess.check_output(['git','diff','--name-only',SOURCE,'--','src','pom.xml','.mvn','mvnw'],cwd=ROOT)==b''
    verify(invocation);OUT.mkdir();write(OUT/'confirmed-candidates.json',confirmed);write(OUT/'unconfirmed-candidates.json',unconfirmed)
    result=dict(actualExit=code,source=SOURCE,begin=begin,stages=stages,primaryProposed=280,jdkParsedInputs=len(statuses),
      independentFixtureVectors=self_vectors,confirmedCandidates=len(confirmed),unconfirmedCandidates=len(unconfirmed),
      confirmedSha256=sha((OUT/'confirmed-candidates.json').read_bytes()),unconfirmedSha256=sha((OUT/'unconfirmed-candidates.json').read_bytes()),
      confirmedOwnerCounts=dict(Counter(row['owner'] for row in confirmed)),actualRegistered=0,
      productTestsExecuted=0,targetClassLoading=0,targetClassesCompiled=0,actualNativeActions=0,actualVmActions=0,
      coverage=None,newTestIds=0,newMain=0,formalUpdated=False,newAccepted=0,effortPercent=None,
      wholeG13Accepted=False,whole451Accepted=False)
    write(SLOT/'manifest.safe.json',result);write(OUT/'manifest.json',result)
    print(json.dumps(dict(actualExit=code,independentParsed=len(statuses),confirmed=len(confirmed),unconfirmed=len(unconfirmed),manifestSha256=sha((OUT/'manifest.json').read_bytes()))))
    raise SystemExit(code)

if __name__=='__main__':main()
