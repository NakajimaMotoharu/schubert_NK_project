"""Closed safe session Main Maven NullAway compile and whole fixtures; no backend/held binary."""
from pathlib import Path
import copy,hashlib,json,os,re,shutil,subprocess,sys,xml.etree.ElementTree as ET,zipfile
import pg9666_pagination_static as c
R=Path.cwd();B=R/'evidence/01_PT/018_NK-OPS-001';TC=R.parent/'toolchain';RUNS=R.parent/'pgpt-runs/PG379';W=RUNS/'pg27950-nq-search26-normal-v1';O=B/'evidence/PG27950-nq-search26-normal-v1';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ld=lambda p:json.loads(p.read_text());wr=lambda p,j:p.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n');ref=lambda p:dict(path=str(p.relative_to(R)),sha256=sha(p));phase=sys.argv[1]
base='src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/';main=[base+'form/NotificationSearchForm.java',base+'form/QuestionSearchForm.java'];tests=['tools/quality/architecture/NotificationSearchInputContractTest.java','tools/quality/architecture/QuestionSearchInputContractTest.java'];totals=[12,14];expected=[]
for p,n in zip(tests,totals):
 s=(R/p).read_text();assert not any(x in s for x in ['TemporaryInfrastructureException','FingerprintKeyRing','ResponseSnapshotCodec','WebStartupException','@BeforeAll','@TempDir','ProcessBuilder','DriverManager','DataSource','java.nio.file','Class.forName']);methods=re.findall(r'@Test\s*(?:@Timeout\([^\n]+\)\s*)?void (\w+)\s*\(',s);assert len(methods)==n;expected.extend(dict(classname='dev.codex.schubert.nk.web.form.'+Path(p).stem,name=x+'()') for x in methods)
assert len(expected)==26 and len(main)==2
inputs={p:sha(R/p) for p in main+tests+['pom.xml','src/schubert-nk-web/pom.xml']};protoPath=B/'evidence/PG26278-protocol-unicode-main-compile-v1/manifest.json';proto=ld(protoPath);jar=Path(proto['jar']['path']);assert sha(jar)==proto['jar']['sha256'] and all(sha(R/p)==h for p,h in proto['inputHashes'].items());inputs.update(proto['inputHashes']);jdk=TC/'jdk-25.0.4/bin';maven=TC/'m2/wrapper/dists/apache-maven-3.9.12/6068d197/bin/mvn';ann=TC/'m2/repository/org/jspecify/jspecify/1.0.1/jspecify-1.0.1.jar';console=TC/'junit-platform-console-standalone-1.13.4.jar';websdk=[];deps={str(p):sha(p) for p in [jar,ann,console,*websdk]}
if phase=='prepare':
 assert not W.exists() and not O.exists();W.mkdir();O.mkdir();c.SLOT=O
 for p in main:
  assert not any(x in (R/p).read_text() for x in ['TemporaryInfrastructureException','FingerprintKeyRing','ResponseSnapshotCodec','WebStartupException','java.nio.file','java.net.Socket','DataSource']);to=W/'src/main/java'/p.split('/src/main/java/')[1];to.parent.mkdir(parents=True,exist_ok=True);to.write_bytes((R/p).read_bytes());assert sha(to)==inputs[p]
 ns='http://maven.apache.org/POM/4.0.0';ET.register_namespace('',ns);tag=lambda n:'{'+ns+'}'+n;root=ET.Element(tag('project'));add=lambda e,n,v:ET.SubElement(e,tag(n))
 for n,v in [('modelVersion','4.0.0'),('groupId','dev.codex.schubert.quality'),('artifactId','nq-search26-safe-subset'),('version','0.1.0-SNAPSHOT')]:add(root,n,v).text=v
 props=add(root,'properties',None)
 for n,v in [('maven.compiler.release','25'),('project.build.sourceEncoding','UTF-8'),('error-prone.version','2.50.0'),('nullaway.version','0.14.1'),('pgpt.protocol.jar',str(jar))]:add(props,n,v).text=v
 ds=add(root,'dependencies',None)
 for group,artifact,version in [('org.jspecify','jspecify','1.0.1')]:
  d=add(ds,'dependency',None)
  for n,v in [('groupId',group),('artifactId',artifact),('version',version)]:add(d,n,v).text=v

 d=add(ds,'dependency',None)
 for n,v in [('groupId','dev.codex.schubert.quality'),('artifactId','current-qualified-protocol'),('version','0.1.0-SNAPSHOT'),('scope','system'),('systemPath','${pgpt.protocol.jar}')]:add(d,n,v).text=v
 plugins=add(add(root,'build',None),'plugins',None);compiler=next(p for p in ET.parse(R/'pom.xml').getroot().findall('.//'+tag('plugin')) if p.findtext(tag('artifactId'))=='maven-compiler-plugin');plugins.append(copy.deepcopy(compiler));ET.ElementTree(root).write(W/'pom.xml',encoding='unicode',xml_declaration=True)
 stages={'nullaway-compile':c.step('nullaway-compile',[str(maven),'-o','--no-transfer-progress','-Dmaven.repo.local='+str(TC/'m2/repository'),'-Dmaven.test.skip=true','compile'],W,timeout=180)};assert stages['nullaway-compile']['actualExit']==0 and not stages['nullaway-compile']['timedOut']
 (W/'test-classes').mkdir();stages['test-compile']=c.step('test-compile',[str(jdk/'javac'),'--release','25','-g','-proc:none','-implicit:none','-encoding','UTF-8','-Xlint:all','-Werror','-cp',str(W/'target/classes')+':'+':'.join(deps),'-d',str(W/'test-classes'),*[str(R/p) for p in tests]],R);assert stages['test-compile']['actualExit']==0 and not stages['test-compile']['timedOut']
 (W/'component').mkdir();physical={}
 for p in (W/'target/classes').rglob('*.class'):
  n=str(p.relative_to(W/'target/classes'));to=W/'component'/n;to.parent.mkdir(parents=True,exist_ok=True);to.write_bytes(p.read_bytes());physical[n]=sha(p)
 with zipfile.ZipFile(jar) as z:
  for n,h in proto['physicalClassHashes'].items():
   data=z.read(n);assert hashlib.sha256(data).hexdigest()==h;to=W/'component'/n;to.parent.mkdir(parents=True,exist_ok=True);to.write_bytes(data);physical[n]=h
 assert len(physical)==178
 v=dict(actualExit=0,inputHashes=inputs,dependencies=deps,apiMainSources=main,apiTestSources=tests,physicalClassHashes=physical,mainClassHashes={str(p.relative_to(W/'target/classes')):sha(p) for p in (W/'target/classes').rglob('*.class')},testClassHashes={str(p.relative_to(W/'test-classes')):sha(p) for p in (W/'test-classes').rglob('*.class')},currentProto=ref(protoPath),stages=stages,selectedClasses=sorted({x['classname'] for x in expected}),expectedCases=expected,expectedTests=26,newDefinitions=0,compilerConfiguration='EXACT_ROOT_RELEASE25_ERRORPRONE2500_NULLAWAY0141_NO_PROC_NONE_FOR_MAIN',MainSourceSubsetCount=2,MainSafeClosureRebuilt=True,wholeProjectMainRebuilt=False,rootCompilerSha256=hashlib.sha256(ET.tostring(compiler)).hexdigest(),subsetPomSha256=sha(W/'pom.xml'),productTestsExecuted=0,actualHeldClassBinaryAccess=False,fullReportExpectedPartial=True);wr(O/'manifest.json',v);print(json.dumps(dict(actualExit=0,MainSources=2,physicalClasses=178,expectedTests=26)));raise SystemExit(0)
assert phase=='run';m=ld(O/'manifest.json');assert m['inputHashes']==inputs and m['dependencies']==deps
for folder,key in [('component','physicalClassHashes'),('test-classes','testClassHashes')]:assert m[key]=={str(p.relative_to(W/folder)):sha(p) for p in (W/folder).rglob('*.class')}
source=sys.argv[2];assert re.fullmatch('[0-9a-f]{40}',source)
for p,h in inputs.items():assert hashlib.sha256(subprocess.check_output(['git','show',source+':'+p])).hexdigest()==h
pfPath=B/'evidence/PG27954-nq-search26-preflight-v1/manifest.json';pf=ld(pfPath);assert pf['actualExit']==0 and pf['inputHashes']==inputs
U=RUNS/'pg27956-nq-search26-v1';A=B/'evidence/PG27956-nq-search26-v1';assert not U.exists() and not A.exists();U.mkdir();A.mkdir();(U/'tmp').mkdir();c.SLOT=A;session='PG27956-NQ-SEARCH26';agent=TC/'m2/repository/org/jacoco/org.jacoco.agent/0.8.15/org.jacoco.agent-0.8.15-runtime.jar';cli=TC/'org.jacoco.cli-0.8.15-nodeps.jar';runtime=':'.join([str(W/'target/classes'),str(W/'test-classes'),*deps]);cmd=[str(jdk/'java'),'-Djava.io.tmpdir='+str(U/'tmp'),'-Dfile.encoding=UTF-8','-Duser.timezone=Asia/Tokyo','-Djunit.jupiter.execution.parallel.enabled=false','-Djunit.jupiter.extensions.autodetection.enabled=false','-javaagent:'+str(agent)+'=destfile='+str(U/'jacoco.exec')+',sessionid='+session+',append=false','-Xlog:class+init=info:file='+str(U/'class-init.log'),'-jar',str(console),'execute','--disable-banner','--class-path',runtime,*[a for name in m['selectedClasses'] for a in ['--select-class',name]],'--reports-dir',str(U/'xml'),'--fail-if-no-tests','--details','summary'];begin=dict(producerSha256=sha(Path(__file__).resolve()),source=source,productionCoreMain='089a7eb5de7d743e17d5524f012095fa70673f76',inputHashes=inputs,dependencies=deps,physicalClassHashes=m['physicalClassHashes'],expectedCases=expected,expectedTests=26,selectedClasses=m['selectedClasses'],session=session,prepare=ref(O/'manifest.json'),preflight=ref(pfPath),oldExecUnion=False,actualBackendOrHeldClassActions=0);wr(A/'begin.json',begin);stages={'unit':c.step('unit',cmd,U,timeout=180)}
for label,args in [('coverage',['report',str(U/'jacoco.exec'),'--classfiles',str(W/'component'),'--xml',str(U/'coverage.xml')]),('classinfo',['classinfo',str(W/'component')]),('execinfo',['execinfo',str(U/'jacoco.exec')])]:stages[label]=c.step(label,[str(jdk/'java'),'-jar',str(cli),*args],R)
actual=[]
for p in (U/'xml').glob('TEST-*.xml'):
 for x in ET.parse(p).findall('testcase'):actual.append(dict(classname=x.get('classname'),name=x.get('name'),failure=x.find('failure') is not None,error=x.find('error') is not None,skipped=x.find('skipped') is not None))
v=dict(actualExit=stages['unit']['actualExit'],begin=begin,stages=stages,cases=actual,tests=len(actual),failures=sum(x['failure'] for x in actual),errors=sum(x['error'] for x in actual),skipped=sum(x['skipped'] for x in actual),formalUpdated=False,whole451Accepted=False);wr(A/'manifest.json',v);print(json.dumps({k:v[k] for k in ['actualExit','tests','failures','errors','skipped']}));sys.exit(v['actualExit'])
