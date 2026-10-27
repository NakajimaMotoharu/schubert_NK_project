"""Independent historical sets/current26-to12 XML/hash/context join; eight negative metadata vectors."""
from pathlib import Path
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from pg11462_current_gc_fake_guard_delta_post import historical
from pg11662_current_db_pool_binding_fatal_case_delta_post import CHAIN
from pg11054_api_request_context import original_match

SOURCE='21daf2722f9b280ec005b1b971300774a1d3716f'
OUT=data.BASE/'PG11782-current-jdbc-collector-literal-delta-post-v1'
PIN='37154957f609bd2a59fe16b9f6e413e10b88c964240a6c53dbf7fb5685a4320a'

def require(value,expected):
    if any(value.get(k)!=v for k,v in expected.items()):raise ValueError('exact current14 corrections plus raw12/current reasons, all prior fixes/new8 retained required')

def main():
    invocation=capture(__file__);assert not OUT.exists();ids,refs,pending=historical()
    for folder,pin in [*CHAIN,('PG11660-current-db-pool-binding-fatal-case-delta-v1','dee8229dd3dbb1d2af8498d052beb3b1f9a814ba4718932e8fb01bf00e565eb8'),('PG11690-current-standard-composition-literal-delta-v1','ccb7aeead6352e24366214aede9948d3bfda1c7bf649b9bbb70d18d6d7821695'),('PG11720-current-jvm-system-literal-delta-v1','9034f7ef66b5b6a283df6f021e33aa2aed43dfe5b3817ce6f786c345b2871639'),('PG11750-current-mq-recorder-literal-delta-v1','687847fc012bb9850865b0570ab427c1df3e687626a53a75bb774e813f2287f2')]:
        p=data.BASE/folder/'manifest.json';m=data.read_checked(p,pin);d=data.read_checked(p.parent/'delta.json',m['deltaSha256']);scope=set(d['removedFindingIds'])|{r['id'] for r in d['freshRows']};reviewed={r['id'] for r in d['freshRows'] if r['contextManifestSha256']};ids=(ids-set(d['removedFindingIds']))|set(d['addedFindingIds']);refs=(refs-scope)|reviewed;pending=(pending-scope)|reviewed
    assert [len(ids),len(refs),len(pending)]==[8826,3085,562]
    p=data.BASE/'PG11780-current-jdbc-collector-literal-delta-v1/manifest.json';m=data.read_checked(p,PIN);d=data.read_checked(p.parent/'delta.json',m['deltaSha256'])
    normal=data.read_checked(data.BASE/'PG11764-jdbc-collector-literal-six-compile-v1/manifest.json','a47324817b02678e07f4b83fdd7450ac1f58bb3aef28c910bdd05cddc2df20f0');old=data.read_checked(data.BASE/'PG11734-mq-recorder-literal-six-compile-v1/manifest.json','7d0f5f532b32896695e553c7ae886cdfef02595cbeb3c54c85c78b95b541505b');hashes=normal['begin']['inputHashes'];assert all(data.sha((data.ROOT/path).read_bytes())==h for path,h in hashes.items());changed={path:h for path,h in hashes.items() if h!=old['begin']['inputHashes'][path]};assert changed==d['sourceInputDelta'] and len(changed)==2
    sp=data.BASE/'PG11768-jdbc-collector-literal-static-v1';st=data.read_checked(sp/'manifest.json','1fb16cae2dcaf613917f2a8bd4abce746130911ecf3525ab45b66c00748b3c68');raw=(sp/'pmd.xml').read_bytes();assert data.sha(raw)==st['reports']['pmd']['sha256'];actual=[(str(Path(f.get('name')).relative_to(data.ROOT)),n) for f in ET.fromstring(raw) if f.tag.rpartition('}')[2]=='file' for n in f if n.tag.rpartition('}')[2]=='violation']
    root=data.read_checked(data.BASE/'PG10690-current-global-static-post-v1/findings.json','92b57b1840edb7258e1e180b06a2f69af94fae594f9c9c549a0378b439116966');mapped={(path,tuple(sorted(n.attrib.items()))):original_match(path,n,root,actual)['id'] for path,n in actual}
    cp=data.BASE/'PG11771-jdbc-collector-owner-context-v1';cm=data.read_checked(cp/'manifest.json','64a2ab92fd7052a20b648757f326d1fdacc6d42bdc9c930d314b492a379abef1');context=data.read_checked(cp/'review.json',cm['reviewSha256']);contexts={r['id']:r for r in context['rows']};post=data.read_checked(data.BASE/'PG11773-jdbc-collector-owner-context-post-v1/manifest.json','e2dba97dfdd1195e72f2abd48bacf56887e6820766711c9bdfa98159269f8cb1');assert post['source']==SOURCE and post['actualExit']==0
    assert len(mapped)==len(set(mapped.values()))==len(d['freshRows'])==len(contexts)==12
    for row in d['freshRows']:
        assert mapped[(row['path'],tuple(sorted(row['attributes'].items())))]==row['id'] and row['currentInputSha256']==changed[row['path']] and row['source']==SOURCE and row['sourceKind']=='TEST' and not row['oldRuntimeReassigned']
        cr=contexts[row['id']];assert cr['source']==SOURCE and cr['reason'] and cr['sourceSha256']==row['currentInputSha256'] and cr['attributes']==row['attributes'] and cr['originalRowSha256']==row['originalRowSha256'] and cr['currentWholeJoinPending']
        assert row['contextManifestSha256']=='64a2ab92fd7052a20b648757f326d1fdacc6d42bdc9c930d314b492a379abef1' and row['status']=='SOURCE_REBOUND_CURRENT_WHOLE_PENDING'
    scope={r['id'] for r in root if r['path'] in changed}&ids;fresh=set(mapped.values());removed=scope-fresh
    assert len(scope)==26 and len(scope&refs)==12 and not scope&pending and len(removed)==14 and removed==set(d['removedFindingIds']) and not d['addedFindingIds'] and all(r['rule'] in ('AvoidDuplicateLiterals','AssignmentInOperand') for r in root if r['id'] in removed)
    ids-=removed;refs=(refs-scope)|fresh;pending=(pending-scope)|fresh
    assert len({r['id'] for r in root}-ids)==605 and len([i for i in ids if i.startswith('PMD-NEW-')])==8
    expected=dict(actualExit=0,source=SOURCE,sourceDerivedRaw=len(ids),totalPriorCorrections=605,totalIntroducedDiagnosticsRetained=8,joinedContextWarnings=len(refs),sourceReboundCurrentWholePending=len(pending),actualViolationCount=None,wholeF03Accepted=False,newAccepted=0)
    require(m,expected);negatives=0
    for key,value in [('source','0'*40),('sourceDerivedRaw',8847),('totalPriorCorrections',619),('totalIntroducedDiagnosticsRetained',0),('joinedContextWarnings',3086),('sourceReboundCurrentWholePending',562),('actualViolationCount',0),('wholeF03Accepted',True)]:
        bad=dict(m);bad[key]=value;assert bad!=m
        try:require(bad,expected)
        except ValueError:negatives+=1
        else:raise AssertionError('incorrect current set metadata accepted')
    verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,deltaManifestSha256=PIN,sourceDerivedRaw=len(ids),joinedContextWarnings=len(refs),sourceReboundCurrentWholePending=len(pending),unreferenced=len(ids-refs),totalCorrections=605,allIntroducedDiagnosticsRetained=8,metadataNegativeVectors=negatives,productTestsExecuted=0,coverage=None,wholeF03Accepted=False,newAccepted=0,effortPercent=None));print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__=='__main__':main()
