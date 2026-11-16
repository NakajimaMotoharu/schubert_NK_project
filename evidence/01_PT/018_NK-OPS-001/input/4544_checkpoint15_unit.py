"""One ordinary current-source whole15 JUnit JVM; no application entrypoints/native exporters."""
from pathlib import Path
import datetime
import hashlib
import json
import platform
import re
import subprocess
import sys
import xml.etree.ElementTree as ET

r=Path.cwd();sys.path.insert(0,str(r/'tools/quality'))
import pg9666_pagination_static as stage
b=r/'evidence/01_PT/018_NK-OPS-001';tc=r.parent/'toolchain'
load=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
pp=b/'evidence/PG36976-checkpoint15-prepare-static-v2/manifest.json';p=load(pp)
ap=b/'evidence/PG36980-checkpoint15-static-admission-v2/manifest.json';admission=load(ap)
assert p['actualExit']==admission['actualExit']==0 and admission['applicable']==admission['unclassified']==0
assert admission['prepare']==dict(path=str(pp.relative_to(r)),sha256=sha(pp))
unit=sys.argv[1];assert re.fullmatch('[0-9a-f]{40}',unit)
assert unit==subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
inputs={**p['mainInputHashes'],**p['testSourceHashes']}
for path,h in inputs.items():
    assert sha(r/path)==h==hashlib.sha256(subprocess.check_output(['git','show',unit+':'+path])).hexdigest()
work=Path(p['work']);classes=work/'test-classes';component=work/'component'
assert all(sha(component/n)==h for n,h in p['physicalClassHashes'].items())
assert {str(f.relative_to(classes)):sha(f) for f in classes.rglob('*.class')}==p['testPhysicalHashes']
assert all(sha(Path(path))==h for path,h in p['toolDependencyHashes'].items())
out=b/'evidence/PG36982-checkpoint15-unit-v1';slot=r.parent/'pgpt-runs/PG379/pg36982-checkpoint15-unit-v1'
assert not out.exists() and not slot.exists();out.mkdir();slot.mkdir();xml=slot/'xml';xml.mkdir()
session='PG36982-CHECKPOINT-PUBLIC15';agent=tc/'m2/repository/org/jacoco/org.jacoco.agent/0.8.15/org.jacoco.agent-0.8.15-runtime.jar'
command=[str(tc/'jdk-25.0.4/bin/java'),'-Dfile.encoding=UTF-8','-Duser.timezone=Asia/Tokyo',
    '-Xlog:class+init=info:file='+str(slot/'class-init.log'),
    '-javaagent:'+str(agent)+'=destfile='+str(slot/'jacoco.exec')+',append=false,sessionid='+session,
    '-cp',str(classes)+':'+p['classpath'],'org.junit.platform.console.ConsoleLauncher','execute',
    '--disable-banner','--details=summary','--fail-if-no-tests','--reports-dir',str(xml)]
expected=[]
for path,count in p['wholeTestSourceCounts'].items():
    text=(r/path).read_text();package=re.search(r'package ([\w.]+);',text).group(1)
    command+=['--select-class',package+'.'+Path(path).stem]
    expected.extend((package+'.'+Path(path).stem,n+'()') for n in re.findall(r'@Test\s+void\s+(\w+)\s*\(',text))
assert len(expected)==15 and len(set(expected))==15
begin=dict(source=unit,sourceCore=p['sourceCore'],branch=subprocess.check_output(['git','branch','--show-current'],text=True).strip(),
    run=session,atUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),os=platform.platform(),
    command=command,expectedTests=15,expectedCases=expected,inputHashes=inputs,
    prepare=dict(path=str(pp.relative_to(r)),sha256=sha(pp)),staticAdmission=dict(path=str(ap.relative_to(r)),sha256=sha(ap)),
    measurementAgentSha256=sha(agent),reservedNativeAgentSelected=False,knownSourceChange='BUG2803 three preserveFatal catalogs, original whole12 oracle semantics kept; three new fatal tests')
(out/'begin.json').open('x').write(json.dumps(begin,indent=2)+'\n')
stage.SLOT=out;stage.ENV=dict(PATH=str(tc/'jdk-25.0.4/bin')+':/usr/bin:/bin',JAVA_HOME=str(tc/'jdk-25.0.4'),LANG='C.UTF-8')
result=stage.step('whole15',command,slot,timeout=120)
cases=[];failures=errors=skipped=0
for file in sorted(xml.glob('TEST-*.xml')):
    root=ET.parse(file).getroot();failures+=int(root.get('failures',0));errors+=int(root.get('errors',0));skipped+=int(root.get('skipped',0))
    for case in root.findall('testcase'):cases.append(dict(classname=case.get('classname'),name=case.get('name'),result='PASS' if not list(case) else 'NON_PASS'))
value=dict(begin,actualExit=result['actualExit'],timedOut=result['timedOut'],terminalAtUTC=result['endUTC'],
    tests=len(cases),cases=cases,failures=failures,errors=errors,skipped=skipped,
    notRun=len(set(expected)-{(x['classname'],x['name']) for x in cases}),stage=result,
    execSha256=sha(slot/'jacoco.exec') if (slot/'jacoco.exec').is_file() else None,
    classInitLogSha256=sha(slot/'class-init.log') if (slot/'class-init.log').is_file() else None,
    xmlHashes={f.name:sha(f) for f in xml.glob('TEST-*.xml')},
    productEntryPointsInvoked=False,actualDbNetworkVmRootKeyIntentOperations=0,
    nativeBoundaryAbsence='INDEPENDENT_POST_PENDING',oldExecCombined=False,formalUpdated=False,newAcceptance=0)
(out/'manifest.json').open('x').write(json.dumps(value,indent=2)+'\n')
print(json.dumps({k:value[k] for k in ['actualExit','tests','failures','errors','skipped','notRun','timedOut']}))
sys.exit(result['actualExit'])
