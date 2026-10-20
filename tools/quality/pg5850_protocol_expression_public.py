"""Independently read original105 XML/counters and all1666 bytes, never PT or native execution."""
import json
import os
import xml.etree.ElementTree as ET
from pg5540_snapshot_scratch_selected import ROOT,sha
from pg5844_protocol_expression_green import CASES,COUNTS,TARGETS,source_test_names

SOURCE='86287c3fb83b483050b88dce04bc644961682bc4';W=ROOT.parent/'pgpt-runs/PG379'


def four100(counters):
    return len(counters)==6 and all(set(c)=={'LINE','METHOD','CLASS','BRANCH'}and all(c[k]['missed']==0 and(c[k]['covered']>0 or k=='BRANCH')for k in c)for c in counters.values())


def main():
    path=W/'pg5844-protocol-expression-selected105-v1/manifest.safe.json';v=json.loads(path.read_bytes());snapshot=path.parent/'source';base=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional';sp=base/'PG5848-protocol-expression-static-v1/manifest.json';s=json.loads(sp.read_bytes());private=W/'pg5848-protocol-expression-static-v1/manifest.safe.json'
    if sha(sp)!='3c2ce6616b6b050543ec7ab9e580f2f2890d8bbf58fc7597da35a913c2f24100'or sha(private)!=s['privateManifestSha256']or sha(path)!=s['selectedManifestSha256']:raise ValueError('actual current105 and full source/static proof')
    proof=json.loads(private.read_bytes());expected={};actual={};xmls={};physical={};counters={}
    for module,classes in CASES.items():
        target=snapshot/('src/schubert-nk-'+module+'/target')
        for cls in classes:
            name='dev.codex.schubert.nk.'+cls;p=snapshot/('src/schubert-nk-'+module+'/src/test/java')/(name.replace('.','/')+'.java');expected[name]=source_test_names(p)
            if len(expected[name])!=COUNTS[cls.rsplit('.',1)[1]]:raise ValueError('exact Test source inventory')
        for p in(target/'surefire-reports').glob('TEST-*.xml'):
            tree=ET.parse(p).getroot();name=tree.get('name')
            if name in actual:raise ValueError('no duplicate suite')
            actual[name]=set();xmls[name]=sha(p)
            for case in tree.findall('testcase'):
                method=case.get('name','').split('(',1)[0]
                if method in actual[name]or any(n.tag in('failure','error','skipped','flakyFailure','flakyError','rerunFailure','rerunError')for n in case.iter()):raise ValueError('every actual selected case PASS exactly once')
                actual[name].add(method)
        physical.update({module+':'+p.relative_to(target/'classes').as_posix():sha(p)for p in(target/'classes').rglob('*.class')})
        if module in TARGETS:
            report=ET.parse(target/'site/jacoco/jacoco.xml').getroot();by_name={c.get('name'):c for c in report.findall('package/class')}
            for name in TARGETS[module]:
                node=by_name['dev/codex/schubert/nk/'+name];counters[module+':'+name]={c.get('type'):{'covered':int(c.get('covered')),'missed':int(c.get('missed'))}for c in node.findall('counter')if c.get('type')in('LINE','METHOD','CLASS','BRANCH')}
    sources={p.relative_to(snapshot).as_posix():sha(p)for p in snapshot.glob('src/*/src/main/java/**/*.java')}
    if not(v['actualExit']==0 and v['source']==proof['source']==SOURCE and v['phaseExits']==[0,0]and v['sourceFixed']and actual==expected and sum(map(len,actual.values()))==105 and len(actual)==26 and physical==proof['auxClassHashes']and len(physical)==1666 and sources==proof['allSourceHashes']and len(sources)==851 and counters==v['targetCounters']and four100(counters)and not any(v['staticIssues'].values())and set(v['staticIssues'])==set(CASES)and s['rawDiagnosticsRemovedByPg']==8 and s['pmdRawFindings']==1586):raise ValueError('actual105/26, six targets100 and exactly eight PG diagnostics removed')
    value={'actualExit':0,'source':SOURCE,'branch':'dev-foundation','run':'pg5844-protocol-expression-selected105-v1','startedUTC':v['startedUTC'],'completedUTC':v['completedUTC'],'archiveSha256':v['archiveSha256'],'originalManifestSha256':sha(path),'staticManifestSha256':sha(sp),'xmlHashes':xmls,'tests':105,'suites':26,'protocolTests':96,'newTestCasesAdded':0,'physicalMain':1666,'mainSource':851,'changedPhysicalClasses':s['changedPhysicalClasses'],'unchangedPhysicalClasses':s['unchangedPhysicalClasses'],'targetCounters':counters,'targetFour100':True,'rawDiagnosticsRemovedByPg':8,'pmdRawFindings':1586,'pmdProcessingErrors':0,'checkstyleFindings':0,'staticSixModuleIssues':v['staticIssues'],'phaseExits':[0,0],'toolchain':{'jdk':'25.0.4','maven':'3.9.12','jacoco':'0.8.15','spotbugs':'4.10.4.0'},'formalAccepted':False,'fullSourceFormalQualificationPending':True,'oldWholeNativeImported':False,'ptAlternativeCompleted':0,'vmActions':0}
    out=base/'PG5850-protocol-expression105-v1';os.umask(0o077);out.mkdir()
    with(out/'manifest.json').open('x')as f:json.dump(value,f,ensure_ascii=False,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    print(json.dumps({'actualExit':0,'tests':105,'targetSixFour100':True,'fixedRawDiagnostics':8,'rawRemaining':1586,'manifestSha256':sha(out/'manifest.json')}))


if __name__=='__main__':main()
