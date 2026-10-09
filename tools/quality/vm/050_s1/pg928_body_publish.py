"""Publish selected real-body evidence; never substitute host for native acceptance."""
import hashlib,json,platform,zipfile,xml.etree.ElementTree as E
from pathlib import Path
T=Path(__file__).resolve().parents[4]
W=Path('/home/mini/codex/project1/work/pgpt-runs/PG379')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def classes(p):
    with zipfile.ZipFile(p)as z:return{n:hashlib.sha256(z.read(n)).hexdigest()for n in z.namelist()if n.endswith('.class')}
if __name__=='__main__':
    base=W/'pg925-body-selected-v2';r=json.loads((base/'run.safe.json').read_bytes());assert r['actualExit']==0
    for path,h in r['files'].items():assert sha(base/path)==h
    methods={};xmls={};changed=[];tests=suites=0
    for module in ('bootstrap','api'):
        b=base/module;jar='schubert-nk-'+module+'-0.1.0-SNAPSHOT.jar'
        now=classes(b/jar);old=classes(W/'pg915-snapshot-six-host-v1'/module/jar);assert now.keys()==old.keys()
        for n in now:
            if now[n]!=old[n]:changed.append(n)
        for p in b.glob('TEST-*.xml'):
            x=E.parse(p).getroot();assert all(int(x.get(k,'0'))==0 for k in ('failures','errors','skipped'))
            assert not any(y.tag.lower()in ('flakyfailure','flakyerror','rerunfailure','rerunerror')for y in x.iter())
            tests+=int(x.get('tests'));suites+=1;xmls[module+'/'+p.name]=sha(p)
        bugs=E.parse(b/'spotbugsXml.xml').getroot();assert not bugs.findall('.//BugInstance')and not bugs.findall('.//Error')
        for c in E.parse(b/'jacoco.xml').getroot().findall('package/class'):
            for m in c.findall('method'):
                if (c.get('name').endswith('/InspectorApplication')and m.get('name')in ('execute','readMaintenanceOwner'))or(c.get('name').endswith('/ChildStartupContext')and m.get('name')=='verifyDaemon'):
                    v={x.get('type'):{'covered':int(x.get('covered')),'missed':int(x.get('missed'))}for x in m.findall('counter')}
                    assert all(x['missed']==0 for x in v.values());methods[c.get('name')+'.'+m.get('name')+m.get('desc')]=v
    assert tests==60 and suites==8
    assert set(changed)=={'dev/codex/schubert/nk/bootstrap/ChildStartupContext.class','dev/codex/schubert/nk/bootstrap/ChildStartupContext$NativeIo.class','dev/codex/schubert/nk/api/file/InspectorApplication.class'}
    target=T/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG925-body-host-v2/manifest.json';assert not target.exists()
    v={k:r[k]for k in ('source','startedUTC','endedUTC','command','actualExit','candidateDeployed','installedVmSource')}
    v.update(program='NK-OPS-001',branch='dev-foundation',wbsLeaves=['WBS-P004-04','WBS-P018-03.02'],testIds=['PT-APP-925001','PT-APP-925002','PT-APP-925003','PT-COMMON-925004'],environment={'OS':platform.platform(),'JDK':'25.0.4','Maven':'3.9.12','JaCoCo':'0.8.15','SpotBugs':'4.10.4','NullAway':'0.14.1'},tests=tests,suites=suites,FESFlakyNotRun=0,staticIssues=0,methods=methods,changedClassNames=sorted(changed),byteComparisonReference='4ebf34debdda9c655717af8acae09b571efd8133',independentOracle='615 hand-written owner frame and fixed progress/SQL row counts; guard IO before credentials/SQL; guard-present success and replay once; second capture foreign UID refuses',expected='guard IOException generic rejection/zero SQL; available guard SUCCESS and same run replay row1; malformed frame IOException; missing reader credential exception; changed UID IOException',actual='All stated assertions passed, held roots closed and buffers wiped',runManifestSha256=sha(base/'run.safe.json'),privateLogSha256=sha(base/'build.private.log'),xmlHashes=xmls,artifactHashes={m+'/'+n:sha(base/m/n)for m in ('bootstrap','api')for n in ('jacoco.xml','jacoco.exec','spotbugsXml.xml','schubert-nk-'+m+'-0.1.0-SNAPSHOT.jar')},formalAccepted=False,wholeClassOrWbsClosed=False,oldNativeImported=False,wholeRegressionPending=True,rawExported=False,bugIds=[],specification='evidence/01_PT/018_NK-OPS-001/615_Inspector実body_guard・claim境界_PT仕様.md')
    print('*** Begin Patch\n*** Add File: '+str(target));print('\n'.join('+'+l for l in json.dumps(v,ensure_ascii=False,indent=2).splitlines()));print('*** End Patch')
