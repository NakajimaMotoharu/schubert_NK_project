"""Publish only independent selected hashes/counters, same-byte diagnostic not full-source gate."""
import hashlib,json,platform,xml.etree.ElementTree as E,zipfile
from pathlib import Path
T=Path(__file__).resolve().parents[4];W=Path('/home/mini/codex/project1/work/pgpt-runs/PG379')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def classes(p):
    with zipfile.ZipFile(p)as z:return{n:hashlib.sha256(z.read(n)).hexdigest()for n in z.namelist()if n.endswith('.class')}
if __name__=='__main__':
    base=W/'pg919-inspector-selected-v1';r=json.loads((base/'run.safe.json').read_bytes());assert r['actualExit']==0
    for path,h in r['files'].items():assert sha(base/path)==h
    batch=base/'batch';old=W/'pg915-snapshot-six-host-v1/batch';jar='schubert-nk-batch-0.1.0-SNAPSHOT.jar';assert classes(batch/jar)==classes(old/jar)
    tests=0;xmls={}
    for p in batch.glob('TEST-*.xml'):
        v=E.parse(p).getroot();assert all(int(v.get(k,'0'))==0 for k in ('failures','errors','skipped'));tests+=int(v.get('tests'));xmls[p.name]=sha(p)
    assert tests==66 and len(xmls)==8 and not E.parse(batch/'spotbugsXml.xml').getroot().findall('.//BugInstance')
    root=E.parse(batch/'jacoco.xml').getroot();counts={}
    for c in root.findall('package/class'):
        name=c.get('name')
        if name.rsplit('/',1)[-1]in('InspectorEnvironmentFiles','InspectorEnvironmentPublisher','InspectorUnitProbe$NativeReader'):
            counts[name]={v.get('type'):{'covered':int(v.get('covered')),'missed':int(v.get('missed'))}for v in c.findall('counter')}
    target=T/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG919-inspector-host-v1/manifest.json';assert not target.exists()
    value={'program':'NK-DAT-001/NK-OPS-001','wbsLeaf':'WBS-P004-04','testIds':['PT-INSPECTOR-919001','PT-INSPECTOR-919002','PT-INSPECTOR-919003','PT-INSPECTOR-919004'],'source':r['source'],'productionMainByteReference':'4ebf34debdda9c655717af8acae09b571efd8133','installedVmSource':r['installedVmSource'],'branch':'dev-foundation','startedUTC':r['startedUTC'],'endedUTC':r['endedUTC'],'command':r['command'],'environment':{'OS':platform.platform(),'JDK':'25.0.4','Maven':'3.9.12','JaCoCo':'0.8.15','SpotBugs':'4.10.4','NullAway':'0.14.1'},'actualExit':0,'tests':66,'suites':8,'FESFlakyNotRun':0,'staticIssues':0,'runManifestSha256':sha(base/'run.safe.json'),'privateLogSha256':sha(base/'build.private.log'),'xmlHashes':xmls,'coverageSha256':sha(batch/'jacoco.xml'),'execSha256':sha(batch/'jacoco.exec'),'jarSha256':sha(batch/jar),'staticSha256':sha(batch/'spotbugsXml.xml'),'all343MainClassByteMismatch':0,'classCounters':counts,'expected':'foreign retirement refused/unlink0 and original bytes retained; own retirement once; known stale entries refused/no mutation; unknown unrelated data preserved; three actual monotonic expiry boundaries TIMEOUT/all streams closed/owned child stopped','actual':'All four cases passed with explicit resource assertions; Files/Publisher four100; NativeReader branch100 with four native-boundary lines still unexecuted','independentOracle':'SS341/343/352 fixed owner/namespace/5s cap and literal controlled provider deadlines in 613/testmethods, not production-generated expected','bugIds':[],'coverageExclusions':False,'oldNativeImported':False,'fullRegressionForThisTestSource':False,'diagnosticSameMainByteOnly':True,'formalAccepted':False,'wholeWbsAcceptedDelta':0,'rawExported':False,'specification':'evidence/01_PT/018_NK-OPS-001/613_Inspector残異常系_独立PT仕様.md'}
    observation={'source':r['source'],'run':'PG919','tests':66,'suites':8,'staticIssues':0,'mainByteReference':'4ebf34debdda9c655717af8acae09b571efd8133','classCounters':counts,'differentTestSourceDiagnosticOnly':True,'formalAccepted':False,'wholeLeafClosed':False,'evidence':str(target.relative_to(T))}
    wbs=T/'documents/400_PGPT/470_PMO/486_WBS現行実績.json';assert '"currentPG919InspectorObservation"'not in wbs.read_text()
    print('*** Begin Patch\n*** Add File: '+str(target));print('\n'.join('+'+l for l in json.dumps(value,ensure_ascii=False,indent=2).splitlines()))
    print('*** Update File: '+str(wbs)+'\n@@\n {\n+  "currentPG919InspectorObservation": '+json.dumps(observation,ensure_ascii=False,separators=(',',':'))+',\n*** End Patch')
