"""Independently re-read original81 XML, actual eight counters and all1666 bytes; no PT."""
import json
import os
import re
import xml.etree.ElementTree as ET
from pg5540_snapshot_scratch_selected import ROOT,sha
from pg5856_terminal_green import CASES,COUNTS,TARGETS
from pg5800_rollback_green import source_test_names
from pg5862_terminal_qualification import SOURCE,W,added_cases


def main():
    path=W/'pg5856-terminal-selected81-v3/manifest.safe.json';v=json.loads(path.read_bytes());snapshot=path.parent/'source';begin=json.loads((path.parent/'begin.safe.json').read_bytes())
    base=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional';sp=base/'PG5858-terminal-static-v1/manifest.json';s=json.loads(sp.read_bytes());private=W/'pg5858-terminal-static-v1/manifest.safe.json'
    if sha(private)!=s['privateManifestSha256']or s['selectedManifestSha256']!=sha(path)or s['actualExit']!=0 or s['source']!=SOURCE:raise ValueError('actual current static/source proof')
    static=json.loads(private.read_bytes());actual={};expected={};xmls={};physical={};trace=[];new=set(added_cases());counters={}
    for module,classes in CASES.items():
        target=snapshot/('src/schubert-nk-'+module+'/target')
        for cls in classes:
            name='dev.codex.schubert.nk.'+cls;source=snapshot/('src/schubert-nk-'+module+'/src/test/java')/(name.replace('.','/')+'.java');expected[name]=source_test_names(source)
            if len(expected[name])!=COUNTS[cls.rsplit('.',1)[1]]:raise ValueError('fixed Test inventory')
        for p in(target/'surefire-reports').glob('TEST-*.xml'):
            tree=ET.parse(p).getroot();name=tree.get('name')
            if name in actual:raise ValueError('unique original suite')
            actual[name]=set();xmls[name]=sha(p)
            for c in tree.findall('testcase'):
                method=c.get('name','').split('(',1)[0]
                if method in actual[name]or any(n.tag in('failure','error','skipped','flakyFailure','flakyError','rerunFailure','rerunError')for n in c.iter()):raise ValueError('all cases exactly once and PASS only')
                actual[name].add(method)
                if(name,method)in new:
                    match=re.match(r'term(\d{3})',method)
                    if not match:raise ValueError('one independent design identity')
                    trace.append({'designTestId':'PT-JMS-TERM'+match[1],'class':name,'method':method,'xmlSha256':sha(p)})
        physical.update({module+':'+p.relative_to(target/'classes').as_posix():sha(p)for p in(target/'classes').rglob('*.class')})
        if module in TARGETS:
            nodes={c.get('name'):c for c in ET.parse(target/'site/jacoco/jacoco.xml').getroot().findall('package/class')}
            for name in TARGETS[module]:
                node=nodes['dev/codex/schubert/nk/'+name];counters[module+':'+name]={c.get('type'):{'covered':int(c.get('covered')),'missed':int(c.get('missed'))}for c in node.findall('counter')if c.get('type')in('LINE','METHOD','CLASS','BRANCH')}
    sources={p.relative_to(snapshot).as_posix():sha(p)for p in snapshot.glob('src/*/src/main/java/**/*.java')}
    if not(v['actualExit']==0 and v['source']==begin['source']==static['source']==SOURCE and v['sourceFixed']and v['phaseExits']==[0,0]and actual==expected and sum(map(len,actual.values()))==81 and len(actual)==22 and physical==static['auxClassHashes']and len(physical)==1666 and sources==static['allSourceHashes']and len(sources)==851 and counters==v['targetCounters']and set(v['staticIssues'])==set(CASES)and not any(v['staticIssues'].values())and {r['designTestId']for r in trace}=={'PT-JMS-TERM'+str(i).zfill(3)for i in range(1,5)}):raise ValueError('actual81/current Main/static/counters/trace')
    value={'actualExit':0,'source':SOURCE,'branch':'dev-foundation','run':path.parent.name,'startedUTC':v['startedUTC'],'completedUTC':v['completedUTC'],'archiveSha256':v['archiveSha256'],'originalManifestSha256':sha(path),'staticManifestSha256':sha(sp),'xmlHashes':xmls,'caseTrace':sorted(trace,key=lambda r:r['designTestId']),'tests':81,'suites':22,'mainSource':851,'physicalMain':1666,'phaseExits':[0,0],'staticIssues':v['staticIssues'],'targetCounters':counters,'targetFour100':v['targetFour100'],'formalAccepted':False,'fullCoverageClaimed':False,'ptAlternativeCompleted':0,'fullRegressionPending':True,'BUG1501Open':True,'vmActions':0,'toolchain':{'jdk':'25.0.4','maven':'3.9.12','jacoco':'0.8.15','spotbugs':'4.10.4.0'}}
    out=base/'PG5866-terminal81-v1';os.umask(0o077);out.mkdir()
    with(out/'manifest.json').open('x')as f:json.dump(value,f,ensure_ascii=False,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    print(json.dumps({'actualExit':0,'tests':81,'newDesignIdsTraced':4,'targetFour100':v['targetFour100'],'manifestSha256':sha(out/'manifest.json')}))


if __name__=='__main__':main()
