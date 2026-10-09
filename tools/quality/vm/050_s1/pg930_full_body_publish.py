"""Publish fresh whole-source XML/static/counters and partial WBS evidence only."""
import hashlib,json,platform,xml.etree.ElementTree as E
from pathlib import Path
T=Path(__file__).resolve().parents[4];W=Path('/home/mini/codex/project1/work/pgpt-runs/PG379')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
if __name__=='__main__':
    root=W/'pg926-body-six-host-v1';p=root/'manifest.safe.json';m=json.loads(p.read_bytes())
    assert sha(p)=='4ae512d3b3a8e85d81fcd8e9ef04279fff58114c42e9b158adc61299d8211fdf'and m['actualExit']==0
    counts={}
    names={'ChildStartupContext','InspectorUnitSnapshot','InspectorEnvironmentFiles','InspectorEnvironmentPublisher','InspectorApplication','InspectorUnitProbe$NativeReader'}
    for module in ('bootstrap','api','batch'):
        for c in E.parse(root/module/'jacoco.xml').getroot().findall('package/class'):
            if c.get('name').split('/')[-1]in names:counts[c.get('name')]={x.get('type'):{'covered':int(x.get('covered')),'missed':int(x.get('missed'))}for x in c.findall('counter')}
    closed=[k for k,v in counts.items()if all(v[x]['missed']==0 for x in ('LINE','METHOD','CLASS','BRANCH'))];assert len(closed)==4
    target=T/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG926-927-body-full-host-v1/manifest.json';assert not target.exists()
    v={'program':'NK-DAT-001/NK-OPS-001','branch':'dev-foundation','source':m['candidateSource'],'started':(root/'started').read_text().strip(),'completed':(root/'completed').read_text().strip(),'command':['python3 -B tools/quality/vm/050_s1/pg926_body_full.py','python3 -B tools/quality/vm/050_s1/pg927_body_full_collect.py'],'environment':{'OS':platform.platform(),'Python':platform.python_version(),'JDK':'25.0.4','Maven':'3.9.12','JaCoCo':'0.8.15','SpotBugs':'4.10.4','NullAway':'0.14.1'},'tests':m['tests'],'suites':m['suites'],'mainClasses':m['mainClasses'],'actualExit':0,'FESFlakyNotRun':0,'staticModules':6,'staticIssues':0,'qualifiedNullableCompile':True,'elapsedSeconds':m['elapsedSeconds'],'sourceFilesSha256':sha(root/'source-files.sha256'),'privateLogSha256':sha(root/'build.private.log'),'fullManifestSha256':sha(p),'moduleEvidence':m['moduleResults'],'changedClassNames':m['changedClassNames'],'classCounters':counts,'classesFourCounters100':closed,'independentOracle':'612..615 literal state/owner bytes, SQL row1 replay and resource conditions; original existing per-program expectations kept, production method not used to generate expected','testIds':['PT-SNAPSHOT-911001..009','PT-INSPECTOR-919001..004','PT-COMMON-922001..002','PT-APP-925001..003','PT-COMMON-925004'],'specification':'evidence/01_PT/018_NK-OPS-001/616_当source実body全六回帰_仕様・結果.md','remainingHostOnly':m['remainingHostOnly'],'selectedRunsAdded':False,'oldNativeImported':False,'candidateDeployed':False,'installedVmSource':m['installedVmSource'],'formalAccepted':False,'global100':False,'wholeWbsAccepted':False,'exclusions':False,'rawExported':False}
    obs={k:v[k]for k in ('source','tests','suites','staticModules','staticIssues','remainingHostOnly','classCounters','classesFourCounters100','candidateDeployed','oldNativeImported','formalAccepted','wholeWbsAccepted')};obs.update(run='PG926/927',sameSourceRun=True,wholeAcceptedDelta=0,scopeAdded=0,evidence=str(target.relative_to(T)))
    wbs=T/'documents/400_PGPT/470_PMO/486_WBS現行実績.json';assert '"currentPG926HostObservation"'not in wbs.read_text()
    print('*** Begin Patch\n*** Add File: '+str(target));print('\n'.join('+'+x for x in json.dumps(v,ensure_ascii=False,indent=2).splitlines()))
    print('*** Update File: '+str(wbs)+'\n@@\n {\n+  "currentPG926HostObservation": '+json.dumps(obs,ensure_ascii=False,separators=(',',':'))+',\n*** End Patch')
