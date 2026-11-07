"""Whole original pure ApiStopBudget Test plus two new atomic-notification cases; no API runtime."""
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
import pg9666_pagination_static as c
r=Path.cwd();w=r.parent/'pgpt-runs/PG379';tc=r.parent/'toolchain';jdk=tc/'jdk-25.0.4/bin';source=sys.argv[1];sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();write=lambda p,x:Path(p).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
normalp=w/'pg22084-api-stop-state-six-main-compile-v1/manifest.safe.json';normal=json.loads(normalp.read_text());assert normal['actualExit']==0
main='src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/bootstrap/ApiStopBudget.java';test=main.replace('/main/','/test/').replace('.java','Test.java');driver=str(Path(__file__).relative_to(r));inputs={n:sha(r/n) for n in [main,test,driver]}
for n,h in inputs.items():assert h==hashlib.sha256(subprocess.check_output(['git','show',source+':'+n])).hexdigest()
assert normal['begin']['inputHashes'][main]==inputs[main]
for n,h in normal['begin']['inputHashes'].items():assert sha(r/n)==h
jar=normal['jars']['api'];assert sha(jar['path'])==jar['sha256'];console=tc/'junit-platform-console-standalone-1.13.4.jar';assert sha(console)=='3fdfc37e29744a9a67dd5365e81467e26fbde0b7aa204e6f8bbe79eeaa7ae892';agent=tc/'m2/repository/org/jacoco/org.jacoco.agent/0.8.15/org.jacoco.agent-0.8.15-runtime.jar';cli=tc/'org.jacoco.cli-0.8.15-nodeps.jar'
slot=w/'pg22090-api-stop-state-twenty-unit-v1';assert not slot.exists();slot.mkdir();c.SLOT=slot;(slot/'classes').mkdir();(slot/'tmp').mkdir();cp=jar['path']+':'+str(console);pkg='dev/codex/schubert/nk/api/bootstrap/';session='PG22090-API-STOP-ATOMIC20';cls='dev.codex.schubert.nk.api.bootstrap.ApiStopBudgetTest'
begin=dict(source=source,productionCoreMain=normal['source'],normalManifest=dict(path=str(normalp),sha256=sha(normalp)),inputHashes=inputs,dependencies={jar['path']:jar['sha256']},toolHashes={str(p):sha(p) for p in [console,agent,cli,jdk/'java',jdk/'javac']},testsExpected=20,newUniqueTests=2,existingCasesRequalified=18,selectedClass=cls,session=session,manualCoverageExclusions=[],oldExecUnion=False,independence='Whole original pure ApiStopBudgetTest/Fixture; only JDK primitives and own bounded threads; no ApiProcessLifetime or external runtime construction')
write(slot/'begin.json',begin);stages={};stages['compile']=c.step('compile',[str(jdk/'javac'),'--release','25','-proc:none','-Xlint:all','-Werror','-cp',cp,'-d',str(slot/'classes'),test],r);assert stages['compile']['actualExit']==0
cmd=[str(jdk/'java'),'-Djava.io.tmpdir='+str(slot/'tmp'),'-Dfile.encoding=UTF-8','-Duser.timezone=Asia/Tokyo','-Xlog:class+init=info:file='+str(slot/'class-init.stdout'),'-javaagent:'+str(agent)+'=destfile='+str(slot/'jacoco.exec')+',sessionid='+session+',append=false','-jar',str(console),'execute','--disable-banner','--class-path',str(slot/'classes')+':'+jar['path'],'--reports-dir',str(slot/'xml'),'--fail-if-no-tests','--details','summary','--config','junit.jupiter.execution.parallel.enabled=false','--config','junit.jupiter.extensions.autodetection.enabled=false','--select-class',cls]
stages['unit']=c.step('unit',cmd,r,timeout=180);assert stages['unit']['actualExit']==0
cases=[]
for p in sorted((slot/'xml').glob('TEST-*.xml')):
 for t in E.parse(p).getroot().findall('testcase'):
  assert not any(t.findall(k) for k in ['failure','error','skipped']);cases.append((t.get('classname'),t.get('name')))
expected={v+'()' for v in re.findall(r'@Test\s+void\s+(\w+)\(',Path(test).read_text())};assert len(cases)==len(set(cases))==len(expected)==20 and all(v[0]==cls for v in cases) and {v[1] for v in cases}==expected
initialised=set(re.findall(r"Initializing '([^']+)",(slot/'class-init.stdout').read_text()));products=sorted(n for n in initialised if n.startswith('dev/codex/schubert/nk/'));assert all(n==pkg+'ApiStopBudget' or n.startswith(pkg+'ApiStopBudgetTest') for n in products)
component=slot/'component';component.mkdir();entry=pkg+'ApiStopBudget.class'
with zipfile.ZipFile(jar['path']) as z:
 target=component/entry;target.parent.mkdir(parents=True);target.write_bytes(z.read(entry));physical={entry[:-6]:sha(target)}
for label,args in [('coverage',['report',str(slot/'jacoco.exec'),'--classfiles',str(component),'--sourcefiles',str(r/'src/schubert-nk-api/src/main/java'),'--xml',str(slot/'coverage.xml')]),('classinfo',['classinfo',str(component)]),('execinfo',['execinfo',str(slot/'jacoco.exec')])]:
 stages[label]=c.step(label,[str(jdk/'java'),'-jar',str(cli),*args],r);assert stages[label]['actualExit']==0
nodes=E.parse(slot/'coverage.xml').getroot().findall('.//package/class');assert len(nodes)==1 and nodes[0].get('name')==entry[:-6];counters={x.get('type'):dict(covered=int(x.get('covered')),missed=int(x.get('missed'))) for x in nodes[0].findall('counter')};assert all(x['missed']==0 for x in counters.values());four={k:counters[k] for k in ['LINE','METHOD','CLASS','BRANCH']};assert all(x['covered']>0 for x in four.values())
ids=re.findall(r'class 0x([0-9a-f]{16}) (\S+)',(slot/'classinfo.stdout').read_text());assert len(ids)==1 and ids[0][1]==entry[:-6];ex=(slot/'execinfo.stdout').read_text();assert ex.count('Session "')==1 and 'Session "'+session+'"' in ex and re.search(r'^'+ids[0][0]+r'\s+\d+ of\s+\d+\s+'+re.escape(entry[:-6])+r'$',ex,re.M)
v=dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),source=source,productionCoreMain=normal['source'],begin=begin,stages=stages,tests=20,newUniqueTests=2,requalifiedExistingTests=18,failures=0,errors=0,skipped=0,cases=cases,coverage={entry[:-6]:counters},fourCounters=four,physical=physical,classIds=ids,session=session,initialisedProduct=products,heldFourInitialisations=0,callerTests='ApiProcessLifetimeTest NOT_RUN_HOLD',whole451Accepted=False,formalUpdated=False,newAcceptance=0,effortRate=None)
write(slot/'manifest.json',v);out=r/'evidence/01_PT/018_NK-OPS-001/evidence/PG22090-api-stop-state-twenty-unit-v1';assert not out.exists();out.mkdir();files={}
for p in [*slot.iterdir(),*sorted((slot/'xml').glob('TEST-*.xml'))]:
 if p.is_file():
  n='original-manifest.json' if p.name=='manifest.json' else p.name;assert n not in files;shutil.copyfile(p,out/n);files[n]=sha(out/n)
v.update(originalManifest=dict(path=str(slot/'manifest.json'),sha256=sha(slot/'manifest.json')),files=files);write(out/'manifest.json',v);print(json.dumps(dict(actualExit=0,tests=20,newUnique=2,fourCounters=four,manifestSha256=sha(out/'manifest.json'))))
