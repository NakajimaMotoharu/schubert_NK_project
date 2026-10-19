"""Rebind unchanged production/static bytes, preserve raw PMD and join three exact local-sink findings."""
import json
import os
import xml.etree.ElementTree as ET
from collections import Counter
from pg5540_snapshot_scratch_selected import ROOT,sha
from pg5738_local_audit_selected import SLOT as SELECTED
from pg5058_whole_case_projection import project_xml
from pmd_diagnostic_identity import diagnostic_row


def main():
    w=ROOT.parent/'pgpt-runs/PG379';path=w/SELECTED/'manifest.safe.json';v=json.loads(path.read_bytes());snapshot=path.parent/'source'
    sp=ROOT/'evidence/01_PT/001_NK-PRO-001/evidence/provisional/PG5734-enum48-static-v1/manifest.json'
    if sha(sp)!='81aa7ea5f48a0c93762d629f43bbdeeb8672a2379a69e175641499b680838e3a':raise ValueError('immutable original public static proof')
    public=json.loads(sp.read_bytes());private=w/'pg5734-enum48-static-v1/manifest.safe.json'
    if sha(private)!=public['privateManifestSha256']:raise ValueError('original static input metadata')
    old=json.loads(private.read_bytes())
    sources={p.relative_to(snapshot).as_posix():sha(p)for p in snapshot.glob('src/*/src/main/java/**/*.java')}
    if not(v['actualExit']==0 and v['selectedQualified']and v['sourceFixed']and(v['tests'],v['suites'])==(12,7)and sources==old['allSourceHashes']and v['allPhysicalMainSha256']==old['auxClassHashes']):raise ValueError('all849 source and1664 actual Main unchanged; actual new PT first')
    cases=[]
    for name,row in sorted(v['xmlHashes'].items()):
        filename='TEST-'+name+'.xml';xml=snapshot/('src/schubert-nk-'+row['module']+'/target/surefire-reports')/filename
        cases.extend(project_xml(row['module'],filename,xml.read_bytes(),row['sha256']))
    if len(cases)!=12 or len({r['testId']for r in cases})!=12:raise ValueError('original12 case identities')
    coverage=snapshot/'src/schubert-nk-web/target/site/jacoco/jacoco.xml';tree=ET.parse(coverage).getroot();methods=[m for c in tree.findall('package/class')if c.get('name')=='dev/codex/schubert/nk/web/logging/WebRequestLogProducer'for m in c.findall('method')if m.get('name')=='local']
    if len(methods)!=1:raise ValueError('exact local method report')
    counters={c.get('type'):{'covered':int(c.get('covered')),'missed':int(c.get('missed'))}for c in methods[0].findall('counter')}
    if not all(counters[k]['missed']==0 and counters[k]['covered']>0 for k in('LINE','METHOD','BRANCH')):raise ValueError('local actual line/method/branch all100')
    raw=w/'pg5734-enum48-static-v1/pmd.xml'
    if sha(raw)!=old['pmdXmlSha256']:raise ValueError('exact original XML, no analyzer replay')
    origin=w/'pg5732-enum48-selected-v2/source';rows=[]
    for file in ET.parse(raw).getroot().findall('{*}file'):
        relative=os.path.relpath(file.get('name'),origin)
        if relative not in sources:raise ValueError('all diagnostic paths in bound production')
        for violation in file.findall('{*}violation'):rows.append(diagnostic_row(relative,sources[relative],violation,len(rows)+1))
    if len(rows)!=1599 or len({r['findingId']for r in rows})!=1599:raise ValueError('all raw1599 individually unique')
    reviewed=[]
    for row in rows:
        if row['sourcePath'].endswith('/web/logging/WebRequestLogProducer.java')and(row['rule'],int(row['beginline']))in{('EmptyCatchBlock',225),('AvoidCatchingGenericException',225),('AvoidCatchingGenericException',230)}:
            row.update(status='REQUIRED_CONTRACT',reviewRef='1187_Web監査sink故障・独立契約仕様.md',designRefs=['SS312 §11','SS351 §3.1'],testRefs=['PT-F03-LOG001','PT-F03-LOG002','PT-F03-LOG003','PT-F03-LOG004'],reason='Exact local sink Runtime failure is followed outside catch by one bounded owner terminal signal and false return; complete returns before DB. Callback Runtime is bounded without raw cause; Error identity propagates. Not a successful audit/NPE normalization.',rawWarningRetained=True)
            reviewed.append(row['findingId'])
    if len(reviewed)!=3:raise ValueError('only three exact sink diagnostic spans')
    legacy=Counter(r['legacyFindingId']for r in rows);begin=json.loads((path.parent/'begin.safe.json').read_bytes())
    value={'actualExit':0,'source':v['source'],'productionMainSourceEquivalentTo':old['source'],'all849SourceAnd1664PhysicalMainEqual':True,'tests':12,'suites':7,'failedOrSkipped':v['failedOrSkipped'],'caseRefs':cases,'xmlHashes':v['xmlHashes'],'commands':begin['commands'],'archiveSha256':v['archiveSha256'],'selectedManifestSha256':sha(path),'staticSourceManifestSha256':sha(sp),'rawPmdXmlSha256':sha(raw),'pmdRawFindings':1599,'pmdReexecuted':False,'rawWarningRemoved':0,'newIdentitySchema':2,'uniqueFindingIds':1599,'legacyCollisionGroups':sum(n>1 for n in legacy.values()),'legacyCollidingRows':sum(n for n in legacy.values()if n>1),'individualSinkReviewed':3,'reviewedFindingIds':reviewed,'statusCounts':dict(Counter(r['status']for r in rows)),'localMethodCounters':counters,'webCoverageXmlSha256':sha(coverage),'ptAlternativeCompleted':0,'formalAccepted':False,'F03Accepted':False,'fullCoverageClaimed':False,'liveResourcesVerified':False,'vmActions':0}
    out=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG5740-local-audit-review-v1';os.umask(0o077);out.mkdir(parents=True)
    for name,data in [('manifest.json',value),('findings.json',rows)]:
        with(out/name).open('x')as f:json.dump(data,f,ensure_ascii=False,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    print(json.dumps({k:value[k]for k in('actualExit','source','tests','suites','uniqueFindingIds','legacyCollisionGroups','legacyCollidingRows','individualSinkReviewed','localMethodCounters','F03Accepted')}))
    print(json.dumps({'manifestSha256':sha(out/'manifest.json'),'findingsSha256':sha(out/'findings.json')}))


if __name__=='__main__':main()
