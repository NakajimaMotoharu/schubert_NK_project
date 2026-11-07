"""Whole existing pure Web stop Test; original-red or changed-source regression. No server/Root."""
from pathlib import Path
import datetime
import hashlib
import json
import re
import shutil
import subprocess
import sys
import xml.etree.ElementTree as E
import zipfile
import pg9666_pagination_static as capture
r=Path.cwd();w=r.parent/'pgpt-runs/PG379';tc=r.parent/'toolchain';jdk=tc/'jdk-25.0.4/bin'
mode,normal_name,slot_name,source=sys.argv[1:];assert mode in {'red','full'}
assert re.fullmatch(r'[0-9a-f]{40}',source) and re.fullmatch(r'pg\d+-[a-z0-9-]+',normal_name) and re.fullmatch(r'PG\d+-[a-z0-9-]+',slot_name)
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();write=lambda p,x:Path(p).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
normal_path=w/normal_name/'manifest.safe.json';normal=json.loads(normal_path.read_text());assert normal['actualExit']==0
main='src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/bootstrap/WebRuntimeStop.java'
test='src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/bootstrap/WebRuntimeStopTest.java';driver=str(Path(__file__).resolve().relative_to(r))
inputs={n:sha(r/n) for n in [main,test,driver]}
for n,h in inputs.items():assert hashlib.sha256(subprocess.check_output(['git','show',source+':'+n])).hexdigest()==h
assert inputs[main]==normal['begin']['inputHashes'][main]
for dep in normal['jars'].values():assert sha(dep['path'])==dep['sha256']
console=tc/'junit-platform-console-standalone-1.13.4.jar';assert sha(console)=='3fdfc37e29744a9a67dd5365e81467e26fbde0b7aa204e6f8bbe79eeaa7ae892'
tomcat=tc/'m2/repository/org/apache/tomcat/embed/tomcat-embed-core/11.0.25/tomcat-embed-core-11.0.25.jar';jspec=tc/'m2/repository/org/jspecify/jspecify/1.0.1/jspecify-1.0.1.jar'
deps={normal['jars']['web']['path']:normal['jars']['web']['sha256'],str(tomcat):sha(tomcat),str(jspec):sha(jspec)}
cp=':'.join([*deps,str(console)]);slot=w/slot_name.lower();assert not slot.exists();slot.mkdir();capture.SLOT=slot;(slot/'classes').mkdir();(slot/'tmp').mkdir()
cls='dev.codex.schubert.nk.web.bootstrap.WebRuntimeStopTest';method='stop006SignedClockWrapKeepsRelativeBudgetAndDetectsExpiry';pkg='dev/codex/schubert/nk/web/bootstrap/'
begin=dict(atJST=datetime.datetime.now().astimezone().isoformat(),mode=mode,source=source,productionCoreMain=normal['source'],normalManifest=dict(path=str(normal_path),sha256=sha(normal_path)),inputHashes=inputs,dependencies=deps,consoleSha256=sha(console),testSelection=cls+'#'+method if mode=='red' else cls,independence='Whole original Test, only lambdas/AtomicLong/JDK exceptions; SessionStoreException graph walk, no external operations; Tomcat LifecycleException value only',testsExpected=1 if mode=='red' else 6,scope='WebRuntimeStop whole source and all original five tests plus one new independent vector',noOldExecUnion=True,manualCoverageExclusions=[])
write(slot/'begin.json',begin);stages={}
stages['compile']=capture.step('compile',[str(jdk/'javac'),'--release','25','-proc:none','-Xlint:all','-Werror','-cp',cp,'-d',str(slot/'classes'),test],r);assert stages['compile']['actualExit']==0
stages['exception-metadata']=capture.step('exception-metadata',[str(jdk/'javap'),'-cp',str(tomcat),'-c','-p','org.apache.catalina.LifecycleException'],r);assert stages['exception-metadata']['actualExit']==0
assert 'static {}' not in (slot/'exception-metadata.stdout').read_text()
cmd=[str(jdk/'java'),'-Djava.io.tmpdir='+str(slot/'tmp'),'-Duser.timezone=Asia/Tokyo','-Xlog:class+init=info:file='+str(slot/'class-init.log')]
agent=tc/'m2/repository/org/jacoco/org.jacoco.agent/0.8.15/org.jacoco.agent-0.8.15-runtime.jar';cli=tc/'org.jacoco.cli-0.8.15-nodeps.jar';session=slot_name+'-WEBSTOP'
if mode=='full':cmd+=['-javaagent:'+str(agent)+'=destfile='+str(slot/'jacoco.exec')+',sessionid='+session+',append=false']
cmd+=['-jar',str(console),'execute','--disable-banner','--class-path',str(slot/'classes')+':'+':'.join(deps),'--reports-dir',str(slot/'xml'),'--fail-if-no-tests','--details','summary','--select-method' if mode=='red' else '--select-class',begin['testSelection']]
stages['unit']=capture.step('unit',cmd,r,timeout=120)
cases=[]
for p in sorted((slot/'xml').glob('TEST-*.xml')):
 for t in E.parse(p).getroot().findall('testcase'):cases.append(dict(classname=t.get('classname'),name=t.get('name'),failure=bool(t.findall('failure')),error=bool(t.findall('error')),skipped=bool(t.findall('skipped'))))
assert len(cases)==begin['testsExpected'] and all(t['classname']==cls for t in cases)
initialised=set(re.findall(r"Initializing '([^']+)",(slot/'class-init.log').read_text()))
held=['dev/codex/schubert/nk/api/error/TemporaryInfrastructureException','dev/codex/schubert/nk/web/bootstrap/WebStartupException','dev/codex/schubert/nk/api/idempotency/FingerprintKeyRing','dev/codex/schubert/nk/api/idempotency/ResponseSnapshotCodec']
assert not set(held)&initialised
allowed={pkg+'WebRuntimeStop',pkg+'WebRuntimeStopTest','dev/codex/schubert/nk/web/session/SessionStoreException','dev/codex/schubert/nk/web/session/InvalidSessionRowException'}
product_initialised=sorted(n for n in initialised if n.startswith('dev/codex/schubert/nk/'))
assert all(n in allowed or n.startswith(pkg+'WebRuntimeStopTest$$Lambda') for n in product_initialised)
assert not any(n.startswith(('org/postgresql/','org/apache/activemq/','com/microsoft/playwright/','sun/nio/ch/SocketChannelImpl')) for n in initialised)
coverage={};physical={};four={}
if mode=='red':
 assert stages['unit']['actualExit']==1 and sum(t['error'] for t in cases)==1 and not any(t['failure'] or t['skipped'] for t in cases)
 assert 'Web stop unconfirmed' in ''.join(p.read_text() for p in (slot/'xml').glob('TEST-*.xml'))
 status='EXPECTED_EXISTING_BUG_REPRODUCED_NOT_PASS'
else:
 assert stages['unit']['actualExit']==0 and not any(t['failure'] or t['error'] or t['skipped'] for t in cases)
 expected={v+'()' for v in re.findall(r'@Test\s+void\s+(\w+)\(',Path(test).read_text())};assert {t['name'] for t in cases}==expected and len(expected)==6
 component=slot/'component';component.mkdir()
 with zipfile.ZipFile(normal['jars']['web']['path']) as z:
  names=sorted(n for n in z.namelist() if n in [pkg+'WebRuntimeStop.class',pkg+'WebRuntimeStop$Step.class']);assert len(names)==2
  for n in names:
   p=component/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(z.read(n));physical[n[:-6]]=sha(p)
 for label,args in [('coverage',['report',str(slot/'jacoco.exec'),'--classfiles',str(component),'--sourcefiles',str(r/'src/schubert-nk-web/src/main/java'),'--xml',str(slot/'coverage.xml')]),('classinfo',['classinfo',str(component)]),('execinfo',['execinfo',str(slot/'jacoco.exec')])]:
  stages[label]=capture.step(label,[str(jdk/'java'),'-jar',str(cli),*args],r);assert stages[label]['actualExit']==0
 coverage={n.get('name'):{c.get('type'):dict(covered=int(c.get('covered')),missed=int(c.get('missed'))) for c in n.findall('counter')} for n in E.parse(slot/'coverage.xml').getroot().findall('.//package/class')}
 assert set(coverage)==set(physical) and coverage[pkg+'WebRuntimeStop$Step']=={}
 assert all(c['missed']==0 for counters in coverage.values() for c in counters.values())
 four={k:coverage[pkg+'WebRuntimeStop'][k] for k in ['LINE','METHOD','CLASS','BRANCH']};assert all(c['covered']>0 and c['missed']==0 for c in four.values())
 status='CHANGED_SOURCE_SIX_CASES_FOUR_COUNTERS100'
value=dict(actualExit=stages['unit']['actualExit'],status=status,atJST=datetime.datetime.now().astimezone().isoformat(),source=source,productionCoreMain=normal['source'],begin=begin,stages=stages,tests=len(cases),cases=cases,failures=sum(t['failure'] for t in cases),errors=sum(t['error'] for t in cases),skipped=sum(t['skipped'] for t in cases),physical=physical,coverage=coverage,fourCounters=four,productInitialised=product_initialised,heldFourInitialisations=0,newUniqueMethods=1 if mode=='full' else 0,requalifiedExistingMethods=5 if mode=='full' else 0,whole451Accepted=False,formalUpdated=False,effortRate=None)
write(slot/'manifest.json',value)
pub=r/'evidence/01_PT/018_NK-OPS-001/evidence'/slot_name;assert not pub.exists();pub.mkdir();files={}
for p in [*slot.iterdir(),*sorted((slot/'xml').glob('TEST-*.xml'))]:
 if p.is_file():
  name='original-manifest.json' if p.name=='manifest.json' else 'original-class-init.stdout' if p.name=='class-init.log' else p.name
  assert name not in files;shutil.copyfile(p,pub/name);files[name]=sha(pub/name)
value['files']=files;value['originalManifest']=dict(path=str(slot/'manifest.json'),sha256=sha(slot/'manifest.json'));write(pub/'manifest.json',value)
print(json.dumps(dict(actualExit=value['actualExit'],tests=len(cases),status=status,fourCounters=four,manifestSha256=sha(pub/'manifest.json'))))
