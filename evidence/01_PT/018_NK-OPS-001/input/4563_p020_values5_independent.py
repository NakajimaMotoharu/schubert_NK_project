"""Qualify the genuine new5 only; never combine its execution data with prior124."""
from pathlib import Path
import datetime
import gzip
import hashlib
import json
import re
import shutil
import subprocess
import xml.etree.ElementTree as ET

r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';w=r.parent/'pgpt-runs/PG379';tc=r.parent/'toolchain';slot=w/'pg37022-common-values5-unit-v1';classes=w/'pg37012-p020-remote124-recovered/mainclasses'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();load=lambda p:json.loads(p.read_text());ref=lambda p:dict(path=str(p.relative_to(r)),sha256=sha(p))
u=load(slot/'terminal.json');begin=load(slot/'begin.json');prior=load(b/'evidence/PG37016-p020-whole124-independent-v1/manifest.json');assert u['actualExit']==0 and u['testUnchanged'] and u['mainPhysicalUnchanged']
assert u['source']=='6cc5994cb354226eb4803180f290147332d0ffdc' and sha(r/begin['testPath'])==begin['testSha256'] and sha(r/begin['specPath'])==begin['specSha256']
assert all(sha(classes/n)==h for n,h in begin['physicalClassHashes'].items()) and begin['physicalClassHashes']==prior['classSha256']
expected={'comparisonResultKeepsValueIdentityAfterCallerListMutation()','baselineNumbersUseAllThreeTypedComponentsInValueIdentity()','treeStatsPreserveOrderedSymlinkValuesInDiagnosticAndIdentity()','validationResultValueIncludesBothFailuresAndMetrics()','targetEnumerationOwnsItsArrayAndHashCollisionIsStillUnknown()'}
cases=[]
for name,h in u['xmlHashes'].items():
 assert sha(slot/'xml'/name)==h;tree=ET.parse(slot/'xml'/name).getroot();assert all(int(tree.get(k,0))==0 for k in ['failures','errors','skipped'])
 for c in tree.findall('testcase'):
  assert c.get('classname')=='dev.codex.schubert.characterization.CommonValueContractTest' and not any(c.findall('.//'+tag) for tag in ['failure','error','skipped']) and all(x.tag in ['system-out','system-err'] for x in c);cases.append(c.get('name'))
assert len(cases)==len(set(cases))==5 and set(cases)==expected and sha(slot/'jacoco.exec')==u['execSha256']
out=b/'evidence/PG37024-values5-independent-v1';assert not out.exists();out.mkdir()
qualified=load(b/'evidence/PG31432-generated-code-supplemental-tool-v1/compile.json');assert load(b/'evidence/PG31434-generated-code-tool-selftest-v1/manifest.json')['toolTests']==12
for p in qualified['dependencies']:assert sha(Path(p['path']))==p['sha256']
cmd=[str(tc/'jdk-25.0.4/bin/java'),'-cp',':'.join([str(w/'pg31432-generated-code-supplemental-tool-v1/toolclasses'),*[p['path'] for p in qualified['dependencies']]]),'org.jacoco.core.internal.analysis.UnfilteredCodeMeasurement',str(slot/'jacoco.exec'),*[str(classes/n) for n in sorted(begin['physicalClassHashes'])]]
with (out/'unfiltered.stdout').open('xb') as stdout,(out/'unfiltered.stderr').open('xb') as stderr:child=subprocess.run(cmd,stdout=stdout,stderr=stderr,timeout=120)
assert child.returncode==0
measurements={};methods=[]
for line in (out/'unfiltered.stdout').read_text().splitlines():
 f=line.split('\t')
 if f[0]=='CLASS':row=dict(name=f[1],id=f[2],counters={});measurements[f[1]]=row;offset=6
 else:row=dict(className=f[1],name=f[2],descriptor=f[3],counters={});methods.append(row);offset=5
 for item in f[offset:]:k,miss,hit=item.split(':');row['counters'][k]=dict(missed=int(miss),covered=int(hit))
assert set(measurements)==set(prior['classIds']) and all(row['id']==prior['classIds'][n] for n,row in measurements.items())
records=['ArtifactComparator$ComparisonResult','GateCli$BaselineNumbers','GateCli$TreeStats','GateContractValidator$ValidationResult'];catalog=[]
for m in methods:
 short=m['className'].rsplit('/',1)[-1]
 if (short in records and m['name'] in ['toString','hashCode','equals']) or (short=='TargetAdapter$Target' and m['name'] in ['values','valueOf']):catalog.append(m)
assert len(catalog)==14 and all(all(v['missed']==0 for v in m['counters'].values()) for m in catalog)
parse=next(m for m in methods if m['className'].endswith('/TargetAdapter$Target') and m['name']=='parse')
initializing=set(re.findall(r"Initializing '([^']+)'",(slot/'class-init.log').read_text()));assert not any(n.startswith(('dev/codex/schubert/nk/','com/microsoft/playwright/')) for n in initializing)
for name in ['begin.json','terminal.json','jacoco.exec','checkstyle.xml']:
 shutil.copyfile(slot/name,out/name)
shutil.copytree(slot/'xml',out/'xml')
with (out/'class-init.log.gz').open('xb') as f:f.write(gzip.compress((slot/'class-init.log').read_bytes(),mtime=0))
v=dict(actualExit=0,terminalAtUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),sourceCore=u['sourceCore'],actualUnitSource=u['source'],run=u['run'],success=5,failed=0,errors=0,skipped=0,notRun=0,wholeSuite='CommonValueContractTest',caseTestIds=[dict(id='PT-CHR-VALUE'+f'{i:03d}',name=name,result='PASS') for i,name in enumerate(['comparisonResultKeepsValueIdentityAfterCallerListMutation()','baselineNumbersUseAllThreeTypedComponentsInValueIdentity()','treeStatsPreserveOrderedSymlinkValuesInDiagnosticAndIdentity()','validationResultValueIncludesBothFailuresAndMetrics()','targetEnumerationOwnsItsArrayAndHashCollisionIsStillUnknown()'],1)],allMainSourceAndPhysicalSameAs124=True,physicalSha256=begin['physicalClassHashes'],classIds=prior['classIds'],rawGeneratedMethodsQualified14=catalog,targetParseRaw=parse,allClassMeasurements=measurements,allMethodMeasurements=methods,allRawMissingRetained=True,oldExecUnion=False,prior124Reexecuted=False,rawEntireMain100Claimed=False,privateReflection=False,realNativeBrowserDbRootActions=0,whole451Accepted=False,newAcceptance=0,formalUpdated=False,files={str(p.relative_to(out)):sha(p) for p in sorted(out.rglob('*')) if p.is_file()},priorProofReference=ref(b/'evidence/PG37016-p020-whole124-independent-v1/manifest.json'),staticProofReference=ref(b/'evidence/PG37020-p020-current-quality-join-v1/manifest.json'),unfilteredCommand=cmd,unfilteredExit=child.returncode)
(out/'manifest.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(dict(actualExit=0,success=5,rawGeneratedMethodsQualified=14,targetParseRaw=parse['counters'],sameMain10=True,old124Reexecuted=False,execUnion=False,newAcceptance=0)))
