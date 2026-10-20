"""Read original partial API red; never repeat it or count skipped Web as executed."""
import json
import os
import xml.etree.ElementTree as ET
from pg5774_jms_primary_selected import RED
from pg5540_snapshot_scratch_selected import ROOT,sha


def main():
    w=ROOT.parent/'pgpt-runs/PG379';path=w/'pg5774-jms-primary-red-v1/manifest.safe.json';v=json.loads(path.read_bytes());snapshot=path.parent/'source'
    q=json.loads((ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG5754-current3932-cases/qualification.json').read_bytes());static=json.loads((w/'pg5750-exception-static-v1/manifest.safe.json').read_bytes())
    if not(v['actualExit']==1 and v['phaseExits']==[0,1]and v['tests']==12 and v['suites']==6 and not v['purposefulRedEstablished']):raise ValueError('original incomplete red retained exactly')
    if {tuple(r)for r in v['failedOrSkipped']}!={r for r in RED if '.api.'in r[0]}:raise ValueError('exact original two API purpose assertions')
    physical=v['allPhysicalMainSha256'];missing=set(q['allPhysicalMainSha256'])-set(physical)
    if not missing or missing!={k for k in q['allPhysicalMainSha256']if k.startswith('web:')}or any(q['allPhysicalMainSha256'][k]!=h for k,h in physical.items()):raise ValueError('all actual five-module bytes match; only Web is unbuilt')
    if {p.relative_to(snapshot).as_posix():sha(p)for p in snapshot.glob('src/*/src/main/java/**/*.java')}!=static['allSourceHashes']:raise ValueError('all849 Main source unchanged')
    failures=[]
    for p in snapshot.glob('src/*/target/surefire-reports/TEST-*.xml'):
        for case in ET.parse(p).getroot().findall('testcase'):
            if any(c.tag in('error','skipped','flakyFailure','flakyError','rerunFailure','rerunError')for c in case.iter()):raise ValueError('no unexpected XML error/flaky/skip accepted')
            for f in case.findall('failure'):failures.append({'class':case.get('classname'),'method':case.get('name'),'type':f.get('type'),'message':f.get('message')})
    if len(failures)!=2 or any(f['type']!='org.opentest4j.AssertionFailedError'or'IllegalArgumentException'not in f['message']for f in failures):raise ValueError('self-suppression purpose only')
    value={'assessmentExit':0,'originalActualExit':1,'originalSource':v['source'],'productionMainSource':q['productionSource'],'originalManifestSha256':sha(path),'purposefulApiRedEstablished':True,'wholeRedEstablished':False,'webTestsNotRun':2,'apiPurposeFailures':failures,'actualCompiledMainClasses':len(physical),'actualAllCompiledBytesEqualBaseline':True,'unbuiltMainClasses':len(missing),'all849MainSourceUnchanged':True,'testsReexecuted':0,'formalAccepted':False,'ptAlternativeCompleted':0}
    os.umask(0o077);out=w/'pg5774-red-api-assessment-v1';out.mkdir(mode=0o700)
    with(out/'manifest.safe.json').open('x')as f:json.dump(value,f,sort_keys=True);f.flush();os.fsync(f.fileno())
    print(json.dumps(value));print(json.dumps({'manifestSha256':sha(out/'manifest.safe.json')}))


if __name__=='__main__':main()
