"""Closed safe session Main Maven NullAway compile and whole fixtures; no backend/held binary."""
from pathlib import Path
import copy,hashlib,json,re,xml.etree.ElementTree as ET,zipfile
import pgpt_closed_host_profile as policy
import pg9666_pagination_static as c
import subprocess, sys
from pgpt_spotbugs_contract import canonical_plugin
R = Path.cwd()
B = R / 'evidence/01_PT/018_NK-OPS-001'
TC = R.parent / 'toolchain'
RUNS = R.parent / 'pgpt-runs/PG379'
variant = sys.argv[1]
assert variant in ('before','after')
tag_run = {'before':'38188','after':'38190'}[variant]
W = RUNS / f'pg{tag_run}-borrowed-file-{variant}-v1'
O = B / f'evidence/PG{tag_run}-borrowed-file-{variant}-prepare-v1'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
ld = lambda p: json.loads(p.read_text())
wr = lambda p,j: p.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n')
ref = lambda p: dict(path=str(p.relative_to(R)),sha256=sha(p))
phase = 'prepare'
start = ld(next((R/'documents/400_PGPT/470_PMO/601_WBS66短期実行_20261117').glob('178_*')))
main = start['mainSources']
old_tests = start['testSources']
assert all(sha(R/p)==start['beforeHashes'][p] for p in old_tests+[main[2]])
new_tests = [p.removesuffix('Test.java')+'NamespaceContractTest.java' for p in old_tests]
tests = old_tests+new_tests if variant=='after' else []
expected=[]
for path, count in zip(tests,[2,3,1,1]):
    text=(R/path).read_text()
    assert not any(x in text for x in ['TemporaryInfrastructureException','FingerprintKeyRing','ResponseSnapshotCodec','WebStartupException','@BeforeAll','ProcessBuilder','DriverManager','DataSource','Class.forName','setPosixFilePermissions','createSymbolicLink','createLink','setOwner'])
    methods=re.findall(r'@Test\s+void (\w+)\s*\(([^)]*)\)',text)
    assert len(methods)==count
    for name, args in methods:
        assert args in ('','@TempDir Path root')
        expected.append(dict(classname=path.split('/src/test/java/')[1][:-5].replace('/','.'),name=name+('()' if not args else '(Path)')))
assert len(expected)==(7 if variant=='after' else 0)
inputs={p:sha(R/p) for p in main+tests+['pom.xml','src/schubert-nk-web/pom.xml']};protoPath=B/'evidence/PG37688-web-enum-current-protocol176-v1/manifest.json';proto=ld(protoPath);jar=Path(proto['jar']['path']);assert sha(jar)==proto['jar']['sha256'] and all(sha(R/p)==h for p,h in proto['inputHashes'].items());inputs.update(proto['inputHashes']);jdk=TC/'jdk-25.0.4/bin';maven=TC/'m2/wrapper/dists/apache-maven-3.9.12/6068d197/bin/mvn';ann=TC/'m2/repository/org/jspecify/jspecify/1.0.1/jspecify-1.0.1.jar';console=TC/'junit-platform-console-standalone-1.13.4.jar';deps={str(p):sha(p) for p in [jar,ann,console]};sdk={};assert all(sha(Path(n))==h for n,h in sdk.items());deps.update(sdk)
if phase=='prepare':
 assert not W.exists() and not O.exists();W.mkdir();O.mkdir();c.SLOT=O
 for p in main:
  assert not any(x in (R/p).read_text() for x in ['TemporaryInfrastructureException','FingerprintKeyRing','ResponseSnapshotCodec','WebStartupException','java.nio.file','java.net.Socket','DataSource']);policy.relative_name(p.split('/src/main/java/')[1][:-5]+'.class');to=W/'src/main/java'/p.split('/src/main/java/')[1];to.parent.mkdir(parents=True,exist_ok=True);old = subprocess.check_output(['git','show',start['values']['productionCoreMain']+':'+p])
  assert hashlib.sha256(old).hexdigest()==start['beforeHashes'][p]
  current = (R/p).read_bytes()
  name = Path(p).stem
  added = f'private {name}() {{\n    throw new AssertionError("static namespace");\n  }}'.encode()
  original = f'private {name}() {{}}'.encode()
  assert current.replace(added,original)==old
  to.write_bytes(old if variant=='before' else current)
  inputs[p] = sha(to)
 ns='http://maven.apache.org/POM/4.0.0';ET.register_namespace('',ns);tag=lambda n:'{'+ns+'}'+n;root=ET.Element(tag('project'));add=lambda e,n,v:ET.SubElement(e,tag(n))
 for n,v in [('modelVersion','4.0.0'),('groupId','dev.codex.schubert.quality'),('artifactId','borrowed-file-codec-isolated'),('version','0.1.0-SNAPSHOT')]:add(root,n,v).text=v
 props=add(root,'properties',None)
 for n,v in [('maven.compiler.release','25'),('project.build.sourceEncoding','UTF-8'),('error-prone.version','2.50.0'),('nullaway.version','0.14.1'),('pgpt.protocol.jar',str(jar))]:add(props,n,v).text=v
 ds=add(root,'dependencies',None)
 for group,artifact,version in [('org.jspecify','jspecify','1.0.1')]:
  d=add(ds,'dependency',None)
  for n,v in [('groupId',group),('artifactId',artifact),('version',version)]:add(d,n,v).text=v
 d=add(ds,'dependency',None)
 for n,v in [('groupId','dev.codex.schubert.quality'),('artifactId','current-qualified-protocol'),('version','0.1.0-SNAPSHOT'),('scope','system'),('systemPath','${pgpt.protocol.jar}')]:add(d,n,v).text=v
 for sdk_index,sdk_path in enumerate(sdk):
  d=add(ds,'dependency',None)
  for n,v in [('groupId','dev.codex.schubert.quality'),('artifactId','prepared-sdk-'+str(sdk_index)),('version','1'),('scope','system'),('systemPath',sdk_path)]:add(d,n,v).text=v
 plugins=add(add(root,'build',None),'plugins',None);compiler=next(p for p in ET.parse(R/'pom.xml').getroot().findall('.//'+tag('plugin')) if p.findtext(tag('artifactId'))=='maven-compiler-plugin');plugins.append(copy.deepcopy(compiler));plugins.append(copy.deepcopy(canonical_plugin((R/'src/schubert-nk-web/pom.xml').read_text())));ET.ElementTree(root).write(W/'pom.xml',encoding='unicode',xml_declaration=True)
 stages={'nullaway-compile':c.step('nullaway-compile',[str(maven),'-o','--no-transfer-progress','-Dmaven.repo.local='+str(TC/'m2/repository'),'-Dmaven.test.skip=true','compile'],W,timeout=180)};assert stages['nullaway-compile']['actualExit']==0 and not stages['nullaway-compile']['timedOut']
 (W/'test-classes').mkdir()
 if tests:
  stages['test-compile']=c.step('test-compile',[str(jdk/'javac'),'--release','25','-g','-proc:none','-implicit:none','-encoding','UTF-8','-Xlint:all','-Werror','-cp',str(W/'target/classes')+':'+':'.join(deps),'-d',str(W/'test-classes'),*[str(R/p) for p in tests]],R);assert stages['test-compile']['actualExit']==0 and not stages['test-compile']['timedOut']
 (W/'component').mkdir();physical={}
 for p in (W/'target/classes').rglob('*.class'):
  n=str(p.relative_to(W/'target/classes'));policy.relative_name(n);to=W/'component'/n;to.parent.mkdir(parents=True,exist_ok=True);to.write_bytes(p.read_bytes());physical[n]=sha(p)
 with zipfile.ZipFile(jar) as z:
  for n,h in proto['physicalClassHashes'].items():
   policy.relative_name(n);data=z.read(n);assert hashlib.sha256(data).hexdigest()==h;to=W/'component'/n;to.parent.mkdir(parents=True,exist_ok=True);to.write_bytes(data);physical[n]=h
 assert len(physical)==len(proto['physicalClassHashes'])+len(list((W/'target/classes').rglob('*.class')))
 for binary in (W/'test-classes').rglob('*.class'):policy.relative_name(str(binary.relative_to(W/'test-classes')))
 v=dict(actualExit=0,inputHashes=inputs,dependencies=deps,apiMainSources=main,apiTestSources=tests,physicalClassHashes=physical,mainClassHashes={str(p.relative_to(W/'target/classes')):sha(p) for p in (W/'target/classes').rglob('*.class')},testClassHashes={str(p.relative_to(W/'test-classes')):sha(p) for p in (W/'test-classes').rglob('*.class')},currentProto=ref(protoPath),stages=stages,selectedClasses=sorted({x['classname'] for x in expected}),expectedCases=expected,expectedTests=len(expected),newDefinitions=2 if tests else 0,necessaryPriorDefinitions=5,compilerConfiguration='EXACT_ROOT_RELEASE25_ERRORPRONE2500_NULLAWAY0141_NO_PROC_NONE_FOR_MAIN',MainSourceSubsetCount=3,MainSafeClosureRebuilt=True,wholeProjectMainRebuilt=False,rootCompilerSha256=hashlib.sha256(ET.tostring(compiler)).hexdigest(),subsetPomSha256=sha(W/'pom.xml'),productTestsExecuted=0,actualHeldClassBinaryAccess=False,fullReportExpectedPartial=True);wr(O/'manifest.json',v);print(json.dumps(dict(actualExit=0,variant=variant,MainSources=3,physicalClasses=len(physical),expectedTests=len(expected))))
