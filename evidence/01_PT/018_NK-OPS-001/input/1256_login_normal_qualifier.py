"""Exact public Main subset: strict NullAway build, static checks, then one pinned normal run."""
from pathlib import Path
import copy,hashlib,json,os,re,subprocess,sys,zipfile,xml.etree.ElementTree as ET
import pg9666_pagination_static as c
R=Path.cwd();B=R/'evidence/01_PT/018_NK-OPS-001';TC=R.parent/'toolchain';RUNS=R.parent/'pgpt-runs/PG379';phase=sys.argv[1];assert phase in ['compile','compile-recover','static','run'];sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();load=lambda p:json.loads(Path(p).read_bytes());write=lambda p,v:Path(p).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
red=load(B/'evidence/PG26476-jms-provider-original-red-v1/manifest.json');assert red['actualExit']==0 and red['failures']==2
prefix='src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/messaging/';security='src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/security/';guards=[security+'MqLoginClient.java',security+'MqLoginExchangeException.java'];main=guards+[prefix+n+'.java' for n in ['JmsRequestReplyClient','JmsRequestReplyException','JmsRequestSender','ReplyCorrelationRegistry','PendingReply']];packages=[prefix+'package-info.java',security+'package-info.java'];tests=[security.replace('/main/','/test/')+'MqLoginClientTest.java']+[prefix.replace('/main/','/test/')+n+'.java' for n in ['JmsRequestReplyClientTest','ReplyCorrelationRegistryTest']];classes=['dev.codex.schubert.nk.web.security.MqLoginClientTest','dev.codex.schubert.nk.web.messaging.JmsRequestReplyClientTest','dev.codex.schubert.nk.web.messaging.ReplyCorrelationRegistryTest'];expected=[]
for p,cl,n in zip(tests,classes,[7,10,7]):
 text=(R/p).read_text();methods=re.findall(r'@Test\b[^\n]*\n\s*void (\w+)\s*\(',text);assert len(methods)==n
 assert not any(v in text for v in ['@BeforeAll','@TempDir','EmbeddedActiveMQ','ActiveMQConnectionFactory','ProcessBuilder','Class.forName','java.nio.file','java.net.']);expected.extend(dict(classname=cl,name=m+'()') for m in methods)
held=['TemporaryInfrastructureException','FingerprintKeyRing','ResponseSnapshotCodec','WebStartupException']
for p in main+packages:assert not any(h in (R/p).read_text() for h in held)
proto=load(B/'evidence/PG26278-protocol-unicode-main-compile-v1/manifest.json');jar=Path(proto['jar']['path']);assert sha(jar)==proto['jar']['sha256'] and all(sha(R/p)==h for p,h in proto['inputHashes'].items())
protoCompile=B/'evidence/PG26304-protocol-unicode-full130-compile-v3/manifest.json';protoTest=load(protoCompile);protoTest['testSources']=protoTest['tests'];protoTest['resources']=load(B/'evidence/PG26280-protocol-unicode-full130-compile-v1/manifest.json')['resources'];protoClasses=RUNS/'pg26304-protocol-unicode-full130-compile-v3/classes';protoResources=RUNS/'pg26280-protocol-unicode-full130-compile-v1/resources';assert protoTest['actualExit']==0 and protoTest['expectedTests']==130
for p in protoTest['testSources']+protoTest['resources']:assert sha(R/p)==protoTest['inputHashes'][p]
assert protoTest['classHashes']=={str(p.relative_to(protoClasses)):sha(p) for p in protoClasses.rglob('*.class')}
oldProto=load(B/'evidence/PG26310-protocol-unicode-full130-unit-v1/manifest.json');assert oldProto['begin']['compileManifestSha256']==sha(protoCompile);protoCases=oldProto.get('cases') or oldProto.get('expectedCases')
if protoCases is None:protoCases=oldProto['begin']['expectedCases']
expected.extend(dict(classname=x['classname'],name=x['name']) for x in protoCases);assert len(expected)==154 and len({(x['classname'],x['name']) for x in expected})==154
console=TC/'junit-platform-console-standalone-1.13.4.jar';vendor=[Path(p) for p in red['dependencies'] if '/jakarta.jms-api/' in p or '/jspecify/' in p];deps={str(p):sha(p) for p in [jar,console,*vendor]};assert all(h==red['dependencies'][p] for p,h in deps.items());cp=':'.join(deps);jdk=TC/'jdk-25.0.4/bin';maven=TC/'m2/wrapper/dists/apache-maven-3.9.12/6068d197/bin/mvn';work=RUNS/'pg26524-login-pure-main-subset-v1';pc=B/'evidence/PG26524-login-pure-main-subset-v1';ps=B/'evidence/PG26526-login-pure-static-v1';inputs={p:sha(R/p) for p in main+packages+tests+['pom.xml',str(Path(__file__).relative_to(R))]};inputs.update({p:protoTest['inputHashes'][p] for p in protoTest['testSources']+protoTest['resources']})
if phase=='compile':
 assert not work.exists() and not pc.exists();work.mkdir();pc.mkdir();c.SLOT=pc;(work/'test-classes').mkdir()
 for p in main+packages:
  target=work/'src/main/java'/p.split('/src/main/java/')[1];target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes((R/p).read_bytes())
 ns='http://maven.apache.org/POM/4.0.0';ET.register_namespace('',ns);tag=lambda n:'{'+ns+'}'+n;root=ET.Element(tag('project'));add=lambda r,n,t:ET.SubElement(r,tag(n));
 for n,t in [('modelVersion','4.0.0'),('groupId','dev.codex.schubert.quality'),('artifactId','login-public-boundary-subset'),('version','0.1.0-SNAPSHOT')]:add(root,n,t).text=t
 props=add(root,'properties',None)
 for n,t in [('maven.compiler.release','25'),('project.build.sourceEncoding','UTF-8'),('error-prone.version','2.50.0'),('nullaway.version','0.14.1')]:add(props,n,t).text=t
 dependencies=add(root,'dependencies',None)
 for g,a,v in [('org.jspecify','jspecify','1.0.1'),('jakarta.jms','jakarta.jms-api','3.1.0'),('dev.codex.schubert.quality','fixed-protocol','0.1.0')]:
  dep=add(dependencies,'dependency',None)
  for n,t in [('groupId',g),('artifactId',a),('version',v)]:add(dep,n,t).text=t
  if a=='fixed-protocol':add(dep,'scope',None).text='system';add(dep,'systemPath',None).text=str(jar)
 build=add(root,'build',None);plugins=add(build,'plugins',None);parent=ET.parse(R/'pom.xml').getroot();compiler=next(x for x in parent.findall('.//'+tag('plugin')) if x.findtext(tag('artifactId'))=='maven-compiler-plugin');plugins.append(copy.deepcopy(compiler));ET.ElementTree(root).write(work/'pom.xml',encoding='unicode',xml_declaration=True)
 stages={'nullaway-compile':c.step('nullaway-compile',[str(maven),'-o','--no-transfer-progress','-Dmaven.repo.local='+str(TC/'m2/repository'),'-Dmaven.test.skip=true','compile'],work,timeout=180)};assert stages['nullaway-compile']['actualExit']==0
 stages['test-compile']=c.step('test-compile',[str(jdk/'javac'),'-g','-proc:none','-implicit:none','--release','25','-encoding','UTF-8','-Xlint:all','-Werror','-cp',str(work/'target/classes')+':'+cp,'-d',str(work/'test-classes'),*tests],R);assert stages['test-compile']['actualExit']==0
 phase='compile-recover'
if phase=='compile-recover':
 assert work.exists() and pc.exists() and not (pc/'manifest.json').exists()
 stages={k:load(pc/(k+'-exit.safe.json')) for k in ['nullaway-compile','test-compile']}
 for k,v in stages.items():
  assert v['actualExit']==0 and not v['timedOut']
  for stream in ['stdout','stderr']:assert sha(pc/(k+'.'+stream))==v[stream+'Sha256']
 for p in main+packages:assert sha(work/'src/main/java'/p.split('/src/main/java/')[1])==sha(R/p)
 physical={str(p.relative_to(work/'target/classes')):sha(p) for p in (work/'target/classes').rglob('*.class')};assert len(physical)==12
 expectedPhysical={p.split('/src/main/java/')[1].replace('.java','.class') for p in main+packages}|{'dev/codex/schubert/nk/web/messaging/JmsRequestReplyException$Reason.class','dev/codex/schubert/nk/web/security/MqLoginClient$Reply.class','dev/codex/schubert/nk/web/security/MqLoginExchangeException$Reason.class'};assert set(physical)==expectedPhysical
 write(pc/'manifest.json',dict(actualExit=0,inputHashes=inputs,dependencies=deps,stages=stages,mainSources=main,packageSources=packages,mainClassHashes=physical,testClassHashes={str(p.relative_to(work/'test-classes')):sha(p) for p in (work/'test-classes').rglob('*.class')},subsetPomSha256=sha(work/'pom.xml'),compilerConfiguration='EXACT_ROOT_PLUGIN_RELEASE25_NULLAWAY_0141_ERRORPRONE2500',protoCompileManifestSha256=sha(B/'evidence/PG26278-protocol-unicode-main-compile-v1/manifest.json'),wholeProtocol130ClassesReused=True,expectedCases=expected,selectedClasses=classes+sorted({x['classname'] for x in protoCases}),expectedTests=154,productTestsExecuted=0,heldActualClassFilesRead=False));print(json.dumps(dict(actualExit=0,expectedTests=154,MainPhysical=12,NullAway='FRESH_PASS',productTestsExecuted=0)));sys.exit(0)
cm=load(pc/'manifest.json');assert cm['actualExit']==0 and cm['inputHashes']==inputs and cm['dependencies']==deps;assert cm['mainClassHashes']=={str(p.relative_to(work/'target/classes')):sha(p) for p in (work/'target/classes').rglob('*.class')}
if phase=='static':
 assert not ps.exists();ps.mkdir();c.SLOT=ps;sg=TC/'static-gates-20261015';pmd=[sg/'record-fix-v1/pmd-record-1298.jar',*sorted((sg/'pmd-bin-7.28.0/lib').glob('*.jar'))];listing=ps/'sources.txt';listing.write_text(''.join(str(R/p)+'\n' for p in tests[:1]));stages={}
 stages['pmd']=c.step('pmd',[str(jdk/'java'),'-cp',':'.join(map(str,pmd)),'net.sourceforge.pmd.cli.PmdCli','check','--file-list',str(listing),'--rulesets',str(R/'tools/quality/static/pmd.xml'),'--use-version','java-25','--aux-classpath',str(TC/'jdk-25.0.4/lib/jrt-fs.jar')+':'+cp+':'+str(work/'target/classes'),'--no-cache','--format','xml','--report-file',str(ps/'pmd.xml')],R)
 stages['checkstyle']=c.step('checkstyle',[str(jdk/'java'),'-jar',str(sg/'checkstyle-14.3.0-all.jar'),'-c',str(R/'tools/quality/static/checkstyle.xml'),'-f','xml','-o',str(ps/'checkstyle.xml'),'@'+str(listing)],R)
 stages['spotbugs']=c.step('spotbugs',[str(maven),'-o','--no-transfer-progress','-Dmaven.repo.local='+str(TC/'m2/repository'),'-Dmaven.test.skip=true','com.github.spotbugs:spotbugs-maven-plugin:4.10.4.0:check'],work,timeout=180)
 sb=work/'target/spotbugsXml.xml';assert sb.exists();(ps/'spotbugs.xml').write_bytes(sb.read_bytes());root=ET.parse(sb).getroot();summary=dict(bugs=len(root.findall('.//BugInstance')),missing=len(root.findall('.//MissingClass')),errors=len(root.findall('.//Error')),classStats=sorted(x.get('class') for x in root.findall('.//ClassStats')))
 write(ps/'manifest.json',dict(actualExit=0,stages=stages,inputHashes=inputs,dependencies=deps,spotbugs=summary,applicability='PENDING_EXPLICIT_SOURCE_CONTEXT_CLASSIFICATION',productTestsExecuted=0));print(json.dumps(dict(actualExit=0,stages={k:v['actualExit'] for k,v in stages.items()},spotbugs=summary)));sys.exit(0)
source=sys.argv[2];assert re.fullmatch('[0-9a-f]{40}',source)
for p,h in inputs.items():assert hashlib.sha256(subprocess.check_output(['git','show',source+':'+p])).hexdigest()==h
pf=B/'evidence/PG26528-login-pure-preflight-v1/manifest.json';fm=load(pf);assert fm['actualExit']==0 and fm['inputHashes']==inputs
U=RUNS/'pg26530-login-connected154-v1';out=B/'evidence/PG26530-login-connected154-v1';assert not U.exists() and not out.exists();U.mkdir();out.mkdir();(U/'component').mkdir();(U/'tmp').mkdir();c.SLOT=out
with zipfile.ZipFile(jar) as z:
 for n,h in proto['physicalClassHashes'].items():
  data=z.read(n);assert hashlib.sha256(data).hexdigest()==h;p=U/'component'/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
for n,h in cm['mainClassHashes'].items():
 p=U/'component'/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes((work/'target/classes'/n).read_bytes());assert sha(p)==h
physical={str(p.relative_to(U/'component')):sha(p) for p in (U/'component').rglob('*.class')};assert len(physical)==188
agent=TC/'m2/repository/org/jacoco/org.jacoco.agent/0.8.15/org.jacoco.agent-0.8.15-runtime.jar';cli=TC/'org.jacoco.cli-0.8.15-nodeps.jar';session='PG26530-LOGIN-CONNECTED154';runtime=':'.join(map(str,[work/'target/classes',work/'test-classes',protoClasses,protoResources,jar,*vendor]));cmd=[str(jdk/'java'),'-Djava.io.tmpdir='+str(U/'tmp'),'-Dfile.encoding=UTF-8','-Duser.timezone=Asia/Tokyo','-Djunit.jupiter.extensions.autodetection.enabled=false','-Djunit.jupiter.execution.parallel.enabled=false','-javaagent:'+str(agent)+'=destfile='+str(U/'jacoco.exec')+',sessionid='+session+',append=false','-Xlog:class+init=info:file='+str(U/'class-init.log'),'-jar',str(console),'execute','--disable-banner','--class-path',runtime,*[a for cl in cm['selectedClasses'] for a in ['--select-class',cl]],'--reports-dir',str(U/'xml'),'--fail-if-no-tests','--details','summary'];begin=dict(source=source,productionCoreMain='236ffddc83a08f1ba8f2ac5c3932e381371acd59',inputHashes=inputs,dependencies=deps,physicalClassHashes=physical,expectedCases=expected,expectedTests=154,session=session,selectedClasses=cm['selectedClasses'],preflightManifestSha256=sha(pf),compileManifestSha256=sha(pc/'manifest.json'),oldExecUnion=False,actualBrokerOrHeldOperations=False);write(out/'begin.json',begin);stages={'unit':c.step('unit',cmd,R,timeout=180)}
for label,args in [('coverage',['report',str(U/'jacoco.exec'),'--classfiles',str(U/'component'),'--xml',str(U/'coverage.xml')]),('classinfo',['classinfo',str(U/'component')]),('execinfo',['execinfo',str(U/'jacoco.exec')])]:stages[label]=c.step(label,[str(jdk/'java'),'-jar',str(cli),*args],R)
cases=[]
for p in (U/'xml').glob('TEST-*.xml'):
 for t in ET.parse(p).findall('testcase'):cases.append(dict(classname=t.get('classname'),name=t.get('name'),failure=t.find('failure') is not None,error=t.find('error') is not None,skipped=t.find('skipped') is not None))
v=dict(actualExit=stages['unit']['actualExit'],begin=begin,stages=stages,cases=cases,tests=len(cases),failures=sum(x['failure'] for x in cases),errors=sum(x['error'] for x in cases),skipped=sum(x['skipped'] for x in cases),global451Accepted=False,wholeWbsP00502Accepted=False,formalUpdated=False);write(out/'manifest.json',v);print(json.dumps({k:v[k] for k in ['actualExit','tests','failures','errors','skipped']}));sys.exit(v['actualExit'])
