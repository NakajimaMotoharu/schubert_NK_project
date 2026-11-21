"""Independently check the current ordinary JDBC Outbox run and record its exact boundary."""
from datetime import datetime,timezone
from hashlib import sha256
import json,os,subprocess
from pathlib import Path
from xml.etree import ElementTree as ET
from jacoco_readonly_exec_subset import decode

R=Path.cwd()
OPS=R/'evidence/01_PT/018_NK-OPS-001/evidence'
TC=R.parent/'toolchain'
JDK=TC/'jdk-25.0.4/bin'
UNIT=next(OPS.glob('PG41410*/manifest.json'))
OUT=OPS/'PG41412-p00405-outbox-jdbc-independent-v1'
WORK=R.parent/'pgpt-runs/PG379'/OUT.name

def pin(p):
    return dict(path=str(p),sha256=sha256(p.read_bytes()).hexdigest())

def get(row):
    p=Path(row['path'])
    assert pin(p)==row
    return p

def crc(raw):
    value=0
    for byte in raw:
        value^=byte
        for _ in range(8):
            value=((value>>1)^0xd800000000000000) if value&1 else value>>1
    return f'{value:016x}'

report=json.loads(UNIT.read_bytes())
assert report['actualExit']==report['failures']==report['errors']==report['skipped']==report['notRun']==0
assert report['driverClasspathEntries']==report['actualDbOps']==report['heldClassesOpened']==0
assert len(report['currentMainInputs'])==10 and report['tests']==12
for item in report['currentMainInputs']+report['unchangedJdkProxyTestInputs']:
    get(item)
xml=ET.parse(get(report['jupiter'])).getroot()
assert xml.get('tests')=='12' and not any(xml.findall('.//'+n) for n in ('failure','error','skipped'))
previous=json.loads(get(report['oldIndependent']).read_bytes())
files={p.as_posix().split('/target/classes/',1)[1].removesuffix('.class'):p for p in map(get,report['currentClassFiles'])}
assert len(files)==10 and set(files)==set(previous['rawPerClass'])
measured={n for n in files if not n.endswith('/package-info')}
unit_exec=get(report['originalExec'])
independent=decode(unit_exec.read_bytes(),measured)
assert len(independent['sessions'])==1 and len(independent['classes'])==len(measured)==8
assert bytes.fromhex(independent['sessions'][0]['labelBytesHex']).decode('ascii')==report['run']
assert all(int(independent['classes'][n]['crc64'],16)==int(crc(files[n].read_bytes()),16) for n in measured)
m2=TC/'m2/repository'
deps=[m2/'org/jacoco/org.jacoco.core/0.8.15/org.jacoco.core-0.8.15.jar',*(
    m2/f'org/ow2/asm/{n}/9.10.1/{n}-9.10.1.jar' for n in ('asm','asm-commons','asm-tree'))]
cp=os.pathsep.join(map(str,deps))
OUT.mkdir()
WORK.mkdir(mode=0o700)
steps={}
def run(name,argv):
    cmd=list(map(str,argv))
    process=subprocess.run(cmd,capture_output=True,timeout=90,check=False)
    out,err=OUT/(name+'.stdout.txt'),OUT/(name+'.stderr.txt')
    out.write_bytes(process.stdout)
    err.write_bytes(process.stderr)
    steps[name]=dict(argv=cmd,actualExit=process.returncode,stdout=pin(out),stderr=pin(err))
    assert process.returncode==0
    return process.stdout.decode()
target=WORK/'analyzer'
analyzer=R/'tools/quality/jacoco/UnfilteredCodeMeasurement.java'
run('compile-raw',[JDK/'javac','--release','25','-proc:none','-Xlint:all','-Werror','-cp',cp,'-d',target,analyzer])
raw=run('raw',[JDK/'java','-cp',str(target)+os.pathsep+cp,'org.jacoco.core.internal.analysis.UnfilteredCodeMeasurement',
    '--strict-original-exec','--line-deficits',unit_exec,*files.values()])
all_codes={}
for line in raw.splitlines():
    fields=line.split('\t')
    if fields[0]=='CLASS':
        name=fields[1]
        assert name not in all_codes and fields[2]==crc(files[name].read_bytes())
        all_codes[name]={key:dict(missed=int(missed),covered=int(covered))
            for key,missed,covered in (s.split(':') for s in fields[6:])}
assert set(all_codes)==set(files)
repo=next(n for n in files if n.endswith('/JdbcOutboxRepository'))
counters=all_codes[repo]
assert all(counters[k]['missed']==0 for k in ('LINE','METHOD','CLASS','BRANCH'))
assert previous['whole451Accepted'] is False
framework=next(OPS.glob('PG40580*/manifest.json'))
f=json.loads(framework.read_bytes())
assert f['explicitExitDependencies']==['WBS-F02','WBS-F03']
assert {Path(x['owner']).stem for x in f['localOwnerSourceBindings']}=={'RequiredColumn','LogProjectionDatabaseException'}
for item in f['localOwnerSourceBindings']:
    assert not subprocess.check_output(['git','diff','--name-only',f['productionCore'],report['testedSource'],'--',item['owner'],*item['fixtureFiles']])
result=dict(run=OUT.name,actualExit=0,terminalAtUTC=datetime.now(timezone.utc).isoformat(),source=report['testedSource'],core=report['productionCore'],
    unit=pin(UNIT),scopeOwnersPrior=pin(framework),physicalClasses=10,executedPositiveCrc=8,originalExecMerged=False,
    tests=12,passed=12,failure=0,notRun=0,rawRepository=counters,classes=all_codes,previousRawRepository=previous['rawPerClass'][repo],
    separateReferenceScopeSource=pin(next(OPS.glob('PG41406*/manifest.json'))),
    unchangedOriginalComponentOwners=2,totalOriginalComponentOwners=4,actualDbAcceptance=False,
    whole451=False,wholeP00405=False,formalDelta=0,steps=steps)
(OUT/'manifest.json').write_text(json.dumps(result,indent=2)+'\n')
print(counters,len(all_codes))
