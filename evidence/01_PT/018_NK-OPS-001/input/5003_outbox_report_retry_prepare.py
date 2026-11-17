"""Closed safe session Main Maven NullAway compile and whole fixtures; no backend/held binary."""
from pathlib import Path
import copy,hashlib,json,os,re,shutil,subprocess,sys,xml.etree.ElementTree as ET,zipfile
import pg9666_pagination_static as c
from pgpt_spotbugs_contract import canonical_plugin
R=Path.cwd();B=R/'evidence/01_PT/018_NK-OPS-001';TC=R.parent/'toolchain';RUNS=R.parent/'pgpt-runs/PG379';W=RUNS/'pg38288-outbox-report-retry-prepare-v1';O=B/'evidence/PG38288-outbox-report-retry-prepare-v1';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ld=lambda p:json.loads(p.read_text());wr=lambda p,j:p.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n');ref=lambda p:dict(path=str(p.relative_to(R)),sha256=sha(p));phase=sys.argv[1]
start=ld(next((R/'documents/400_PGPT/470_PMO/601_WBS66短期実行_20261117').glob('221_*')))
main=[item['path'] for item in start['mains'].values()]
tests=[v['path'] for v in start['tests'].values()]
tests.append(tests[0].replace('OutboxPolicyTest','OutboxRetryScheduleCatalogTest'))
totals=[4,3,3,1]
resources=[]
expected=[]
for p,n in zip(tests,totals):
 s=(R/p).read_text();assert not any(x in s for x in ['TemporaryInfrastructureException','FingerprintKeyRing','ResponseSnapshotCodec','WebStartupException','@BeforeAll','@TempDir','ProcessBuilder','DriverManager','DataSource','Class.forName','setPosixFilePermissions','setOwner','createLink','createSymbolicLink']);methods=re.findall(r'@Test\s*(?:@Timeout\([^\n]+\)\s*)?void (\w+)\s*\(',s);assert len(methods)==n;expected.extend(dict(classname=re.search(r'package ([a-zA-Z0-9_.]+);',s).group(1)+'.'+Path(p).stem,name=x+'()') for x in methods)
assert len(expected)==11 and len(main)==3
inputs={p:sha(R/p) for p in main+tests+resources+['pom.xml','src/schubert-nk-api/pom.xml']};jdk=TC/'jdk-25.0.4/bin';maven=TC/'m2/wrapper/dists/apache-maven-3.9.12/6068d197/bin/mvn';ann=TC/'m2/repository/org/jspecify/jspecify/1.0.1/jspecify-1.0.1.jar';console=TC/'junit-platform-console-standalone-1.13.4.jar';sdkPaths=[];deps={str(p):sha(p) for p in [ann,console,*sdkPaths]}
assert all(inputs[item['path']]==item['sha256'] for item in (*start['mains'].values(),*start['tests'].values()))
if phase=='prepare':
 assert not W.exists() and not O.exists();W.mkdir();O.mkdir();c.SLOT=O
 for p in resources:
  target=W/'test-classes'/p.split('/src/test/resources/')[1];target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes((R/p).read_bytes());assert sha(target)==inputs[p]
 for p in main:
  assert not any(x in (R/p).read_text() for x in ['TemporaryInfrastructureException','FingerprintKeyRing','ResponseSnapshotCodec','WebStartupException','java.net.Socket','DataSource']);to=W/'src/main/java'/p.split('/src/main/java/')[1];to.parent.mkdir(parents=True,exist_ok=True);to.write_bytes((R/p).read_bytes());assert sha(to)==inputs[p]
 ns='http://maven.apache.org/POM/4.0.0';ET.register_namespace('',ns);tag=lambda n:'{'+ns+'}'+n;root=ET.Element(tag('project'));add=lambda e,n,v:ET.SubElement(e,tag(n))
 for n,v in [('modelVersion','4.0.0'),('groupId','dev.codex.schubert.quality'),('artifactId','outbox-report-retry-safe-subset'),('version','0.1.0-SNAPSHOT')]:add(root,n,v).text=v
 props=add(root,'properties',None)
 for n,v in [('maven.compiler.release','25'),('project.build.sourceEncoding','UTF-8'),('error-prone.version','2.50.0'),('nullaway.version','0.14.1'),('pgpt.profile','closed-outbox-report-retry-jdk-only')]:add(props,n,v).text=v
 ds=add(root,'dependencies',None)
 for group,artifact,version in [('org.jspecify','jspecify','1.0.1')]:
  d=add(ds,'dependency',None)
  for n,v in [('groupId',group),('artifactId',artifact),('version',version)]:add(d,n,v).text=v


 for index,path in enumerate(sdkPaths):
  d=add(ds,'dependency',None)
  for n,v in [('groupId','dev.codex.schubert.quality'),('artifactId','closed-sdk-'+str(index)),('version','1'),('scope','system'),('systemPath',str(path))]:add(d,n,v).text=v

 plugins=add(add(root,'build',None),'plugins',None);compiler=next(p for p in ET.parse(R/'pom.xml').getroot().findall('.//'+tag('plugin')) if p.findtext(tag('artifactId'))=='maven-compiler-plugin');plugins.append(copy.deepcopy(compiler));plugins.append(copy.deepcopy(canonical_plugin((R/'src/schubert-nk-api/pom.xml').read_bytes())));ET.ElementTree(root).write(W/'pom.xml',encoding='unicode',xml_declaration=True)
 stages={'nullaway-compile':c.step('nullaway-compile',[str(maven),'-o','--no-transfer-progress','-Dmaven.repo.local='+str(TC/'m2/repository'),'-Dmaven.test.skip=true','compile'],W,timeout=180)};assert stages['nullaway-compile']['actualExit']==0 and not stages['nullaway-compile']['timedOut']
 (W/'test-classes').mkdir();stages['test-compile']=c.step('test-compile',[str(jdk/'javac'),'--release','25','-g','-proc:none','-implicit:none','-encoding','UTF-8','-Xlint:all','-Werror','-cp',str(W/'target/classes')+':'+':'.join(deps),'-d',str(W/'test-classes'),*[str(R/p) for p in tests]],R);assert stages['test-compile']['actualExit']==0 and not stages['test-compile']['timedOut']
 (W/'component').mkdir();physical={}
 for p in (W/'target/classes').rglob('*.class'):
  n=str(p.relative_to(W/'target/classes'));to=W/'component'/n;to.parent.mkdir(parents=True,exist_ok=True);to.write_bytes(p.read_bytes());physical[n]=sha(p)
 assert len(physical)==3
main_bytes={p.relative_to(W/'target/classes').as_posix():sha(p) for p in (W/'target/classes').rglob('*.class')}
assert main_bytes==physical
test_bytes={p.relative_to(W/'test-classes').as_posix():sha(p) for p in (W/'test-classes').rglob('*.class')}
assert all(any(key.endswith('/'+name.rsplit('.',1)[-1]+'.class') for key in test_bytes) for name in {x['classname'] for x in expected})
v=dict(actualExit=0,inputHashes=inputs,dependencies=deps,apiMainSources=main,apiTestSources=tests,
       physicalClassHashes=physical,mainClassHashes=main_bytes,testClassHashes=test_bytes,
       resourceCopies={p:sha(W/'test-classes'/p.split('/src/test/resources/')[1]) for p in resources},
       stages=stages,selectedClasses=sorted({x['classname'] for x in expected}),expectedCases=expected,
       expectedTests=11,newDefinitions=1,compilerConfiguration='EXACT_ROOT_RELEASE25_ERRORPRONE2500_NULLAWAY0141',
       MainSourceSubsetCount=3,MainSafeClosureRebuilt=True,wholeProjectMainRebuilt=False,
       rootCompilerSha256=hashlib.sha256(ET.tostring(compiler)).hexdigest(),subsetPomSha256=sha(W/'pom.xml'),
       productTestsExecuted=0,actualHeldClassBinaryAccess=False,fullReportExpectedPartial=True,
       prepareWrapperActualExit=0,
       wrapperFailure=None,
       compileReexecutedForRecovery=False)
wr(O/'manifest.json',v)
print(json.dumps(dict(actualExit=0,MainSources=len(main),physicalClasses=len(physical),expectedTests=len(expected))))
