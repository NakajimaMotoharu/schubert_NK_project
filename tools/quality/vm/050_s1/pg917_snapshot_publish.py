"""Emit sanitized fresh host partial-observation patch; never exports raw native/session/logs."""
import hashlib,json,platform,xml.etree.ElementTree as E
from pathlib import Path

T=Path(__file__).resolve().parents[4]
W=Path('/home/mini/codex/project1/work/pgpt-runs/PG379')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
if __name__=='__main__':
    root=W/'pg915-snapshot-six-host-v1';p=root/'manifest.safe.json';m=json.loads(p.read_bytes())
    assert m['actualExit']==0 and m['tests']==3550 and m['suites']==523 and m['staticIssues']==0
    assert m['candidateSource']=='4ebf34debdda9c655717af8acae09b571efd8133'
    assert m['changedClassNames']==['dev/codex/schubert/nk/batch/platform/InspectorUnitSnapshot.class']
    c=next(c for c in E.parse(root/'batch/jacoco.xml').getroot().findall('package/class')if c.get('name').endswith('/InspectorUnitSnapshot'))
    counts={x.get('type'):{'covered':int(x.get('covered')),'missed':int(x.get('missed'))}for x in c.findall('counter')}
    assert all(counts[k]['missed']==0 for k in ('LINE','METHOD','CLASS','BRANCH'))
    runs={}
    for suffix in ('v3','v4','v5'):
        base=W/('pg911-snapshot-selected-'+suffix);r=json.loads((base/'run.safe.json').read_bytes());assert r['actualExit']==0
        tests=suites=0
        for xml in (base/'batch').glob('TEST-*.xml'):
            q=E.parse(xml).getroot();assert all(int(q.get(k,'0'))==0 for k in ('failures','errors','skipped'));tests+=int(q.get('tests'));suites+=1
        runs[suffix]={'source':r['source'],'actualExit':0,'tests':tests,'suites':suites,'startedUTC':r['startedUTC'],'endedUTC':r['endedUTC'],'manifestSha256':sha(base/'run.safe.json'),'command':r['command']}
    target=T/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG911-916-snapshot-host-v1/manifest.json';assert not target.exists()
    value={'schemaVersion':1,'program':'NK-DAT-001/NK-OPS-001','wbsLeaf':'WBS-P004-04','testIds':['PT-SNAPSHOT-91100'+str(i)for i in range(1,10)],'branch':'dev-foundation','source':m['candidateSource'],'started':(root/'started').read_text().strip(),'completed':(root/'completed').read_text().strip(),'command':['python3 -B tools/quality/vm/050_s1/pg915_snapshot_full.py','python3 -B tools/quality/vm/050_s1/pg916_snapshot_full_collect.py'],'environment':{'OS':platform.platform(),'python':platform.python_version(),'JDK':'25.0.4','Maven':'3.9.12','JaCoCo':'0.8.15','SpotBugs':'4.10.4','NullAway':'0.14.1'},'actualExit':0,'tests':3550,'suites':523,'FESFlakyNotRun':0,'staticModules':6,'staticIssues':0,'qualifiedNullableCompile':True,'elapsedSeconds':m['elapsedSeconds'],'sourceFilesSha256':sha(root/'source-files.sha256'),'privateLogSha256':sha(root/'build.private.log'),'fullManifestSha256':sha(p),'mainClasses':1632,'snapshotClass':c.get('name'),'snapshotCounters':counts,'independentOracle':'SS341/343/352 literal 18fields/state partition/target status table; input and expected in 612 and InspectorHeldStateContractTest, never produced by production method','expectedResult':'All nine literal contract cases succeed; Snapshot four counters 100%','actualResult':'Nine tests succeeded in fresh full run; Snapshot four counters missed0','selectedRunsNotAddedToFull':runs,'bugs':['BUG-996','BUG-997'],'YKT':['YKT-765','YKT-766'],'decision':'PG-D407','failedAttemptsPreserved':['PG911v1 not-run1','PG911v2 F1','PG912 dependency install1'],'coverageExclusions':False,'remainingHostOnly':m['remainingHostOnly'],'oldNativeImported':False,'installedVmSource':m['installedVmSource'],'candidateDeployed':False,'global100':False,'formalAccepted':False,'wholeWbsAcceptedDelta':0,'rawExported':False,'moduleEvidence':{k:{'tests':v['tests'],'suites':v['suites'],'xmlHashes':v['xmlHashes'],'jarSha256':v['jarSha256'],'execSha256':v['execSha256'],'coverageSha256':v['coverageSha256'],'staticSha256':v['staticSha256']}for k,v in m['moduleResults'].items()},'specification':'evidence/01_PT/018_NK-OPS-001/612_Inspector状態判定_独立PT追加仕様.md'}
    observation={'source':m['candidateSource'],'run':'PG915/916','tests':3550,'suites':523,'staticModules':6,'staticIssues':0,'sameSourceRun':True,'snapshotClassCounters':counts,'remainingHostOnly':m['remainingHostOnly'],'candidateDeployed':False,'oldNativeImported':False,'formalAccepted':False,'wholeAcceptedDelta':0,'scopeAdded':0,'artifactOwner':'WBS-P004-04','wholeLeafClosed':False,'evidence':str(target.relative_to(T))}
    wbs=T/'documents/400_PGPT/470_PMO/486_WBS現行実績.json';raw=wbs.read_text();assert '"currentPG915HostObservation"'not in raw
    print('*** Begin Patch\n*** Add File: '+str(target));print('\n'.join('+'+l for l in json.dumps(value,ensure_ascii=False,indent=2).splitlines()))
    print('*** Update File: '+str(wbs)+'\n@@\n {\n+  "currentPG915HostObservation": '+json.dumps(observation,ensure_ascii=False,separators=(',',':'))+',\n*** End Patch')
