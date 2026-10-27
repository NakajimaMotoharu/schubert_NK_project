"""Independent historical sets/current13-to3 correction XML/hash/context join; eight unequal negative metadata vectors."""
from pathlib import Path
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from pg11462_current_gc_fake_guard_delta_post import historical
from pg11662_current_db_pool_binding_fatal_case_delta_post import CHAIN
from pg11054_api_request_context import original_match

SOURCE='ee82637a750105243ddeac665c61d27a781e5cf1'
OUT=data.BASE/'PG12122-current-authz-fixture-delta-post-v1'
PIN='0a0eec4237dc25616488cd267d1e3c82a30a315e0e140a4e69e646689125d44e'

def require(value,expected):
    if any(value.get(k)!=v for k,v in expected.items()):raise ValueError('exact current28 Test source correction with all775 fixes and raw3/current reasons, all prior fixes/new8 retained required')

def main():
    invocation=capture(__file__);assert not OUT.exists();ids,refs,pending=historical()
    for folder,pin in [*CHAIN,('PG11660-current-db-pool-binding-fatal-case-delta-v1','dee8229dd3dbb1d2af8498d052beb3b1f9a814ba4718932e8fb01bf00e565eb8'),('PG11690-current-standard-composition-literal-delta-v1','ccb7aeead6352e24366214aede9948d3bfda1c7bf649b9bbb70d18d6d7821695'),('PG11720-current-jvm-system-literal-delta-v1','9034f7ef66b5b6a283df6f021e33aa2aed43dfe5b3817ce6f786c345b2871639'),('PG11750-current-mq-recorder-literal-delta-v1','687847fc012bb9850865b0570ab427c1df3e687626a53a75bb774e813f2287f2'),('PG11780-current-jdbc-collector-literal-delta-v1','37154957f609bd2a59fe16b9f6e413e10b88c964240a6c53dbf7fb5685a4320a'),('PG11820-current-job-outbox-value-literal-delta-v1','2b0a3f645a9be16e1ce5267a5d9d2e8aa016dc9be0d1ab4d04b09fb44b1d878d'),('PG11850-current-mq-media-collector-value-delta-v1','8a0764023d4bcf3d3a4781fc8f38450d11b98141ce5af6fdea33ff763e976e42'),('PG11880-current-web-exporter-fixture-delta-v1','b72c0cd9d6b7a16a261742b9e5403bcf7b3f9c027b1ee264998c9a9f9324fdd6'),('PG11910-current-session-json-fixture-delta-v1','6758bab7f719df7b3faa8c9f9636726d8ac7b2a504572c37d66eade0e5d6ff30')]:
        p=data.BASE/folder/'manifest.json';m=data.read_checked(p,pin);d=data.read_checked(p.parent/'delta.json',m['deltaSha256']);scope=set(d['removedFindingIds'])|{r['id'] for r in d['freshRows']};reviewed={r['id'] for r in d['freshRows'] if r['contextManifestSha256']};ids=(ids-set(d['removedFindingIds']))|set(d['addedFindingIds']);refs=(refs-scope)|reviewed;pending=(pending-scope)|reviewed
    p=data.BASE/'PG11940-current-storage-attribute-fixture-delta-v1/manifest.json';prior=data.read_checked(p,'deab744572911ffb42236296858414377a9466d69bca6206ec2050027352813f');d=data.read_checked(p.parent/'delta.json',prior['deltaSha256']);scope=set(d['removedFindingIds'])|{r['id'] for r in d['freshRows']};reviewed={r['id'] for r in d['freshRows'] if r['contextManifestSha256']};ids=(ids-set(d['removedFindingIds']))|set(d['addedFindingIds']);refs=(refs-scope)|reviewed;pending=(pending-scope)|reviewed
    p=data.BASE/'PG11970-current-jms-proxy-fixture-delta-v1/manifest.json';prior=data.read_checked(p,'f984e15c42f752f486dcf54750f383d22fd5fa92fa7a425c27074b3b3edcd17e');d=data.read_checked(p.parent/'delta.json',prior['deltaSha256']);scope=set(d['removedFindingIds'])|{r['id'] for r in d['freshRows']};reviewed={r['id'] for r in d['freshRows'] if r['contextManifestSha256']};ids=(ids-set(d['removedFindingIds']))|set(d['addedFindingIds']);refs=(refs-scope)|reviewed;pending=(pending-scope)|reviewed
    p=data.BASE/'PG12000-current-web-business-wire-fixture-delta-v1/manifest.json';prior=data.read_checked(p,'d80140f38a55b3f2c554fb88f18bf82e18665233697381e0c0440fc8ea43401f');d=data.read_checked(p.parent/'delta.json',prior['deltaSha256']);scope=set(d['removedFindingIds'])|{r['id'] for r in d['freshRows']};reviewed={r['id'] for r in d['freshRows'] if r['contextManifestSha256']};ids=(ids-set(d['removedFindingIds']))|set(d['addedFindingIds']);refs=(refs-scope)|reviewed;pending=(pending-scope)|reviewed
    p=data.BASE/'PG12030-current-web-business-record-rebind-v1/manifest.json';prior=data.read_checked(p,'50e64f71443493a53d77da457f82b6d7c08a2a871e7bdcabb70d1347c2a86b47');d=data.read_checked(p.parent/'delta.json',prior['deltaSha256']);scope=set(d['removedFindingIds'])|{r['id'] for r in d['freshRows']};reviewed={r['id'] for r in d['freshRows'] if r['contextManifestSha256']};ids=(ids-set(d['removedFindingIds']))|set(d['addedFindingIds']);refs=(refs-scope)|reviewed;pending=(pending-scope)|reviewed
    p=data.BASE/'PG12060-current-api-web-scrape-fixture-delta-v1/manifest.json';prior=data.read_checked(p,'0227dc9c2406467a27a7b95674e3d680a56e3e4149ea0937a2f22ffbfad09370');d=data.read_checked(p.parent/'delta.json',prior['deltaSha256']);scope=set(d['removedFindingIds'])|{r['id'] for r in d['freshRows']};reviewed={r['id'] for r in d['freshRows'] if r['contextManifestSha256']};ids=(ids-set(d['removedFindingIds']))|set(d['addedFindingIds']);refs=(refs-scope)|reviewed;pending=(pending-scope)|reviewed
    p=data.BASE/'PG12090-current-media-wire-fixture-delta-v1/manifest.json';prior=data.read_checked(p,'a7a15a3a66183c8762b9b4e13639b352045990a31c019de03fc49a99ef888a55');d=data.read_checked(p.parent/'delta.json',prior['deltaSha256']);scope=set(d['removedFindingIds'])|{r['id'] for r in d['freshRows']};reviewed={r['id'] for r in d['freshRows'] if r['contextManifestSha256']};ids=(ids-set(d['removedFindingIds']))|set(d['addedFindingIds']);refs=(refs-scope)|reviewed;pending=(pending-scope)|reviewed
    assert [len(ids),len(refs),len(pending)]==[8652,3101,638]
    p=data.BASE/'PG12120-current-authz-fixture-delta-v1/manifest.json';m=data.read_checked(p,PIN);d=data.read_checked(p.parent/'delta.json',m['deltaSha256'])
    normal=data.read_checked(data.BASE/'PG12104-authz-fixture-six-compile-v1/manifest.json','1cffddad23dd78451013a1bb325a7e84682d733fb80d57f3205279d12d9774f9');old=data.read_checked(data.BASE/'PG12074-media-wire-fixture-six-compile-v1/manifest.json','2a15c3279d00cd2509f156e85442ae46124a3f1c5e8ea1b6b9ed0c82e29e81b0');hashes=normal['begin']['inputHashes'];assert all(data.sha((data.ROOT/path).read_bytes())==h for path,h in hashes.items());changed={path:h for path,h in hashes.items() if h!=old['begin']['inputHashes'][path]};assert changed==d['sourceInputDelta'] and len(changed)==1
    sp=data.BASE/'PG12109-authz-fixture-static-v2';st=data.read_checked(sp/'manifest.json','debf7b4ce804a32e6b5c797e4fc5b1a2c129bf7caa065a1891487e50fa31ff6b');raw=(sp/'pmd.xml').read_bytes();assert data.sha(raw)==st['reports']['pmd']['sha256'];actual=[(str(Path(f.get('name')).relative_to(data.ROOT)),n) for f in ET.fromstring(raw) if f.tag.rpartition('}')[2]=='file' for n in f if n.tag.rpartition('}')[2]=='violation']
    root=data.read_checked(data.BASE/'PG10690-current-global-static-post-v1/findings.json','92b57b1840edb7258e1e180b06a2f69af94fae594f9c9c549a0378b439116966');mapped={(path,tuple(sorted(n.attrib.items()))):original_match(path,n,root,actual)['id'] for path,n in actual}
    cp=data.BASE/'PG12111-authz-fixture-context-v1';cm=data.read_checked(cp/'manifest.json','6a121b49363d0e06818a1444a0938477220d6ae9b23e8588d739d748978a5a22');context=data.read_checked(cp/'review.json',cm['reviewSha256']);contexts={r['id']:r for r in context['rows']};post=data.read_checked(data.BASE/'PG12113-authz-fixture-context-post-v1/manifest.json','59fa4f28c7d477a4b920f17edb772d16447dc3145220aa36cb2ffc60dd334158');assert post['source']==SOURCE and post['actualExit']==0
    assert len(mapped)==len(set(mapped.values()))==len(d['freshRows'])==len(contexts)==3
    for row in d['freshRows']:
        assert mapped[(row['path'],tuple(sorted(row['attributes'].items())))]==row['id'] and row['currentInputSha256']==changed[row['path']] and row['source']==SOURCE and row['sourceKind']=='TEST' and not row['oldRuntimeReassigned']
        cr=contexts[row['id']];assert cr['source']==SOURCE and cr['reason'] and cr['sourceSha256']==row['currentInputSha256'] and cr['attributes']==row['attributes'] and cr['originalRowSha256']==row['originalRowSha256'] and cr['currentWholeJoinPending']
        assert row['contextManifestSha256']=='6a121b49363d0e06818a1444a0938477220d6ae9b23e8588d739d748978a5a22' and row['status']=='SOURCE_REBOUND_CURRENT_WHOLE_PENDING'
    scope={r['id'] for r in root if r['path'] in changed}&ids;fresh=set(mapped.values());removed=scope-fresh
    assert len(scope)==13 and len(scope&refs)==2 and len(scope&pending)==0 and len(removed)==10 and removed==set(d['removedFindingIds']) and not d['addedFindingIds'] and all(r['rule'] in ('AvoidDuplicateLiterals',) for r in root if r['id'] in removed)
    original_scope={r['id'] for r in root if r['path'] in changed};assert len(original_scope)==13 and len(original_scope-ids)==0 and len(set(d['removedFindingIds']))==10 and d['priorScopeCorrectionsRetained']==0
    ids-=removed;refs=(refs-scope)|fresh;pending=(pending-scope)|fresh
    assert len({r['id'] for r in root}-ids)==775 and len([i for i in ids if i.startswith('PMD-NEW-')])==8
    expected=dict(actualExit=0,source=SOURCE,sourceDerivedRaw=len(ids),totalPriorCorrections=775,totalIntroducedDiagnosticsRetained=8,joinedContextWarnings=len(refs),sourceReboundCurrentWholePending=len(pending),actualViolationCount=None,wholeF03Accepted=False,newAccepted=0)
    require(m,expected);negatives=0
    for key,value in [('source','0'*40),('sourceDerivedRaw',8812),('totalPriorCorrections',605),('totalIntroducedDiagnosticsRetained',0),('joinedContextWarnings',3093),('sourceReboundCurrentWholePending',574),('actualViolationCount',0),('wholeF03Accepted',True)]:
        bad=dict(m);bad[key]=value;assert bad!=m
        try:require(bad,expected)
        except ValueError:negatives+=1
        else:raise AssertionError('incorrect current set metadata accepted')
    verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,deltaManifestSha256=PIN,sourceDerivedRaw=len(ids),joinedContextWarnings=len(refs),sourceReboundCurrentWholePending=len(pending),unreferenced=len(ids-refs),totalCorrections=775,allIntroducedDiagnosticsRetained=8,metadataNegativeVectors=negatives,productTestsExecuted=0,coverage=None,wholeF03Accepted=False,newAccepted=0,effortPercent=None));print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__=='__main__':main()
