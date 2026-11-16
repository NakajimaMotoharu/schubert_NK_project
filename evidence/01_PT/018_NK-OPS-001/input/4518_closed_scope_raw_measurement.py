"""Unfiltered every-physical measurement of one original exec; no product execution or exclusions."""
from pathlib import Path
import datetime
import hashlib
import json
import subprocess
import sys

r=Path.cwd();sys.path.insert(0,str(r/'tools/quality'))
import pgpt_closed_host_profile as policy
b=r/'evidence/01_PT/018_NK-OPS-001'
load=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
ref=lambda p:dict(path=str(p.relative_to(r)),sha256=sha(p))
c=load(Path(sys.argv[1]));out=Path(sys.argv[2]);assert out.parent==b/'evidence' and not out.exists()
post_path=r/c['slots']['post']/'manifest.json';post=load(post_path)
prepared=load(r/c['slots']['prepare']/'manifest.json')
assert post['actualExit']==0 and post['tests']==c['expectedTests'] and not post['oldExecCombined']
folder=r.parent/'pgpt-runs/PG379'/c['privateDirs']['prepare']/'component'
names=sorted(prepared['physicalClassHashes']);assert set(names)==set(c['physicalClasses'])
for name in names:policy.relative_name(name)
files=[folder/name for name in names];assert {n:sha(p) for n,p in zip(names,files)}==prepared['physicalClassHashes']
for name,h in post['inputHashes'].items():
    assert sha(r/name)==h==hashlib.sha256(subprocess.check_output(['git','show',post['source']+':'+name])).hexdigest()
def crc(raw):
    assert int.from_bytes(raw[6:8],'big')==69
    value=0
    for byte in raw:
        value^=byte
        for _ in range(8):value=(value>>1)^0xd800000000000000 if value&1 else value>>1
    return f'{value:016x}'
ids={n[:-6]:crc(p.read_bytes()) for n,p in zip(names,files)};assert ids==post['classIds']
compiled=load(b/'evidence/PG31432-generated-code-supplemental-tool-v1/compile.json')
selftest=load(b/'evidence/PG31434-generated-code-tool-selftest-v1/manifest.json')
assert selftest['actualExit']==0 and selftest['toolTests']==12
for pin in compiled['dependencies']+[dict(path=str(r/compiled['source']['path']),sha256=compiled['source']['sha256'])]:
    assert sha(Path(pin['path']))==pin['sha256']
exec_file=post_path.parent/'jacoco.exec';assert sha(exec_file)==post['files']['jacoco.exec']
tool=r.parent/'pgpt-runs/PG379/pg31432-generated-code-supplemental-tool-v1/toolclasses'
command=[str(r.parent/'toolchain/jdk-25.0.4/bin/java'),'-cp',':'.join([str(tool),*[x['path'] for x in compiled['dependencies']]]),
    'org.jacoco.core.internal.analysis.UnfilteredCodeMeasurement',str(exec_file),*map(str,files)]
out.mkdir();start=datetime.datetime.now(datetime.timezone.utc).isoformat()
result=subprocess.run(command,capture_output=True,timeout=60)
(out/'analysis.stdout').open('xb').write(result.stdout);(out/'analysis.stderr').open('xb').write(result.stderr)
assert result.returncode==0
classes={};methods=[]
for line in result.stdout.decode().splitlines():
    fields=line.split('\t')
    if fields[0]=='CLASS':
        assert len(fields)==12;row=dict(name=fields[1],id=fields[2],dataPresent=fields[3]=='true',probes=int(fields[4]),access=int(fields[5]),counters={})
        classes[fields[1]]=row;offset=6
    else:
        assert fields[0]=='METHOD' and len(fields)==11
        row=dict(className=fields[1],name=fields[2],descriptor=fields[3],access=int(fields[4]),counters={});methods.append(row);offset=5
    for value in fields[offset:]:
        key,missed,covered=value.split(':');row['counters'][key]=dict(missed=int(missed),covered=int(covered))
assert set(classes)==set(ids) and all(row['id']==ids[n] for n,row in classes.items())
assert len(methods)==sum(post['actualJvmCodeMethodCounts'].values())
keys=['LINE','METHOD','CLASS','BRANCH','INSTRUCTION']
targets=set(c['targetClasses'])
totals={key:{role:sum(classes[n]['counters'][key][role] for n in targets) for role in ['missed','covered']} for key in keys}
assert {n:sha(p) for n,p in zip(names,files)}==prepared['physicalClassHashes'] and sha(exec_file)==post['files']['jacoco.exec']
for name,h in post['files'].items():assert sha(post_path.parent/name)==h
measure=dict(actualExit=0,terminalAtUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),
    sourceCore=c['productionCoreMain'],unitSource=post['source'],run=c['id'],tests=post['tests'],
    originalPost=ref(post_path),originalExec=ref(exec_file),rawMeasurementCommand=command,
    rawMeasurementExit=result.returncode,rawMeasurementStartUTC=start,classes=classes,methods=methods,
    independentCrc=ids,allPhysicalHashes=prepared['physicalClassHashes'],allPhysicalClassesRetained=True,
    targetClasses=sorted(targets),targetRawCounters=totals,
    targetRawFour100=all(totals[k]['missed']==0 and totals[k]['covered']>0 for k in keys[:4]),
    componentRawFour100=all(row['counters'][k]['missed']==0 for row in classes.values() for k in keys[:4]),
    helperMissedMethods=[x for x in methods if x['className'] not in targets and x['counters']['METHOD']['missed']],
    files={p.name:sha(p) for p in out.iterdir() if p.is_file()},manualExclusions=[],oldExecCombined=False,
    measurementProductDefinitionsOrInitialization=0,measurementApplicationTests=0,formalUpdated=False,newAcceptance=0)
(out/'manifest.json').open('x').write(json.dumps(measure,indent=2)+'\n')
print(json.dumps(dict(actualExit=0,tests=post['tests'],physical=len(classes),targetCounters=totals,
    targetRawFour100=measure['targetRawFour100'],wholeComponentRawFour100=measure['componentRawFour100'])))
