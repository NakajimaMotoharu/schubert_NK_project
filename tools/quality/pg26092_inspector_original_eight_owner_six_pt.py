"""Changed original Inspector8 + six independent Test-owned child boundaries, no service admission."""
from pathlib import Path
import datetime as dt,hashlib,json,os,subprocess,sys,shutil,xml.etree.ElementTree as ET
import pg9666_pagination_static as stage
from host_tool_invocation import capture,verify
R=Path(__file__).resolve().parents[2];B=R/'evidence/01_PT/018_NK-OPS-001';TC=R.parent/'toolchain';S=R.parent/'pgpt-runs/PG379/pg26092-inspector-whole8-owner6-v1';O=B/'evidence/PG26092-inspector-whole8-owner6-v1'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();load=lambda p:json.loads(p.read_text());write=lambda p,v:p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
assert Path.cwd()==R and len(sys.argv)==1 and not S.exists() and not O.exists();inv=capture(__file__)
P=B/'evidence/PG26088-inspector-current-preflight-v1/manifest.json';assert sha(P)=='20f4dd0abf55069506604ea2ef52c3b1ad807a2b706183f4ec648b4a7d1b2b2d';pf=load(P)
assert pf['actualExit']==0 and pf['applicableStaticViolations']==0
for name in ['JAVA_TOOL_OPTIONS','JDK_JAVA_OPTIONS','_JAVA_OPTIONS','CLASSPATH']:assert name not in os.environ
assert os.environ.get('SCHUBERT_SHELLCHECK') in [None,'/home/mini/codex/project1/work/toolchain/shellcheck-0.11.0/root/usr/bin/shellcheck']
for n,h in {**pf['testSourceHashes'],**pf['readOnlyPublicInputs'],**pf['childGuardSourceHashes']}.items():
 assert sha(R/n)==h and hashlib.sha256(subprocess.check_output(['git','show','HEAD:'+n],cwd=R)).hexdigest()==h
for n,h in {**pf['dependencies'],**pf['toolBinaryHashes']}.items():assert sha(Path(n))==h
for row in pf['normalJars'].values():assert sha(Path(row['path']))==row['sha256']
normal=R.parent/'pgpt-runs/PG379/pg22084-api-stop-state-six-main-compile-v1/manifest.safe.json';assert sha(normal)==pf['normalManifestSha256'];nm=load(normal);assert nm['source']==pf['productionCoreMain'] and nm['testsExecuted'] is False and nm['actualExit']==0
head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip();os.umask(0o077);S.mkdir();classes=S/'classes';classes.mkdir();tmp=S/'tmp';tmp.mkdir();fixture=S/'public-fixture-root';fixture.mkdir()
for n,h in pf['readOnlyPublicInputs'].items():
 target=fixture/n;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(R/n,target);assert sha(target)==h
console=TC/'junit-platform-console-standalone-1.13.4.jar';gson=TC/'m2/repository/com/google/code/gson/gson/2.14.0/gson-2.14.0.jar';annotation=TC/'m2/repository/org/jspecify/jspecify/1.0.1/jspecify-1.0.1.jar';jdk=TC/'jdk-25.0.4/bin';agent=TC/'m2/repository/org/jacoco/org.jacoco.agent/0.8.15/org.jacoco.agent-0.8.15-runtime.jar';assert str(agent) in pf['dependencies']
# Parent Test compile needs only JUnit/Gson/annotation, not any Production classes.
compilecp=os.pathsep.join(map(str,[console,gson,annotation]));external=[n for n in pf['dependencies'] if n.endswith('.jar') and n not in [str(console),str(annotation)]]
runtimecp=os.pathsep.join([str(classes),*[v['path'] for v in pf['normalJars'].values()],*external,str(annotation)])
selected=['dev.codex.schubert.nk.api.maintenance.InspectorDeploymentTest','dev.codex.schubert.nk.api.maintenance.InspectorChildOwnerTest'];session='PG26092-INSPECTOR-WHOLE8-OWNER6'
begin=dict(source=head,productionCoreMain=nm['source'],startUTC=dt.datetime.now(dt.timezone.utc).isoformat(),invocation=inv,preflight=dict(path=str(P.relative_to(R)),sha256=sha(P)),testSourceHashes=pf['testSourceHashes'],publicInputs=pf['readOnlyPublicInputs'],childGuardSourceHashes=pf['childGuardSourceHashes'],normalJarHashes=pf['normalJars'],dependencies=pf['dependencies'],toolBinaryHashes=pf['toolBinaryHashes'],expectedMethods=pf['expectedMethods'],session=session,expectedTests=14,originalTests=8,additionalOwnerFixtureTests=6,sourceFixed=True,actualServiceVmDbActions=0,childBusinessAdmission=False,javaMainCoverageClaimed=False,staticManifest=pf['staticManifest']);write(S/'begin.safe.json',begin);stage.SLOT=S
steps={};steps['compile']=stage.step('compile',[str(jdk/'javac'),'--release','25','-proc:none','-implicit:none','-Xlint:all','-Werror','-cp',compilecp,'-d',str(classes),*[str(R/n) for n in pf['testSourceHashes']]],S,timeout=90)
actual=steps['compile']['actualExit']
if actual==0:
 steps['unit']=stage.step('unit',[str(jdk/'java'),'-Djava.io.tmpdir='+str(tmp),'-Dfile.encoding=UTF-8','-Duser.language=ja','-Duser.country=JP','-Duser.timezone=Asia/Tokyo','-Dnk.pt.repository='+str(fixture),'-Djunit.jupiter.extensions.autodetection.enabled=false','-Djunit.jupiter.execution.parallel.enabled=false','-javaagent:'+str(agent)+'=destfile='+str(S/'jacoco.exec')+',append=false,sessionid='+session,'-Xlog:class+init=info:file='+str(S/'class-init.log'),'-cp',str(console)+os.pathsep+runtimecp,'org.junit.platform.console.ConsoleLauncher','execute','--disable-banner','--class-path',runtimecp,'--reports-dir',str(S/'xml'),'--fail-if-no-tests','--details','summary',*[a for n in selected for a in ['--select-class',n]]],S,timeout=180);actual=steps['unit']['actualExit']
cases=[];xmls={}
if (S/'xml').exists():
 for p in (S/'xml').glob('TEST-*.xml'):
  xmls[p.name]=sha(p)
  for c in ET.parse(p).getroot().findall('testcase'):cases.append(dict(className=c.get('classname'),name=c.get('name'),nonPass=[n.tag for n in c if n.tag in ['failure','error','skipped']]))
public={}
for p in (fixture/'src/schubert-nk-api/target/inspector-deployment').glob('*/*.json'):
 d=load(p);assert set(d)=={'method','command','exitCode','stdout','stderr'} and not any(v in str(d) for v in ['CREDENTIALS_DIRECTORY=','INVOCATION_ID=','JAVA_TOOL_OPTIONS=']);public[str(p.relative_to(fixture))]=sha(p)
expected={(selected[i],method) for i,methods in enumerate(pf['expectedMethods'].values()) for method in methods};observed={(c['className'],c['name'].split('(')[0]) for c in cases}
passed=actual==0 and len(cases)==14 and len(observed)==14 and observed==expected and not any(c['nonPass'] for c in cases) and len(public)==50
held=['TemporaryInfrastructureException','FingerprintKeyRing','ResponseSnapshotCodec','WebStartupException'];hits=[]
if (S/'class-init.log').exists():
 for l in (S/'class-init.log').read_text().splitlines():
  if any(n in l for n in held):hits.append(l)
passed=passed and not hits
for n,h in {**pf['testSourceHashes'],**pf['readOnlyPublicInputs'],**pf['childGuardSourceHashes']}.items():assert sha(R/n)==h
verify(inv);v=dict(actualExit=0 if passed else 1,atJST=dt.datetime.now().astimezone().isoformat(),source=head,productionCoreMain=nm['source'],begin=begin,stages=steps,cases=cases,xmlHashes=xmls,publicToolReceiptHashes=public,originalTopLevelToolReceipts=len(public),execSha256=sha(S/'jacoco.exec') if (S/'jacoco.exec').exists() else None,session=session,parentHeldFourInitializations=len(hits),childNoNativeAdmissionBasis='Unchanged five source guards, empty child environment, absent reserved agent; child native/VM coverage not measured',actualServiceVmDbActions=0,javaMainCoverageClaimed=False,newCoverageMeasurements=0,newTestIds=6,productTestsExecuted=len(cases),newAcceptance=0,formalUpdated=False,effortRate=None,qualification='RAW_TERMINAL_ONLY_INDEPENDENT_POST_PENDING',toolSha256=sha(Path(__file__)))
write(S/'manifest.safe.json',v);O.mkdir();write(O/'manifest.json',v)
for p in (S/'xml').glob('TEST-*.xml'):shutil.copyfile(p,O/p.name)
for n in ['compile.stdout','compile.stderr','unit.stdout','unit.stderr']:
 if (S/n).exists():shutil.copyfile(S/n,O/n)
print(json.dumps(dict(actualExit=v['actualExit'],tests=len(cases),receipts=len(public),heldFour=len(hits),source=head,manifestSha256=sha(O/'manifest.json'))));raise SystemExit(v['actualExit'])
