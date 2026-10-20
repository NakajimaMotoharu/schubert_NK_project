"""Independent original66 XML/physical hash projection; no production/test invocation."""
import json
import os
import re
import xml.etree.ElementTree as ET
from pg5540_snapshot_scratch_selected import ROOT,sha
from pg5828_isolation_green import CASES,COUNTS
from pg5800_rollback_green import source_test_names
from pg5832_isolation_whole import SOURCE,W
from pg5834_isolation_qualification import added_cases


def main():
    path=W/'pg5828-isolation-selected66-v1/manifest.safe.json';v=json.loads(path.read_bytes());snapshot=path.parent/'source';begin=json.loads((path.parent/'begin.safe.json').read_bytes())
    base=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional';sp=base/'PG5830-isolation-static-v1/manifest.json';s=json.loads(sp.read_bytes());private=W/'pg5830-isolation-static-v1/manifest.safe.json'
    if sha(sp)!='a8db12fed46184684ec8d911266dedac6206f42ca65be2fcd8f8c424ab6bbf8f'or sha(private)!=s['privateManifestSha256']or s['selectedManifestSha256']!=sha(path):raise ValueError('original current static proof')
    static=json.loads(private.read_bytes());actual={};expected={};xmls={};physical={};trace=[];new=set(added_cases())
    for module,classes in CASES.items():
        target=snapshot/('src/schubert-nk-'+module+'/target')
        for cls in classes:
            name='dev.codex.schubert.nk.'+cls;source=snapshot/('src/schubert-nk-'+module+'/src/test/java')/(name.replace('.','/')+'.java');expected[name]=source_test_names(source)
            if len(expected[name])!=COUNTS[cls.rsplit('.',1)[1]]:raise ValueError('fixed independent Test inventory')
        for p in(target/'surefire-reports').glob('TEST-*.xml'):
            tree=ET.parse(p).getroot();name=tree.get('name')
            if name in actual:raise ValueError('no duplicate suite')
            actual[name]=set();xmls[name]=sha(p)
            for c in tree.findall('testcase'):
                method=c.get('name','').split('(',1)[0]
                if method in actual[name]or any(n.tag in('failure','error','skipped','flakyFailure','flakyError','rerunFailure','rerunError')for n in c.iter()):raise ValueError('every selected case exactly once, PASS only')
                actual[name].add(method)
                if(name,method)in new:
                    match=re.match(r'iso(\d{3})',method)
                    if not match:raise ValueError('one design ID per new method')
                    trace.append({'designTestId':'PT-JMS-ISO'+match[1],'class':name,'method':method,'xmlSha256':sha(p)})
        physical.update({module+':'+p.relative_to(target/'classes').as_posix():sha(p)for p in(target/'classes').rglob('*.class')})
    sources={p.relative_to(snapshot).as_posix():sha(p)for p in snapshot.glob('src/*/src/main/java/**/*.java')}
    if not(v['actualExit']==0 and v['source']==begin['source']==static['source']==SOURCE and v['sourceFixed']and v['phaseExits']==[0,0]and actual==expected and sum(map(len,actual.values()))==66 and len(actual)==18 and physical==static['auxClassHashes']and sources==static['allSourceHashes']and set(v['staticIssues'])==set(CASES)and not any(v['staticIssues'].values())and {r['designTestId']for r in trace}=={'PT-JMS-ISO'+str(i).zfill(3)for i in range(1,13)}):raise ValueError('exact66 current source/Main/static/trace')
    value={'actualExit':0,'source':SOURCE,'branch':'dev-foundation','run':'pg5828-isolation-selected66-v1','startedUTC':v['startedUTC'],'completedUTC':v['completedUTC'],'archiveSha256':v['archiveSha256'],'originalManifestSha256':sha(path),'staticManifestSha256':sha(sp),'xmlHashes':xmls,'caseTrace':sorted(trace,key=lambda r:r['designTestId']),'tests':66,'suites':18,'mainSource':851,'physicalMain':1666,'phaseExits':[0,0],'staticIssues':v['staticIssues'],'targetCounters':v['targetCounters'],'targetFour100':v['targetFour100'],'formalAccepted':False,'fullCoverageClaimed':False,'ptAlternativeCompleted':0,'fullRegressionPending':True,'BUG1494Open':True,'vmActions':0,'toolchain':{'jdk':'25.0.4','maven':'3.9.12','jacoco':'0.8.15','spotbugs':'4.10.4.0'}}
    out=base/'PG5831-isolation66-v1';os.umask(0o077);out.mkdir()
    with(out/'manifest.json').open('x')as f:json.dump(value,f,ensure_ascii=False,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    print(json.dumps({'actualExit':0,'tests':66,'newDesignIdsTraced':12,'allEightTargets100':v['targetFour100'],'manifestSha256':sha(out/'manifest.json')}))


if __name__=='__main__':main()
