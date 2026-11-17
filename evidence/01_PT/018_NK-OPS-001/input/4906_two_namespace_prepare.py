"""Root compiler before/after immutable snapshots for two pure static helpers. No Product runs."""
from pathlib import Path
import copy,datetime,hashlib,json,re,sys,xml.etree.ElementTree as E,zipfile
import pg9666_pagination_static as c
import pgpt_closed_host_profile as policy
from pgpt_spotbugs_contract import canonical_plugin
r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';tc=r.parent/'toolchain';runs=r.parent/'pgpt-runs/PG379';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ld=lambda p:json.loads(p.read_bytes());ref=lambda p:dict(path=str(p.relative_to(r)),sha256=sha(p));phase=sys.argv[1];assert phase in ['before','after'];stem='pg38028-two-namespace-before-v1' if phase=='before' else 'pg38030-two-namespace-after-v1';w=runs/stem;out=b/'evidence'/('PG38028-two-namespace-before-prepare-v1' if phase=='before' else 'PG38030-two-namespace-after-prepare-v1');assert not w.exists() and not out.exists();main=['src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/database/RequiredColumn.java','src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/media/ContentDispositionFactory.java'];tests=['src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/database/RequiredColumnTest.java','src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/media/ContentDispositionFactoryTest.java'];newtests=['src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/database/RequiredColumnNamespaceContractTest.java','src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/media/ContentDispositionNamespaceContractTest.java'];before=ld(b/'evidence/PG38026-two-pure-namespace-before-fix-v1/manifest.json');assert all(sha(r/n)==h for n,h in before['testHashes'].items())
if phase=='before':assert {n:sha(r/n) for n in main}==before['sourceHashes']
else:tests+=newtests
expected=[]
for n in tests:
 text=(r/n).read_text();assert not any(s in text for s in ['TemporaryInfrastructureException','FingerprintKeyRing','ResponseSnapshotCodec','WebStartupException','ProcessBuilder','@BeforeAll','@TempDir','DriverManager','DataSource','java.nio.file']);methods=re.findall(r'@Test\s*(?:@DisplayName\([^\n]+\)\s*)?void (\w+)\s*\(',text);assert len(methods)==1;expected.extend(dict(classname=re.search(r'package ([A-Za-z0-9_.]+);',text).group(1)+'.'+Path(n).stem,name=m+'()') for m in methods)
protofile=b/'evidence/PG37688-web-enum-current-protocol176-v1/manifest.json';proto=ld(protofile);jar=Path(proto['jar']['path']);assert sha(jar)==proto['jar']['sha256'] and all(sha(r/n)==h for n,h in proto['inputHashes'].items());inputs={n:sha(r/n) for n in main+tests+['pom.xml','src/schubert-nk-api/pom.xml','src/schubert-nk-web/pom.xml']};inputs.update(proto['inputHashes']);ann=tc/'m2/repository/org/jspecify/jspecify/1.0.1/jspecify-1.0.1.jar';console=tc/'junit-platform-console-standalone-1.13.4.jar';deps={str(p):sha(p) for p in [jar,ann,console]};w.mkdir();out.mkdir();c.SLOT=out
for n in main:
 text=(r/n).read_text();assert not any(s in text for s in ['TemporaryInfrastructureException','FingerprintKeyRing','ResponseSnapshotCodec','WebStartupException','java.nio.file','java.lang.foreign','ProcessBuilder','DriverManager','DataSource']);rel=n.split('/src/main/java/')[1];policy.relative_name(rel[:-5]+'.class');p=w/'src/main/java'/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes((r/n).read_bytes())
ns='http://maven.apache.org/POM/4.0.0';E.register_namespace('',ns);tag=lambda n:'{'+ns+'}'+n;root=E.Element(tag('project'));add=lambda p,n,v:E.SubElement(p,tag(n))
for n,v in [('modelVersion','4.0.0'),('groupId','dev.codex.schubert.quality'),('artifactId','pure-two-namespace-'+phase),('version','0.1.0-SNAPSHOT')]:add(root,n,v).text=v
props=add(root,'properties',None)
for n,v in [('maven.compiler.release','25'),('project.build.sourceEncoding','UTF-8'),('error-prone.version','2.50.0'),('nullaway.version','0.14.1')]:add(props,n,v).text=v
ds=add(root,'dependencies',None)
for i,p in enumerate([jar,ann]):
 d=add(ds,'dependency',None)
 for n,v in [('groupId','dev.codex.schubert.quality'),('artifactId','pinned-'+str(i)),('version','1'),('scope','system'),('systemPath',str(p))]:add(d,n,v).text=v
plugins=add(add(root,'build',None),'plugins',None);compiler=next(p for p in E.parse(r/'pom.xml').getroot().findall('.//'+tag('plugin')) if p.findtext(tag('artifactId'))=='maven-compiler-plugin');plugins.append(copy.deepcopy(compiler));plugins.append(copy.deepcopy(canonical_plugin((r/'src/schubert-nk-web/pom.xml').read_text())));E.ElementTree(root).write(w/'pom.xml',encoding='unicode',xml_declaration=True);maven=tc/'m2/wrapper/dists/apache-maven-3.9.12/6068d197/bin/mvn';jdk=tc/'jdk-25.0.4/bin';stages={'nullaway-compile':c.step('nullaway-compile',[str(maven),'-o','--no-transfer-progress','-Dmaven.repo.local='+str(tc/'m2/repository'),'-Dmaven.test.skip=true','compile'],w,timeout=180)};assert stages['nullaway-compile']['actualExit']==0 and not stages['nullaway-compile']['timedOut'];physical={};(w/'component').mkdir()
for p in (w/'target/classes').rglob('*.class'):
 n=str(p.relative_to(w/'target/classes'));policy.relative_name(n);to=w/'component'/n;to.parent.mkdir(parents=True,exist_ok=True);to.write_bytes(p.read_bytes());physical[n]=sha(p)
mainhashes=dict(physical);assert len(mainhashes)==2
with zipfile.ZipFile(jar) as z:
 for n,h in proto['physicalClassHashes'].items():
  policy.relative_name(n);raw=z.read(n);assert hashlib.sha256(raw).hexdigest()==h;to=w/'component'/n;to.parent.mkdir(parents=True,exist_ok=True);to.write_bytes(raw);physical[n]=h
assert len(physical)==178
for n in mainhashes:
 name=n[:-6].replace('/','.');stages['abi-'+Path(n).stem]=c.step('abi-'+Path(n).stem,[str(jdk/'javap'),'-public','-classpath',str(w/'target/classes'),name],w);assert stages['abi-'+Path(n).stem]['actualExit']==0
if phase=='after':
 (w/'test-classes').mkdir();stages['test-compile']=c.step('test-compile',[str(jdk/'javac'),'--release','25','-g','-proc:none','-implicit:none','-encoding','UTF-8','-Xlint:all','-Werror','-cp',str(w/'target/classes')+':'+':'.join(deps),'-d',str(w/'test-classes'),*[str(r/n) for n in tests]],r);assert stages['test-compile']['actualExit']==0 and not stages['test-compile']['timedOut']
v=dict(actualExit=0,terminalAtUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),phase=phase,work=str(w),inputHashes=inputs,dependencies=deps,apiMainSources=main,apiTestSources=tests,physicalClassHashes=physical,mainClassHashes=mainhashes,testClassHashes={str(p.relative_to(w/'test-classes')):sha(p) for p in (w/'test-classes').rglob('*.class')} if phase=='after' else {},currentProto=ref(protofile),stages=stages,expectedCases=expected,expectedTests=len(expected),newDefinitions=2 if phase=='after' else 0,compilerConfiguration='EXACT_ROOT_RELEASE25_ERRORPRONE2500_NULLAWAY0141_ANNOTATED_PACKAGE_JSPECIFY_JDK',rootCompilerSha256=hashlib.sha256(E.tostring(compiler)).hexdigest(),subsetPomSha256=sha(w/'pom.xml'),productTestsExecuted=0,oldFixtureSourcesUnchanged=True,actualDbRootNativeVmKeyAuthorityActions=0);(out/'manifest.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n');print(dict(actualExit=0,phase=phase,Main2=2,physical=178,productTests=0,expectedTests=len(expected)))
