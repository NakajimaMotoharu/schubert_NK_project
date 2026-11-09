"""Original API Outbox repository/collector whole18 using owned JDBC proxies and memory SDK."""
from pathlib import Path
import datetime,hashlib,json,os,subprocess,sys,xml.etree.ElementTree as E,zipfile
import pg9666_pagination_static as stage
from host_tool_invocation import capture,verify
R=Path(__file__).resolve().parents[2];B=R/'evidence/01_PT/018_NK-OPS-001';RUNS=R.parent/'pgpt-runs/PG379';TC=R.parent/'toolchain';S=RUNS/'pg25450-api-outbox-jdbc-original-whole18-v1';O=B/'evidence/PG25450-api-outbox-jdbc-original-whole18-v1';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();load=lambda p:json.loads(p.read_bytes());write=lambda p,v:p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
assert len(sys.argv)==1 and Path.cwd()==R
invocation=capture(__file__);P=B/'evidence/PG25448-api-outbox-jdbc-current-console-preflight-v1/manifest.json';pf=load(P);assert pf['actualExit']==0 and pf['entrypointSha256']==sha(Path(__file__))
assert not S.exists() and not O.exists();assert all(n not in os.environ for n in ['JAVA_TOOL_OPTIONS','JDK_JAVA_OPTIONS','_JAVA_OPTIONS','CLASSPATH'])
normal=RUNS/'pg22084-api-stop-state-six-main-compile-v1/manifest.safe.json';assert sha(normal)==pf['normalManifestSha256'];nm=load(normal);assert nm['source']==pf['productionCoreMain'] and type(nm['actualExit']) is int and nm['actualExit']==0 and nm['testsExecuted'] is False and nm['testStatus']=='NOT_RUN_COMPILE_ONLY_NOT_PASS'
for path,digest in pf['inputHashes'].items():assert sha(R/path)==digest
for path,digest in pf['dependencies'].items():assert sha(Path(path))==digest
api=Path(nm['jars']['api']['path']);assert sha(api)==nm['jars']['api']['sha256']
assert set(pf['targetClassNames'])==set(pf['targetClassHashes']) and len(pf['targetClassNames'])==3
assert pf['selected']==['dev.codex.schubert.nk.api.monitoring.OutboxObservationRepositoryTest', 'dev.codex.schubert.nk.api.monitoring.OutboxMetricCollectorTest']
S.mkdir();(S/'classes').mkdir();(S/'component').mkdir();(S/'tmp').mkdir();stage.SLOT=S
with zipfile.ZipFile(api) as z:
 for member,digest in pf['targetClassHashes'].items():
  assert member in pf['targetClassNames'];raw=z.read(member);assert hashlib.sha256(raw).hexdigest()==digest;(S/'component'/Path(member).name).write_bytes(raw)
vendor=[Path(p) for p in pf['vendorJars']];assert all(sha(p)==pf['vendorJars'][str(p)] for p in vendor);console=TC/'junit-platform-console-standalone-1.13.4.jar';agent=TC/'m2/repository/org/jacoco/org.jacoco.agent/0.8.15/org.jacoco.agent-0.8.15-runtime.jar';annotation=TC/'m2/repository/org/jspecify/jspecify/1.0.1/jspecify-1.0.1.jar';cli=TC/'org.jacoco.cli-0.8.15-nodeps.jar';jdk=TC/'jdk-25.0.4/bin';tests=[R/path for path in pf['testPaths']];classpath=os.pathsep.join(map(str,[S/'classes',api,*vendor,annotation]));head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip();session='PG25450-API-OUTBOX-JDBC-ORIGINAL-WHOLE18'
begin=dict(source=head,productionCoreMain=nm['source'],startUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),invocation=invocation,preflight=dict(path=str(P.relative_to(R)),sha256=sha(P)),inputHashes=pf['inputHashes'],dependencies=pf['dependencies'],targetClassHashes=pf['targetClassHashes'],selected=pf['selected'],expectedTests=18,session=session,newMethods=0,originalEighteenWhole=True,oldExecUnion=False,actualBackendActions=0,actualRootVmNativeActions=0);write(S/'begin.json',begin)
steps={};steps['compile']=stage.step('compile',[str(jdk/'javac'),'--release','25','-proc:none','-implicit:none','-Xlint:all','-Werror','-cp',os.pathsep.join(map(str,[api,*vendor,annotation,console])),'-d',str(S/'classes'),*map(str,tests)],S,timeout=90)
if steps['compile']['actualExit']==0:
 steps['unit']=stage.step('unit',[str(jdk/'java'),'-Djava.io.tmpdir='+str(S/'tmp'),'-Dfile.encoding=UTF-8','-Duser.language=ja','-Duser.country=JP','-Duser.timezone=Asia/Tokyo','-Djunit.jupiter.extensions.autodetection.enabled=false','-Djunit.jupiter.execution.parallel.enabled=false','-javaagent:'+str(agent)+'=destfile='+str(S/'jacoco.exec')+',sessionid='+session+',append=false','-Xlog:class+init=info:file='+str(S/'class-init.log'),'-jar',str(console),'execute','--disable-banner','--class-path',classpath,'--reports-dir',str(S/'xml'),'--fail-if-no-tests','--details','summary',*[v for name in pf['selected'] for v in ['--select-class',name]]],S,timeout=180)
actual=steps.get('unit',steps['compile'])['actualExit']
if actual==0:
 for name,command in [('coverage',[str(jdk/'java'),'-jar',str(cli),'report',str(S/'jacoco.exec'),'--classfiles',str(S/'component'),'--xml',str(S/'coverage.xml')]),('execinfo',[str(jdk/'java'),'-jar',str(cli),'execinfo',str(S/'jacoco.exec')]),('classinfo',[str(jdk/'java'),'-jar',str(cli),'classinfo',str(S/'component')])]:
  steps[name]=stage.step(name,command,S,timeout=90)
  if steps[name]['actualExit']!=0:actual=steps[name]['actualExit'];break
verify(invocation)
for path,digest in pf['inputHashes'].items():assert sha(R/path)==digest
for path,digest in pf['dependencies'].items():assert sha(Path(path))==digest
cases=[];xmlHashes={}
for p in sorted((S/'xml').glob('TEST-*.xml')):
 xmlHashes[p.name]=sha(p)
 for t in E.parse(p).getroot().findall('testcase'):cases.append(dict(className=t.get('classname'),name=t.get('name'),nonPass=[n.tag for n in t if n.tag in ['failure','error','skipped']]))
v=dict(actualExit=actual,atJST=datetime.datetime.now().astimezone().isoformat(),source=head,productionCoreMain=nm['source'],begin=begin,stages=steps,cases=cases,xmlHashes=xmlHashes,qualification='RAW_TERMINAL_ONLY_INDEPENDENT_POST_PENDING',productTestsExecuted=len(cases),newProductTests=0,newAcceptance=0,formalUpdated=False,effortRate=None,whole451Accepted=False)
write(S/'manifest.json',v);O.mkdir();write(O/'manifest.json',v);print(json.dumps(dict(actualExit=actual,tests=len(cases),source=head,manifestSha256=sha(O/'manifest.json'))));raise SystemExit(actual)
