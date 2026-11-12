"""Original intact Music actual-MVC six and projection eight; closed host-only source snapshot."""
from pathlib import Path
import copy,hashlib,json,re,shutil,subprocess,sys,xml.etree.ElementTree as ET,zipfile
import pg9666_pagination_static as c
R=Path.cwd();B=R/'evidence/01_PT/018_NK-OPS-001';TC=R.parent/'toolchain';RUNS=R.parent/'pgpt-runs/PG379';W=RUNS/'pg27742-music-whole14-normal-v1';O=B/'evidence/PG27742-music-whole14-normal-v1';ld=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ref=lambda p:dict(path=str(p.relative_to(R)),sha256=sha(p));wr=lambda p,x:p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n');phase=sys.argv[1]
closure=ld(B/'evidence/PG27740-music-template-whole14-closure-before-v1/manifest.json');main=list(closure['newSafeMainInputHashes']);priorPath=R/closure['reusedRootTwenty']['path'];prior=ld(priorPath);oldW=RUNS/'pg27600-trace-menu24-normal-v1';assert sha(priorPath)==closure['reusedRootTwenty']['sha256'];assert all(sha(R/p)==h for p,h in closure['reusedRootMainSourceHashes'].items());assert prior['mainClassHashes']=={str(p.relative_to(oldW/'target/classes')):sha(p) for p in (oldW/'target/classes').rglob('*.class')}
tests=['src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/view/'+n+'.java' for n in ['MusicHierarchyTemplateTest','MusicHierarchyViewModelTest']];totals=[6,8];expected=[]
for p,n in zip(tests,totals):
 s=(R/p).read_text();assert not any(x in s for x in ['@BeforeAll','DataSource','DriverManager','WebLogDatabaseFixture','ProcessBuilder','Class.forName','TemporaryInfrastructureException','FingerprintKeyRing','ResponseSnapshotCodec','WebStartupException']);methods=re.findall(r'@Test\s*void (\w+)\(',s);assert len(methods)==n;expected.extend(dict(classname=p.split('/src/test/java/')[1][:-5].replace('/','.'),name=x+'()') for x in methods)
assert len(expected)==14 and len(main)==9
resources=['src/schubert-nk-web/src/main/resources/'+p for p in ['templates/music.html','templates/music-sections.html','templates/fragments/layout.html','static/css/schubert.css']];inputs={p:sha(R/p) for p in [*main,*tests,*resources,'pom.xml','src/schubert-nk-web/pom.xml']};inputs.update(closure['reusedRootMainSourceHashes'])
protoPath=B/'evidence/PG26278-protocol-unicode-main-compile-v1/manifest.json';proto=ld(protoPath);jar=Path(proto['jar']['path']);assert sha(jar)==proto['jar']['sha256'] and all(sha(R/p)==h for p,h in proto['inputHashes'].items());inputs.update(proto['inputHashes']);sdk={p:h for p,h in prior['dependencies'].items() if 'schubert-nk-' not in p}
oldView=ld(R/'evidence/01_PT/015_NK-WEB-001/evidence/PG24370-pure-view-seven-bounded-sixtyfour-independent-v1/compile-manifest.json')
for p,h in oldView['dependencies'].items():
 if 'schubert-nk-' not in p and Path(p).name!='commons-logging-1.4.0.jar':sdk[p]=h
for group,artifact,version in [('org/springframework/security','spring-security-web','7.1.1'),('io/micrometer','micrometer-observation','1.16.7'),('io/micrometer','micrometer-commons','1.16.7')]:
 p=TC/'m2/repository'/group/artifact/version/(artifact+'-'+version+'.jar');sdk[str(p)]=sha(p)
assert all(sha(Path(p))==h for p,h in sdk.items())
jdk=TC/'jdk-25.0.4/bin';maven=TC/'m2/wrapper/dists/apache-maven-3.9.12/6068d197/bin/mvn';console=TC/'junit-platform-console-standalone-1.13.4.jar';rootjar=W/'root-twenty-safe23.jar';deps={str(jar):sha(jar),**sdk}
if phase=='prepare':
 assert not W.exists() and not O.exists();W.mkdir();O.mkdir();c.SLOT=O
 with zipfile.ZipFile(rootjar,'w',compression=zipfile.ZIP_STORED) as z:
  for n,h in prior['mainClassHashes'].items():
   assert not any(n.endswith('/'+x+'.class') for x in ['TemporaryInfrastructureException','FingerprintKeyRing','ResponseSnapshotCodec','WebStartupException']);data=(oldW/'target/classes'/n).read_bytes();assert hashlib.sha256(data).hexdigest()==h;z.writestr(n,data)
 for p in main:
  to=W/'src/main/java'/p.split('/src/main/java/')[1];to.parent.mkdir(parents=True,exist_ok=True);to.write_bytes((R/p).read_bytes())
 for p in resources:
  rel=p.split('/src/main/resources/')[1]
  for base in [W/'resources',W/'web-fixture/src/main/resources']:
   to=base/rel;to.parent.mkdir(parents=True,exist_ok=True);to.write_bytes((R/p).read_bytes())
 deps[str(rootjar)]=sha(rootjar);ns='http://maven.apache.org/POM/4.0.0';ET.register_namespace('',ns);tag=lambda n:'{'+ns+'}'+n;root=ET.Element(tag('project'));add=lambda e,n,v:ET.SubElement(e,tag(n))
 for n,v in [('modelVersion','4.0.0'),('groupId','dev.codex.schubert.quality'),('artifactId','music-whole14-safe-source'),('version','0.1.0-SNAPSHOT')]:add(root,n,v).text=v
 props=add(root,'properties',None)
 for n,v in [('maven.compiler.release','25'),('project.build.sourceEncoding','UTF-8'),('error-prone.version','2.50.0'),('nullaway.version','0.14.1')]:add(props,n,v).text=v
 ds=add(root,'dependencies',None)
 for index,(p,h) in enumerate(deps.items()):
  if p==str(console):continue
  d=add(ds,'dependency',None)
  for n,v in [('groupId','dev.codex.schubert.quality.cached'),('artifactId','qualified-sdk-'+str(index)),('version','1'),('scope','system'),('systemPath',p)]:add(d,n,v).text=v
 plugins=add(add(root,'build',None),'plugins',None);compiler=next(p for p in ET.parse(R/'pom.xml').getroot().findall('.//'+tag('plugin')) if p.findtext(tag('artifactId'))=='maven-compiler-plugin');plugins.append(copy.deepcopy(compiler));ET.ElementTree(root).write(W/'pom.xml',encoding='unicode',xml_declaration=True)
 stages={'nullaway-compile':c.step('nullaway-compile',[str(maven),'-o','--no-transfer-progress','-Dmaven.repo.local='+str(TC/'m2/repository'),'-Dmaven.test.skip=true','compile'],W,timeout=180)};assert stages['nullaway-compile']['actualExit']==0 and not stages['nullaway-compile']['timedOut']
 (W/'test-classes').mkdir();stages['test-compile']=c.step('test-compile',[str(jdk/'javac'),'--release','25','-g','-proc:none','-implicit:none','-encoding','UTF-8','-Xlint:all','-Werror','-cp',str(W/'target/classes')+':'+':'.join(deps),'-d',str(W/'test-classes'),*[str(R/p) for p in tests]],R);assert stages['test-compile']['actualExit']==0
 (W/'component').mkdir();physical={}
 for p in (W/'target/classes').rglob('*.class'):
  n=str(p.relative_to(W/'target/classes'));to=W/'component'/n;to.parent.mkdir(parents=True,exist_ok=True);to.write_bytes(p.read_bytes());physical[n]=sha(p)
 assert len(physical)==12
 for sourceJar,expectedClasses in [(rootjar,prior['mainClassHashes']),(jar,proto['physicalClassHashes'])]:
  with zipfile.ZipFile(sourceJar) as z:
   for n,h in expectedClasses.items():
    assert n not in physical;data=z.read(n);assert hashlib.sha256(data).hexdigest()==h;to=W/'component'/n;to.parent.mkdir(parents=True,exist_ok=True);to.write_bytes(data);physical[n]=h
 assert len(physical)==211
 v=dict(actualExit=0,inputHashes=inputs,dependencies=deps,apiMainSources=main,apiTestSources=tests,resourceSources=resources,reusedRootTwenty=ref(priorPath),reusedRootMainSources=20,reusedRootMainClasses=23,physicalClassHashes=physical,mainClassHashes={str(p.relative_to(W/'target/classes')):sha(p) for p in (W/'target/classes').rglob('*.class')},testClassHashes={str(p.relative_to(W/'test-classes')):sha(p) for p in (W/'test-classes').rglob('*.class')},selectedClasses=sorted({x['classname'] for x in expected}),expectedCases=expected,expectedTests=14,newDefinitions=0,stages=stages,rootCompilerSha256=hashlib.sha256(ET.tostring(compiler)).hexdigest(),subsetPomSha256=sha(W/'pom.xml'),MainSourceSubsetCount=9,MainSafeClosureRebuilt=True,productTestsExecuted=0,actualHeldOrBackendActions=0,fullReportExpectedPartial=True);wr(O/'manifest.json',v);print(json.dumps(dict(actualExit=0,newMainSources=9,newPhysical=12,reusedRoot=23,fullPhysical=211,expectedTests=14)));raise SystemExit(0)
assert phase=='run';deps[str(rootjar)]=sha(rootjar);m=ld(O/'manifest.json');assert m['inputHashes']==inputs and m['dependencies']==deps
for folder,key in [('component','physicalClassHashes'),('target/classes','mainClassHashes'),('test-classes','testClassHashes')]:assert m[key]=={str(p.relative_to(W/folder)):sha(p) for p in (W/folder).rglob('*.class')}
source=sys.argv[2];assert re.fullmatch('[0-9a-f]{40}',source)
for p,h in inputs.items():assert hashlib.sha256(subprocess.check_output(['git','show',source+':'+p])).hexdigest()==h
pf=B/'evidence/PG27746-music-whole14-preflight-v1/manifest.json';assert ld(pf)['actualExit']==0 and ld(pf)['inputHashes']==inputs
U=RUNS/'pg27748-music-whole14-v1';A=B/'evidence/PG27748-music-whole14-v1';assert not U.exists() and not A.exists();U.mkdir();A.mkdir();(U/'tmp').mkdir();c.SLOT=A;session='PG27748-MUSIC-WHOLE14';agent=TC/'m2/repository/org/jacoco/org.jacoco.agent/0.8.15/org.jacoco.agent-0.8.15-runtime.jar';cli=TC/'org.jacoco.cli-0.8.15-nodeps.jar';runtime=':'.join([str(W/'target/classes'),str(W/'test-classes'),str(W/'resources'),*deps]);cmd=[str(jdk/'java'),'-Djava.io.tmpdir='+str(U/'tmp'),'-Dfile.encoding=UTF-8','-Duser.timezone=Asia/Tokyo','-Djunit.jupiter.execution.parallel.enabled=false','-Djunit.jupiter.extensions.autodetection.enabled=false','-javaagent:'+str(agent)+'=destfile='+str(U/'jacoco.exec')+',sessionid='+session+',append=false','-Xlog:class+init=info:file='+str(U/'class-init.log'),'-jar',str(console),'execute','--disable-banner','--class-path',runtime,*[a for name in m['selectedClasses'] for a in ['--select-class',name]],'--reports-dir',str(U/'xml'),'--fail-if-no-tests','--details','summary'];begin=dict(producerSha256=sha(Path(__file__).resolve()),source=source,productionCoreMain='edaf641333266660ec79a6e070c98b7a79bbccac',inputHashes=inputs,dependencies=deps,physicalClassHashes=m['physicalClassHashes'],expectedCases=expected,expectedTests=14,selectedClasses=m['selectedClasses'],session=session,prepare=ref(O/'manifest.json'),preflight=ref(pf),oldExecUnion=False,actualBusinessBackendOrHeldClassActions=0,ownedFixtureCwd=str(W/'web-fixture'));wr(A/'begin.json',begin);stages={'unit':c.step('unit',cmd,W/'web-fixture',timeout=180)}
for label,args in [('coverage',['report',str(U/'jacoco.exec'),'--classfiles',str(W/'component'),'--xml',str(U/'coverage.xml')]),('classinfo',['classinfo',str(W/'component')]),('execinfo',['execinfo',str(U/'jacoco.exec')])]:stages[label]=c.step(label,[str(jdk/'java'),'-jar',str(cli),*args],R)
actual=[]
for p in (U/'xml').glob('TEST-*.xml'):
 for x in ET.parse(p).findall('testcase'):actual.append(dict(classname=x.get('classname'),name=x.get('name'),failure=x.find('failure') is not None,error=x.find('error') is not None,skipped=x.find('skipped') is not None))
v=dict(actualExit=stages['unit']['actualExit'],begin=begin,stages=stages,cases=actual,tests=len(actual),failures=sum(x['failure'] for x in actual),errors=sum(x['error'] for x in actual),skipped=sum(x['skipped'] for x in actual),formalUpdated=False,whole451Accepted=False);wr(A/'manifest.json',v);print(json.dumps({k:v[k] for k in ['actualExit','tests','failures','errors','skipped']}));sys.exit(v['actualExit'])
