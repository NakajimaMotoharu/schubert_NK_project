"""Independent raw XML/source/CRC/static binding; runs no Product, JUnit or analyzer."""
from pathlib import Path
import datetime
import hashlib
import json
import re
import subprocess
import sys
import xml.etree.ElementTree as E
import zipfile
r=Path.cwd();w=r.parent/'pgpt-runs/PG379';base=r/'evidence/01_PT/018_NK-OPS-001/evidence';sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();load=lambda p:json.loads(Path(p).read_text())
unit=base/'PG22090-api-stop-state-twenty-unit-v1';m=load(unit/'manifest.json');assert sha(unit/'manifest.json')=='95faef01085b82bf04edbb5ed8e34df304c98684e61c672b00b9245d6cc215ee' and m['actualExit']==0 and m['tests']==20 and m['newUniqueTests']==2 and m['requalifiedExistingTests']==18 and all(m[k]==0 for k in ['failures','errors','skipped'])
assert m['source']=='db91036a8df7b18c605beb6a03eb4f380b03182f' and m['productionCoreMain']=='7aed8eace7c844c2f79f2e39db766faf914890d5'
for n,h in m['files'].items():assert sha(unit/n)==h
for n,h in m['begin']['inputHashes'].items():assert sha(r/n)==h==hashlib.sha256(subprocess.check_output(['git','show',m['source']+':'+n])).hexdigest()
for n,h in m['begin']['toolHashes'].items():assert sha(n)==h
raw=Path(m['originalManifest']['path']);assert sha(raw)==m['originalManifest']['sha256'];original=load(raw);assert original['cases']==m['cases'] and original['stages']==m['stages']
for label,stage in m['stages'].items():assert stage['actualExit']==0 and not stage['timedOut'] and sha(raw.parent/(label+'.stdout'))==stage['stdoutSha256'] and sha(raw.parent/(label+'.stderr'))==stage['stderrSha256']
actual=[];environment=[]
for p in sorted((raw.parent/'xml').glob('TEST-*.xml')):
 tree=E.parse(p).getroot();assert all(int(tree.get(k,'0'))==0 for k in ['failures','errors','skipped'])
 for t in tree.findall('testcase'):
  assert not any(t.findall(k) for k in ['failure','error','skipped']);actual.append((t.get('classname'),t.get('name')))
 props={v.get('name'):v.get('value') for v in tree.findall('properties/property')};environment.append({k:props.get(k) for k in ['java.version','java.vendor','os.name','os.version','os.arch']});assert props['java.io.tmpdir']==str(raw.parent/'tmp')
test='src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/bootstrap/ApiStopBudgetTest.java';methods=re.findall(r'@Test\s+void\s+(\w+)\(',Path(test).read_text());assert len(actual)==len(set(actual))==len(methods)==20 and {v+'()' for v in methods}=={v for _,v in actual} and all(c=='dev.codex.schubert.nk.api.bootstrap.ApiStopBudgetTest' for c,_ in actual)
normalp=w/'pg22084-api-stop-state-six-main-compile-v1/manifest.safe.json';normal=load(normalp);assert sha(normalp)=='b2f07209804d71ee2ffbc4d9aca5311d4e6cf15721c74bcde411f86538cf4f27' and normal['actualExit']==0 and normal['source']==m['productionCoreMain'] and len(normal['begin']['inputHashes'])==1036 and len(normal['normalPhysicalClassHashes'])==1845
for n,h in normal['begin']['inputHashes'].items():assert sha(r/n)==h
for v in normal['jars'].values():assert sha(v['path'])==v['sha256']
assert len(normal['classIdentity']['changedPhysical'])==3
pkg='dev/codex/schubert/nk/api/bootstrap/';target=pkg+'ApiStopBudget'
with zipfile.ZipFile(normal['jars']['api']['path']) as z:
 assert set(m['physical'])=={target} and hashlib.sha256(z.read(target+'.class')).hexdigest()==m['physical'][target]
node=E.parse(unit/'coverage.xml').getroot().find('.//class');assert node is not None and node.get('name')==target and len(E.parse(unit/'coverage.xml').getroot().findall('.//class'))==1
counters={v.get('type'):dict(covered=int(v.get('covered')),missed=int(v.get('missed'))) for v in node.findall('counter')};assert m['coverage']=={target:counters} and all(v['missed']==0 for v in counters.values());assert m['fourCounters']=={k:dict(covered=v,missed=0) for k,v in [('LINE',26),('METHOD',6),('CLASS',1),('BRANCH',12)]}
assert {v.get('name') for v in node.findall('method')}=={'<init>','<clinit>','begin','stopping','remainingNanos','time'}
ex=(unit/'execinfo.stdout').read_text();assert ex.count('Session "')==1 and 'Session "PG22090-API-STOP-ATOMIC20"' in ex and re.search(r'^aac04d643a58f83d\s+27 of\s+29\s+'+re.escape(target)+r'$',ex,re.M)
assert 'ApiProcessLifetime' not in ex
initialised=set(re.findall(r"Initializing '([^']+)",(unit/'class-init.stdout').read_text()));products=sorted(n for n in initialised if n.startswith('dev/codex/schubert/nk/'));assert products==m['initialisedProduct'] and all(n==target or n.startswith(pkg+'ApiStopBudgetTest') for n in products)
assert not any(n.startswith(('org/postgresql/','org/apache/activemq/','com/microsoft/playwright/','sun/nio/ch/SocketChannelImpl')) for n in initialised)
staticp=base/'PG22106-api-stop-static-independent-input-v1/manifest.json';s=load(staticp);assert re.fullmatch('[0-9a-f]{64}',sys.argv[1]) and sha(staticp)==sys.argv[1] and s['actualExit']==0 and s['productionCoreMain']==normal['source']
for n,h in s['files'].items():assert sha(staticp.parent/n)==h
for n,h in s['styleInputHashes'].items():assert sha(r/n)==h
sb=load(staticp.parent/'six-static.json');assert sb['actualExit']==0 and sb['normalCompileManifestSha256']==sha(normalp) and len(sb['reports'])==6 and all(v['bugs']==v['errors']==v['missing']==0 for v in sb['reports'].values())
style=load(staticp.parent/'style-raw.json');judgments=load(staticp.parent/'style-applicability.json');assert len(style['findings'])==len(judgments['judgments'])==25 and judgments['rawPmdExit']==style['stages']['pmd']['actualExit']==4 and judgments['applicableViolations']==judgments['processingErrors']==judgments['checkstyle']==0
for i,(finding,judge) in enumerate(zip(style['findings'],judgments['judgments'])):
 assert judge['ordinal']==i and judge['raw']==finding and judge['actualViolation'] is False and judge['reason'] and judge['sourceSha256']==sha(r/finding['path'])
 start,end=int(finding['attributes']['beginline']),int(finding['attributes']['endline']);assert judge['sourceSpan']==(r/finding['path']).read_text().splitlines()[start-1:end]
 assert finding['attributes']['rule']!='AvoidLiteralsInIfCondition'
probe=load(staticp.parent/'probe-interpretation.json');assert probe['unhit']==[23,25] and probe['rawHit']==27 and probe['rawTotal']==29 and probe['sourceConditionBranches']==dict(covered=2,missed=0) and not probe['newCoverageExecution'] and probe['wholePhysicalSourceIncluded']
pmp=r/s['probeManifest']['path'];pm=load(pmp);assert sha(pmp)==s['probeManifest']['sha256'] and pm['execSha256']==sha(unit/'jacoco.exec') and pm['productTestsExecuted']==pm['productInitialisations']==0
bytep=r/s['bytecodeManifest']['path'];byte=load(bytep);assert sha(bytep)==s['bytecodeManifest']['sha256'] and byte['actualExit']==0 and byte['productInitialisations']==0 and byte['sameClaimPublishedThroughBudget'] and byte['remainingUnderOriginalLock']
for n,h in byte['sourceInputHashes'].items():assert sha(r/n)==h
assert byte['stages']['format']['actualExit']==0 and not byte['stages']['format']['timedOut']
assert m['begin']['manualCoverageExclusions']==[] and not m['begin']['oldExecUnion']
head=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip();driver=str(Path(__file__).relative_to(r));assert sha(__file__)==hashlib.sha256(subprocess.check_output(['git','show',head+':'+driver])).hexdigest()
out=base/'PG22110-api-stop-twenty-independent-post-v1';assert not out.exists();out.mkdir();v=dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),checkerSource=head,checkerSha256=sha(__file__),source=m['source'],productionCoreMain=m['productionCoreMain'],unitManifest=dict(path=str((unit/'manifest.json').relative_to(r)),sha256=sha(unit/'manifest.json')),staticManifest=dict(path=str(staticp.relative_to(r)),sha256=sha(staticp)),tests=20,newUniqueTests=2,requalifiedExistingTests=18,newWholeSourceProofs=0,fourCounters=m['fourCounters'],rawProbeHit=27,rawProbeTotal=29,compilerFinallyCopiesDocumented=True,physicalClasses=1,normalClasses=1845,normalChangedClasses=3,environment=environment,productTestsReexecuted=0,heldFourInitialisations=0,callerDynamicStatus='NOT_RUN_HOLD',bugStatus='BUG2416/YKT2161 OPEN_PENDING_CALLER_DYNAMIC',testQualityBug='BUG2417/YKT2162 finite scope tested',whole451Accepted=False,formalUpdated=False,newAcceptance=0,effortRate=None)
(out/'manifest.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,tests=20,newUniqueTests=2,fourCounters=m['fourCounters'],manifestSha256=sha(out/'manifest.json'))))
