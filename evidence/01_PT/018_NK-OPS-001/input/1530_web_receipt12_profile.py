"""Whole existing Receipt9 and Recovery4, exact normal three physical classes only."""
from pathlib import Path
import hashlib,json,re,subprocess,sys,zipfile,xml.etree.ElementTree as ET
import pg9666_pagination_static as c
R=Path.cwd();B=R/'evidence/01_PT/018_NK-OPS-001';TC=R.parent/'toolchain';RUNS=R.parent/'pgpt-runs/PG379';W=RUNS/'pg27232-web-receipt12-profile-v1';O=B/'evidence/PG27232-web-receipt12-profile-v1';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();load=lambda p:json.loads(p.read_text());wr=lambda p,v:p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n');ref=lambda p:dict(path=str(p.relative_to(R)),sha256=sha(p));phase=sys.argv[1]
np=B/'evidence/PG22106-api-stop-static-independent-input-v1/normal.json';n=load(np);assert sha(np)=='b2f07209804d71ee2ffbc4d9aca5311d4e6cf15721c74bcde411f86538cf4f27'
base='dev/codex/schubert/nk/web/receipt/';names=[base+x+'.class' for x in ['ReceiptReference','ReceiptReferenceRepository','ReceiptReferenceRepository$Work','ReceiptReferenceException']]+['dev/codex/schubert/nk/web/session/'+x+'.class' for x in ['SessionStoreException','InvalidSessionRowException','package-info']];paths=sorted({'src/schubert-nk-web/src/main/java/'+x[:-6].split('$')[0]+'.java' for x in names});tests=['src/schubert-nk-web/src/test/java/'+base+x+'.java' for x in ['ReceiptReferencePortTest','ReceiptFailureGraph329Test']];inputs={p:sha(R/p) for p in paths+tests}
assert all(inputs[p]==n['begin']['inputHashes'][p] for p in paths)
held=['TemporaryInfrastructureException','FingerprintKeyRing','ResponseSnapshotCodec','WebStartupException']
for p in tests:
 s=(R/p).read_text();assert not any(x in s for x in held+['@BeforeAll','@TempDir','DriverManager','getConnection(','ProcessBuilder','Class.forName('])
expected=[]
for p,total in zip(tests,[9,3]):
 methods=re.findall(r'@Test\s*(?:@DisplayName\("[^\n]*"\)\s*)?void (\w+)\s*\(',(R/p).read_text());assert len(methods)==total;expected.extend(dict(classname=p.split('/src/test/java/')[1][:-5].replace('/','.'),name=x+'()') for x in methods)
assert len(expected)==12
console=TC/'junit-platform-console-standalone-1.13.4.jar';ann=TC/'m2/repository/org/jspecify/jspecify/1.0.1/jspecify-1.0.1.jar';deps={str(p):sha(p) for p in [console,ann]};jdk=TC/'jdk-25.0.4/bin'
if phase=='prepare':
 assert not W.exists() and not O.exists();W.mkdir();O.mkdir();c.SLOT=O
 for d in ['component','test-classes']:(W/d).mkdir()
 with zipfile.ZipFile(Path(n['jars']['web']['path'])) as z:
  for name in names:
   data=z.read(name);assert hashlib.sha256(data).hexdigest()==n['normalPhysicalClassHashes']['web:'+name];p=W/'component'/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
 stage=c.step('test-compile',[str(jdk/'javac'),'--release','25','-g','-proc:none','-implicit:none','-encoding','UTF-8','-Xlint:all','-Werror','-cp',str(W/'component')+':'+':'.join(deps),'-d',str(W/'test-classes'),*[str(R/p) for p in tests]],R);assert stage['actualExit']==0 and not stage['timedOut']
 v=dict(actualExit=0,inputHashes=inputs,dependencies=deps,apiMainSources=paths,apiTestSources=tests,apiExactReadClassEntries=names,apiWholeJarHashedOrOtherEntryPayloadRead=False,physicalClassHashes={str(p.relative_to(W/'component')):sha(p) for p in (W/'component').rglob('*.class')},testClassHashes={str(p.relative_to(W/'test-classes')):sha(p) for p in (W/'test-classes').rglob('*.class')},normalMain=ref(np),selectedClasses=sorted({x['classname'] for x in expected}),expectedCases=expected,expectedTests=12,stages={'test-compile':stage},productTestsExecuted=0,newDefinitions=0,MainRebuilt=False,actualHeldClassBinaryAccess=False);assert len(v['physicalClassHashes'])==7;wr(O/'manifest.json',v);print(json.dumps(dict(actualExit=0,expectedTests=12,physical=7)));raise SystemExit(0)
assert phase=='run';m=load(O/'manifest.json');assert m['inputHashes']==inputs and m['dependencies']==deps
for dirname,key in [('component','physicalClassHashes'),('test-classes','testClassHashes')]:assert m[key]=={str(p.relative_to(W/dirname)):sha(p) for p in (W/dirname).rglob('*.class')}
source=sys.argv[2];assert re.fullmatch('[0-9a-f]{40}',source)
for p,h in inputs.items():assert hashlib.sha256(subprocess.check_output(['git','show',source+':'+p])).hexdigest()==h
pfpath=B/'evidence/PG27233-web-receipt12-preflight-v1/manifest.json';pf=load(pfpath);assert pf['actualExit']==0 and pf['inputHashes']==inputs
U=RUNS/'pg27234-web-receipt12-v1';A=B/'evidence/PG27234-web-receipt12-v1';assert not U.exists() and not A.exists();U.mkdir();A.mkdir();(U/'tmp').mkdir();c.SLOT=A
agent=TC/'m2/repository/org/jacoco/org.jacoco.agent/0.8.15/org.jacoco.agent-0.8.15-runtime.jar';cli=TC/'org.jacoco.cli-0.8.15-nodeps.jar';session='PG27234-WEB-RECEIPT12';runtime=':'.join(map(str,[W/'component',W/'test-classes',ann]))
cmd=[str(jdk/'java'),'-Djava.io.tmpdir='+str(U/'tmp'),'-Dfile.encoding=UTF-8','-Duser.timezone=Asia/Tokyo','-Djunit.jupiter.execution.parallel.enabled=false','-Djunit.jupiter.extensions.autodetection.enabled=false','-javaagent:'+str(agent)+'=destfile='+str(U/'jacoco.exec')+',sessionid='+session+',append=false','-Xlog:class+init=info:file='+str(U/'class-init.log'),'-jar',str(console),'execute','--disable-banner','--class-path',runtime,*[a for name in m['selectedClasses'] for a in ['--select-class',name]],'--reports-dir',str(U/'xml'),'--fail-if-no-tests','--details','summary']
begin=dict(source=source,productionCoreMain='13e6c050db76b202b03b1d7653cc368c178cae76',inputHashes=inputs,dependencies=deps,physicalClassHashes=m['physicalClassHashes'],expectedCases=expected,expectedTests=12,selectedClasses=m['selectedClasses'],session=session,prepare=ref(O/'manifest.json'),preflight=ref(pfpath),oldExecUnion=False,actualBackendOrHeldClassActions=0);wr(A/'begin.json',begin)
stages={'unit':c.step('unit',cmd,U,timeout=180)}
for label,args in [('coverage',['report',str(U/'jacoco.exec'),'--classfiles',str(W/'component'),'--xml',str(U/'coverage.xml')]),('classinfo',['classinfo',str(W/'component')]),('execinfo',['execinfo',str(U/'jacoco.exec')])]:stages[label]=c.step(label,[str(jdk/'java'),'-jar',str(cli),*args],R)
actual=[]
for p in (U/'xml').glob('TEST-*.xml'):
 for x in ET.parse(p).findall('testcase'):actual.append(dict(classname=x.get('classname'),name=x.get('name'),failure=x.find('failure') is not None,error=x.find('error') is not None,skipped=x.find('skipped') is not None))
v=dict(actualExit=stages['unit']['actualExit'],begin=begin,stages=stages,cases=actual,tests=len(actual),failures=sum(x['failure'] for x in actual),errors=sum(x['error'] for x in actual),skipped=sum(x['skipped'] for x in actual),formalUpdated=False,whole451Accepted=False);wr(A/'manifest.json',v);print(json.dumps({k:v[k] for k in ['actualExit','tests','failures','errors','skipped']}));sys.exit(v['actualExit'])
