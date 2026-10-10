"""Exact current production class byte and real owned test child capture; not global union."""
import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess
import xml.etree.ElementTree as ET
from pg1271_current_native_gap import W,J,SOURCE,HOST_SHA,require,sha


def qualify(raw, lower_ms, upper_ms):
    root=ET.fromstring(raw)
    sessions=root.findall('sessioninfo')
    require(len(sessions)==2 and len({s.attrib['id']for s in sessions})==2)
    require(all(lower_ms<=int(s.attrib['start'])<=int(s.attrib['dump'])<=upper_ms for s in sessions))
    classes=[c for p in root.findall('package')for c in p.findall('class')if c.attrib['name']=='dev/codex/schubert/nk/bootstrap/FixedNativeCoverageStopHold']
    require(len(classes)==1)
    counters={c.attrib['type']:{'missed':int(c.attrib['missed']),'covered':int(c.attrib['covered'])}for c in classes[0].findall('counter')}
    require(all(counters[k]['missed']==0 and counters[k]['covered']>0 for k in ['LINE','METHOD','CLASS','BRANCH']))
    return {'sessionCount':2,'sameClassByteMatch':True,'classCounters':counters,'wholeBootstrapOrFormalAccepted':False}


def main():
    os.umask(0o077)
    host=W/'pg1018-stream-six-host-v2';selected=W/'pg1272-stop-hold-selected-v1'
    h=json.loads((host/'manifest.safe.json').read_bytes());s=json.loads((selected/'manifest.safe.json').read_bytes())
    require(sha(host/'manifest.safe.json')==HOST_SHA and h['candidateSource']==SOURCE and s['actualExit']==0 and s['productionSource']==SOURCE and s['testCounts']=={'tests':6,'failures':0,'errors':0,'skipped':0}and s['staticIssues']==0)
    execfile=selected/'selected.exec';require(sha(execfile)==s['execSha256'])
    jar=host/'bootstrap/schubert-nk-bootstrap-0.1.0-SNAPSHOT.jar';require(sha(jar)==h['moduleResults']['bootstrap']['jarSha256'])
    target=W/'pg1273-stop-hold-selected-counter-v1';require(not os.path.lexists(target));target.mkdir(mode=0o700)
    cp=[str(W/'pg1271-current-native-gap-v1/classes')]
    repo=Path('/home/mini/codex/project1/work/toolchain/m2/repository')
    for pattern in ('org/jacoco/org.jacoco.core/0.8.15/*.jar','org/jacoco/org.jacoco.report/0.8.15/*.jar','org/ow2/asm/asm/9.10.1/*.jar','org/ow2/asm/asm-tree/9.10.1/*.jar','org/ow2/asm/asm-commons/9.10.1/*.jar'):
        paths=list(repo.glob(pattern));require(len(paths)==1);cp.append(str(paths[0]))
    xml=target/'selected.xml'
    result=subprocess.run([str(J/'java'),'-cp',':'.join(cp),'NativeCoverageXml471',str(jar),str(xml),str(execfile)],capture_output=True,timeout=45)
    with(target/'counter.private.log').open('xb')as f:f.write(result.stdout);f.write(result.stderr);f.flush();os.fsync(f.fileno())
    require(result.returncode==0 and not result.stderr and b'classMismatch0=true'in result.stdout)
    millis=lambda stamp:int(datetime.datetime.fromisoformat(stamp).timestamp()*1000)
    value=qualify(xml.read_bytes(),millis(s['startedUTC'])-1000,millis(s['completedUTC'])+1000)
    value.update(actualExit=0,productionSource=SOURCE,selectedOperatorSource=s['operatorSource'],testCount=6,selectedManifestSha256=sha(selected/'manifest.safe.json'),selectedExecSha256=sha(execfile),xmlSha256=sha(xml),oldNativeOrHostExecImported=False,appNativeEvidence=False,sourceOrClassExclusions=False)
    with(target/'manifest.safe.json').open('x')as f:json.dump(value,f,sort_keys=True);f.flush();os.fsync(f.fileno())
    print(json.dumps(dict(value,manifestSha256=sha(target/'manifest.safe.json'))));return 0


if __name__=='__main__':raise SystemExit(main())
