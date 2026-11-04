"""Owned, finite BUG2263 original-red/current-green driver; no backend or old launcher invocation."""
import sys,json,hashlib,datetime,os,subprocess,shutil,xml.etree.ElementTree as ET
from pathlib import Path
import pg9666_pagination_static as runner
ROOT=Path('/home/mini/codex/project1/work/pgpt-foundation');TC=ROOT.parent/'toolchain';RUNS=ROOT.parent/'pgpt-runs/PG379'
MODE=sys.argv[1];assert MODE in ('red','green');slot=RUNS/('pg18634-jms-uuid-original-red-v1' if MODE=='red' else 'pg18638-jms-uuid-canonical-green-v1');assert not slot.exists();slot.mkdir();runner.SLOT=slot
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(n,v):(slot/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
p=RUNS/'pg18630-web-reply-dlq-unit-v1/begin.safe.json';base=json.loads(p.read_text());deps={**base['dependencies'],**base['sdkDependencies']};api=RUNS/'pg14216-typed-marker-guard-six-compile-v1/snapshot/src/schubert-nk-api/target/schubert-nk-api-0.1.0-SNAPSHOT.jar';deps[str(api)]='5c909f702eeaa78d43da0cb9be8435c6697ed8f1cf5e1bca7e01d6722e3583a1';ann=TC/'m2/repository/org/jspecify/jspecify/1.0.0/jspecify-1.0.0.jar';deps[str(ann)]=sha(ann)
for path,digest in deps.items():assert sha(path)==digest,(path,'dependency changed')
classes=['dev.codex.schubert.nk.api.messaging.guard.JmsMessageGuardTest','dev.codex.schubert.nk.web.messaging.JmsReplyDecoderTest'];mainclasses=[c[:-4] if c.endswith('Test') else c for c in classes]
tests=[ROOT/'src'/('schubert-nk-api' if '.api.' in c else 'schubert-nk-web')/'src/test/java'/Path(c.replace('.','/')+'.java') for c in classes];mains=[ROOT/'src'/('schubert-nk-api' if '.api.' in c else 'schubert-nk-web')/'src/main/java'/Path(c.replace('.','/')+'.java') for c in mainclasses]
head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip();before={'mode':MODE,'head':head,'originalMainSource':'6b53efeec87f3ec36a840dd8e7759656cb4aee5c','testHashes':{str(p.relative_to(ROOT)):sha(p) for p in tests},'mainHashes':{str(p.relative_to(ROOT)):sha(p) for p in mains},'dependencies':deps,'driverSha256':sha(__file__),'startUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'actualBackendActions':0,'reusedOldResults':False,'selection':classes,'expectedUniqueMethods':2 if MODE=='red' else 14,'redExpectedOutcome':'FAILED2_NOT_PASS' if MODE=='red' else None}
if MODE=='red':
 for p in mains:assert p.read_bytes()==subprocess.check_output(['git','show',before['originalMainSource']+':'+str(p.relative_to(ROOT))],cwd=ROOT)
else:
 for p in [*mains,*tests]:assert p.read_bytes()==subprocess.check_output(['git','show',head+':'+str(p.relative_to(ROOT))],cwd=ROOT),'green must use committed source'
save('begin.safe.json',before);(slot/'classes').mkdir();stages={};jdk=TC/'jdk-25.0.4/bin';cp=os.pathsep.join(deps)
if MODE=='red':
 fmt=TC/'google-java-format-1.36.1-all-deps.jar';stages['format']=runner.step('format',[str(jdk/'java'),'-jar',str(fmt),'--replace',*map(str,tests)],ROOT);assert stages['format']['actualExit']==0
 before['testHashes']={str(p.relative_to(ROOT)):sha(p) for p in tests};save('begin.safe.json',before)
sources=tests if MODE=='red' else [*mains,*tests]
stages['compile']=runner.step('compile',[str(jdk/'javac'),'--release','25','-proc:none','-Xlint:all','-Werror','-cp',cp,'-d',str(slot/'classes'),*map(str,sources)],ROOT);assert stages['compile']['actualExit']==0
console=next(k for k in deps if 'junit-platform-console-standalone' in k);cmd=[str(jdk/'java')];session='PG18638-JMS-CANONICAL-UUID'
if MODE=='green':
 agent=next(k for k in base['toolHashes'] if 'agent' in k);assert sha(agent)==base['toolHashes'][agent];cmd+=['-javaagent:'+agent+'=destfile='+str(slot/'jacoco.exec')+',sessionid='+session+',append=false','-Xlog:class+init=info:file='+str(slot/'class-init.log')]
cmd+=['-jar',console,'execute','--disable-banner','--class-path',str(slot/'classes')+os.pathsep+cp,'--reports-dir',str(slot/'xml'),'--fail-if-no-tests','--details','summary']
for c in classes:cmd+=['--select-method',c+'#identityPropertiesMustRetainExactLowercaseCanonicalUuidText'] if MODE=='red' else ['--select-class',c]
stages['unit']=runner.step('unit',cmd,ROOT);case=[]
for p in (slot/'xml').glob('TEST-*.xml'):
 for c in ET.parse(p).getroot().findall('.//testcase'):case.append({'classname':c.get('classname'),'name':c.get('name'),'failure':bool(c.findall('failure')),'error':bool(c.findall('error')),'skipped':bool(c.findall('skipped'))})
if MODE=='red':assert len(case)==2 and sum(c['failure'] for c in case)==2 and not any(c['error'] or c['skipped'] for c in case) and stages['unit']['actualExit']==1
else:
 assert stages['unit']['actualExit']==0 and len(case)==14 and not any(c['failure'] or c['error'] or c['skipped'] for c in case)
 cli=next(k for k in base['toolHashes'] if 'cli' in k);assert sha(cli)==base['toolHashes'][cli];(slot/'component').mkdir()
 for c in mainclasses:
  src=slot/'classes'/Path(c.replace('.','/')+'.class');dst=slot/'component'/src.relative_to(slot/'classes');dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,dst)
 stages['coverage']=runner.step('coverage',[str(jdk/'java'),'-jar',cli,'report',str(slot/'jacoco.exec'),'--classfiles',str(slot/'component'),'--sourcefiles',str(ROOT/'src/schubert-nk-api/src/main/java'),'--sourcefiles',str(ROOT/'src/schubert-nk-web/src/main/java'),'--xml',str(slot/'coverage.xml'),'--csv',str(slot/'coverage.csv')],ROOT);assert stages['coverage']['actualExit']==0
 for label,args in [('execinfo',['execinfo',str(slot/'jacoco.exec')]),('classinfo',['classinfo',str(slot/'component')])]:stages[label]=runner.step(label,[str(jdk/'java'),'-jar',cli,*args],ROOT);assert stages[label]['actualExit']==0
manifest={'actualExit':stages['unit']['actualExit'],'source':head if MODE=='green' else before['originalMainSource'],'mode':MODE,'begin':before,'stages':stages,'cases':case,'tests':len(case),'failures':sum(c['failure'] for c in case),'errors':sum(c['error'] for c in case),'skipped':sum(c['skipped'] for c in case),'formalUpdated':False,'newAccepted':0,'mainSourceChanged':MODE=='green','whole451Accepted':False,'files':{str(p.relative_to(slot)):sha(p) for p in slot.rglob('*') if p.is_file() and p.name!='manifest.safe.json'}};save('manifest.safe.json',manifest);print(json.dumps({'slot':str(slot),'manifestSha256':sha(slot/'manifest.safe.json'),'actualUnitExit':manifest['actualExit'],'tests':len(case),'failures':manifest['failures'],'stages':{k:v['actualExit'] for k,v in stages.items()}}))
