"""Publish exact selected case identities and method counters, never raw XML properties or DB."""
import datetime
import hashlib
import json
import os
import platform
from pathlib import Path
import xml.etree.ElementTree as E

ROOT=Path(__file__).resolve().parents[2]
W=ROOT.parent/'pgpt-runs/PG379'
RUN=W/'pg4848-expiry-host-tools-selected-v1'
PUBLIC=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG4848-ssc301302-selected-v1'
SOURCE='04bbdb73b532537e3546191d72dee913b17629a0'


def sha(value):return hashlib.sha256(value).hexdigest()


def cases(raw,expected_class):
    root=E.fromstring(raw)
    if root.get('name')!=expected_class or any(root.get(k)!='0'for k in ('failures','errors','skipped')):raise ValueError('exact passed original suite first')
    records=[]
    for node in root.findall('testcase'):
        if node.get('classname')!=expected_class or not node.get('name')or any(node.find(k)is not None for k in ('failure','error','skipped','flakyFailure','flakyError','rerunFailure','rerunError')):raise ValueError('actual successful cases only')
        name=node.get('name');test_id=None
        if expected_class.endswith('.ApiAdmittedConfigurationTest'):
            if not name.startswith('ssc301')or not name[6:9].isdigit():raise ValueError('fixed SSC301 independent case mapping')
            test_id='PT-OPS-API-CONFIG-SSC301'+name[6:9]
        elif expected_class.endswith('.RetainedExpiryAuditTest'):
            if not name.startswith('ssc302')or not name[6:9].isdigit():raise ValueError('fixed SSC302 independent case mapping')
            test_id='PT-OPS-EXPIRY-AUDIT-SSC302'+name[6:9]
        records.append({'class':expected_class,'method':name,'testId':test_id,'actualResult':'PASS','newIndependentCase':test_id is not None})
    if len(records)!=int(root.get('tests','-1'))or not records or len({r['method']for r in records})!=len(records):raise ValueError('nonempty unique exact declared case count')
    return records


def main():
    result=json.loads((RUN/'manifest.safe.json').read_bytes());begin=json.loads((RUN/'begin.safe.json').read_bytes())
    if not(result['actualExit']==result['actualMavenExit']==0 and result['sourceSnapshot']==SOURCE and result['tests']==59 and result['suites']==10 and not result['reasons']):raise ValueError('actual combined passed59/10 fixed source first')
    for name,digest in begin['inputs'].items():
        if sha((RUN/'source'/name).read_bytes())!=digest:raise ValueError('original fixed selected input changed')
    collected=[];suites=[]
    for name,digest in result['xmlSha256'].items():
        module=next(m for m in ('protocol','storage','bootstrap','api','web','batch')if (RUN/'source'/('src/schubert-nk-'+m+'/target/surefire-reports/TEST-'+name+'.xml')).is_file())
        path=RUN/'source'/('src/schubert-nk-'+module+'/target/surefire-reports/TEST-'+name+'.xml');raw=path.read_bytes()
        if sha(raw)!=digest:raise ValueError('original actual report SHA required')
        records=cases(raw,name)
        if sorted(r['method']for r in records)!=begin['expectedMethods'][name]:raise ValueError('complete independently captured expected identity set')
        collected+=records;suites.append({'class':name,'module':module,'originalXmlSha256':digest,'tests':len(records)})
    ids={r['testId']for r in collected if r['newIndependentCase']}
    expected={'PT-OPS-API-CONFIG-SSC301'+str(i).zfill(3)for i in range(1,9)}|{'PT-OPS-EXPIRY-AUDIT-SSC302'+str(i).zfill(3)for i in range(1,15)}
    if len(collected)!=59 or ids!=expected:raise ValueError('exact22 new case IDs plus37 related cases')
    value={'kind':'LIMITED_SELECTED_EVIDENCE_NOT_FORMAL_ACCEPTANCE','actualExit':0,'actualMavenExit':0,'productionCandidateSource':SOURCE,'run':'PG4848','tests':59,'suites':10,'newIndependentCases':22,'relatedCases':37,'FESFlakyNotRun':0,'cases':collected,'suiteProofs':suites,'actualMethodCounters':result['coverage'],'wholeProgramCoverage100':False,'formalAccepted':False,'acceptedLeafDelta':0,'effortPercent':None,'wholeRegression':False,'sourceInputInventorySha256':sha(json.dumps(begin['inputs'],sort_keys=True).encode()),'originalManifestSha256':sha((RUN/'manifest.safe.json').read_bytes()),'originalBeginSha256':sha((RUN/'begin.safe.json').read_bytes()),'originalMavenLogSha256':result['mavenLogSha256'],'command':result['command'],'startedUTC':result['startUTC'],'completedUTC':result['endUTC'],'hostPostgres':begin['hostPostgres'],'environment':{'os':'Linux','jdk':'25.0.4','maven':'3.9.12','jacoco':'0.8.15','postgresql':'18.6'},'specs':['1018_API認可内設定失敗分類・SSC301単体仕様.md','1019_保持Expiry監査比較・SSC302単体仕様.md'],'linkedBugs':['BUG1388','BUG1389'],'rawPropertiesLogsDatabaseSessionExported':False,'vmActions':0,'mavenReissued':False,'recordedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat()}
    value['environment']['os']=platform.platform()
    os.umask(0o077);PUBLIC.mkdir(parents=True)
    with(PUBLIC/'manifest.json').open('x')as f:json.dump(value,f,ensure_ascii=False,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    print(json.dumps({'actualExit':0,'publicManifest':str((PUBLIC/'manifest.json').relative_to(ROOT)),'manifestSha256':sha((PUBLIC/'manifest.json').read_bytes()),'tests':59,'newIndependentCases':22,'formalAccepted':False}));return 0


if __name__=='__main__':raise SystemExit(main())
