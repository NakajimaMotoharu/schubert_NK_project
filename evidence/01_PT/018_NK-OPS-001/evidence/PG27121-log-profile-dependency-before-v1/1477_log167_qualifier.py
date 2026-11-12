"""Whole existing17 User query tests + required current dependencies142; no actual DB/held binaries."""
from pathlib import Path
import hashlib,json,re,subprocess,sys,zipfile,xml.etree.ElementTree as ET
import pg9666_pagination_static as c
R=Path.cwd(); B=R/'evidence/01_PT/018_NK-OPS-001'; TC=R.parent/'toolchain'; RUNS=R.parent/'pgpt-runs/PG379'
W=RUNS/'pg27116-log167-profile-v1';O=B/'evidence/PG27116-log167-profile-v1'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();load=lambda p:json.loads(p.read_text());wr=lambda p,v:p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n');ref=lambda p:dict(path=str(p.relative_to(R)),sha256=sha(p));phase=sys.argv[1]
np=B/'evidence/PG22106-api-stop-static-independent-input-v1/normal.json';n=load(np);assert sha(np)=='b2f07209804d71ee2ffbc4d9aca5311d4e6cf15721c74bcde411f86538cf4f27'
ap=B/'evidence/PG26744-authorization-current-independent-v1/manifest.json';auth=load(ap)
cp=B/'evidence/PG26648-canonical-independent-v2/manifest.json';canon=load(cp);cu=load(cp.parent/'unit-manifest.json');cw=RUNS/'pg26628-canonical-pure-main-v1/target/classes';ct=RUNS/'pg26628-canonical-pure-main-v1/test-classes-v2'
authnames=[p for p in auth['physicalClassHashes'] if '/api/' in p];assert len(authnames)==6
ownnames=['dev/codex/schubert/nk/api/'+x+'.class' for x in ['application/log/LogRequest','persistence/LogQueryRepository','persistence/LogQueryException','database/RequiredColumn','application/log/LogQueryAuditWriter','application/log/LogQueryAuditWriter$Event','application/log/package-info','persistence/package-info','database/package-info']]
names=ownnames+authnames
paths=sorted({'src/schubert-nk-api/src/main/java/'+x.removesuffix('.class').split('$',1)[0]+'.java' for x in names})
for p in paths:assert sha(R/p)==n['begin']['inputHashes'][p]
canoninputs=cu['begin']['inputHashes'];assert all(sha(R/p)==h for p,h in canoninputs.items())
for name,h in canon['physicalClassHashes'].items():assert sha(cw/name)==h
tests=['src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/application/log/'+x+'.java' for x in ['LogPlainContractTest','LogSqlContractTest','LogSearchAuditPortTest']]
authTest='src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/security/AuthorizationServiceTest.java';assert sha(R/authTest)==auth['inputHashes'][authTest]
held=['TemporaryInfrastructureException','FingerprintKeyRing','ResponseSnapshotCodec','WebStartupException']
for p in tests+[authTest]:
 s=(R/p).read_text();assert not any(x in s for x in held+['@BeforeAll','@TempDir','DriverManager','DataSource','getConnection(','ProcessBuilder','Class.forName('])
pp=B/'evidence/PG26278-protocol-unicode-main-compile-v1/manifest.json';proto=load(pp);jar=Path(proto['jar']['path']);assert sha(jar)==proto['jar']['sha256'] and all(sha(R/p)==h for p,h in proto['inputHashes'].items())
tp=B/'evidence/PG26304-protocol-unicode-full130-compile-v3/manifest.json';pt=load(tp);ptroot=RUNS/'pg26304-protocol-unicode-full130-compile-v3/classes';resources=load(B/'evidence/PG26280-protocol-unicode-full130-compile-v1/manifest.json')['resources'];resourceRoot=RUNS/'pg26280-protocol-unicode-full130-compile-v1/resources'
assert pt['classHashes']=={str(p.relative_to(ptroot)):sha(p) for p in ptroot.rglob('*.class')}
for p in pt['tests']+resources:assert sha(R/p)==pt['inputHashes'][p]
prior=load(B/'evidence/PG26310-protocol-unicode-full130-unit-v1/manifest.json');expected=[dict(classname=x['classname'],name=x['name']) for x in prior['cases']]
expected.extend(dict(classname=x['classname'],name=x['name']) for x in cu['cases'])
for p in tests+[authTest]:
 methods=re.findall(r'@Test\b[^\n]*\n\s*void (\w+)\s*\(',(R/p).read_text());assert len(methods)=={'LogPlainContractTest.java':8,'LogSqlContractTest.java':9,'LogSearchAuditPortTest.java':8,'AuthorizationServiceTest.java':2}[Path(p).name]
 expected.extend(dict(classname=p.split('/src/test/java/')[1][:-5].replace('/','.'),name=x+'()') for x in methods)
assert len(expected)==167 and len({(x['classname'],x['name']) for x in expected})==167
inputs={p:sha(R/p) for p in paths+tests+[authTest]+list(canoninputs)+list(proto['inputHashes'])+pt['tests']+resources}
console=TC/'junit-platform-console-standalone-1.13.4.jar';ann=TC/'m2/repository/org/jspecify/jspecify/1.0.1/jspecify-1.0.1.jar';gson=TC/'m2/repository/com/google/code/gson/gson/2.14.0/gson-2.14.0.jar';assert '<version>2.14.0</version>' in (R/'src/schubert-nk-api/pom.xml').read_text();deps={str(p):sha(p) for p in [jar,console,ann,gson]};jdk=TC/'jdk-25.0.4/bin'
if phase=='prepare':
 assert not W.exists() and not O.exists();W.mkdir();O.mkdir();c.SLOT=O
 for d in ['api-main','component','test-classes']:(W/d).mkdir()
 with zipfile.ZipFile(Path(n['jars']['api']['path'])) as z:
  for name in names:
   assert not any(name.endswith('/'+h+'.class') for h in held)
   data=z.read(name);assert hashlib.sha256(data).hexdigest()==n['normalPhysicalClassHashes']['api:'+name]
   for d in ['api-main','component']:
    p=W/d/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
 for name,h in canon['physicalClassHashes'].items():
  for d in ['api-main','component']:
   p=W/d/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes((cw/name).read_bytes())
 with zipfile.ZipFile(jar) as z:
  for name,h in proto['physicalClassHashes'].items():
   data=z.read(name);assert hashlib.sha256(data).hexdigest()==h;p=W/'component'/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
 physical={str(p.relative_to(W/'component')):sha(p) for p in (W/'component').rglob('*.class')};assert len(physical)==196
 # Compile only these four complete ordinary fixture files; cached canonical/protocol tests unchanged.
 stage=c.step('test-compile',[str(jdk/'javac'),'--release','25','-g','-proc:none','-implicit:none','-encoding','UTF-8','-Xlint:all','-Werror','-cp',str(W/'api-main')+':'+':'.join(deps),'-d',str(W/'test-classes'),*[str(R/p) for p in tests+[authTest]]],R)
 assert stage['actualExit']==0
 canonicalTests={str(p.relative_to(ct)):sha(p) for p in ct.rglob('*.class')};assert len(canonicalTests)==3
 v=dict(actualExit=0,inputHashes=inputs,dependencies=deps,apiMainSources=paths,apiTestSources=tests+[authTest],apiExactReadClassEntries=names,apiWholeJarHashedOrOtherEntryPayloadRead=False,physicalClassHashes=physical,protoMain=ref(pp),protoTest=ref(tp),normalMain=ref(np),canonicalProof=ref(cp),authorizationProof=ref(ap),canonicalTestClassHashes=canonicalTests,testClassHashes={str(p.relative_to(W/'test-classes')):sha(p) for p in (W/'test-classes').rglob('*.class')},selectedClasses=sorted({x['classname'] for x in expected}),expectedCases=expected,expectedTests=167,stages={'test-compile':stage},MainRebuilt=False,productTestsExecuted=0,actualFourClassBinaryAccess=False,repositoryExceptionalBranchesNotAccepted=True)
 wr(O/'manifest.json',v);print(json.dumps(dict(actualExit=0,expectedTests=167,physical=192,newTestDefinitions=0)));sys.exit(0)
assert phase=='run';m=load(O/'manifest.json');assert m['inputHashes']==inputs and m['dependencies']==deps
assert m['physicalClassHashes']=={str(p.relative_to(W/'component')):sha(p) for p in (W/'component').rglob('*.class')}
assert m['canonicalTestClassHashes']=={str(p.relative_to(ct)):sha(p) for p in ct.rglob('*.class')}
source=sys.argv[2];assert re.fullmatch('[0-9a-f]{40}',source)
for p,h in inputs.items():assert hashlib.sha256(subprocess.check_output(['git','show',source+':'+p])).hexdigest()==h
pfpath=B/'evidence/PG27118-log167-preflight-v1/manifest.json';pf=load(pfpath);assert pf['actualExit']==0 and pf['inputHashes']==inputs
U=RUNS/'pg27120-log167-v1';A=B/'evidence/PG27120-log167-v1';assert not U.exists() and not A.exists();U.mkdir();A.mkdir();(U/'tmp').mkdir();c.SLOT=A
agent=TC/'m2/repository/org/jacoco/org.jacoco.agent/0.8.15/org.jacoco.agent-0.8.15-runtime.jar';cli=TC/'org.jacoco.cli-0.8.15-nodeps.jar';session='PG27120-LOG167';runtime=':'.join(map(str,[W/'api-main',W/'test-classes',ct,ptroot,resourceRoot,jar,ann,gson]))
cmd=[str(jdk/'java'),'-Djava.io.tmpdir='+str(U/'tmp'),'-Dfile.encoding=UTF-8','-Duser.timezone=Asia/Tokyo','-Djunit.jupiter.execution.parallel.enabled=false','-Djunit.jupiter.extensions.autodetection.enabled=false','-javaagent:'+str(agent)+'=destfile='+str(U/'jacoco.exec')+',sessionid='+session+',append=false','-Xlog:class+init=info:file='+str(U/'class-init.log'),'-jar',str(console),'execute','--disable-banner','--class-path',runtime,*[a for name in m['selectedClasses'] for a in ['--select-class',name]],'--reports-dir',str(U/'xml'),'--fail-if-no-tests','--details','summary']
begin=dict(source=source,productionCoreMain='a695e0da99a5b7749cd1f70a200a767fd3906d3b',inputHashes=inputs,dependencies=deps,physicalClassHashes=m['physicalClassHashes'],expectedCases=expected,expectedTests=167,selectedClasses=m['selectedClasses'],session=session,prepare=ref(O/'manifest.json'),preflight=ref(pfpath),oldExecUnion=False,actualBackendOrHeldClassActions=0);wr(A/'begin.json',begin)
stages={'unit':c.step('unit',cmd,R,timeout=180)}
for label,args in [('coverage',['report',str(U/'jacoco.exec'),'--classfiles',str(W/'component'),'--xml',str(U/'coverage.xml')]),('classinfo',['classinfo',str(W/'component')]),('execinfo',['execinfo',str(U/'jacoco.exec')])]:stages[label]=c.step(label,[str(jdk/'java'),'-jar',str(cli),*args],R)
actual=[]
for p in (U/'xml').glob('TEST-*.xml'):
 for x in ET.parse(p).findall('testcase'):actual.append(dict(classname=x.get('classname'),name=x.get('name'),failure=x.find('failure') is not None,error=x.find('error') is not None,skipped=x.find('skipped') is not None))
v=dict(actualExit=stages['unit']['actualExit'],begin=begin,stages=stages,cases=actual,tests=len(actual),failures=sum(x['failure'] for x in actual),errors=sum(x['error'] for x in actual),skipped=sum(x['skipped'] for x in actual),formalUpdated=False,whole451Accepted=False);wr(A/'manifest.json',v);print(json.dumps({k:v[k] for k in ['actualExit','tests','failures','errors','skipped']}));sys.exit(v['actualExit'])
