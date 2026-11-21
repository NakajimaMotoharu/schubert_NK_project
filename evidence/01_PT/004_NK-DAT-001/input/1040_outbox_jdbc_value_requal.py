"""Requalify the approved ordinary JDBC Outbox port with the current value classes."""
from datetime import datetime, timezone
import hashlib,json,os,shutil,subprocess
from pathlib import Path
from xml.etree import ElementTree as ET
from pgpt_public_unit_xml import copy_public_evidence

R=Path.cwd()
TC=R.parent/'toolchain'
JDK=TC/'jdk-25.0.4'
OPS=R/'evidence/01_PT/018_NK-OPS-001'
RUN='PG41410-p00405-current-outbox-value-jdbc-v1'
OUT=OPS/'evidence'/RUN
WORK=R.parent/'pgpt-runs/PG379'/RUN

def git(*args):
    return subprocess.check_output(['git',*args])

def pin(p):
    return dict(path=str(p),sha256=hashlib.sha256(p.read_bytes()).hexdigest())

def save(p,d):
    with p.open('x') as f:
        json.dump(d,f,indent=2)
        f.write('\n')

profile_path=next((OPS/'input').glob('5193_*.json'))
profile=json.loads(profile_path.read_bytes())
prior_path=next((OPS/'evidence').glob('PG39656*/manifest.json'))
prior=json.loads(prior_path.read_bytes())
old_unit=next((OPS/'evidence').glob('PG39653*/manifest.json'))
old_unit_value=json.loads(old_unit.read_bytes())
prepare_path=R/prior['proofs']['prepare']['path']
assert pin(prepare_path)['sha256']==prior['proofs']['prepare']['sha256']
prepare=json.loads(prepare_path.read_bytes())
old_pom=R.parent/'pgpt-runs/PG379'/profile['privateDirs']['prepare']/'pom.xml'
assert pin(old_pom)['sha256']==prepare['subsetPomSha256']
mains=[Path(p) for p in profile['mainSources']]
tests=[Path(row['path']) for row in profile['testSources']]
assert len(mains)==10 and len(tests)==2 and profile['sdkJars']==['com/google/code/findbugs/jsr305/3.0.2/jsr305-3.0.2.jar']
source=git('rev-parse','HEAD').decode().strip()
core='2611e1acbd57955d591d52e5348999ea293e068d'
assert not git('diff','--name-only',core,source,'--',*map(str,mains))
changes=git('diff','--name-only',prior['source'],source,'--',*map(str,mains+tests),*profile['pomInputs']).decode().splitlines()
assert len(changes)==2 and {Path(p).name for p in changes}=={'OutboxEntry.java','OutboxRequest.java'}
for p in mains+tests:
    assert p.read_bytes()==git('show',f'{source}:{p}')
deps=[Path(p) for p,d in profile['preparedDependencyHashes'].items() if pin(Path(p))['sha256']==d]
assert len(deps)==3 and {p.name for p in deps}=={'jspecify-1.0.1.jar','junit-platform-console-standalone-1.13.4.jar','jsr305-3.0.2.jar'}
for forbidden in ('postgresql','artemis','hikari'):
    assert not any(forbidden in str(p).lower() for p in deps)
raw_xml_pom=ET.parse(old_pom)
parent=ET.parse(R/'pom.xml')
ns='{http://maven.apache.org/POM/4.0.0}'
def compiler(xml):
    return next(ET.tostring(p) for p in xml.iter(ns+'plugin') if p.findtext(ns+'artifactId')=='maven-compiler-plugin')
assert compiler(raw_xml_pom)==compiler(parent)
WORK.mkdir(mode=0o700)
OUT.mkdir()
shutil.copyfile(old_pom,WORK/'pom.xml')
for p in mains:
    dst=WORK/Path(*p.parts[2:])
    dst.parent.mkdir(parents=True,exist_ok=True)
    shutil.copyfile(p,dst)
    assert pin(p)['sha256']==pin(dst)['sha256']
env=dict(PATH=str(JDK/'bin')+':/usr/bin:/bin',JAVA_HOME=str(JDK),LANG='C.UTF-8',TZ='Asia/Tokyo',HOME=os.environ['HOME'])
steps={}
def execute(stage,cmd):
    argv=list(map(str,cmd))
    res=subprocess.run(argv,cwd=WORK,env=env,capture_output=True,check=False,timeout=100)
    a,b=WORK/(stage+'.out'),WORK/(stage+'.err')
    a.write_bytes(res.stdout)
    b.write_bytes(res.stderr)
    steps[stage]=dict(argv=argv,actualExit=res.returncode,stdout=pin(a),stderr=pin(b))
    save(OUT/(stage+'-exit.json'),steps[stage])
    assert res.returncode==0, (stage,res.returncode)
    return res.stdout
maven=TC/'m2/wrapper/dists/apache-maven-3.9.12/6068d197/bin/mvn'
execute('maven-compile',[maven,'-o','-B','-ntp','-f',WORK/'pom.xml',
    '-Dmaven.repo.local='+str(TC/'m2/repository'),'-Dmaven.test.skip=true','compile'])
classes=WORK/'target/classes'
physical=sorted(classes.rglob('*.class'))
assert len(physical)==len(prepare['physicalClassHashes'])==10
assert {p.relative_to(classes).as_posix() for p in physical}==set(prepare['physicalClassHashes'])
diff=[p.relative_to(classes).as_posix() for p in physical if pin(p)['sha256']!=prepare['physicalClassHashes'][p.relative_to(classes).as_posix()]]
assert len(diff)==2 and {Path(p).stem for p in diff}=={'OutboxEntry','OutboxRequest'}
test_classes=WORK/'test-classes'
test_classes.mkdir()
cp=os.pathsep.join(map(str,[classes,*deps]))
execute('test-compile',[JDK/'bin/javac','--release','25','-g','-proc:none','-implicit:none','-encoding','UTF-8',
    '-Xlint:all','-Werror','-cp',cp,'-d',test_classes,*(R/p for p in tests)])
agent=TC/'m2/repository/org/jacoco/org.jacoco.agent/0.8.15/org.jacoco.agent-0.8.15-runtime.jar'
unit=WORK/'unit.exec'
reports=WORK/'reports'
target_classes=prepare['selectedClasses']
assert {name.rsplit('.',1)[-1] for name in target_classes}=={p.stem for p in tests}
execute('unit',[JDK/'bin/java',f'-javaagent:{agent}=destfile={unit},sessionid={RUN}',
    '-cp',str(test_classes)+os.pathsep+cp,'org.junit.platform.console.ConsoleLauncher','execute',
    '--disable-ansi-colors','--fail-if-no-tests',*[a for c in target_classes for a in ('--select-class',c)],'--reports-dir',reports])
original_xml=reports/'TEST-junit-jupiter.xml'
xml=ET.parse(original_xml).getroot()
expected={(v['classname'],v['name'].removesuffix('()')) for v in old_unit_value['cases']}
actual={(v.get('classname'),v.get('name').removesuffix('()')) for v in xml.findall('testcase')}
assert len(actual)==len(expected)==int(xml.get('tests'))==12 and actual==expected
assert all(int(xml.get(k))==0 for k in ('errors','failures','skipped'))
public=OUT/'jupiter.xml'
redaction=copy_public_evidence(original_xml,public)
save(OUT/'manifest.json',dict(run=RUN,actualExit=0,terminalAtUTC=datetime.now(timezone.utc).isoformat(),testedSource=source,
    productionCore=core,profile=pin(profile_path),oldIndependent=pin(prior_path),oldOriginalXmlRoster=pin(old_unit),
    sourceChangeCausedRequalification=True,unchangedJdkProxyTestInputs=[pin(p) for p in tests],fixtureRewrites=0,
    currentMainInputs=[pin(p) for p in mains],currentClassFiles=[pin(p) for p in physical],changedPhysical=diff,
    tests=12,failures=0,errors=0,skipped=0,notRun=0,newTests=0,actualDbOps=0,driverClasspathEntries=0,heldClassesOpened=0,
    originalExec=pin(unit),jupiter=pin(public),redaction=redaction,codeBuilds=1,compileRootPolicy=True,
    finalP00405=False,whole451=False,formalDelta=0,steps=steps))
print(RUN,len(actual),[Path(p).stem for p in diff])
