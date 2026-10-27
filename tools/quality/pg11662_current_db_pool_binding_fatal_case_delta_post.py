"""Independent historical sets, current XML, and22 concrete source-context facts; no product replay."""
from collections import Counter
import copy
from pathlib import Path
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from pg11462_current_gc_fake_guard_delta_post import historical
from pg11054_api_request_context import original_match
from public_java_digest_provenance import LEX
from pg11370_source_constructor_owner_audit import functions

SOURCE='b4810698856cc2ae7edabb899a47aad34ef52cc2'
OUT=data.BASE/'PG11662-current-db-pool-binding-fatal-case-delta-post-v1'
CHAIN=[
 ('PG11460-current-gc-fake-guard-delta-v1','3fa311d080bb8aa9ba82cdaf6c0fb45cd739fe4b3131a9d5e1473fcb91c841e2'),
 ('PG11490-current-api-web-gc-literal-delta-v1','07d118026d90370f563c0aa28916a65f05da1b8b9936fef8591db487eddc6a12'),
 ('PG11520-current-metric-http-literal-delta-v1','e97204190f4e62c5fd8dc1135e011f5ee1f2dd3346c462aaf8983508d084b1ab'),
 ('PG11552-current-memory-http-guard-delta-v1','27544edc188e17ec6ec38a7222dc8403298827e25762c67e56cee865e7b1e0bc'),
 ('PG11564-current-batch-repository-reason-delta-v1','7f74d22280372600bb6c8287e831f2759108756310473dc64c7caac364042a0a'),
 ('PG11574-current-four-repository-reason-delta-v1','7d8654ec83c6d8846b109ecb4a6cc11101fb13e904b0a722d96a727b2d316ffe'),
 ('PG11584-current-session-reason-delta-v1','8007dfb863b96964ad4921ff916f0adb21c3121b8fd8394506017f59c3b43432'),
 ('PG11594-current-admission-reason-delta-v1','877f695001a733ead184d078282c4f745836b7261b4628c09782919a1917f4b8'),
 ('PG11604-current-remaining-main-reason-delta-v2','32fc3e82b65c092166fa54ee9848d398cf5d832908823be129796170371f73ce'),
 ('PG11630-current-db-pool-binding-literal-delta-v1','7ed13627439a06052d80f43aca4e74b32d759ecc2daebbfdfe495d1b476829c9')]

def require(value,expected):
    if value!=expected:raise ValueError('exact original20 plus two new references, current-source pending22 and8 actual corrections required')

def main():
    invocation=capture(__file__);assert not OUT.exists();ids,refs,pending=historical()
    for folder,pin in CHAIN:
        p=data.BASE/folder/'manifest.json';m=data.read_checked(p,pin);d=data.read_checked(p.parent/'delta.json',m['deltaSha256'])
        scope=set(d['removedFindingIds'])|{r['id'] for r in d['freshRows']};reviewed={r['id'] for r in d['freshRows'] if r['contextManifestSha256']}
        ids=(ids-set(d['removedFindingIds']))|set(d['addedFindingIds']);refs=(refs-scope)|reviewed;pending=(pending-scope)|reviewed
    assert [len(ids),len(refs),len(pending)]==[8875,3070,531]
    mp=data.BASE/'PG11660-current-db-pool-binding-fatal-case-delta-v1/manifest.json';manifest=data.read_checked(mp,'dee8229dd3dbb1d2af8498d052beb3b1f9a814ba4718932e8fb01bf00e565eb8');delta=data.read_checked(mp.parent/'delta.json',manifest['deltaSha256'])
    normal=data.read_checked(data.BASE/'PG11644-db-pool-binding-fatal-case-six-compile-v1/manifest.json','b6ab06836da09a0be7d6337e3c3d269b030afc06efc18352b9eb1034886b77b6')
    old=data.read_checked(data.BASE/'PG11614-db-pool-binding-literal-six-compile-v1/manifest.json','da1fa15da3656d99970d1bd3afe64efee9a7fe5e153d2144af2f79c69662f16f')
    hashes=normal['begin']['inputHashes'];assert all(data.sha((data.ROOT/p).read_bytes())==h for p,h in hashes.items())
    assert {p:h for p,h in hashes.items() if old['begin']['inputHashes'][p]!=h}==delta['sourceInputDelta'] and len(delta['sourceInputDelta'])==2
    sp=data.BASE/'PG11648-db-pool-binding-fatal-case-static-v1';st=data.read_checked(sp/'manifest.json','acead561d795d044cc51826684268d6b2729f529fd86bd2bfa21688e887869c2');raw=(sp/'pmd.xml').read_bytes();assert data.sha(raw)==st['reports']['pmd']['sha256']
    actual=[(str(Path(f.get('name')).relative_to(data.ROOT)),n) for f in ET.fromstring(raw) if f.tag.rpartition('}')[2]=='file' for n in f if n.tag.rpartition('}')[2]=='violation']
    root=data.read_checked(data.BASE/'PG10690-current-global-static-post-v1/findings.json','92b57b1840edb7258e1e180b06a2f69af94fae594f9c9c549a0378b439116966')
    mapped={(p,tuple(sorted(n.attrib.items()))):original_match(p,n,root,actual)['id'] for p,n in actual};assert len(mapped)==len(set(mapped.values()))==22
    cp=data.BASE/'PG11651-db-pool-binding-current-owner-context-v1';cm=data.read_checked(cp/'manifest.json','581e4415fdddde304b466767d4cebed8a249dd7c82f3a41158b804a5b1df316b');cv=data.read_checked(cp/'review.json',cm['reviewSha256']);contexts={r['id']:r for r in cv['rows']};assert len(contexts)==22
    host=data.read_checked(data.BASE/'PG11646-db-pool-binding-fatal-case-host-v1/manifest.json','056a66e456e83ecdbcaffad464d50ce41d25955286457a364b188b92d43b687a');assert host['source']==SOURCE and host['observedTestExecutions']==30 and host['actualExit']==0
    kinds=Counter()
    for identity,row in contexts.items():
        assert mapped[(row['path'],tuple(sorted(row['attributes'].items())))]==identity and row['source']==SOURCE and row['sourceSha256']==hashes[row['path']]
        worker=row['attributes']['rule']=='CloseResource'
        assert row['attributes']['rule'] in ('DoNotUseThreads','CloseResource') and row['disposition']==('REQUIRED_CONTRACT' if worker else 'CONTEXT_NOT_APPLICABLE') and row['reason'] and row['previousReferenceRetainedAsHistorical']!=worker and row['newDispositionCreated']==worker and row['currentWholeJoinPending']
        text=(data.ROOT/row['path']).read_text();lines=text.splitlines(keepends=True);a=row['attributes'];point=sum(map(len,lines[:int(a['beginline'])-1]))+int(a['begincolumn'])-1;end=sum(map(len,lines[:int(a['endline'])-1]))+int(a['endcolumn'])
        assert data.sha(text[point:end].encode())==row['sourceSpanSha256'];ts=[(m.group(),m.start()) for m in LEX.finditer(text) if not m.group().startswith(('//','/*'))];index=next(i for i,(_,pos) in enumerate(ts) if pos==point)
        ma,mb,name=min((s for s in functions(ts) if s[0]<=index<=s[1]),key=lambda s:s[1]-s[0]);assert name==row['method'] and data.sha('\0'.join(t for t,_ in ts[ma:mb+1]).encode())==row['methodTokenSha256']
        compact=''.join(t for t,_ in ts);assert compact.count('Executors.newFixedThreadPool(2)')==1 and compact.count('workers.submit(')==2
        assert 'finally{release.countDown();workers.shutdownNow();assertTrue(workers.awaitTermination(30,TimeUnit.SECONDS));}' in compact
        assert 'first.get(30,TimeUnit.SECONDS);second.get(30,TimeUnit.SECONDS);' in compact and 'latch.await(30,TimeUnit.SECONDS)' in compact
        assert row['currentCase'] in host['begin']['cases'] and any(c['classname']==row['currentCase']['className'] and c['name']==row['currentCase']['method'] and not c['nonPass'] for c in host['cases'])
        assert row['productTestsExecutedByReview']==0 and not row['oldRuntimeReassigned'];kinds[row['kind']]+=1
    assert kinds==Counter(OWN_TWO_WORKERS=2,OWN_BOUNDED_TASK=4,FINALLY_OWN_STOP_WAIT=4,TYPE_ONLY=2,THREAD_IDENTITY_INTERRUPT_OR_STATE_OBSERVATION=8,REQUIRED_EXECUTOR_BOUNDED_STOP_FINALLY=2)
    fresh={r['id'] for r in delta['freshRows']};assert fresh==set(mapped.values())
    for row in delta['freshRows']:
        assert mapped[(row['path'],tuple(sorted(row['attributes'].items())))]==row['id'] and row['currentInputSha256']==hashes[row['path']] and not row['oldRuntimeReassigned']
        if row['id'] in contexts:assert row['contextManifestSha256']=='581e4415fdddde304b466767d4cebed8a249dd7c82f3a41158b804a5b1df316b' and row['status']=='SOURCE_REBOUND_CURRENT_WHOLE_PENDING'
        else:assert row['contextManifestSha256'] is None and row['status']=='UNCLASSIFIED_RETAINED'
    scope={r['id'] for r in root if r['path'] in delta['sourceInputDelta']}&ids;assert len(scope)==30 and len(scope&refs)==20 and scope&refs<=set(contexts) and scope&pending==scope&refs
    assert len({r['id'] for r in root if r['path'] in delta['sourceInputDelta']})==51 and delta['priorScopeCorrectionsRetained']==21
    removed=scope-fresh;assert len(removed)==8 and removed==set(delta['removedFindingIds']) and not delta['addedFindingIds'] and all(r['rule']=='AvoidLiteralsInIfCondition' for r in root if r['id'] in removed)
    current=ids-removed;cr=(refs-scope)|set(contexts);cpending=(pending-scope)|set(contexts)
    expected=dict(source=SOURCE,raw=len(current),refs=len(cr),pending=len(cpending),withoutReference=len(current-cr),corrections=len({r['id'] for r in root}-current),newRetained=len([i for i in current if i.startswith('PMD-NEW-')]),unclassified=len(fresh-set(contexts)))
    observed=dict(source=manifest['source'],raw=manifest['sourceDerivedRaw'],refs=manifest['joinedContextWarnings'],pending=manifest['sourceReboundCurrentWholePending'],withoutReference=manifest['noCurrentReferenceInThisJoin'],corrections=manifest['totalPriorCorrections'],newRetained=manifest['totalIntroducedDiagnosticsRetained'],unclassified=sum(r['contextManifestSha256'] is None for r in delta['freshRows']))
    require(observed,expected)
    for key,value in [('source','old'),('raw',8875),('refs',3070),('pending',531),('withoutReference',0),('corrections',542),('newRetained',0),('unclassified',1)]:
        bad=copy.deepcopy(observed);bad[key]=value;assert bad!=observed
        try:require(bad,expected)
        except ValueError:pass
        else:raise AssertionError('stale source/reference loss/double correction/invented classification accepted')
    verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,primaryManifestSha256=data.sha(mp.read_bytes()),counts=expected,metadataNegativeVectors=8,
        sourceCount=1810,sourceChanges=2,otherSourcesUnchanged=1808,threadReferencesSourceReauthenticated=20,newIndividualDispositions=0,unclassifiedCurrentScope=0,mainRaw=1512,testRaw=7355,productTestsExecuted=0,coverage=None,wholeCurrentAnalyzerReissued=False,wholeF03Accepted=False,newAccepted=0,effortPercent=None));print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__=='__main__':main()
