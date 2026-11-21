"""Measure the original four ordinary DirectoryCalls defaults against the current real JAR."""
from datetime import datetime,timezone
from hashlib import sha256
import json,os,re,subprocess
from pathlib import Path
from xml.etree import ElementTree as ET
from zipfile import ZipFile

from jacoco_readonly_exec_subset import decode
from pgpt_public_unit_xml import copy_public_evidence

R=Path.cwd()
OPS=R/'evidence/01_PT/018_NK-OPS-001/evidence'
TC=R.parent/'toolchain'
JDK=TC/'jdk-25.0.4/bin'
M2=TC/'m2/repository'
RUN='PG41426-current-storage-directory-defaults-v1'
OUT=OPS/RUN
WORK=R.parent/'pgpt-runs/PG379'/RUN
JAVA_PKG='dev.codex.schubert.nk.storage'
PREFIX=JAVA_PKG.replace('.','/')
NAMES={PREFIX+'/'+n for n in ('DirectoryCalls','StorageIoException','StorageIoException$Reason')}

def ref(p):
    return dict(path=str(p),sha256=sha256(p.read_bytes()).hexdigest())

old_proof=next(OPS.glob('PG23504*/manifest.json'))
old=json.loads(old_proof.read_bytes())
release=next(OPS.glob('PG41322*/manifest.json'))
artifact=json.loads(release.read_bytes())['packagingProof']['artifacts']['storage']['artifact']
jar=Path(artifact['path'])
assert ref(jar)['sha256']==artifact['sha256']
static=next(OPS.glob('PG41312*/manifest.json'))
static_data=json.loads(static.read_bytes())
closure_jar=Path(static_data['currentJar']['path'])
assert ref(closure_jar)==static_data['currentJar']
current=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
mod=Path('src/schubert-nk-storage')
fixture=mod/'src/test/java'/PREFIX/'UnsupportedDirectoryDefaultsPortTest.java'
assert old['actualFilesystemOrDescriptorActions']==0 and old['tests']==4
assert not subprocess.check_output(['git','diff','--name-only',static_data['core'],current,'--',str(mod/'src/main'),'pom.xml'])
assert not subprocess.check_output(['git','diff','--name-only',old['source'],current,'--',str(fixture)])
source_fixture=subprocess.check_output(['git','show',f'{current}:{fixture}'])
assert source_fixture==fixture.read_bytes()
assert b'@TempDir' not in source_fixture and b'createPrivateFile' in source_fixture
assert not any(name in source_fixture for name in (b'Linux',b'DriverManager',b'System.load',b'Class.forName',b'ProcessBuilder'))
OUT.mkdir()
WORK.mkdir(mode=0o700)
sources=WORK/'main-selected'
tests=WORK/'test-classes'
tests.mkdir()
with ZipFile(jar) as z, ZipFile(closure_jar) as independent:
    members={entry for entry in z.namelist() if entry.endswith('.class')}
    assert len(members)==79 and {n+'.class' for n in NAMES}<=members
    for code in sorted(NAMES):
        name=code+'.class'
        body=z.read(name)
        assert body==independent.read(name) and int.from_bytes(body[6:8],'big')==69
        p=sources/name
        p.parent.mkdir(parents=True,exist_ok=True)
        p.write_bytes(body)
original_classes=sorted(sources.rglob('*.class'))
assert len(original_classes)==3
console=TC/'junit-platform-console-standalone-1.13.4.jar'
jspecify=M2/'org/jspecify/jspecify/1.0.1/jspecify-1.0.1.jar'
cp=os.pathsep.join(map(str,(sources,jspecify,console)))
steps={}
def stage(name,argv):
    cmd=list(map(str,argv))
    p=subprocess.run(cmd,capture_output=True,timeout=90,check=False)
    a,b=WORK/(name+'.stdout'),WORK/(name+'.stderr')
    a.write_bytes(p.stdout)
    b.write_bytes(p.stderr)
    steps[name]=dict(argv=cmd,actualExit=p.returncode,stdout=ref(a),stderr=ref(b))
    (OUT/(name+'-exit.json')).write_text(json.dumps(steps[name],indent=2)+'\n')
    assert p.returncode==0,(name,p.returncode)
    return p.stdout.decode()
stage('compile-test',[JDK/'javac','--release','25','-Werror','-Xlint:all','-proc:none','-cp',cp,'-d',tests,fixture])
agent=M2/'org/jacoco/org.jacoco.agent/0.8.15/org.jacoco.agent-0.8.15-runtime.jar'
capture=WORK/'ordinary-unit.exec'
test_name=JAVA_PKG+'.'+fixture.stem
stage('unit',[JDK/'java',f'-javaagent:{agent}=destfile={capture},sessionid={RUN}','-cp',str(tests)+os.pathsep+cp,
 'org.junit.platform.console.ConsoleLauncher','execute','--disable-ansi-colors','--fail-if-no-tests','--select-class',test_name,
 '--reports-dir',WORK/'reports'])
original_xml=WORK/'reports/TEST-junit-jupiter.xml'
public=OUT/'jupiter.xml'
xml=ET.parse(original_xml).getroot()
expected=set(re.findall(r'\bvoid (defaults0\d\d\w+)\(',source_fixture.decode()))
assert len(expected)==4 and xml.get('tests')=='4'
assert {case.get('name').removesuffix('()') for case in xml.findall('testcase')}==expected
assert all(int(xml.get(a))==0 for a in ('errors','failures','skipped'))
xml_redaction=copy_public_evidence(original_xml,public)
exec_probe=decode(capture.read_bytes(),NAMES,strict_class_names=True)
assert len(exec_probe['sessions'])==1 and bytes.fromhex(exec_probe['sessions'][0]['labelBytesHex']).decode()==RUN
tools_cls=WORK/'reader'
libs=[M2/'org/jacoco/org.jacoco.core/0.8.15/org.jacoco.core-0.8.15.jar',*(
    M2/f'org/ow2/asm/{a}/9.10.1/{a}-9.10.1.jar' for a in ('asm','asm-commons','asm-tree'))]
tool_cp=os.pathsep.join(map(str,libs))
stage('compile-reader',[JDK/'javac','--release','25','-Werror','-Xlint:all','-proc:none','-cp',tool_cp,'-d',tools_cls,
 R/'tools/quality/jacoco/UnfilteredCodeMeasurement.java'])
text=stage('raw',[JDK/'java','-cp',str(tools_cls)+os.pathsep+tool_cp,
 'org.jacoco.core.internal.analysis.UnfilteredCodeMeasurement','--strict-original-exec',capture,*original_classes])
measurement={}
for line in text.splitlines():
    parts=line.split('\t')
    if parts[0]=='CLASS':
        name=parts[1]
        assert int(parts[2],16)==int(exec_probe['classes'][name]['crc64'],16)
        measurement[name]={k:dict(missing=int(m),covered=int(c)) for k,m,c in (item.split(':') for item in parts[6:])}
assert set(measurement)==NAMES
top=measurement[PREFIX+'/DirectoryCalls']
assert {k:top[k] for k in ('LINE','METHOD','CLASS','BRANCH')}=={
    'LINE':{'missing':0,'covered':3},'METHOD':{'missing':0,'covered':3},'CLASS':{'missing':0,'covered':1},'BRANCH':{'missing':0,'covered':0}}
(OUT/'raw.tsv').write_text(text)
result=dict(run=RUN,actualExit=0,terminalAtUTC=datetime.now(timezone.utc).isoformat(),source=current,
    currentCore='2611e1acbd57955d591d52e5348999ea293e068d',previous=ref(old_proof),packaging=ref(release),static=ref(static),
    originalJar=artifact,independentlyMatchingClassBytes=[ref(p) for p in original_classes],fixture=ref(fixture),
    exposedPackageTypes=3,tests=4,failures=0,errors=0,skipped=0,notRun=0,newTests=0,
    actualFilesystemOrDescriptorActions=0,backendActions=0,productRebuilds=0,singleExec=True,crcMatched=3,noWarmupUnion=True,
    jupiter=ref(public),xmlRedaction=xml_redaction,readerProbe=ref(capture),raw=ref(OUT/'raw.tsv'),classCounters=measurement,
    rawDirectoryCalls=top,actualNative=False,formalDelta=0,whole451=False,steps=steps)
(OUT/'manifest.json').write_text(json.dumps(result,indent=2)+'\n')
print(RUN,result['tests'],top)
