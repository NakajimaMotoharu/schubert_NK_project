"""Rebind unchanged Main static facts to the final Test source; never rerun the analyzer/PT."""
import copy
import json
import os
import subprocess
from pg5540_snapshot_scratch_selected import ROOT,TC,sha

SOURCE='2e3b0d50679ad6f1a984e25bd400db6f3ad9e798'
W=ROOT.parent/'pgpt-runs/PG379';BASE=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional'
SLOT='pg5810-rollback-static-reauth-v1';PUBLIC='PG5810-rollback-static-reauth-v1'


def bind_identity(old_sources,new_sources,old_classes,new_classes):
    if len(old_sources)!=850 or len(old_classes)!=1665 or old_sources!=new_sources or old_classes!=new_classes:raise ValueError('all850 Main and1665 actual classes exactly unchanged, no partial source borrowing')


def main():
    oldp=W/'pg5804-rollback-static-v1/manifest.safe.json';pub=BASE/'PG5804-rollback-static-v1/manifest.json'
    if sha(oldp)!='3056713dab82cd42ce5242f694ad430d582a8573435eaf91cf7c613c628ce6ec'or sha(pub)!='48fa559a73edeeb7d11fc278fb30d938aa17671e430cb9ede5508ecf43a7c7da':raise ValueError('exact prior actual analyzer and physical proof')
    old=json.loads(oldp.read_bytes());p=W/'pg5800-rollback-selected54-v5/manifest.safe.json';v=json.loads(p.read_bytes());snapshot=p.parent/'source'
    if not(v['source']==SOURCE and v['actualExit']==0 and v['selectedQualified']and v['exactInventory']and v['sourceFixed']and v['phaseExits']==[0,0]and(v['tests'],v['suites'])==(54,15)and not v['failedOrSkipped']and len(v['staticIssues'])==6 and not any(v['staticIssues'].values())):raise ValueError('new Test source current54 and six static0 first')
    sources={p.relative_to(snapshot).as_posix():sha(p)for p in snapshot.glob('src/*/src/main/java/**/*.java')};classes={m+':'+p.relative_to(snapshot/('src/schubert-nk-'+m+'/target/classes')).as_posix():sha(p)for m in v['staticIssues']for p in(snapshot/('src/schubert-nk-'+m+'/target/classes')).rglob('*.class')}
    bind_identity(old['allSourceHashes'],sources,old['auxClassHashes'],classes)
    if classes!=v['allPhysicalMainSha256']:raise ValueError('actual classes, not a declared old map')
    before=W/'pg5800-rollback-selected54-v4/source'
    for name in('pmd.xml','checkstyle.xml'):
        if sha(before/'tools/quality/static'/name)!=sha(snapshot/'tools/quality/static'/name):raise ValueError('all original rules/exclusions fixed')
    if subprocess.check_output(['git','diff',old['source'],SOURCE,'--','pom.xml','.mvn','mvnw','program/characterization','tools/quality/static'],cwd=ROOT):raise ValueError('no build/type/dependency/characterization change')
    if sha(TC/'static-gates-20261015/record-fix-v1/pmd-record-1298.jar')!='4859fb956de018a843abe55ddb92b0a98921878b80525aaa2a77c5b5d8c2820c'or sha(TC/'static-gates-20261015/checkstyle-14.3.0-all.jar')!='754e218ab1fcabb1e1c5f8530e9d3aa37636806c22987bb279dd907a6ee749b2':raise ValueError('same pinned analyzers, no new invocation')
    if sha(oldp.parent/'pmd.xml')!=old['pmdXmlSha256']or sha(oldp.parent/'checkstyle.xml')!=old['checkstyleXmlSha256']:raise ValueError('original analyzer outputs retained')
    out=W/SLOT;os.umask(0o077);out.mkdir(mode=0o700);value=copy.deepcopy(old)
    value.update(source=SOURCE,actualExit=0,executionKind='STATIC_SOURCE_REAUTHENTICATION_NO_ANALYZER_EXECUTION',actualAnalyzerSource=old['source'],actualAnalyzerPrivateManifestSha256=sha(oldp),actualAnalyzerPublicManifestSha256=sha(pub),sourceReauthenticationBasis='all850 full Main source and1665 actual compiled classes identical; rules/build/type dependencies unchanged',analyzerReexecuted=False,selectedManifestSha256=sha(p),selectedTargetActualCounters=v['targetCounters'],newPtExecuted=0,newDispositionsCreated=0,formalAccepted=False)
    path=out/'manifest.safe.json'
    with path.open('x')as f:json.dump(value,f,sort_keys=True);f.flush();os.fsync(f.fileno())
    projected={k:x for k,x in value.items()if k not in('commands','allSourceHashes','auxClassHashes')};projected.update(privateManifestSha256=sha(path),inventoryReferencePath=(pub.parent/'findings.json').relative_to(ROOT).as_posix(),inventorySha256=sha(pub.parent/'findings.json'))
    public=BASE/PUBLIC;public.mkdir()
    with(public/'manifest.json').open('x')as f:json.dump(projected,f,ensure_ascii=False,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    print(json.dumps({'actualExit':0,'source':SOURCE,'actualAnalyzerSource':old['source'],'analyzerReexecuted':False,'mainSourceFiles':850,'physicalMain':1665,'rawFindings':old['pmdRawFindings'],'manifestSha256':sha(public/'manifest.json')}))


if __name__=='__main__':main()
