"""BUG3186: retain successful same-source five-Main NullAway compile; rebuild only whole Tests."""
from pathlib import Path
import datetime, hashlib, json, re, shutil, xml.etree.ElementTree as E, zipfile
import pgpt_closed_host_profile as policy
import pg9666_pagination_static as steps

r=Path.cwd(); b=r/'evidence/01_PT/018_NK-OPS-001'; tc=r.parent/'toolchain'; runs=r.parent/'pgpt-runs/PG379'
load=lambda p:json.loads(p.read_text()); sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
ref=lambda p:dict(path=str(p.relative_to(r)),sha256=sha(p))
closure=load(b/'evidence/PG37714-web-monitoring-family-source-v1/manifest.json')
oldwork=runs/'pg37716-web-monitoring41-v1'; oldout=b/'evidence/PG37716-web-monitoring41-prepare-v1'
oldstage=load(oldout/'nullaway-compile-exit.safe.json')
assert oldstage['actualExit']==0 and not oldstage['timedOut']
for stream in ['stdout','stderr']: assert sha(oldout/('nullaway-compile.'+stream))==oldstage[stream+'Sha256']
for n in closure['mainSources']:
    assert sha(r/n)==closure['sourceHashes'][n]
    assert sha(oldwork/'src/main/java'/n.split('/src/main/java/')[1])==closure['sourceHashes'][n]
    policy.relative_name(n.split('/src/main/java/')[1][:-5]+'.class')
mainhash={str(p.relative_to(oldwork/'target/classes')):sha(p) for p in (oldwork/'target/classes').rglob('*.class')}
assert len(mainhash)==15
proto_path=b/'evidence/PG37688-web-enum-current-protocol176-v1/manifest.json'; proto=load(proto_path)
jar=Path(proto['jar']['path']); assert sha(jar)==proto['jar']['sha256']
assert all(sha(r/n)==h for n,h in proto['inputHashes'].items())
tests=closure['testSources']; expected=[]
for row in tests:
    n=row['path']; text=(r/n).read_text()
    assert not any(x in text for x in ['TemporaryInfrastructureException','FingerprintKeyRing','ResponseSnapshotCodec','WebStartupException','Class.forName','setAccessible','ProcessBuilder','DriverManager','DataSource','java.net.Socket','@BeforeAll','@TestFactory','@ParameterizedTest'])
    methods=re.findall(r'@Test\s*(?:@Timeout\([^\n]+\)\s*)?void (\w+)\s*\(',text)
    assert len(methods)==row['tests']
    expected.extend(dict(classname=n.split('/src/test/java/')[1][:-5].replace('/','.'),name=m+'()') for m in methods)
assert len(expected)==41
work=runs/'pg37730-web-monitoring41-final-v3'; out=b/'evidence/PG37730-web-monitoring41-final-prepare-v3'
assert not work.exists() and not out.exists(); work.mkdir(); out.mkdir(); steps.SLOT=out
shutil.copytree(oldwork/'src',work/'src'); shutil.copytree(oldwork/'target/classes',work/'target/classes')
shutil.copyfile(oldwork/'pom.xml',work/'pom.xml'); (work/'test-classes').mkdir()
resource=r/closure['resource']['path']; assert sha(resource)==closure['resource']['sha256']
dest=work/'test-classes/monitoring/http-route-labels.txt'; dest.parent.mkdir(); dest.write_bytes(resource.read_bytes())
ann=tc/'m2/repository/org/jspecify/jspecify/1.0.1/jspecify-1.0.1.jar'; console=tc/'junit-platform-console-standalone-1.13.4.jar'
deps={str(p):sha(p) for p in [jar,ann,console]}; deps.update(closure['sdkHashes'])
assert all(sha(Path(p))==h for p,h in deps.items())
stages={'test-compile':steps.step('test-compile',[str(tc/'jdk-25.0.4/bin/javac'),'--release','25','-g','-proc:none','-implicit:none','-encoding','UTF-8','-Xlint:all','-Werror','-cp',str(work/'target/classes')+':'+':'.join(deps),'-d',str(work/'test-classes'),*[str(r/t['path']) for t in tests]],r)}
assert stages['test-compile']['actualExit']==0 and not stages['test-compile']['timedOut']
shutil.copytree(work/'target/classes',work/'component'); physical=dict(mainhash)
with zipfile.ZipFile(jar) as archive:
    for n,h in proto['physicalClassHashes'].items():
        policy.relative_name(n); data=archive.read(n); assert hashlib.sha256(data).hexdigest()==h
        to=work/'component'/n; to.parent.mkdir(parents=True,exist_ok=True); to.write_bytes(data); physical[n]=h
assert len(physical)==191 and all(sha(work/'component'/n)==h for n,h in physical.items())
compiler,tag=policy.compiler_element()
assert E.tostring(compiler)==E.tostring(E.parse(work/'pom.xml').getroot().find('.//'+tag('plugin')))
inputs={n:sha(r/n) for n in closure['mainSources']+[x['path'] for x in tests]+['pom.xml','src/schubert-nk-web/pom.xml',closure['resource']['path']]}
inputs.update(proto['inputHashes'])
value=dict(actualExit=0,terminalAtUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),inputHashes=inputs,dependencies=deps,
    apiMainSources=closure['mainSources'],apiTestSources=[x['path'] for x in tests],physicalClassHashes=physical,
    mainClassHashes=mainhash,testClassHashes={str(p.relative_to(work/'test-classes')):sha(p) for p in (work/'test-classes').rglob('*.class')},
    currentProto=ref(proto_path),stages=stages,selectedClasses=sorted({x['classname'] for x in expected}),expectedCases=expected,
    expectedTests=41,newDefinitions=11,necessaryPriorDefinitions=30,MainSourceSubsetCount=5,MainRecompiledNow=False,
    originalMainNullAwayStage=oldstage,originalMainCompileOut=str(oldout.relative_to(r)),originalMainCompileStreams={s:ref(oldout/('nullaway-compile.'+s)) for s in ['stdout','stderr']},
    all15MainBytesSameAsSuccessfulOriginalCompile=True,originalRootCompilerConfiguration=True,
    rootCompilerSha256=hashlib.sha256(E.tostring(compiler)).hexdigest(),subsetPomSha256=sha(work/'pom.xml'),
    productTestsExecuted=0,actualHeldClassBinaryAccess=False,fullReportExpectedPartial=True,resource=closure['resource'])
(out/'manifest.json').write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')
print(dict(actualExit=0,originalMainCompileReusedNotReplayed=True,mainPhysical=15,allPhysical=191,tests41Compiled=True))
