"""Byte-only unfiltered post for one genuine new ordinary Test, no old exec union."""
from pathlib import Path
import datetime,hashlib,json,subprocess
r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';w=r.parent/'pgpt-runs/PG379';tc=r.parent/'toolchain';ld=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ref=lambda p:dict(path=str(p.relative_to(r)),sha256=sha(p))
c=ld(b/'input/4598_p00405_projection1_profile.json');unit=ld(r/c['slots']['unit']/'manifest.json');post=ld(r/c['slots']['post']/'manifest.json');prepare=ld(r/c['slots']['prepare']/'manifest.json');assert unit['actualExit']==post['actualExit']==0 and unit['tests']==post['tests']==1 and unit['failures']==unit['errors']==unit['skipped']==0
work=w/c['privateDirs']['prepare'];slot=w/c['privateDirs']['unit'];names=c['physicalClasses'];assert len(names)==1 and all(sha(work/'target/classes'/n)==h for n,h in prepare['physicalClassHashes'].items())
q=ld(b/'evidence/PG31432-generated-code-supplemental-tool-v1/compile.json');assert ld(b/'evidence/PG31434-generated-code-tool-selftest-v1/manifest.json')['toolTests']==12
assert all(sha(Path(x['path']))==x['sha256'] for x in q['dependencies'])
out=b/'evidence/PG37114-p00405-projection1-unfiltered-v1';assert not out.exists();out.mkdir();command=[str(tc/'jdk-25.0.4/bin/java'),'-cp',':'.join([str(w/'pg31432-generated-code-supplemental-tool-v1/toolclasses'),*[x['path'] for x in q['dependencies']]]),'org.jacoco.core.internal.analysis.UnfilteredCodeMeasurement',str(slot/'jacoco.exec'),*[str(work/'target/classes'/n) for n in names]]
start=datetime.datetime.now(datetime.timezone.utc).isoformat()
with (out/'unfiltered.stdout').open('xb') as stdout,(out/'unfiltered.stderr').open('xb') as stderr:result=subprocess.run(command,stdout=stdout,stderr=stderr,timeout=120)
terminal=datetime.datetime.now(datetime.timezone.utc).isoformat();assert result.returncode==0 and (out/'unfiltered.stderr').stat().st_size==0
classes=[];methods=[]
for line in (out/'unfiltered.stdout').read_text().splitlines():
 f=line.split('\t');isclass=f[0]=='CLASS';assert f[0] in ['CLASS','METHOD'];row=dict(name=f[1],id=f[2],counters={}) if isclass else dict(className=f[1],name=f[2],descriptor=f[3],counters={})
 for item in f[6 if isclass else 5:]:k,miss,hit=item.split(':');row['counters'][k]=dict(missed=int(miss),covered=int(hit))
 (classes if isclass else methods).append(row)
assert len(classes)==len(methods)==1 and methods[0]['name']=='<init>' and methods[0]['descriptor']=='()V' and classes[0]['id']==post['classIds'][classes[0]['name']]
assert all(x['missed']==0 for row in classes+methods for x in row['counters'].values())
assert classes[0]['counters']['BRANCH']==dict(missed=0,covered=0)
v=dict(actualExit=0,startUTC=start,terminalAtUTC=terminal,sourceCore=post['productionCoreMain'],actualUnitSource=post['source'],run=c['id'],tests=1,failed=0,errors=0,skipped=0,notRun=0,post=ref(r/c['slots']['post']/'manifest.json'),command=command,fullPhysicalClasses=classes,allCodeMethods=methods,sourceInputs=unit['begin']['inputHashes'],physicalClassHashes=prepare['physicalClassHashes'],singleExecSha256=sha(slot/'jacoco.exec'),noCodeOrCoverageExclusions=True,rawMissedAllCounters=0,naturalNoBranchClasses=[classes[0]['name']],branchDenominatorZeroNotPositiveCoverage=True,standardPositiveBranchBoolean=False,oldExecCombined=False,actualBackendRootNativeOrHeldClassActions=0,newAcceptance=0,formalUpdated=False,effortCompletionRate=None)
(out/'manifest.json').write_text(json.dumps(v,indent=2)+'\n');print(json.dumps(dict(actualExit=0,tests=1,raw=classes[0]['counters'],branchDenominator=0,newAcceptance=0)))
