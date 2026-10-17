"""Allowlisted actual109/10 and target counters; no raw properties/logs or global credit."""
import datetime
import json
import os
import platform
import pg4852_selected_public_evidence as template
import pg4950_backup_retention_selected as selection

ROOT=selection.ROOT
RUN=ROOT.parent/'pgpt-runs/PG379/pg4952-backup-retention-selected-v1'
PUBLIC=ROOT/'evidence/01_PT/017_NK-BAT-001/evidence/provisional/PG4952-backup-retention-selected-v1'
sha=template.sha


def cases(raw,name):
    records=template.cases(raw,name)
    for record in records:
        if name.endswith('.BackupRetentionRejectionTest'):
            method=record['method'];prefix='backup4950'
            if not method.startswith(prefix)or not method[len(prefix):len(prefix)+3].isdigit():raise ValueError('fixed six Backup case identities')
            record['testId']='PT-BAK-4950-'+method[len(prefix):len(prefix)+3]
            record['newIndependentCase']=True
    return records


def main():
    result=json.loads((RUN/'manifest.safe.json').read_bytes());begin=json.loads((RUN/'begin.safe.json').read_bytes())
    if not(type(result['actualExit'])is int and result['actualExit']==result['actualMavenExit']==0
           and result['productionSource']==selection.MAIN_SOURCE and result['sourceSnapshot']==result['testSourceSnapshot']==begin['sourceSnapshot']
           and result['tests']==109 and result['suites']==10 and not result['reasons']):raise ValueError('actual original109/10/currentMain first')
    for name,digest in begin['inputs'].items():
        if sha((RUN/'source'/name).read_bytes())!=digest:raise ValueError('original frozen input bytes')
    same=selection.verify_main_bytes(RUN/'source')
    if same!=result['coverage']['sameMain']or same['selectedPhysicalMain']!=750:raise ValueError('all750 actual Main bytes still equal deployed04bb')
    records=[];proofs=[]
    for name,digest in result['xmlSha256'].items():
        module=selection.MODULES[name];path=RUN/'source'/('src/schubert-nk-'+module+'/target/surefire-reports/TEST-'+name+'.xml');raw=path.read_bytes()
        if sha(raw)!=digest:raise ValueError('actual XML hash')
        rows=cases(raw,name)
        if sorted(r['method']for r in rows)!=begin['expectedMethods'][name]:raise ValueError('exact fixed actual case names')
        records+=rows;proofs.append({'class':name,'module':module,'tests':len(rows),'originalXmlSha256':digest})
    expected={'PT-BAK-4950-'+str(i).zfill(3)for i in range(1,7)}
    if len(records)!=109 or {r['testId']for r in records if r['newIndependentCase']}!=expected:raise ValueError('six exact new cases and103 related')
    value={'kind':'LIMITED_SELECTED_EVIDENCE_NOT_FORMAL_ACCEPTANCE','actualExit':0,'actualMavenExit':0,
           'productionSource':selection.MAIN_SOURCE,'testSourceSnapshot':result['testSourceSnapshot'],'run':'PG4952',
           'tests':109,'suites':10,'newIndependentCases':6,'relatedCases':103,'FESFlakyNotRun':0,
           'cases':records,'suiteProofs':proofs,'actualMethodCounters':result['coverage'],
           'sameMain':same,'wholeProgramCoverage100':False,'formalAccepted':False,'acceptedLeafDelta':0,
           'effortPercent':None,'wholeRegression':False,'sourceInputInventorySha256':sha(json.dumps(begin['inputs'],sort_keys=True).encode()),
           'originalManifestSha256':sha((RUN/'manifest.safe.json').read_bytes()),'originalBeginSha256':sha((RUN/'begin.safe.json').read_bytes()),
           'originalMavenLogSha256':result['mavenLogSha256'],'command':result['command'],'startedUTC':result['startUTC'],'completedUTC':result['endUTC'],
           'configuredToolVersions':{'jdk':'25.0.4','maven':'3.9.12','jacoco':'0.8.15','spotbugs':'4.10.4.0','formatter':'1.36.1'},
           'hostOS':platform.platform(),'spec':'691_PG4950_Backup保持拒否・所有変化の単体テスト仕様.md',
           'linkedBugs':['BUG-1395','YKT-1161'],'oldPG4950ActualExit':1,'oldPartial14Imported':False,
           'rawPropertiesLogsDatabaseSessionExported':False,'vmActions':0,'mavenReissued':False,
           'recordedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat()}
    os.umask(0o077);PUBLIC.mkdir(parents=True)
    with(PUBLIC/'manifest.json').open('x')as f:json.dump(value,f,ensure_ascii=False,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    print(json.dumps({'actualExit':0,'publicManifest':str((PUBLIC/'manifest.json').relative_to(ROOT)),'sha256':sha((PUBLIC/'manifest.json').read_bytes()),'tests':109,'newIndependentCases':6,'classByteMismatch':0,'formalAccepted':False}));return 0


if __name__=='__main__':raise SystemExit(main())
