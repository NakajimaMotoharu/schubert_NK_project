"""Safe storage graph-only Root compiler/profile; no directory/native or held payloads."""
from pathlib import Path
import copy,hashlib,json,re,subprocess,sys,xml.etree.ElementTree as ET
import pg9666_pagination_static as c
R=Path.cwd();B=R/'evidence/01_PT/018_NK-OPS-001';TC=R.parent/'toolchain';RUNS=R.parent/'pgpt-runs/PG379';W=RUNS/'pg27688-storage-public-graph-v1';O=B/'evidence/PG27689-storage-graph-test-import-v2'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ld=lambda p:json.loads(p.read_text());wr=lambda p,x:p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n');ref=lambda p:dict(path=str(p.relative_to(R)),sha256=sha(p));phase=sys.argv[1];assert phase=='run'
base='src/schubert-nk-storage/src/';main=[base+'main/java/dev/codex/schubert/nk/storage/'+n+'.java' for n in ['StorageIoException','package-info']];test=base+'test/java/dev/codex/schubert/nk/storage/StorageFailureGraphTest.java';allpaths=main+[test,'pom.xml','src/schubert-nk-storage/pom.xml'];inputs={p:sha(R/p) for p in allpaths}
for p in main+[test]:assert not any(s in (R/p).read_text() for s in ['DirectoryCalls','ResourceScope','java.nio.file','ProcessBuilder','Class.forName','TemporaryInfrastructureException','FingerprintKeyRing','ResponseSnapshotCodec','WebStartupException','DriverManager','DataSource'])
methods=re.findall(r'@Test\s*void (\w+)\(', (R/test).read_text());assert len(methods)==4
selected='dev.codex.schubert.nk.storage.StorageFailureGraphTest';expected=[dict(classname=selected,name=n+'()') for n in methods]
jdk=TC/'jdk-25.0.4/bin';maven=TC/'m2/wrapper/dists/apache-maven-3.9.12/6068d197/bin/mvn';ann=TC/'m2/repository/org/jspecify/jspecify/1.0.1/jspecify-1.0.1.jar';console=TC/'junit-platform-console-standalone-1.13.4.jar';deps={str(p):sha(p) for p in [ann,console]}
if phase=='prepare':
 assert not W.exists() and not O.exists();W.mkdir();O.mkdir();c.SLOT=O
 for p in main:
  to=W/'src/main/java'/p.split('/src/main/java/')[1];to.parent.mkdir(parents=True,exist_ok=True);to.write_bytes((R/p).read_bytes())
 ns='http://maven.apache.org/POM/4.0.0';ET.register_namespace('',ns);tag=lambda n:'{'+ns+'}'+n;root=ET.Element(tag('project'));add=lambda e,n,v:ET.SubElement(e,tag(n))
 for n,v in [('modelVersion','4.0.0'),('groupId','dev.codex.schubert.quality'),('artifactId','storage-public-graph-source-subset'),('version','0.1.0-SNAPSHOT')]:add(root,n,v).text=v
 props=add(root,'properties',None)
 for n,v in [('maven.compiler.release','25'),('project.build.sourceEncoding','UTF-8'),('error-prone.version','2.50.0'),('nullaway.version','0.14.1')]:add(props,n,v).text=v
 ds=add(root,'dependencies',None);d=add(ds,'dependency',None)
 for n,v in [('groupId','org.jspecify'),('artifactId','jspecify'),('version','1.0.1')]:add(d,n,v).text=v
 plugins=add(add(root,'build',None),'plugins',None);compiler=next(p for p in ET.parse(R/'pom.xml').getroot().findall('.//'+tag('plugin')) if p.findtext(tag('artifactId'))=='maven-compiler-plugin');plugins.append(copy.deepcopy(compiler));ET.ElementTree(root).write(W/'pom.xml',encoding='unicode',xml_declaration=True)
 stages={'nullaway-compile':c.step('nullaway-compile',[str(maven),'-o','--no-transfer-progress','-Dmaven.repo.local='+str(TC/'m2/repository'),'-Dmaven.test.skip=true','compile'],W,timeout=180)};assert stages['nullaway-compile']['actualExit']==0 and not stages['nullaway-compile']['timedOut']
 (W/'test-classes').mkdir();stages['test-compile']=c.step('test-compile',[str(jdk/'javac'),'--release','25','-g','-proc:none','-implicit:none','-encoding','UTF-8','-Xlint:all','-Werror','-cp',str(W/'target/classes')+':'+':'.join(deps),'-d',str(W/'test-classes'),str(R/test)],R);assert stages['test-compile']['actualExit']==0
 physical={str(p.relative_to(W/'target/classes')):sha(p) for p in (W/'target/classes').rglob('*.class')};assert len(physical)==3
 v=dict(actualExit=0,inputHashes=inputs,dependencies=deps,mainSources=main,testSources=[test],physicalClassHashes=physical,testClassHashes={str(p.relative_to(W/'test-classes')):sha(p) for p in (W/'test-classes').rglob('*.class')},selectedClasses=[selected],expectedCases=expected,expectedTests=4,stages=stages,rootCompilerSha256=hashlib.sha256(ET.tostring(compiler)).hexdigest(),rootCompilerUnchanged=True,MainSources=2,productTestsExecuted=0,actualBackendNativeOrHeldActions=0,subsetPomSha256=sha(W/'pom.xml'));wr(O/'manifest.json',v);print(json.dumps(dict(actualExit=0,MainSources=2,physical=3,expectedTests=4)));raise SystemExit(0)
assert phase=='run';m=ld(O/'manifest.json');assert m['inputHashes']==inputs and m['dependencies']==deps
for folder,key in [('target/classes','physicalClassHashes'),('test-classes-v2','testClassHashes')]:assert m[key]=={str(p.relative_to(W/folder)):sha(p) for p in (W/folder).rglob('*.class')}
source=sys.argv[2];assert re.fullmatch('[0-9a-f]{40}',source)
for p,h in inputs.items():assert hashlib.sha256(subprocess.check_output(['git','show',source+':'+p])).hexdigest()==h
pf=B/'evidence/PG27692-storage-graph-preflight-v1/manifest.json';assert ld(pf)['actualExit']==0 and ld(pf)['inputHashes']==inputs
U=RUNS/'pg27694-storage-public-graph-v1';A=B/'evidence/PG27694-storage-public-graph-v1';assert not U.exists() and not A.exists();U.mkdir();A.mkdir();(U/'tmp').mkdir();c.SLOT=A;session='PG27694-STORAGE-PUBLIC-GRAPH4';agent=TC/'m2/repository/org/jacoco/org.jacoco.agent/0.8.15/org.jacoco.agent-0.8.15-runtime.jar';cli=TC/'org.jacoco.cli-0.8.15-nodeps.jar'
cmd=[str(jdk/'java'),'-Djava.io.tmpdir='+str(U/'tmp'),'-Dfile.encoding=UTF-8','-Duser.timezone=Asia/Tokyo','-Djunit.jupiter.execution.parallel.enabled=false','-Djunit.jupiter.extensions.autodetection.enabled=false','-javaagent:'+str(agent)+'=destfile='+str(U/'jacoco.exec')+',sessionid='+session+',append=false','-Xlog:class+init=info:file='+str(U/'class-init.log'),'-jar',str(console),'execute','--disable-banner','--class-path',str(W/'target/classes')+':'+str(W/'test-classes-v2')+':'+str(ann),'--select-class',selected,'--reports-dir',str(U/'xml'),'--fail-if-no-tests','--details','summary']
begin=dict(source=source,productionCoreMain='edaf641333266660ec79a6e070c98b7a79bbccac',inputHashes=inputs,dependencies=deps,physicalClassHashes=m['physicalClassHashes'],expectedCases=expected,expectedTests=4,selectedClasses=[selected],session=session,prepare=ref(O/'manifest.json'),preflight=ref(pf),actualBackendNativeOrHeldActions=0,oldExecUnion=False);wr(A/'begin.json',begin);stages={'unit':c.step('unit',cmd,U,timeout=90)}
for label,args in [('coverage',['report',str(U/'jacoco.exec'),'--classfiles',str(W/'target/classes'),'--xml',str(U/'coverage.xml')]),('classinfo',['classinfo',str(W/'target/classes')]),('execinfo',['execinfo',str(U/'jacoco.exec')])]:stages[label]=c.step(label,[str(jdk/'java'),'-jar',str(cli),*args],R)
cases=[]
for p in (U/'xml').glob('TEST-*.xml'):
 for x in ET.parse(p).findall('testcase'):cases.append(dict(classname=x.get('classname'),name=x.get('name'),failure=x.find('failure') is not None,error=x.find('error') is not None,skipped=x.find('skipped') is not None))
v=dict(actualExit=stages['unit']['actualExit'],begin=begin,stages=stages,cases=cases,tests=len(cases),failures=sum(x['failure'] for x in cases),errors=sum(x['error'] for x in cases),skipped=sum(x['skipped'] for x in cases),formalUpdated=False,whole451Accepted=False);wr(A/'manifest.json',v);print(json.dumps({k:v[k] for k in ['actualExit','tests','failures','errors','skipped']}));sys.exit(v['actualExit'])
