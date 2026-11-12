"""Closed safe session Main Maven NullAway compile and whole fixtures; no backend/held binary."""
from pathlib import Path
import copy,hashlib,json,os,re,shutil,subprocess,sys,xml.etree.ElementTree as ET,zipfile
import pg9666_pagination_static as c
R=Path.cwd();B=R/'evidence/01_PT/018_NK-OPS-001';TC=R.parent/'toolchain';RUNS=R.parent/'pgpt-runs/PG379';W=RUNS/'pg28014-common-error22-normal-v1';O=B/'evidence/PG28014-common-error22-normal-v1';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ld=lambda p:json.loads(p.read_text());wr=lambda p,j:p.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n');ref=lambda p:dict(path=str(p.relative_to(R)),sha256=sha(p));phase=sys.argv[1]
base='src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/';main=[base+n+'.java' for n in ['security/WebErrorDispatchFilter','error/WebResultMapper','security/package-info']];tests=[base.replace('/main/','/test/')+'security/ErrorControllerPortTest.java',base.replace('/main/','/test/')+'security/ErrorDispatchRestorePortTest.java','tools/quality/architecture/ErrorValueContractTest.java'];totals=[8,8,6];expected=[]
for p,n in zip(tests,totals):
 s=(R/p).read_text();assert not any(x in s for x in ['TemporaryInfrastructureException','FingerprintKeyRing','ResponseSnapshotCodec','WebStartupException','@BeforeAll','@TempDir','ProcessBuilder','DriverManager','DataSource','java.nio.file','Class.forName']);methods=re.findall(r'@Test\s*(?:@Timeout\([^\n]+\)\s*)?void (\w+)\s*\(',s);assert len(methods)==n;expected.extend(dict(classname=re.search(r'package ([a-zA-Z0-9_.]+);',s).group(1)+'.'+Path(p).stem,name=x+'()') for x in methods)
assert len(expected)==22 and len(main)==3
inputs={p:sha(R/p) for p in main+tests+['pom.xml','src/schubert-nk-web/pom.xml']};protoPath=B/'evidence/PG26278-protocol-unicode-main-compile-v1/manifest.json';proto=ld(protoPath);jar=Path(proto['jar']['path']);assert sha(jar)==proto['jar']['sha256'] and all(sha(R/p)==h for p,h in proto['inputHashes'].items());inputs.update(proto['inputHashes']);jdk=TC/'jdk-25.0.4/bin';maven=TC/'m2/wrapper/dists/apache-maven-3.9.12/6068d197/bin/mvn';ann=TC/'m2/repository/org/jspecify/jspecify/1.0.1/jspecify-1.0.1.jar';console=TC/'junit-platform-console-standalone-1.13.4.jar';websdk=[];deps={str(p):sha(p) for p in [jar,ann,console,*websdk]}
cachePath=B/'evidence/PG27742-music-whole14-normal-v1/manifest.json';cache=ld(cachePath);cacheW=RUNS/'pg27742-music-whole14-normal-v1';cachePf=B/'evidence/PG27746-music-whole14-preflight-v1/manifest.json';assert ld(cachePf)['actualExit']==0
cacheNames=['controller/ErrorController','view/ErrorViewModel','error/ProblemViewFactory','security/WebDisplayContext','security/WebCsrfToken','security/WebRequestContext','security/LoginClientAddress','session/SessionPrincipal','session/SessionStoreException','session/InvalidSessionRowException','view/TopBarViewModel','session/package-info'];cacheSources=[base+n+'.java' for n in cacheNames];cacheClasses={n:h for n,h in cache['physicalClassHashes'].items() if any(n=='dev/codex/schubert/nk/web/'+v+'.class' or n.startswith('dev/codex/schubert/nk/web/'+v+'$') for v in cacheNames)}
for p in cacheSources:assert sha(R/p)==cache['inputHashes'][p]
for n,h in cacheClasses.items():assert sha(cacheW/'component'/n)==h
assert len(cacheClasses)==13 and not any(n.endswith('/'+h+'.class') for n in cacheClasses for h in ['TemporaryInfrastructureException','FingerprintKeyRing','ResponseSnapshotCodec','WebStartupException'])
inputs.update({p:cache['inputHashes'][p] for p in cacheSources});rootjar=W/'cached-error-root13.jar';style=B/'evidence/PG28012-common-error22-pre-style-after-v1/manifest.json';sm=ld(style);assert sm['actualExit']==0 and sm['checkstyleFindings']==0 and not sm['rawFindings'] and all(v['actualExit']==0 and not v['timedOut'] for v in sm['stages'].values());assert all(sm['inputHashes'][p]==inputs[p] for p in tests);sdkPaths=[Path(p) for p in cache['dependencies'] if p.startswith(str(TC/'m2/repository')) and p!=str(ann)];assert len(sdkPaths)==len(set(sdkPaths));deps.update({str(p):sha(p) for p in sdkPaths})
if phase=='prepare':
 assert not W.exists() and not O.exists();W.mkdir();O.mkdir();c.SLOT=O
 with zipfile.ZipFile(rootjar,'w',compression=zipfile.ZIP_STORED) as archive:
  for n,h in cacheClasses.items():
   data=(cacheW/'component'/n).read_bytes();assert hashlib.sha256(data).hexdigest()==h;archive.writestr(n,data)
 deps[str(rootjar)]=sha(rootjar)
 for p in main:
  assert not any(x in (R/p).read_text() for x in ['TemporaryInfrastructureException','FingerprintKeyRing','ResponseSnapshotCodec','WebStartupException','java.nio.file','java.net.Socket','DataSource']);to=W/'src/main/java'/p.split('/src/main/java/')[1];to.parent.mkdir(parents=True,exist_ok=True);to.write_bytes((R/p).read_bytes());assert sha(to)==inputs[p]
 ns='http://maven.apache.org/POM/4.0.0';ET.register_namespace('',ns);tag=lambda n:'{'+ns+'}'+n;root=ET.Element(tag('project'));add=lambda e,n,v:ET.SubElement(e,tag(n))
 for n,v in [('modelVersion','4.0.0'),('groupId','dev.codex.schubert.quality'),('artifactId','common-error22-safe-subset'),('version','0.1.0-SNAPSHOT')]:add(root,n,v).text=v
 props=add(root,'properties',None)
 for n,v in [('maven.compiler.release','25'),('project.build.sourceEncoding','UTF-8'),('error-prone.version','2.50.0'),('nullaway.version','0.14.1'),('pgpt.protocol.jar',str(jar))]:add(props,n,v).text=v
 ds=add(root,'dependencies',None)
 for group,artifact,version in [('org.jspecify','jspecify','1.0.1')]:
  d=add(ds,'dependency',None)
  for n,v in [('groupId',group),('artifactId',artifact),('version',version)]:add(d,n,v).text=v

 d=add(ds,'dependency',None)
 for n,v in [('groupId','dev.codex.schubert.quality'),('artifactId','current-qualified-protocol'),('version','0.1.0-SNAPSHOT'),('scope','system'),('systemPath','${pgpt.protocol.jar}')]:add(d,n,v).text=v
 d=add(ds,'dependency',None)
 for n,v in [('groupId','dev.codex.schubert.quality'),('artifactId','qualified-error-root13'),('version','1'),('scope','system'),('systemPath',str(rootjar))]:add(d,n,v).text=v
 for index,path in enumerate(sdkPaths):
  d=add(ds,'dependency',None)
  for n,v in [('groupId','dev.codex.schubert.quality'),('artifactId','qualified-sdk-'+str(index)),('version','1'),('scope','system'),('systemPath',str(path))]:add(d,n,v).text=v
 plugins=add(add(root,'build',None),'plugins',None);compiler=next(p for p in ET.parse(R/'pom.xml').getroot().findall('.//'+tag('plugin')) if p.findtext(tag('artifactId'))=='maven-compiler-plugin');plugins.append(copy.deepcopy(compiler));ET.ElementTree(root).write(W/'pom.xml',encoding='unicode',xml_declaration=True)
 stages={'nullaway-compile':c.step('nullaway-compile',[str(maven),'-o','--no-transfer-progress','-Dmaven.repo.local='+str(TC/'m2/repository'),'-Dmaven.test.skip=true','compile'],W,timeout=180)};assert stages['nullaway-compile']['actualExit']==0 and not stages['nullaway-compile']['timedOut']
 (W/'test-classes').mkdir();stages['test-compile']=c.step('test-compile',[str(jdk/'javac'),'--release','25','-g','-proc:none','-implicit:none','-encoding','UTF-8','-Xlint:all','-Werror','-cp',str(W/'target/classes')+':'+':'.join(deps),'-d',str(W/'test-classes'),*[str(R/p) for p in tests]],R);assert stages['test-compile']['actualExit']==0 and not stages['test-compile']['timedOut']
 (W/'component').mkdir();physical={}
 for p in (W/'target/classes').rglob('*.class'):
  n=str(p.relative_to(W/'target/classes'));to=W/'component'/n;to.parent.mkdir(parents=True,exist_ok=True);to.write_bytes(p.read_bytes());physical[n]=sha(p)
 with zipfile.ZipFile(jar) as z:
  for n,h in proto['physicalClassHashes'].items():
   data=z.read(n);assert hashlib.sha256(data).hexdigest()==h;to=W/'component'/n;to.parent.mkdir(parents=True,exist_ok=True);to.write_bytes(data);physical[n]=h
 with zipfile.ZipFile(rootjar) as archive:
  for n,h in cacheClasses.items():
   assert n not in physical;data=archive.read(n);assert hashlib.sha256(data).hexdigest()==h;to=W/'component'/n;to.parent.mkdir(parents=True,exist_ok=True);to.write_bytes(data);physical[n]=h
 assert len(physical)==193
 v=dict(actualExit=0,inputHashes=inputs,dependencies=deps,apiMainSources=main,apiTestSources=tests,physicalClassHashes=physical,mainClassHashes={str(p.relative_to(W/'target/classes')):sha(p) for p in (W/'target/classes').rglob('*.class')},testClassHashes={str(p.relative_to(W/'test-classes')):sha(p) for p in (W/'test-classes').rglob('*.class')},currentProto=ref(protoPath),reusedRootPrepare=ref(cachePath),reusedRootPreflight=ref(cachePf),reusedRootSourceCount=12,reusedRootPhysicalCount=13,preliminaryStyle=ref(style),stages=stages,selectedClasses=sorted({x['classname'] for x in expected}),expectedCases=expected,expectedTests=22,newDefinitions=0,compilerConfiguration='EXACT_ROOT_RELEASE25_ERRORPRONE2500_NULLAWAY0141_NO_PROC_NONE_FOR_MAIN',MainSourceSubsetCount=3,MainSafeClosureRebuilt=True,wholeProjectMainRebuilt=False,rootCompilerSha256=hashlib.sha256(ET.tostring(compiler)).hexdigest(),subsetPomSha256=sha(W/'pom.xml'),productTestsExecuted=0,actualHeldClassBinaryAccess=False,fullReportExpectedPartial=True);wr(O/'manifest.json',v);print(json.dumps(dict(actualExit=0,MainSources=3,physicalClasses=193,expectedTests=22)));raise SystemExit(0)
assert phase=='run';deps[str(rootjar)]=sha(rootjar);m=ld(O/'manifest.json');assert m['inputHashes']==inputs and m['dependencies']==deps
for folder,key in [('component','physicalClassHashes'),('test-classes','testClassHashes')]:assert m[key]=={str(p.relative_to(W/folder)):sha(p) for p in (W/folder).rglob('*.class')}
source=sys.argv[2];assert re.fullmatch('[0-9a-f]{40}',source)
for p,h in inputs.items():assert hashlib.sha256(subprocess.check_output(['git','show',source+':'+p])).hexdigest()==h
pfPath=B/'evidence/PG28018-common-error22-preflight-v1/manifest.json';pf=ld(pfPath);assert pf['actualExit']==0 and pf['inputHashes']==inputs
U=RUNS/'pg28022-common-error22-v1';A=B/'evidence/PG28022-common-error22-v1';assert not U.exists() and not A.exists();U.mkdir();A.mkdir();(U/'tmp').mkdir();c.SLOT=A;session='PG28022-COMMON-ERROR22';agent=TC/'m2/repository/org/jacoco/org.jacoco.agent/0.8.15/org.jacoco.agent-0.8.15-runtime.jar';cli=TC/'org.jacoco.cli-0.8.15-nodeps.jar';runtime=':'.join([str(W/'target/classes'),str(W/'test-classes'),*deps]);cmd=[str(jdk/'java'),'-Djava.io.tmpdir='+str(U/'tmp'),'-Dfile.encoding=UTF-8','-Duser.timezone=Asia/Tokyo','-Djunit.jupiter.execution.parallel.enabled=false','-Djunit.jupiter.extensions.autodetection.enabled=false','-javaagent:'+str(agent)+'=destfile='+str(U/'jacoco.exec')+',sessionid='+session+',append=false','-Xlog:class+init=info:file='+str(U/'class-init.log'),'-jar',str(console),'execute','--disable-banner','--class-path',runtime,*[a for name in m['selectedClasses'] for a in ['--select-class',name]],'--reports-dir',str(U/'xml'),'--fail-if-no-tests','--details','summary'];begin=dict(producerSha256=sha(Path(__file__).resolve()),source=source,productionCoreMain='e16500d7df27a55082f8c69a68c510414167dbb4',inputHashes=inputs,dependencies=deps,physicalClassHashes=m['physicalClassHashes'],expectedCases=expected,expectedTests=22,selectedClasses=m['selectedClasses'],session=session,prepare=ref(O/'manifest.json'),preflight=ref(pfPath),oldExecUnion=False,actualBackendOrHeldClassActions=0);wr(A/'begin.json',begin);stages={'unit':c.step('unit',cmd,U,timeout=180)}
for label,args in [('coverage',['report',str(U/'jacoco.exec'),'--classfiles',str(W/'component'),'--xml',str(U/'coverage.xml')]),('classinfo',['classinfo',str(W/'component')]),('execinfo',['execinfo',str(U/'jacoco.exec')])]:stages[label]=c.step(label,[str(jdk/'java'),'-jar',str(cli),*args],R)
actual=[]
for p in (U/'xml').glob('TEST-*.xml'):
 for x in ET.parse(p).findall('testcase'):actual.append(dict(classname=x.get('classname'),name=x.get('name'),failure=x.find('failure') is not None,error=x.find('error') is not None,skipped=x.find('skipped') is not None))
v=dict(actualExit=stages['unit']['actualExit'],begin=begin,stages=stages,cases=actual,tests=len(actual),failures=sum(x['failure'] for x in actual),errors=sum(x['error'] for x in actual),skipped=sum(x['skipped'] for x in actual),formalUpdated=False,whole451Accepted=False);wr(A/'manifest.json',v);print(json.dumps({k:v[k] for k in ['actualExit','tests','failures','errors','skipped']}));sys.exit(v['actualExit'])
