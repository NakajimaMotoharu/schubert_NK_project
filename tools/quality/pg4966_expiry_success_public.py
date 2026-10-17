"""Allowlisted actual SSC304 case, static, counter and precise Main delta proof; never formal."""
import datetime
import json
import os
import platform
import pg4852_selected_public_evidence as template
import pg4956_expiry_success_selected as selection

ROOT=selection.ROOT
RUN=ROOT.parent/'pgpt-runs/PG379/pg4964-expiry-success-selected-v1'
PUBLIC=ROOT/'evidence/01_PT/017_NK-BAT-001/evidence/provisional/PG4964-expiry-success-selected-v1'
sha=template.sha


def cases(raw,name):
    records=template.cases(raw,name)
    for record in records:
        if name.endswith('.ExpirySuccessfulScopeTest'):
            method=record['method'];prefix='exp4956'
            if not method.startswith(prefix)or not method[len(prefix):len(prefix)+3].isdigit():raise ValueError('fixed literal Expiry Test IDs')
            record['testId']='PT-EXP-4956-'+method[len(prefix):len(prefix)+3]
            record['newIndependentCase']=True
    return records


def main():
    raise ValueError('DRAFT: actual factory-owned PG4972 qualification required before publication activation')
    # Historical layout retained while the corrected original run is pending.
    result=json.loads((RUN/'manifest.safe.json').read_bytes());begin=json.loads((RUN/'begin.safe.json').read_bytes())
    if not(type(result['actualExit'])is int and result['actualExit']==result['actualMavenExit']==0
           and result['productionSource']==result['sourceSnapshot']==result['testSourceSnapshot']==begin['sourceSnapshot']
           and result['tests']==53 and result['suites']==7 and not result['reasons']):raise ValueError('actual original53/7/all quality gates first')
    for name,digest in begin['inputs'].items():
        if sha((RUN/'source'/name).read_bytes())!=digest:raise ValueError('original immutable input bytes')
    delta=selection.verify_main_bytes(RUN/'source')
    if delta!=result['coverage']['mainDelta']or delta['selectedPhysicalMain']!=752 or delta['unchangedPhysicalMain']!=749:
        raise ValueError('actual Main one modified two declarations/749 unchanged')
    if result['coverage']['freshStaticModules']!={'batch':0,'storage':0,'bootstrap':0}or result['coverage']['formatExit']!=0:
        raise ValueError('actual format/static gates')
    records=[];proofs=[]
    for name,digest in result['xmlSha256'].items():
        module=selection.MODULES[name];path=RUN/'source'/('src/schubert-nk-'+module+'/target/surefire-reports/TEST-'+name+'.xml');raw=path.read_bytes()
        if sha(raw)!=digest:raise ValueError('actual original XML hash')
        rows=cases(raw,name)
        if sorted(r['method']for r in rows)!=begin['expectedMethods'][name]:raise ValueError('exact actual method identity')
        records+=rows;proofs.append({'class':name,'module':module,'tests':len(rows),'originalXmlSha256':digest})
    expected={'PT-EXP-4956-'+str(i).zfill(3)for i in range(1,19)}
    if len(records)!=53 or {r['testId']for r in records if r['newIndependentCase']}!=expected:raise ValueError('eighteen exact new and35 related cases')
    value={'kind':'LIMITED_SELECTED_EVIDENCE_NOT_FORMAL_ACCEPTANCE','actualExit':0,'actualMavenExit':0,
           'productionSource':result['productionSource'],'deployedSource':selection.DEPLOYED,'run':'PG4964',
           'tests':53,'suites':7,'newIndependentCases':18,'relatedCases':35,'FESFlakyNotRun':0,
           'cases':records,'suiteProofs':proofs,'actualMethodCounters':result['coverage'],'mainDelta':delta,
           'wholeProgramCoverage100':False,'formalAccepted':False,'acceptedLeafDelta':0,'effortPercent':None,
           'wholeRegression':False,'newSourceNativePending':True,'oldNativeImported':False,
           'sourceInputInventorySha256':sha(json.dumps(begin['inputs'],sort_keys=True).encode()),
           'originalManifestSha256':sha((RUN/'manifest.safe.json').read_bytes()),'originalBeginSha256':sha((RUN/'begin.safe.json').read_bytes()),
           'originalMavenLogSha256':result['mavenLogSha256'],'command':result['command'],'startedUTC':result['startUTC'],'completedUTC':result['endUTC'],
           'configuredToolVersions':{'jdk':'25.0.4','maven':'3.9.12','jacoco':'0.8.15','spotbugs':'4.10.4.0','formatter':'1.36.1'},
           'hostOS':platform.platform(),'spec':'693_SSC304_Expiry既成功監査・JDBC所有scope単体テスト仕様.md',
           'linkedBugs':['BUG-1396','BUG-1397','BUG-1398','BUG-1399','BUG-1400','YKT-1162','YKT-1163','YKT-1164'],
           'oldFailedOrPartialImported':False,'rawPropertiesLogsDatabaseSessionExported':False,
           'vmActions':0,'mavenReissued':False,'recordedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat()}
    os.umask(0o077);PUBLIC.mkdir(parents=True)
    with(PUBLIC/'manifest.json').open('x')as f:json.dump(value,f,ensure_ascii=False,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    print(json.dumps({'actualExit':0,'publicManifest':str((PUBLIC/'manifest.json').relative_to(ROOT)),
        'sha256':sha((PUBLIC/'manifest.json').read_bytes()),'tests':53,'newIndependentCases':18,'formalAccepted':False}));return 0


if __name__=='__main__':raise SystemExit(main())
