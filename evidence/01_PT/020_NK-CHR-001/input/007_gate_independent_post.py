"""Read-only post of original own synthetic Gate run. No Java/job/runtime/baseline access."""
from pathlib import Path
import json, hashlib, subprocess, zipfile, re, datetime
import xml.etree.ElementTree as E

r=Path.cwd();runs=r.parent/'pgpt-runs/PG379'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
load=lambda p:json.loads(Path(p).read_text())
source='7b9df0b9812b0e3f7445b619261a4dbdce89aa14'
pub=Path('evidence/01_PT/020_NK-CHR-001/evidence/PG21140-gate-synthetic-sixty-v1')
m=load(pub/'manifest.json')
assert sha(pub/'manifest.json')=='1d672d4a736b9b14b684a73822ef1602ee4065b18aa171c37001bfaef7f360cd'
assert m['actualExit']==0 and m['source']==source and m['tests']==60 and m['newMethods']==6 and m['requalifiedExistingInvocations']==54
assert all(m[k]==0 for k in ['failures','errors','skipped']) and m['manualCoverageExclusions']==[] and not m['oldExecUnion'] and not m['realBaselineAccess'] and not m['realChrExecution']
for name,h in m['files'].items():assert '/' not in name and sha(pub/name)==h
for name,h in m['inputHashes'].items():assert sha(name)==h==hashlib.sha256(subprocess.check_output(['git','show',source+':'+name])).hexdigest()
for key in ['producerGitArtifact','verifierGitArtifact']:
 g=m[key];assert hashlib.sha256(subprocess.check_output(['git','show',g['source']+':'+g['path']])).hexdigest()==g['sha256']
assert m['producerGitArtifact']['source']==source and m['driverSha256']==m['producerGitArtifact']['sha256']
slot=Path(m['originalManifest']['path']).parent;raw=load(slot/'manifest.json')
assert sha(slot/'manifest.json')==m['originalManifest']['sha256'] and raw['actualExit']==0 and raw['begin']['inputHashes']==m['inputHashes'] and raw['begin']['source']==source
assert raw['begin']['newMethods']==6 and raw['begin']['existingMethodsSourceRequalification']==54
for key,s in raw['stages'].items():assert s['actualExit']==0 and not s['timedOut'] and sha(slot/(key+'.stdout'))==s['stdoutSha256'] and sha(slot/(key+'.stderr'))==s['stderrSha256']
pre=runs/'pg21136-gate-synthetic-sixty-fixed-compile-v1';actual=[];environment=[]
for name,h in m['originalXmlPins'].items():
 assert sha(name)==h;tree=E.parse(name).getroot();assert all(int(tree.get(k,'0'))==0 for k in ['failures','errors','skipped'])
 for case in tree.findall('testcase'):
  assert not any(case.findall(k) for k in ['failure','error','skipped']);actual.append((case.get('classname'),case.get('name')))
 props={x.get('name'):x.get('value') for x in tree.findall('properties/property')}
 assert props['java.io.tmpdir']==str(slot/'tmp') and props['chr.unitProjectRoot']==str(pre/'synthetic-project')
 assert str(pre/'public-definitions') in props['junit.platform.console.classpath'] if 'junit.platform.console.classpath' in props else True
 environment.append({k:props.get(k) for k in ['os.name','os.arch','os.version','java.version','java.vendor']})
assert sorted(actual)==sorted(map(tuple,m['selectedMethods'])) and len(actual)==len(set(actual))==60
spec=Path('evidence/01_PT/020_NK-CHR-001/020_Gate判定工具自己所有全階層単体仕様.md').read_text()
pairs=re.findall(r'\|(PT-CHR-GS\d{3})\|(\w+)\.(\w+)\|',spec);assert len(pairs)==54
base_methods={(c.rsplit('.',1)[1],n.split('(')[0]) for c,n in actual}
assert {(c,n) for _,c,n in pairs}==base_methods and sum(c.endswith('.GateSyntheticRunPortTest') for c,n in actual)==6
param=[n for c,n in actual if 'rejectsEveryNonPassExecutionStatus' in n];assert set(param)=={'rejectsEveryNonPassExecutionStatus(String)['+str(i)+']' for i in range(1,8)}
normal=load(runs/'pg21088-characterization-tool-original-main-compile-v1/manifest.safe.json');assert normal['source']==m['normalSource']=='087e81a679a576721d8b6d6124fdd881ae9192e5' and normal['actualExit']==0 and len(normal['physicalHashes'])==10
for name,h in normal['begin']['inputHashes'].items():assert sha(name)==h
jar=normal['jar'];assert sha(jar['path'])==jar['sha256']
with zipfile.ZipFile(jar['path']) as z:
 for n,h in m['physicalHashes'].items():assert hashlib.sha256(z.read(n+'.class')).hexdigest()==h
coverage={c.get('name'):{x.get('type'):dict(covered=int(x.get('covered')),missed=int(x.get('missed'))) for x in c.findall('counter')} for c in E.parse(slot/'coverage.xml').getroot().findall('.//package/class')}
assert coverage==m['coverage'] and len(coverage)==2 and all(v['missed']==0 for cs in coverage.values() for v in cs.values())
four={k:sum(cs.get(k,{}).get('covered',0) for cs in coverage.values()) for k in ['LINE','METHOD','CLASS','BRANCH']}
assert four==m['fourCounters']==dict(LINE=488,METHOD=51,CLASS=2,BRANCH=253)
ex=(slot/'execinfo.stdout').read_text();assert ex.count('Session "')==1 and 'Session "'+m['session']+'"' in ex
for name,crc in m['classIds'].items():assert re.search(r'^'+crc+r'\s+\d+ of\s+\d+\s+'+re.escape(name)+r'$',ex,re.M)
static=Path('evidence/01_PT/020_NK-CHR-001/evidence/PG21138-gate-fixed-static-v1/manifest.json');s=load(static)
assert s['inputHashes']==m['inputHashes'] and s['pmdRaw']==16 and s['applicableViolations']==s['checkstyle']==s['processingErrors']==s['spotbugs']==0
assert all(x['applicable'] is False and x['reason'] for x in s['classification'])
for n,h in s['files'].items():assert sha(static.parent/n)==h
oracle=load(pub/'fixture-oracle.json');assert sha(pre/'fixture-oracle.json')==m['fixtureOracle']['sha256']==sha(pub/'fixture-oracle.json')
assert not oracle['actualBaselineAccess'] and not oracle['actualApproval'] and not oracle['actualScreenshot']
own=pre/'synthetic-project';synthetic=oracle['syntheticInputHashes']
for n,h in synthetic.items():assert sha(own/n)==h
for n,h in oracle['publicDesignInputHashes'].items():assert sha(pre/'public-definitions'/Path(n).relative_to('program/characterization/tests/resources'))==h==m['inputHashes'][n]
# Separate independent aggregate over the previously generated own files, never actual baseline.
baseline_files=[n for n in synthetic if n.startswith('program/characterization/baseline/current/')]
assert len(baseline_files)==27
lines=''.join(sha(own/n)+'  '+n+'\n' for n in sorted(baseline_files,key=lambda n:n.encode('utf-8')))
assert lines==oracle['baselineAggregateLines'] and hashlib.sha256(lines.encode()).hexdigest()==oracle['baselineAggregateSha256']
cmd=raw['stages']['unit']['command'];assert '--scan-classpath' not in cmd and str(pre/'public-definitions') in cmd[cmd.index('--class-path')+1].split(':')
assert str(own/'program/characterization/tests/resources') not in cmd[cmd.index('--class-path')+1].split(':')
console=cmd[cmd.index('-jar')+1];sdk=load('evidence/01_PT/015_NK-WEB-001/input/001_login_failure_sdk_static_review.json')
assert sha(console)==sdk['consoleSha256']==raw['begin']['consoleSha256'] and sha(r.parent/'toolchain/jdk-25.0.4/lib/modules')==sdk['jdkModulesSha256']
providers={}
for p in [Path(v) for v in raw['begin']['dependencies']]+[Path(console)]:
 assert sha(p)==(raw['begin']['consoleSha256'] if p==Path(console) else raw['begin']['dependencies'][str(p)])
 with zipfile.ZipFile(p) as z:providers[str(p)]=[n for n in z.namelist() if n=='META-INF/services/java.sql.Driver' or n.startswith(('org/postgresql/','com/microsoft/playwright/'))]
assert all(not v for v in providers.values())
# Old failed whole source/run is preserved and excluded, never summed with this successful source.
red=load('evidence/01_PT/020_NK-CHR-001/evidence/PG21124-gate-original-harness-red-v1/manifest.json');assert red['actualExit']==1 and (red['tests'],red['failures'],red['errors'],red['oldSuccessCredited'])==(60,5,1,0)
out=Path('evidence/01_PT/020_NK-CHR-001/evidence/PG21146-gate-independent-post-v1');assert not out.exists();out.mkdir()
v=dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),source=source,normalSource=m['normalSource'],productionCoreMain=m['productionCoreMain'],originalPost=dict(path=str(pub/'manifest.json'),sha256=sha(pub/'manifest.json')),tests=60,newMethods=6,requalifiedExistingInvocations=54,sourceTestIds=pairs,fourCounters=four,missed=0,physical=2,environment=environment,staticPost=dict(path=str(static),sha256=sha(static)),fixtureOracleSha256=sha(pub/'fixture-oracle.json'),oldFailedRunCredited=0,driverProviderEntries=providers,productTestsReexecuted=0,realBaselineReadOrWritten=False,actualApprovalGranted=False,realChrExecution=False,newAcceptance=0,formalUpdated=False,effortRate=None,checkerSha256=sha(__file__),checkerSource=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip())
(out/'manifest.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(dict(actualExit=0,tests=60,newMethods=6,requalifiedExisting=54,manifestSha256=sha(out/'manifest.json'))))
