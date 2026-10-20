"""Read original isolation red artifacts; no process, JVM, network or PT execution."""
import json
import os
import xml.etree.ElementTree as ET
from pg5826_isolation_red import engine,RED_API,RED_WEB,red_qualified


def main():
    root=engine.ROOT;work=root.parent/'pgpt-runs/PG379';rows=[]
    for phase,slot,wanted in(('red-api','pg5826-isolation-red-api-v2',RED_API),('red-web','pg5826-isolation-red-web-v2',RED_WEB)):
        out=work/slot;path=out/'manifest.safe.json';v=json.loads(path.read_bytes());begin=json.loads((out/'begin.safe.json').read_bytes());snapshot=out/'source'
        actual={};xmls={}
        for p in snapshot.glob('src/*/target/surefire-reports/TEST-*.xml'):
            tree=ET.parse(p).getroot();name=tree.get('name')
            if name in actual:raise ValueError('duplicate original suites')
            actual[name]={c.get('name','').removesuffix('()')for c in tree.findall('testcase')};xmls[p.relative_to(snapshot).as_posix()]=engine.sha(p)
        expected={k:set(v)for k,v in begin['expected'].items()}
        if not v['purposefulRedEstablished']or not red_qualified(snapshot,actual,expected,v['allPhysicalMainSha256'],v['phaseExits'],v['failedOrSkipped'],phase):raise ValueError('independent exact policy failure and original Main proof')
        rows.append({'phase':phase,'run':slot,'source':v['source'],'originalManifestSha256':engine.sha(path),'archiveSha256':v['archiveSha256'],'startedUTC':v['startedUTC'],'completedUTC':v['completedUTC'],'phaseExits':v['phaseExits'],'actualExit':v['actualExit'],'executedCases':v['tests'],'suites':v['suites'],'expectedFailureIds':[list(t)for t in sorted(wanted)],'purposefulRedEstablished':True,'xmlHashes':xmls,'webNotRunRetained':v['webNotRunRetained'],'actualPhysicalMain':len(v['allPhysicalMainSha256']),'unmodifiedProductionSource':'2e3b0d50679ad6f1a984e25bd400db6f3ad9e798'})
    failed=work/'pg5826-isolation-red-api-v1/manifest.safe.json';v=json.loads(failed.read_bytes())
    if v['purposefulRedEstablished']or v['actualExit']!=1 or v['tests']!=7:raise ValueError('original compile failure preserved, not a policy red')
    webfailed=work/'pg5826-isolation-red-web-v1/manifest.safe.json';wv=json.loads(webfailed.read_bytes())
    if wv['purposefulRedEstablished']or wv['actualExit']!=1 or wv['tests']!=8:raise ValueError('original missing test dependency compile failure preserved')
    value={'actualExit':0,'executionKind':'ORIGINAL_RED_ARTIFACT_QUALIFICATION_NOT_PT_PASS','runs':rows,'purposefulFailureCases':8,'productionPtPassCredit':0,'alternativesCompleted':0,'formalAccepted':False,'wholePassIsNotSpecificationAcceptance':True,'BUG1494Open':True,'BUG1496FixtureCompileCorrected':True,'BUG1497FixtureDependencyCorrected':True,'preservedUnqualifiedAttempts':[{'run':'pg5826-isolation-red-api-v1','manifestSha256':engine.sha(failed),'reason':'fixture try lint error; API/Web not run','actualExit':1,'executedCases':7},{'run':'pg5826-isolation-red-web-v1','manifestSha256':engine.sha(webfailed),'reason':'missing API test class dependency; Web not run','actualExit':1,'executedCases':8}],'runtimeOrVmOperations':0}
    target=root/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG5827-isolation-reds-v1';os.umask(0o077);target.mkdir()
    with(target/'manifest.json').open('x')as f:json.dump(value,f,ensure_ascii=False,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    print(json.dumps({'actualExit':0,'purposefulFailureCases':8,'productionPtPassCredit':0,'manifestSha256':engine.sha(target/'manifest.json')}))


if __name__=='__main__':main()
