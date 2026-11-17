"""Independent whole113 XML/session/CRC/init/raw, retaining every helper and native gap."""
from pathlib import Path
import datetime
import hashlib
import json
import re
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET

r=Path.cwd();sys.path.insert(0,str(r/'tools/quality'))
import pg9666_pagination_static as stage
b=r/'evidence/01_PT/018_NK-OPS-001';tc=r.parent/'toolchain'
load=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
ref=lambda p:dict(path=str(p.relative_to(r)),sha256=sha(p))
up=b/'evidence/PG37246-monitor-lock113-unit-v1/manifest.json';unit=load(up)
pp=b/'evidence/PG37242-monitor-lock-oracle-current-preflight-v1/manifest.json';p=load(pp)
assert unit['actualExit']==p['actualExit']==0 and unit['tests']==113
assert all(unit[k]==0 for k in ['failures','errors','skipped','notRun']) and not unit['timedOut']
assert unit['prepare']==ref(pp) and not unit['oldExecCombined']
slot=r.parent/'pgpt-runs/PG379/pg37246-monitor-lock113-unit-v1';prepared=Path(p['work'])
for path,h in unit['inputHashes'].items():
    assert sha(r/path)==h==hashlib.sha256(subprocess.check_output(['git','show',unit['source']+':'+path])).hexdigest()
expected={tuple(x) for x in unit['expectedCases']};cases=[]
def valid_case(case):
    return not any(case.findall('.//'+tag) for tag in ['failure','error','skipped']) and all(x.tag in ['system-out','system-err'] for x in case)
positive=ET.fromstring('<testcase><system-out>public report metadata</system-out></testcase>');assert valid_case(positive)
for tag in ['failure','error','skipped','unknown']:
    assert not valid_case(ET.fromstring('<testcase><'+tag+'/></testcase>'))
for name,h in unit['xmlHashes'].items():
    file=slot/'xml'/name;assert sha(file)==h;root=ET.parse(file).getroot()
    assert all(int(root.get(k,0))==0 for k in ['failures','errors','skipped'])
    for case in root.findall('testcase'):
        assert valid_case(case);cases.append((case.get('classname'),case.get('name')))
assert set(cases)==expected and len(cases)==len(expected)==113
assert sha(slot/'jacoco.exec')==unit['execSha256'] and sha(slot/'class-init.log')==unit['classInitLogSha256']
assert all(sha(prepared/'component'/n)==h for n,h in p['physicalClassHashes'].items())
out=b/'evidence/PG37248-monitor-lock113-independent-post-v1';assert not out.exists();out.mkdir()
for name in unit['xmlHashes']:shutil.copyfile(slot/'xml'/name,out/name)
for name in ['jacoco.exec','class-init.log']:shutil.copyfile(slot/name,out/name)
stage.SLOT=out;stage.ENV=dict(PATH=str(tc/'jdk-25.0.4/bin')+':/usr/bin:/bin',JAVA_HOME=str(tc/'jdk-25.0.4'),LANG='C.UTF-8')
cli=tc/'org.jacoco.cli-0.8.15-nodeps.jar';jdk=tc/'jdk-25.0.4/bin/java'
commands={'execinfo':[str(jdk),'-jar',str(cli),'execinfo',str(out/'jacoco.exec')],
 'coverage':[str(jdk),'-jar',str(cli),'report',str(out/'jacoco.exec'),'--classfiles',str(prepared/'component'),'--xml',str(out/'coverage.xml')]}
qualified=load(b/'evidence/PG31432-generated-code-supplemental-tool-v1/compile.json')
selftest=load(b/'evidence/PG31434-generated-code-tool-selftest-v1/manifest.json')
assert selftest['actualExit']==0 and selftest['toolTests']==12
for pin in qualified['dependencies']+[dict(path=str(r/qualified['source']['path']),sha256=qualified['source']['sha256'])]:assert sha(Path(pin['path']))==pin['sha256']
tool=r.parent/'pgpt-runs/PG379/pg31432-generated-code-supplemental-tool-v1/toolclasses'
names=sorted(p['physicalClassHashes'])
commands['unfiltered']=[str(jdk),'-cp',':'.join([str(tool),*[x['path'] for x in qualified['dependencies']]]),
 'org.jacoco.core.internal.analysis.UnfilteredCodeMeasurement',str(out/'jacoco.exec'),*[str(prepared/'component'/n) for n in names]]
stages={name:stage.step(name,command,out,timeout=120) for name,command in commands.items()}
assert all(x['actualExit']==0 and not x['timedOut'] for x in stages.values())
ex=(out/'execinfo.stdout').read_text();assert ex.count('Session "')==1 and 'Session "'+unit['run']+'"' in ex
probes={n:dict(crc=crc,hit=int(hit),total=int(total)) for crc,hit,total,n in re.findall(r'^([0-9a-f]{16})\s+(\d+) of\s+(\d+)\s+(\S+)$',ex,re.M)}
initializing=set(re.findall(r"Initializing '([^']+)'",(out/'class-init.log').read_text()))
forbidden=['dev/codex/schubert/nk/bootstrap/NativeCoveragePrivateFile',
 'dev/codex/schubert/nk/bootstrap/FixedServiceIdentity$NativeQuery',
 'dev/codex/schubert/nk/storage/LinuxDirectoryCalls','dev/codex/schubert/nk/storage/LinuxInodeSecurity',
 'dev/codex/schubert/nk/batch/platform/RootStartupContext',
 'dev/codex/schubert/nk/batch/platform/MorningParentBudget',
 'dev/codex/schubert/nk/storage/LinuxMonotonicClock',
 'dev/codex/schubert/nk/batch/platform/MorningServiceReadiness$NativeIo',
 'dev/codex/schubert/nk/bootstrap/CallerMonitorProbe',
 'dev/codex/schubert/nk/batch/platform/SystemctlStateSource$NativeProcess']
assert not any(any(n==f or n.startswith(f+'$') or n.startswith(f+'$$') for f in forbidden) for n in initializing)
assert not any(any(n==f or n.startswith(f+'$') for f in forbidden) and v['hit'] for n,v in probes.items())
def crc64(raw):
    assert int.from_bytes(raw[6:8],'big')==69
    value=0
    for byte in raw:
        value^=byte
        for _ in range(8):value=(value>>1)^0xd800000000000000 if value&1 else value>>1
    return f'{value:016x}'
ids={n[:-6]:crc64((prepared/'component'/n).read_bytes()) for n in names}
classes={};methods=[]
for line in (out/'unfiltered.stdout').read_text().splitlines():
    f=line.split('\t')
    if f[0]=='CLASS':
        assert len(f)==12;row=dict(name=f[1],id=f[2],dataPresent=f[3]=='true',probes=int(f[4]),access=int(f[5]),counters={});classes[f[1]]=row;offset=6
    else:
        assert f[0]=='METHOD' and len(f)==11;row=dict(className=f[1],name=f[2],descriptor=f[3],access=int(f[4]),counters={});methods.append(row);offset=5
    for item in f[offset:]:
        k,missed,covered=item.split(':');row['counters'][k]=dict(missed=int(missed),covered=int(covered))
assert set(classes)==set(ids) and all(x['id']==ids[n] for n,x in classes.items())
product={n:v for n,v in probes.items() if n in ids}
assert all(v['crc']==ids[n] and v['hit']>0 and n in initializing for n,v in product.items())
base='dev/codex/schubert/nk/batch/monitoring/'
targets={base+n for n in ['BatchMetricRecorder','MonitoringObservationClock','MonitoringPoller']};assert targets<=set(ids) and len(targets)==3
totals={k:{role:sum(classes[n]['counters'][k][role] for n in targets) for role in ['missed','covered']} for k in ['LINE','METHOD','CLASS','BRANCH','INSTRUCTION']}
assert base+'/UNKNOWN' not in classes
value=dict(actualExit=0,source=unit['source'],sourceCore=unit['sourceCore'],terminalAtUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),
    run=unit['run'],tests=113,failed=0,errors=0,skipped=0,notRun=0,unit=ref(up),prepare=ref(pp),
    actualExpectedCases=sorted(cases),caseResults=[dict(classname=c,name=n,result='PASS') for c,n in sorted(cases)],originalUnitCaseLabelsCorrected=True,consoleSchemaNegatives=4,physicalClasses=1101,targetPhysicalClasses=3,
    classIds=ids,positiveProductCrc=len(product),positiveProductClasses=product,
    forbiddenNativeInitializations=[],forbiddenNativePrefixes=forbidden,allInitializingClasses=sorted(initializing),
    targetRawCounters=totals,targetRawFour100=all(v['missed']==0 for v in totals.values()),
    whole1101RawFour100=False,classes=classes,methods=methods,
    targetMissedMethods=[x for x in methods if x['className'] in targets and any(v['missed'] for v in x['counters'].values())],
    stages=stages,jacocoCliSha256=sha(cli),rawToolSource=qualified['source'],rawToolSelf12Replayed=False,
    files={f.name:sha(f) for f in out.iterdir() if f.is_file()},
    oldExecCombined=False,manualExclusions=[],nativeExporterInvoked=False,rootVmDbKeyIntentOperations=0,
    newOriginalAcceptance=0,whole451Accepted=False,formalUpdated=False)
(out/'manifest.json').open('x').write(json.dumps(value,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(dict(actualExit=0,tests=113,targetRaw=totals,positiveProductCrc=len(product),nativeForbiddenHits=0,targetRawFour100=value['targetRawFour100'])))
