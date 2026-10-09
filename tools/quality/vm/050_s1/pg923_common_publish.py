"""Emit qualified common method diagnostics, never import old native/global results."""
import hashlib,json,platform,zipfile,xml.etree.ElementTree as E
from pathlib import Path
T=Path(__file__).resolve().parents[4];W=Path('/home/mini/codex/project1/work/pgpt-runs/PG379')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def classes(p):
    with zipfile.ZipFile(p)as z:return{n:hashlib.sha256(z.read(n)).hexdigest()for n in z.namelist()if n.endswith('.class')}
if __name__=='__main__':
    base=W/'pg922-common-selected-v1';r=json.loads((base/'run.safe.json').read_bytes());assert r['actualExit']==0
    for path,h in r['files'].items():assert sha(base/path)==h
    b=base/'bootstrap';jar='schubert-nk-bootstrap-0.1.0-SNAPSHOT.jar';assert classes(b/jar)==classes(W/'pg915-snapshot-six-host-v1/bootstrap'/jar)
    xmls={};tests=0
    for p in b.glob('TEST-*.xml'):
        x=E.parse(p).getroot();assert all(int(x.get(k,'0'))==0 for k in ('failures','errors','skipped'));tests+=int(x.get('tests'));xmls[p.name]=sha(p)
    assert tests==38 and len(xmls)==6 and not E.parse(b/'spotbugsXml.xml').getroot().findall('.//BugInstance')
    root=E.parse(b/'jacoco.xml').getroot();methods={}
    for c in root.findall('package/class'):
        for m in c.findall('method'):
            if (c.get('name').endswith('/ChildStartupContext')and m.get('name')=='verifyDaemon')or(c.get('name').endswith('/FixedNativeCoverageCheckpoint')and m.get('name')=='fromCurrentJvm'):
                methods[c.get('name')+'.'+m.get('name')]={x.get('type'):{'covered':int(x.get('covered')),'missed':int(x.get('missed'))}for x in m.findall('counter')}
    target=T/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG922-common-host-v1/manifest.json';assert not target.exists()
    v={'program':'NK-OPS-001','wbsLeaves':['WBS-P018-03.02','WBS-P018-08.02'],'testIds':['PT-COMMON-922001','PT-COMMON-922002'],'source':r['source'],'branch':'dev-foundation','startedUTC':r['startedUTC'],'endedUTC':r['endedUTC'],'command':r['command'],'environment':{'OS':platform.platform(),'JDK':'25.0.4','Maven':'3.9.12','JaCoCo':'0.8.15','SpotBugs':'4.10.4','NullAway':'0.14.1'},'actualExit':0,'tests':38,'suites':6,'FESFlakyNotRun':0,'staticIssues':0,'same102MainClassByteMismatch':0,'mainByteReference':'4ebf34debdda9c655717af8acae09b571efd8133','runManifestSha256':sha(base/'run.safe.json'),'privateLogSha256':sha(base/'build.private.log'),'xmlHashes':xmls,'execSha256':sha(b/'jacoco.exec'),'coverageSha256':sha(b/'jacoco.xml'),'staticSha256':sha(b/'spotbugsXml.xml'),'jarSha256':sha(b/jar),'methods':methods,'independentOracle':'614 literal no authority on absent role/default unchanged JVM; malformed INV must refuse before any manager/kernel observation','expected':'generic IOException/empty default; invalid INV rejects with OS read0','actual':'Both new cases passed with message/no cause/no suppression/JVM input unchanged/manager and kernel0 assertions','formalAccepted':False,'differentTestSourceSameMainByteDiagnosticOnly':True,'oldNativeImported':False,'wholeClassOrWbsClosed':False,'rawExported':False,'bugIds':[],'specification':'evidence/01_PT/018_NK-OPS-001/614_共通起動境界_独立negative_PT仕様.md'}
    print('*** Begin Patch\n*** Add File: '+str(target));print('\n'.join('+'+l for l in json.dumps(v,ensure_ascii=False,indent=2).splitlines()));print('*** End Patch')
