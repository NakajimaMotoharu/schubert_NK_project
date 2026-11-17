"""Measure all176 physical Protocol classes including all163 Code classes and four default-filtered javac maps from the current single execution."""
from pathlib import Path
import datetime
import hashlib
import json
import subprocess
import xml.etree.ElementTree as ET
import pgpt_closed_host_profile as policy

root=Path.cwd();base=root/'evidence/01_PT/018_NK-OPS-001'
load=lambda path:json.loads(path.read_text())
sha=lambda path:hashlib.sha256(path.read_bytes()).hexdigest()
ref=lambda path:dict(path=str(path.relative_to(root)),sha256=sha(path))
postdir=base/'evidence/PG37654-ssc452-grammar-post-v2'
post=load(postdir/'manifest.json');assert post['actualExit']==0 and post['tests']==156
prep=load(base/'evidence/PG37646-ssc452-grammar-prepare-v2/manifest.json');post['physicalClassHashes']=prep['physicalClassHashes']
names=sorted(post['physicalClassHashes']);assert len(names)==len(set(names))==176
for name in names:policy.relative_name(name)
# Only after the exact176 permitted names are admitted may their pinned class files be accessed.
classdir=root.parent/'pgpt-runs/PG379/pg37646-ssc452-grammar-v2/component'
files=[classdir/name for name in names];before={name:sha(path) for name,path in zip(names,files)}
assert before==post['physicalClassHashes']
assert all(sha(root/path)==value for path,value in post['inputHashes'].items())
execpath=postdir/'jacoco.exec';xmlpath=postdir/'original-coverage.xml'
assert sha(execpath)==post['files']['jacoco.exec'] and sha(xmlpath)==post['files']['original-coverage.xml']
default_classes={node.attrib['name']:node for node in ET.parse(xmlpath).getroot().findall('.//package/class')}
assert set(default_classes)<=set(post['classIds'])
assert set(post['classIds'])-set(default_classes)<=set(post['naturalNoCodeClasses'])
compiled=load(base/'evidence/PG31432-generated-code-supplemental-tool-v1/compile.json')
selftest=load(base/'evidence/PG31434-generated-code-tool-selftest-v1/manifest.json')
assert selftest['actualExit']==0 and selftest['toolTests']==12
for pin in compiled['dependencies']+[dict(path=str(root/compiled['source']['path']),sha256=compiled['source']['sha256'])]:assert sha(Path(pin['path']))==pin['sha256']

def crc64(binary):
    assert int.from_bytes(binary[6:8],'big')==69
    value=0
    for byte in binary:
        value^=byte
        for _ in range(8):value=(value>>1)^0xd800000000000000 if value&1 else value>>1
    return f'{value:016x}'

independent_crc={name[:-6]:crc64(path.read_bytes()) for name,path in zip(names,files)}
assert independent_crc==post['classIds']
output=base/'evidence/PG37666-ssc452-grammar-unfiltered-v1';assert not output.exists();output.mkdir()
toolwork=root.parent/'pgpt-runs/PG379/pg31432-generated-code-supplemental-tool-v1'
classpath=':'.join([str(toolwork/'toolclasses'),*[pin['path'] for pin in compiled['dependencies']]])
command=[str(root.parent/'toolchain/jdk-25.0.4/bin/java'),'-cp',classpath,'org.jacoco.core.internal.analysis.UnfilteredCodeMeasurement',str(execpath),*map(str,files)]
started=datetime.datetime.now(datetime.timezone.utc).isoformat();result=subprocess.run(command,capture_output=True,timeout=60)
(output/'analysis.stdout').open('xb').write(result.stdout);(output/'analysis.stderr').open('xb').write(result.stderr)
(output/'analysis-exit.json').open('x').write(json.dumps(dict(command=command,actualExit=result.returncode,startedUTC=started,completedUTC=datetime.datetime.now(datetime.timezone.utc).isoformat()),indent=2)+'\n')
assert result.returncode==0,result.stderr.decode()[:800]
classes={};methods=[]
for line in result.stdout.decode().splitlines():
    fields=line.split('\t')
    if fields[0]=='CLASS':
        assert len(fields)==12;name=fields[1];assert name not in classes
        row=dict(name=name,id=fields[2],dataPresent=fields[3]=='true',probes=int(fields[4]),access=int(fields[5]),counters={});classes[name]=row;start=6
    else:
        assert fields[0]=='METHOD' and len(fields)==11
        row=dict(className=fields[1],name=fields[2],descriptor=fields[3],access=int(fields[4]),counters={});methods.append(row);start=5
    for item in fields[start:]:
        kind,missed,covered=item.split(':');row['counters'][kind]=dict(missed=int(missed),covered=int(covered))
assert set(classes)==set(independent_crc) and all(value['id']==independent_crc[name] for name,value in classes.items())
for name,value in classes.items():assert sum(value['counters']['METHOD'].values())==post['actualJvmCodeMethodCounts'][name]
def default_methods(name):
    node=default_classes.get(name)
    if node is None:return set()
    return {(method.attrib['name'],method.attrib['desc']) for method in node.findall('method') if any(counter.attrib['type']=='METHOD' and int(counter.attrib['missed'])+int(counter.attrib['covered'])>0 for counter in method.findall('counter'))}
filtered=[method for method in methods if (method['name'],method['descriptor']) not in default_methods(method['className'])]
missed=[method for method in methods if method['counters']['METHOD']['missed']]
counter={kind:dict(missed=sum(value['counters'][kind]['missed'] for value in classes.values()),covered=sum(value['counters'][kind]['covered'] for value in classes.values())) for kind in classes[names[0][:-6]]['counters']}
assert sum(counter['METHOD'].values())==len(methods)==sum(post['actualJvmCodeMethodCounts'].values())
assert len(filtered)==len(methods)-sum(post['coverage']['METHOD'].values())
assert before=={name:sha(path) for name,path in zip(names,files)} and sha(execpath)==post['files']['jacoco.exec']
assert all(sha(root/path)==value for path,value in post['inputHashes'].items())

all100=all(counter[k]['missed']==0 for k in ['LINE','METHOD','CLASS','BRANCH','INSTRUCTION'])
report=dict(actualExit=0,terminalAtUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),source=post['source'],productionCoreMain=post['productionCoreMain'],tests=156,failed=0,errors=0,skipped=0,notRun=0,originalPost=ref(postdir/'manifest.json'),originalPrepare=ref(base/'evidence/PG37646-ssc452-grammar-prepare-v2/manifest.json'),originalSingleExec=ref(execpath),classFileHashes=before,independentCrc=independent_crc,classes=classes,methods=methods,all176PhysicalRawCounters=counter,all176PhysicalRawAll100=all100,actualCodeMethods=len(methods),codeClasses=sum(sum(v['counters']['METHOD'].values())>0 for v in classes.values()),naturalNoCodeClasses=[n for n,v in classes.items() if sum(v['counters']['METHOD'].values())==0],defaultFilteredMethods=filtered,missedCodeMethods=missed,missedBranchMethods=[m for m in methods if m['counters']['BRANCH']['missed']],wholeModuleMeasured=True,wholeSixModule451Accepted=False,manualCoverageExclusions=[],oldExecUnion=False,productionClassesDefinedByAnalyzer=0,actualBackendRootNativeVmKeyOperations=0,heldClassfileActions=0,toolSelftest12Replayed=False,formalUpdated=False,newAcceptance=0,effortCompletionRate=None,files={p.name:sha(p) for p in output.iterdir()})
(output/'manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(dict(actualExit=0,physical=len(names),methods=len(methods),rawAll100=all100,counters=counter))
