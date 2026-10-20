"""Qualify original four terminal reds, no new PT or runtime action."""
import json
import os
import xml.etree.ElementTree as ET
from pg5854_committed_terminal_red import engine,RED_API,RED_WEB,red_qualified


def main():
    rows=[];work=engine.ROOT.parent/'pgpt-runs/PG379'
    for phase,wanted in(('red-api',RED_API),('red-web',RED_WEB)):
        out=work/('pg5854-terminal-'+phase+'-v1');p=out/'manifest.safe.json';v=json.loads(p.read_bytes());b=json.loads((out/'begin.safe.json').read_bytes());snapshot=out/'source';actual={};xmls={}
        for path in snapshot.glob('src/*/target/surefire-reports/TEST-*.xml'):
            tree=ET.parse(path).getroot();name=tree.get('name')
            if name in actual:raise ValueError('unique original suites')
            actual[name]={c.get('name','').removesuffix('()')for c in tree.findall('testcase')};xmls[name]=engine.sha(path)
        if not v['purposefulRedEstablished']or not red_qualified(snapshot,actual,{k:set(n)for k,n in b['expected'].items()},v['allPhysicalMainSha256'],v['phaseExits'],v['failedOrSkipped'],phase):raise ValueError('original exact policy failure, source and all Main first')
        rows.append({'phase':phase,'run':out.name,'source':v['source'],'manifestSha256':engine.sha(p),'archiveSha256':v['archiveSha256'],'startedUTC':v['startedUTC'],'completedUTC':v['completedUTC'],'actualExit':1,'phaseExits':v['phaseExits'],'executedCases':v['tests'],'suites':v['suites'],'expectedFailureIds':[list(x)for x in sorted(wanted)],'xmlHashes':xmls,'physicalMain':len(v['allPhysicalMainSha256']),'purposefulRedEstablished':True,'webNotRunRetained':v['webNotRunRetained']})
    value={'actualExit':0,'executionKind':'ORIGINAL_FOUR_RED_ARTIFACT_QUALIFICATION_NOT_PT_PASS','unmodifiedProductionSource':'86287c3fb83b483050b88dce04bc644961682bc4','runs':rows,'purposefulFailureCases':4,'productionPtPassCredit':0,'ptAlternativeCompleted':0,'formalAccepted':False,'BUG1501Open':True,'vmActions':0}
    target=engine.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG5855-terminal-reds-v1';os.umask(0o077);target.mkdir()
    with(target/'manifest.json').open('x')as f:json.dump(value,f,ensure_ascii=False,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    print(json.dumps({'actualExit':0,'purposefulFailureCases':4,'ptPassCredit':0,'manifestSha256':engine.sha(target/'manifest.json')}))


if __name__=='__main__':main()
